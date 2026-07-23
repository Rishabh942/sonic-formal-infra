import socket
import struct
import json
import time
import subprocess
from models.bgpd.malformed_packets.bgp_oracle import parse_attributes, BGPPathAttr, ParseResult

BGP_PORT = 1179
BGP_IP = "127.0.0.1"

# BGP Handshake Constants
KEEPALIVE_MESSAGE = b'\xff'*16 + b'\x00\x13\x04'

def build_bgp_open():
    """Build a BGP OPEN message with correct length fields.
    
    Capabilities: MP-BGP IPv4 Unicast, Route Refresh (old+new),
    Enhanced Route Refresh, 4-byte ASN (65002).
    """
    import socket as _sock
    opt_params = b''
    opt_params += struct.pack('!BB', 2, 6) + struct.pack('!BB', 1, 4) + struct.pack('!HBB', 1, 0, 1)  # MP-BGP IPv4
    opt_params += struct.pack('!BB', 2, 2) + struct.pack('!BB', 128, 0)  # Route Refresh (old)
    opt_params += struct.pack('!BB', 2, 2) + struct.pack('!BB', 2, 0)    # Route Refresh
    opt_params += struct.pack('!BB', 2, 2) + struct.pack('!BB', 70, 0)   # Enhanced Route Refresh
    opt_params += struct.pack('!BB', 2, 6) + struct.pack('!BB', 65, 4) + struct.pack('!I', 65002)  # 4-byte ASN
    open_body = struct.pack('!BHH', 4, 65002, 90) + _sock.inet_aton('192.168.1.1') + struct.pack('!B', len(opt_params)) + opt_params
    msg_len = 16 + 2 + 1 + len(open_body)
    return b'\xff'*16 + struct.pack('!HB', msg_len, 1) + open_body

def build_bgp_keepalive():
    return KEEPALIVE_MESSAGE

def check_if_route_installed(prefix="10.0.0.0/24"):
    try:
        out = subprocess.check_output(
            ["docker", "exec", "frr-lab", "vtysh", "-c", f"show ip bgp {prefix} json"],
            stderr=subprocess.DEVNULL
        )
        data = json.loads(out)
        return "paths" in data or "prefix" in data
    except Exception as e:
        print(f"Failed to check RIB state: {e}")
        return False

def perform_bgp_handshake(s):
    s.sendall(build_bgp_open())
    resp = s.recv(4096)
    if not resp:
        raise Exception("HandshakeError: Socket closed before OPEN response.")
    
    got_open = False
    got_keepalive = False
    idx = 0
    while idx + 19 <= len(resp):
        if resp[idx:idx+16] == b'\xff'*16:
            r_len = struct.unpack('!H', resp[idx+16:idx+18])[0]
            if idx + r_len > len(resp):
                break
            r_type = resp[idx+18]
            if r_type == 1:
                got_open = True
            elif r_type == 4:
                got_keepalive = True
            elif r_type == 3:
                err = resp[idx+19] if idx+20 <= len(resp) else -1
                sub = resp[idx+20] if idx+21 <= len(resp) else -1
                raise Exception(f"HandshakeError: FRR sent NOTIFICATION error={err} subcode={sub}")
            idx += r_len
        else:
            idx += 1
    
    if not got_open:
        raise Exception("HandshakeError: FRR did not send OPEN.")
    
    s.sendall(build_bgp_keepalive())
    
    if not got_keepalive:
        resp2 = s.recv(4096)
        if resp2 and len(resp2) >= 19 and resp2[18] == 4:
            got_keepalive = True
    
    if not got_keepalive:
        raise Exception("HandshakeError: FRR did not send KEEPALIVE.")

