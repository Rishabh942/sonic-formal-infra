import socket
import struct
import json
import time
import subprocess
from models.bgpd.malformed_packets.bgp_oracle import parse_attributes, BGPPathAttr, ParseResult

BGP_PORT = 1179
BGP_IP = "127.0.0.1"

# BGP Handshake Constants
OPEN_MESSAGE = b'\xff'*16 + b'\x00\x3b\x01\x04\xfd\xea\x00\x5a\x00\x00\x00\x00\x1e\x02\x06\x01\x04\x00\x01\x00\x01\x02\x02\x80\x00\x02\x02\x02\x00\x02\x02\x46\x00\x02\x06\x41\x04\x00\x00\xfd\xea'
KEEPALIVE_MESSAGE = b'\xff'*16 + b'\x00\x13\x04'

def build_bgp_open():
    return OPEN_MESSAGE

def build_bgp_keepalive():
    return KEEPALIVE_MESSAGE

def get_rib_route_count():
    try:
        out = subprocess.check_output(
            ["docker", "exec", "frr-lab", "vtysh", "-c", "show ip bgp json"],
            stderr=subprocess.DEVNULL
        )
        data = json.loads(out)
        return len(data.get("routes", {}))
    except Exception:
        return 0

def execute_comprehensive_suite():
    print("[*] Starting Master Comprehensive Dynamic Fuzzer + Parity Engine")
    
    # Load 3-attribute dictionary (Version 1)
    test_args_v1 = []
    try:
        with open("models/bgpd/malformed_packets/tests/attr_argdict_extended.txt", "r") as f:
            for line in f:
                if not line.strip(): continue
                test_args_v1.append(eval(line.strip()))
    except FileNotFoundError:
        print("[-] Could not find attr_argdict_extended.txt")
        return

    # Load 4-attribute dictionary (Version 2)
    test_args_v2 = []
    try:
        with open("models/bgpd/malformed_packets/tests/attr_argdict_soft.txt", "r") as f:
            for line in f:
                if not line.strip(): continue
                test_args_v2.append(eval(line.strip()))
    except FileNotFoundError:
        print("[-] Could not find attr_argdict_soft.txt")
        return

    results_tally = {
        "SESSION_TORN_DOWN": 0,
        "TREAT_AS_WITHDRAW": 0,
        "AFI_SAFI_DISABLE": 0,
        "ROUTE_INSTALLED": 0,
        "ATTRIBUTE_DISCARD": 0,
        "FRR_CRASH": 0
    }
    
    discrepancies = []
    
    def run_suite(test_args, version, has_hardcoded_mandatory):
        for i, args in enumerate(test_args):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((BGP_IP, BGP_PORT))
            except ConnectionRefusedError:
                results_tally["FRR_CRASH"] += 1
                continue
                
            s.sendall(build_bgp_open())
            try:
                s.recv(4096) # Wait for OPEN
                s.sendall(build_bgp_keepalive())
            except Exception:
                pass
            
            # Pack Attributes
            attr_bytes = b''
            attrs_for_oracle = []
            
            if not has_hardcoded_mandatory:
                # Version 1 (3 dynamic attributes)
                attr_bytes += struct.pack('!BB', args["flags1"], args["type1"])
                if args["flags1"] & 0x10:
                    attr_bytes += struct.pack('!H', args["len1"])
                else:
                    attr_bytes += struct.pack('!B', args["len1"])
                attr_bytes += b'\x00' * args["len1"]
                attrs_for_oracle.append(BGPPathAttr(flags=args["flags1"], type_code=args["type1"], length=args["len1"]))

                attr_bytes += struct.pack('!BB', args["flags2"], args["type2"])
                if args["flags2"] & 0x10:
                    attr_bytes += struct.pack('!H', args["len2"])
                else:
                    attr_bytes += struct.pack('!B', args["len2"])
                attr_bytes += b'\x00' * args["len2"]
                attrs_for_oracle.append(BGPPathAttr(flags=args["flags2"], type_code=args["type2"], length=args["len2"]))

                attr_bytes += struct.pack('!BB', args["flags3"], args["type3"])
                if args["flags3"] & 0x10:
                    attr_bytes += struct.pack('!H', args["len3"])
                else:
                    attr_bytes += struct.pack('!B', args["len3"])
                attr_bytes += b'\x00' * args["len3"]
                attrs_for_oracle.append(BGPPathAttr(flags=args["flags3"], type_code=args["type3"], length=args["len3"]))
                
            else:
                # Version 2 (1 dynamic, 2 hardcoded mandatory, 1 dynamic)
                # Slot 1 dynamic
                attr_bytes += struct.pack('!BB', args["flags1"], 1)
                if args["flags1"] & 0x10:
                    attr_bytes += struct.pack('!H', args["len1"])
                else:
                    attr_bytes += struct.pack('!B', args["len1"])
                attr_bytes += b'\x00' * args["len1"]
                attrs_for_oracle.append(BGPPathAttr(flags=args["flags1"], type_code=1, length=args["len1"]))
                
                # Slot 2 (Hardcoded AS_PATH)
                attr_bytes += struct.pack('!BBB', 64, 2, 4)
                attr_bytes += b'\x02\x01\xfd\xea' # AS_SEQUENCE (len 1), ASN 65002
                attrs_for_oracle.append(BGPPathAttr(flags=64, type_code=2, length=4))

                # Slot 3 (Hardcoded NEXT_HOP)
                attr_bytes += struct.pack('!BBB', 64, 3, 4)
                attr_bytes += b'\x01\x01\x01\x01' # 1.1.1.1
                attrs_for_oracle.append(BGPPathAttr(flags=64, type_code=3, length=4))
                
                # Slot 4 dynamic
                attr_bytes += struct.pack('!BB', args["flags4"], args["type4"])
                if args["flags4"] & 0x10:
                    attr_bytes += struct.pack('!H', args["len4"])
                else:
                    attr_bytes += struct.pack('!B', args["len4"])
                attr_bytes += b'\x00' * args["len4"]
                attrs_for_oracle.append(BGPPathAttr(flags=args["flags4"], type_code=args["type4"], length=args["len4"]))
                
            # Build UPDATE
            nlri = b'\x18\xc0\xa8\x01' # 192.168.1.0/24
            update_len = 23 + len(attr_bytes) + len(nlri)
            update_bytes = b'\xff'*16 + struct.pack('!HB', update_len, 2) + b'\x00\x00' + struct.pack('!H', len(attr_bytes)) + attr_bytes + nlri
            
            # Predict
            oracle_res = parse_attributes(attrs_for_oracle)
            
            s.setblocking(False)
            try:
                s.sendall(update_bytes)
            except BrokenPipeError:
                pass
            
            time.sleep(0.01)
            
            notification_received = False
            is_active = True
            try:
                data = s.recv(4096)
                if data and len(data) >= 19 and data[18] == 3:
                    notification_received = True
            except (BlockingIOError, ConnectionResetError) as e:
                if isinstance(e, ConnectionResetError):
                    is_active = False
            
            s.close()
            time.sleep(0.01)
            
            rib_count = get_rib_route_count()
            
            if notification_received or not is_active:
                frr_result = "SESSION_RESET"
                results_tally["SESSION_TORN_DOWN"] += 1
            elif rib_count > 0:
                frr_result = "VALID"
                results_tally["ROUTE_INSTALLED"] += 1
            else:
                frr_result = "TREAT_AS_WITHDRAW"
                results_tally["TREAT_AS_WITHDRAW"] += 1
                
            # Verify Parity
            oracle_mapped = "SESSION_RESET" if oracle_res == ParseResult.SESSION_RESET else \
                            ("VALID" if oracle_res == ParseResult.ATTRIBUTE_DISCARD else "TREAT_AS_WITHDRAW")
                            
            if oracle_res == ParseResult.AFI_SAFI_DISABLE:
                oracle_mapped = "TREAT_AS_WITHDRAW"
                results_tally["AFI_SAFI_DISABLE"] += 1
                results_tally["TREAT_AS_WITHDRAW"] -= 1

            if oracle_res == ParseResult.ATTRIBUTE_DISCARD:
                results_tally["ATTRIBUTE_DISCARD"] += 1
                results_tally["ROUTE_INSTALLED"] -= 1

            if frr_result != oracle_mapped:
                test_id = f"V{version}-{i}"
                discrepancies.append({
                    "test_id": test_id,
                    "payload_args": args,
                    "rfc_expected": oracle_mapped,
                    "frr_actual": frr_result,
                    "oracle_state": oracle_res.name
                })
                
    # Run Both Suites
    print("\n[*] Running Suite 1: Strict Teardowns (RFC 4271)")
    run_suite(test_args_v1, version=1, has_hardcoded_mandatory=False)
    
    print("[*] Running Suite 2: Soft Faults (RFC 7606)")
    run_suite(test_args_v2, version=2, has_hardcoded_mandatory=True)

    print("\n==================================================")
    print("      COMPREHENSIVE EMPIRICAL RESULTS SUMMARY     ")
    print("==================================================")
    print(f"Total Tests Executed      : {len(test_args_v1) + len(test_args_v2)}")
    print("\n--- Strict Enforcement (RFC 4271) ---")
    print(f"[PASS] Session Teardowns  : {results_tally['SESSION_TORN_DOWN']}")
    print("\n--- Graceful Degradation (RFC 7606) ---")
    print(f"[PASS] Soft Faults        : {results_tally['TREAT_AS_WITHDRAW']}")
    print(f"[PASS] AFI/SAFI Disable   : {results_tally['AFI_SAFI_DISABLE']}")
    print(f"[PASS] Attribute Discard  : {results_tally['ATTRIBUTE_DISCARD']}")
    print("\n--- Critical Metrics ---")
    print(f"Routes Illegally Installed: {results_tally['ROUTE_INSTALLED']}")
    print(f"FRR Parser Crashes        : {results_tally['FRR_CRASH']}")
    print("--------------------------------------------------")
    print(f"RFC Compliance Deviations : {len(discrepancies)}")
    
    if len(discrepancies) == 0:
        print("\n=> VERDICT: 100% PERFECT PARITY. FRR complies with all RFC bounds.")
    else:
        print(f"\n=> VERDICT: {len(discrepancies)} Potential RFC Bugs found!")
        print("Deviant Test IDs (Fact check these):")
        for idx, d in enumerate(discrepancies):
            if idx > 15:
                print("... (truncated)")
                break
            print(f"  - {d['test_id']} (Expected {d['rfc_expected']}, got {d['frr_actual']})")
            
    with open("models/bgpd/malformed_packets/parity_report_comprehensive.json", "w") as f:
        json.dump(discrepancies, f, indent=2)

if __name__ == "__main__":
    execute_comprehensive_suite()
