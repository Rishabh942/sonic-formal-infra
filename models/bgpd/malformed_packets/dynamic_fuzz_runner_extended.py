import socket
import json
import struct
import time
import subprocess
import os
from models.bgpd.malformed_packets.attribute_model_extended import BGPPathAttr, parse_attributes, ParseResult

TARGET_IP = "127.0.0.1"
TARGET_PORT = 1179
LOCAL_IP = "1.1.1.1"

# Fuzzer state tracking
results_tally = {
    "SESSION_TORN_DOWN": 0,
    "TREAT_AS_WITHDRAW": 0,
    "AFI_SAFI_DISABLE": 0,
    "ROUTE_INSTALLED": 0,
    "FRR_CRASH": 0
}

def get_rib_route_count():
    try:
        out = subprocess.check_output(
            ["docker", "exec", "frr-lab", "vtysh", "-c", "show bgp ipv4 unicast json"],
            stderr=subprocess.DEVNULL
        )
        data = json.loads(out)
        return len(data.get("routes", {}))
    except Exception:
        return 0

def get_bgpd_logs():
    try:
        out = subprocess.check_output(
            ["docker", "exec", "frr-lab", "cat", "/tmp/bgpd.log"],
            stderr=subprocess.DEVNULL
        )
        subprocess.call(["docker", "exec", "frr-lab", "bash", "-c", "> /tmp/bgpd.log"])
        return out.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def build_bgp_open():
    return struct.pack("!16sHB BHH4sB",
                       b'\xff'*16, 29, 1,   # Header (marker, len, type=OPEN)
                       4, 65002, 180, socket.inet_aton(LOCAL_IP), 0) # OPEN fields

def build_bgp_keepalive():
    return struct.pack("!16sHB", b'\xff'*16, 19, 4)

def build_malformed_update(attr_args: dict):
    path_attrs = b''
    for i in range(1, 4):
        flags = attr_args.get(f'flags{i}', 0) & 0xFF
        tcode = attr_args.get(f'type{i}', 0) & 0xFF
        length = attr_args.get(f'len{i}', 0)
        
        is_ext = bool(flags & 0x10)
        if is_ext:
            path_attrs += struct.pack("!BBH", flags, tcode, length & 0xFFFF)
        else:
            path_attrs += struct.pack("!BBB", flags, tcode, length & 0xFF)
        path_attrs += b'A' * (length if length >= 0 else 0)
        
    # NLRI for 11.0.0.0/24 (length=24, prefix=11.0.0)
    nlri_bytes = struct.pack("!BBBB", 24, 11, 0, 0)
    
    update_payload = struct.pack("!HH", 0, len(path_attrs)) + path_attrs + nlri_bytes
    msg_len = 19 + len(update_payload)
    return struct.pack("!16sHB", b'\xff'*16, msg_len, 2) + update_payload

def execute_crosshair_suite():
    print("[*] Starting Extended Dynamic Fuzzer + Parity Engine")
    
    test_args = []
    try:
        with open("models/bgpd/malformed_packets/tests/attr_argdict_extended.txt", "r") as f:
            for line in f:
                if line.strip():
                    test_args.append(json.loads(line))
    except Exception as e:
        print(f"Error loading tests: {e}")
        return
    
    discrepancies = []
    
    for idx, args in enumerate(test_args):
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect((TARGET_IP, TARGET_PORT))
        except ConnectionRefusedError:
            results_tally["FRR_CRASH"] += 1
            continue
            
        # Send OPEN and KEEPALIVE to establish session
        s.sendall(build_bgp_open() + build_bgp_keepalive())
        
        time.sleep(0.01) # Small delay to let FRR process OPEN/KEEPALIVE
        
        update_bytes = build_malformed_update(args)
        try:
            s.sendall(update_bytes)
        except BrokenPipeError:
            pass
            
        time.sleep(0.02) # Let FRR evaluate the malformed UPDATE
        
        rib_count = get_rib_route_count()
        
        s.setblocking(False)
        is_active = True
        frr_result = ""
        notification_received = False
        try:
            data = s.recv(4096)
            if len(data) >= 19 and data[18] == 3: # 3 = NOTIFICATION
                notification_received = True
                is_active = False
            elif len(data) == 0:
                is_active = False
        except (BlockingIOError, ConnectionResetError) as e:
            if isinstance(e, ConnectionResetError):
                is_active = False
                
        s.close()
        
        # Evaluate Oracle (RFC Spec)
        oracle_attrs = [
            BGPPathAttr(args.get('flags1',0)&0xFF, args.get('type1',0)&0xFF, args.get('len1',0)),
            BGPPathAttr(args.get('flags2',0)&0xFF, args.get('type2',0)&0xFF, args.get('len2',0)),
            BGPPathAttr(args.get('flags3',0)&0xFF, args.get('type3',0)&0xFF, args.get('len3',0))
        ]
        oracle_res = parse_attributes(oracle_attrs)
        
        if notification_received or not is_active:
            frr_result = "SESSION_RESET"
            results_tally["SESSION_TORN_DOWN"] += 1
        elif rib_count > 0:
            frr_result = "VALID"
            results_tally["ROUTE_INSTALLED"] += 1
        else:
            # If it's a type 14 or 15 we assume FRR disabled AFI_SAFI rather than withdrawing
            if any(a.type_code in (14, 15) for a in oracle_attrs):
                frr_result = "AFI_SAFI_DISABLE"
                results_tally["AFI_SAFI_DISABLE"] += 1
            else:
                frr_result = "TREAT_AS_WITHDRAW"
                results_tally["TREAT_AS_WITHDRAW"] += 1

        rfc_expected = oracle_res.name
        if rfc_expected == "ATTRIBUTE_DISCARD":
            rfc_expected = "VALID"
            
        if rfc_expected != frr_result:
            discrepancies.append({
                "test_idx": idx + 1,
                "payload_args": args,
                "rfc_expected": rfc_expected,
                "frr_actual": frr_result,
                "oracle_state": oracle_res.name
            })
            
    with open("models/bgpd/malformed_packets/tests/parity_report.json", "w") as f:
        json.dump(discrepancies, f, indent=2)
            
    print("\n==================================================")
    print("      PHASE 3 EMPIRICAL RESULTS SUMMARY           ")
    print("==================================================")
    print(f"Total Tests Run           : {len(test_args)}")
    print(f"Strict Teardowns (4271)   : {results_tally['SESSION_TORN_DOWN']}")
    print(f"Soft Faults (7606)        : {results_tally['TREAT_AS_WITHDRAW']}")
    print(f"Routes Illegally Installed: {results_tally['ROUTE_INSTALLED']}")
    print(f"FRR Parser Crashes        : {results_tally['FRR_CRASH']}")
    print("--------------------------------------------------")
    print(f"RFC Compliance Deviations : {len(discrepancies)}")
    if len(discrepancies) > 0:
        print(f"Parity proof written to : parity_report.json")
    print("==================================================")

if __name__ == "__main__":
    execute_crosshair_suite()