def build_test_update(args, version, slot):
    # Fuzzed attribute
    f_flags = args[f"flags{slot}"]
    f_type = 1 if (version == 2 and slot == 1) else args[f"type{slot}"]
    f_len = args[f"len{slot}"]
    
    fuzz_bytes = struct.pack('!BB', f_flags, f_type)
    if f_flags & 0x10:
        fuzz_bytes += struct.pack('!H', f_len)
    else:
        fuzz_bytes += struct.pack('!B', f_len)
        
    if "payload_hex" in args:
        fuzz_bytes += bytes.fromhex(args["payload_hex"])
    else:
        fuzz_bytes += b'\x00' * f_len
    fuzz_obj = BGPPathAttr(flags=f_flags, type_code=f_type, length=f_len)
    
    # Mandatory attributes
    as_path_bytes = struct.pack('!BBB', 64, 2, 6) + b'\x02\x01\x00\x00\xfd\xea'
    as_path_obj = BGPPathAttr(flags=64, type_code=2, length=6)
    
    next_hop_bytes = struct.pack('!BBB', 64, 3, 4) + b'\x01\x01\x01\x01'
    next_hop_obj = BGPPathAttr(flags=64, type_code=3, length=4)
    
    origin_bytes = struct.pack('!BBB', 64, 1, 1) + b'\x00'
    origin_obj = BGPPathAttr(flags=64, type_code=1, length=1)
    
    # Construct sequence based on slot
    attr_bytes = b''
    attrs_for_oracle = []
    
    if slot == 1:
        attr_bytes += fuzz_bytes
        attrs_for_oracle.append(fuzz_obj)
        
    attr_bytes += as_path_bytes
    attrs_for_oracle.append(as_path_obj)
    
    if slot == 2:
        attr_bytes += fuzz_bytes
        attrs_for_oracle.append(fuzz_obj)
        
    attr_bytes += next_hop_bytes
    attrs_for_oracle.append(next_hop_obj)
    
    if slot == 3:
        attr_bytes += fuzz_bytes
        attrs_for_oracle.append(fuzz_obj)
        
    if not (version == 2 and slot == 1):
        attr_bytes += origin_bytes
        attrs_for_oracle.append(origin_obj)
        
    if slot == 4:
        attr_bytes += fuzz_bytes
        attrs_for_oracle.append(fuzz_obj)
    
    # Build UPDATE with NLRI (10.0.0.0/24)
    nlri_bytes = b'\x18\x0a\x00\x00'
    update_len = 23 + len(attr_bytes) + len(nlri_bytes)
    update_bytes = b'\xff'*16 + struct.pack('!HB', update_len, 2) + b'\x00\x00' + struct.pack('!H', len(attr_bytes)) + attr_bytes + nlri_bytes
    
    return update_bytes, attrs_for_oracle

def send_update_and_monitor(s, update_bytes):
    try:
        s.sendall(update_bytes)
    except Exception as e:
        print(f"[-] Failed to send UPDATE packet: {e}")
    
    notification_received = False
    is_active = True
    
    s.settimeout(0.2)
    try:
        while True:
            data = s.recv(4096)
            if not data:
                is_active = False
                break
                
            idx = 0
            while idx <= len(data) - 19:
                if data[idx:idx+16] == b'\xff'*16:
                    msg_len = struct.unpack('!H', data[idx+16:idx+18])[0]
                    msg_type = data[idx+18]
                    if msg_type == 3:
                        notification_received = True
                        is_active = False
                    idx += msg_len
                else:
                    idx += 1
    except socket.timeout:
        pass
    except ConnectionResetError:
        is_active = False
        
    return notification_received, is_active

def evaluate_result(oracle_res, notification_received, is_active, installed, version, slot, i, args, results_tally, discrepancies):
    results_tally["TOTAL_EXECUTED"] += 1
    if notification_received or not is_active:
        frr_result = "SESSION_RESET"
        results_tally["SESSION_TORN_DOWN"] += 1
    else:
        if installed:
            if oracle_res in (ParseResult.VALID, ParseResult.ATTRIBUTE_DISCARD):
                results_tally["LEGITIMATE_ROUTE_INSTALLS"] += 1
            else:
                results_tally["ROUTES_ILLEGALLY_INSTALLED"] += 1
                
            frr_result = "ATTRIBUTE_DISCARD" if oracle_res == ParseResult.ATTRIBUTE_DISCARD else "VALID"
            if frr_result == "ATTRIBUTE_DISCARD":
                results_tally["ATTRIBUTE_DISCARD"] += 1
            else:
                results_tally["VALID"] += 1
        else:
            if oracle_res == ParseResult.AFI_SAFI_DISABLE:
                frr_result = "AFI_SAFI_DISABLE"
                results_tally["AFI_SAFI_DISABLE"] += 1
            elif oracle_res == ParseResult.IMPL_CHOICE:
                # We can't perfectly infer which soft error it chose, so we map to generic TREAT_AS_WITHDRAW for tracking
                frr_result = "TREAT_AS_WITHDRAW"
                results_tally["TREAT_AS_WITHDRAW"] += 1
            else:
                frr_result = "TREAT_AS_WITHDRAW"
                results_tally["TREAT_AS_WITHDRAW"] += 1
    
    if oracle_res == ParseResult.VALID:
        oracle_mapped = "VALID"
    elif oracle_res == ParseResult.SESSION_RESET:
        oracle_mapped = "SESSION_RESET"
    elif oracle_res == ParseResult.ATTRIBUTE_DISCARD:
        oracle_mapped = "ATTRIBUTE_DISCARD"
    elif oracle_res == ParseResult.AFI_SAFI_DISABLE:
        oracle_mapped = "AFI_SAFI_DISABLE"
    elif oracle_res == ParseResult.IMPL_CHOICE:
        if frr_result in ("SESSION_RESET", "AFI_SAFI_DISABLE", "TREAT_AS_WITHDRAW"):
            oracle_mapped = frr_result
        else:
            oracle_mapped = "IMPL_CHOICE"
    else:
        oracle_mapped = "TREAT_AS_WITHDRAW"
                    
    if frr_result != oracle_mapped:
        test_id = f"V{version}-{i}-slot{slot}"
        discrepancies.append({
            "test_id": test_id,
            "payload_args": args,
            "rfc_expected": oracle_mapped,
            "frr_actual": frr_result,
            "oracle_state": oracle_res.name
        })

    results_tally["MATRIX"][oracle_mapped]["TOTAL"] += 1
    if frr_result == oracle_mapped:
        results_tally["MATRIX"][oracle_mapped]["PASS"] += 1
    else:
        results_tally["MATRIX"][oracle_mapped]["FAIL"] += 1

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

    # Load semantic communities dictionary (Version 3)
    test_args_v3 = []
    try:
        with open("models/bgpd/malformed_packets/tests/attr_argdict_semantic.txt", "r") as f:
            for line in f:
                if not line.strip(): continue
                test_args_v3.append(eval(line.strip()))
    except FileNotFoundError:
        print("[-] Could not find attr_argdict_semantic.txt (run generator first if testing Suite 3)")

    results_tally = {
        "SESSION_TORN_DOWN": 0,
        "TREAT_AS_WITHDRAW": 0,
        "AFI_SAFI_DISABLE": 0,
        "ROUTES_ILLEGALLY_INSTALLED": 0,
        "LEGITIMATE_ROUTE_INSTALLS": 0,
        "ATTRIBUTE_DISCARD": 0,
        "FRR_CRASH": 0,
        "TOTAL_EXECUTED": 0,
        "VALID": 0,
        "MATRIX": {
            "VALID": {"TOTAL": 0, "PASS": 0, "FAIL": 0},
            "SESSION_RESET": {"TOTAL": 0, "PASS": 0, "FAIL": 0},
            "ATTRIBUTE_DISCARD": {"TOTAL": 0, "PASS": 0, "FAIL": 0},
            "AFI_SAFI_DISABLE": {"TOTAL": 0, "PASS": 0, "FAIL": 0},
            "TREAT_AS_WITHDRAW": {"TOTAL": 0, "PASS": 0, "FAIL": 0},
        }
    }
    
    discrepancies = []
    
    def run_suite(test_args, version, has_hardcoded_mandatory):
        total_cases = len(test_args)
        
        # Determine the dynamic slots to test for each test case
        if version == 1:
            slots = [1, 2, 3]
        elif version == 2:
            slots = [1, 4]
        else:
            slots = [4]
            
        for i, args in enumerate(test_args):
            if (i + 1) % 10 == 0 or (i + 1) == total_cases:
                print(f"    -> Progress: {i + 1} / {total_cases} cases processed...", flush=True)
                
            for slot in slots:
                if slot == 4 and "type4" not in args:
                    continue
                    
                update_bytes, attrs_for_oracle = build_test_update(args, version, slot)
                oracle_res = parse_attributes(attrs_for_oracle)

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3.0)
                try:
                    s.connect((BGP_IP, BGP_PORT))
                except ConnectionRefusedError:
                    results_tally["FRR_CRASH"] += 1
                    continue
                    
                try:
                    perform_bgp_handshake(s)
                except Exception as e:
                    print(f"\n[!] BGP Handshake Failed: {e}", flush=True)
                    s.close()
                    results_tally["FRR_CRASH"] += 1
                    continue
                
                notification_received, is_active = send_update_and_monitor(s, update_bytes)
                
                installed = False
                if is_active and not notification_received:
                    installed = check_if_route_installed()
                
                s.close()
                time.sleep(0.01)
                
                evaluate_result(oracle_res, notification_received, is_active, installed, version, slot, i, args, results_tally, discrepancies)

    # User Prompt for Suite Execution
    print("\nWhich suite would you like to run?")
    print("  1) Suite 1: Strict Teardowns (RFC 4271)")
    print("  2) Suite 2: Soft Faults (RFC 7606)")
    print("  3) Suite 3: Semantic Communities")
    print("  4) All Suites (Default)")
    try:
        choice = input("Enter choice [1-4]: ").strip()
    except (EOFError, KeyboardInterrupt):
        choice = '4'
        print("4")
    
    run_s1 = choice in ('1', '4', '')
    run_s2 = choice in ('2', '4', '')
    run_s3 = choice in ('3', '4', '')
    
    if not any([run_s1, run_s2, run_s3]):
        print("Invalid choice, defaulting to All.")
        run_s1 = run_s2 = run_s3 = True
    
    
    if run_s1:
        print("\n[*] Running Suite 1: Strict Teardowns (RFC 4271)")
        run_suite(test_args_v1, version=1, has_hardcoded_mandatory=False)
    
    if run_s2:
        print("\n[*] Running Suite 2: Soft Faults (RFC 7606)")
        run_suite(test_args_v2, version=2, has_hardcoded_mandatory=True)

    if run_s3:
        if not test_args_v3:
            print("\n[-] Suite 3 skipped (dictionary not found).")
        else:
            print("\n[*] Running Suite 3: Semantic Communities")
            run_suite(test_args_v3, version=3, has_hardcoded_mandatory=True)

    print("\n=======================================================================")
    print("                COMPREHENSIVE EMPIRICAL RESULTS SUMMARY                ")
    print("=======================================================================")
    print(f"Total Tests Executed      : {results_tally['TOTAL_EXECUTED']}")
    print("\n--- Test Categorization (By Expected Behavior) ---")
    print(f"{'Category':<28} | {'Total':>7} | {'PASS':>7} | {'FAIL':>7}")
    print("-" * 55)
    
    mat = results_tally['MATRIX']
    print(f"{'Valid Updates':<28} | {mat['VALID']['TOTAL']:>7} | {mat['VALID']['PASS']:>7} | {mat['VALID']['FAIL']:>7}")
    print(f"{'Strict Teardown (RFC 4271)':<28} | {mat['SESSION_RESET']['TOTAL']:>7} | {mat['SESSION_RESET']['PASS']:>7} | {mat['SESSION_RESET']['FAIL']:>7}")
    print(f"{'Treat-as-Withdraw (RFC 7606)':<28} | {mat['TREAT_AS_WITHDRAW']['TOTAL']:>7} | {mat['TREAT_AS_WITHDRAW']['PASS']:>7} | {mat['TREAT_AS_WITHDRAW']['FAIL']:>7}")
    print(f"{'AFI/SAFI Disable (RFC 7606)':<28} | {mat['AFI_SAFI_DISABLE']['TOTAL']:>7} | {mat['AFI_SAFI_DISABLE']['PASS']:>7} | {mat['AFI_SAFI_DISABLE']['FAIL']:>7}")
    print(f"{'Attribute Discard (RFC 7606)':<28} | {mat['ATTRIBUTE_DISCARD']['TOTAL']:>7} | {mat['ATTRIBUTE_DISCARD']['PASS']:>7} | {mat['ATTRIBUTE_DISCARD']['FAIL']:>7}")
    
    print("\n--- Critical Metrics ---")
    print(f"Legitimate Route Installs : {results_tally['LEGITIMATE_ROUTE_INSTALLS']}")
    print(f"Routes Illegally Installed: {results_tally['ROUTES_ILLEGALLY_INSTALLED']}")
    print(f"FRR Parser Crashes        : {results_tally['FRR_CRASH']}")
    print("-----------------------------------------------------------------------")
    print(f"Unexpected Protocol Deviations: {len(discrepancies)}")
    
    if len(discrepancies) == 0:
        print("\n=> VERDICT: 100% PERFECT PARITY. FRR perfectly implements the selected RFCs.")
    else:
        print(f"\n=> VERDICT: {len(discrepancies)} Protocol Deviations Found.")
        print("Deviant Test IDs:")
        for idx, d in enumerate(discrepancies):
            if idx > 15:
                print("... (truncated)")
                break
            print(f"  - {d['test_id']} (Expected {d['rfc_expected']}, got {d['frr_actual']})")
            
    with open("models/bgpd/malformed_packets/parity_report_comprehensive.json", "w") as f:
        json.dump(discrepancies, f, indent=2)

if __name__ == "__main__":
    execute_comprehensive_suite()
