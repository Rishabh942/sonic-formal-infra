import socket
import select
import sys
import time
import logging
import threading
import os
import json
from scapy.all import *
from scapy.contrib.bgp import *

# Import the shared primitives from the new mbt architecture
from mbt.prims import addr_t, to_ipv4_address

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
)
logger = logging.getLogger("BGPFuzzer")

load_contrib("bgp")

target_ip   = "127.0.0.1"
target_port = 1179

# ---------------------------------------------------------------------------
# BGP message templates (Now utilizing mbt.prims for IPs)
# ---------------------------------------------------------------------------

# Generate deterministic IPs using mbt logic instead of hardcoded strings
fuzzer_bgp_id = to_ipv4_address(addr_t(1))
fuzzer_nexthop = to_ipv4_address(addr_t(2))

bgp_open = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="OPEN") / \
           BGPOpen(version=4, my_as=65002, hold_time=180, bgp_id=fuzzer_bgp_id, opt_params=[])

bgp_keepalive = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="KEEPALIVE")

setORIGIN   = BGPPathAttr(type_flags=0x40, type_code="ORIGIN",
                          attribute=BGPPAOrigin(origin="IGP"))
setAS_valid = BGPPathAttr(type_flags=0x40, type_code="AS_PATH",
                          attribute=BGPPAASPath(segments=[
                              BGPPAASPath.ASPathSegment(segment_type=2, segment_value=[65002])]))
setNEXTHOP  = BGPPathAttr(type_flags=0x40, type_code="NEXT_HOP",
                          attribute=[BGPPANextHop(next_hop=fuzzer_nexthop)])


def compile_clean_packet(path_attributes, prefixes):
    pkt = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="UPDATE") / \
          BGPUpdate(withdrawn_routes_len=0, path_attr=path_attributes, nlri=prefixes)
    if BGPHeader in pkt:  del pkt[BGPHeader].len
    if BGPUpdate in pkt:  del pkt[BGPUpdate].path_attr_len
    return bytes(pkt)


bgp_valid_update      = compile_clean_packet(
    [setORIGIN, setAS_valid, setNEXTHOP], [BGPNLRI_IPv4(prefix="11.0.0.0/24")])
bgp_missing_mandatory = compile_clean_packet(
    [setORIGIN, setNEXTHOP],              [BGPNLRI_IPv4(prefix="10.0.0.0/24")])

setAS_bad_flags = BGPPathAttr(type_flags=0, type_code="AS_PATH",
                              attribute=BGPPAASPath(segments=[
                                  BGPPAASPath.ASPathSegment(segment_type=2, segment_value=[65002])]))
bgp_bad_flags = compile_clean_packet(
    [setORIGIN, setAS_bad_flags, setNEXTHOP], [BGPNLRI_IPv4(prefix="12.0.0.0/24")])

bgp_bad_length_bytes     = bytearray(bgp_valid_update)
bgp_bad_length_bytes[25] = 150
bgp_bad_length           = bytes(bgp_bad_length_bytes)

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

CURRENT_RFC_STANDARD = "7606"
SHUTDOWN_SERVER      = False

# ---------------------------------------------------------------------------
# FSM states (mock server only)
# ---------------------------------------------------------------------------

FSM_CONNECT     = "CONNECT"
FSM_OPENSENT    = "OPENSENT"
FSM_ESTABLISHED = "ESTABLISHED"


# ---------------------------------------------------------------------------
# preflight_check
# ---------------------------------------------------------------------------

def preflight_check(ip, port, timeout=5.0):
    logger.info("[PREFLIGHT] Checking BGP daemon at %s:%d ...", ip, port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
    except ConnectionRefusedError:
        logger.error(
            "[PREFLIGHT] FAILED — Connection refused on %s:%d.\n"
            "  Is bgpd running?  Try:\n"
            "    docker exec -it frr-lab /usr/lib/frr/bgpd -d -f /etc/frr/frr.conf\n"
            "  Or check with:  docker exec frr-lab ps aux | grep bgpd",
            ip, port
        )
        return False
    except socket.timeout:
        logger.error(
            "[PREFLIGHT] FAILED — TCP connect timed out on %s:%d.\n"
            "  The port may be firewalled or bgpd is not bound to this address.",
            ip, port
        )
        return False
    except OSError as e:
        logger.error("[PREFLIGHT] FAILED — OS error connecting to %s:%d: %s", ip, port, e)
        return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        logger.info("[PREFLIGHT] TCP connected to %s:%d successfully.", ip, port)
        s.close()
        return True
    except Exception as e:
        logger.error("[PREFLIGHT] TCP connection failed: %s", e)
        return False


# ---------------------------------------------------------------------------
# Helper: send NOTIFICATION and close (mock server only)
# ---------------------------------------------------------------------------

def _send_notification(sock, error_code, error_subcode):
    try:
        notif = BGPHeader(type="NOTIFICATION") / \
                BGPNotification(error_code=error_code, error_subcode=error_subcode, data=b"")
        sock.send(bytes(notif))
        time.sleep(0.1)
    except Exception:
        pass
    finally:
        try:
            sock.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# FSM-aware mock server
# ---------------------------------------------------------------------------

def handle_client(client_sock):
    client_sock.settimeout(2.0)
    fsm_state = FSM_CONNECT

    try:
        try:
            data = client_sock.recv(4096)
        except socket.timeout:
            return
        if not data:
            return

        if len(data) < 19 or data[:16] != b'\xff' * 16:
            _send_notification(client_sock, 1, 2)
            return

        msg_type = data[18]
        if msg_type != 1:
            logger.warning("[SERVER FSM] Received msg type %d in %s — FSM Error (5/0)",
                           msg_type, fsm_state)
            _send_notification(client_sock, 5, 0)
            return

        fsm_state = FSM_OPENSENT
        client_sock.send(bytes(bgp_open))
        client_sock.send(bytes(bgp_keepalive))

        try:
            data = client_sock.recv(4096)
        except socket.timeout:
            return
        if not data:
            return

        if len(data) < 19 or data[:16] != b'\xff' * 16:
            _send_notification(client_sock, 1, 2)
            return

        msg_type = data[18]
        if msg_type != 4:
            logger.warning("[SERVER FSM] Received msg type %d in %s — FSM Error (5/0)",
                           msg_type, fsm_state)
            _send_notification(client_sock, 5, 0)
            return

        fsm_state = FSM_ESTABLISHED

        while True:
            try:
                data = client_sock.recv(4096)
            except socket.timeout:
                break
            if not data:
                break

            if data == bytes(bgp_keepalive):
                continue
            elif data == bgp_valid_update:
                continue
            elif data == bgp_missing_mandatory:
                if CURRENT_RFC_STANDARD == "4271":
                    _send_notification(client_sock, 3, 3)
                else:
                    logger.info("[SERVER] RFC 7606 treat-as-withdraw: missing mandatory attr")
                    continue
            elif data == bgp_bad_flags:
                if CURRENT_RFC_STANDARD == "4271":
                    _send_notification(client_sock, 3, 4)
                else:
                    logger.info("[SERVER] RFC 7606 treat-as-withdraw: bad flags")
                    continue
            elif data == bgp_bad_length:
                _send_notification(client_sock, 1, 2)
                return
            else:
                logger.warning("[SERVER] Unrecognised payload in ESTABLISHED, ignoring.")
                continue
            return

    except Exception as e:
        logger.debug("[SERVER] handle_client exception: %s", e)
    finally:
        try:
            client_sock.close()
        except Exception:
            pass


def bgp_mock_server():
    global SHUTDOWN_SERVER
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((target_ip, target_port))
    server_sock.listen(10)
    server_sock.settimeout(0.5)
    logger.info("Mock BGP Daemon listening on port %d...", target_port)
    while not SHUTDOWN_SERVER:
        try:
            client_sock, addr = server_sock.accept()
            t = threading.Thread(target=handle_client, args=(client_sock,))
            t.daemon = True
            t.start()
        except socket.timeout:
            continue
        except Exception as e:
            logger.error("Server accept error: %s", e)
            break
    server_sock.close()
    logger.info("Mock BGP Daemon stopped.")


# ---------------------------------------------------------------------------
# is_fatal_framing_error
# ---------------------------------------------------------------------------

def is_fatal_framing_error(payload_bytes):
    try:
        if not payload_bytes:
            return False
        packet = BGPHeader(payload_bytes)
        if BGPUpdate not in packet:
            return False
        update_layer = packet[BGPUpdate]
        actual_attr_bytes    = len(raw(update_layer.path_attr)) \
                               if hasattr(update_layer, 'path_attr') else 0
        declared_attr_length = update_layer.path_attr_len \
                               if hasattr(update_layer, 'path_attr_len') else actual_attr_bytes
        return declared_attr_length > actual_attr_bytes
    except Exception:
        return True


# ---------------------------------------------------------------------------
# classify_sequence
# ---------------------------------------------------------------------------

def classify_sequence(sequence):
    UPDATE_ACTIONS = {
        "RCV_UPDATE_MISSING_MANDATORY",
        "RCV_UPDATE_BAD_FLAGS",
        "RCV_UPDATE_BAD_LENGTH",
        "RCV_VALID_UPDATE",
    }
    saw_open      = False
    saw_keepalive = False
    for step in sequence:
        action = step["action_event"]
        if action == "RCV_OPEN":
            saw_open = True
        elif action == "RCV_KEEPALIVE":
            saw_keepalive = True
        elif action in UPDATE_ACTIONS:
            if not (saw_open and saw_keepalive):
                return "PRE_HANDSHAKE"
            return "POST_HANDSHAKE"
    return "HANDSHAKE_ONLY"


# ---------------------------------------------------------------------------
# complete_bgp_handshake
# ---------------------------------------------------------------------------

def complete_bgp_handshake(sock, session_buf, timeout=2.0):
    start          = time.time()
    seen_open      = False
    seen_keepalive = False

    idx = 0
    while idx + 19 <= len(session_buf):
        if session_buf[idx:idx + 16] == b'\xff' * 16:
            length   = int.from_bytes(session_buf[idx + 16:idx + 18], 'big')
            if idx + length > len(session_buf): break
            msg_type = session_buf[idx + 18]
            if   msg_type == 1: seen_open      = True
            elif msg_type == 4: seen_keepalive = True
            elif msg_type == 3: return False, session_buf[idx:]
            idx += length
        else:
            idx += 1
    session_buf = session_buf[idx:]
    if seen_open and seen_keepalive:
        return True, session_buf

    while time.time() - start < timeout:
        ready = select.select([sock], [], [], 0.1)
        if ready[0]:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    return False, session_buf
                session_buf += chunk
                idx = 0
                while idx + 19 <= len(session_buf):
                    if session_buf[idx:idx + 16] == b'\xff' * 16:
                        length   = int.from_bytes(session_buf[idx + 16:idx + 18], 'big')
                        if idx + length > len(session_buf): break
                        msg_type = session_buf[idx + 18]
                        if   msg_type == 1: seen_open      = True
                        elif msg_type == 4: seen_keepalive = True
                        elif msg_type == 3: return False, session_buf[idx:]
                        idx += length
                    else:
                        idx += 1
                session_buf = session_buf[idx:]
                if seen_open and seen_keepalive:
                    return True, session_buf
            except (BlockingIOError, ConnectionResetError):
                pass
    return False, session_buf


# ---------------------------------------------------------------------------
# _scan_buffer_for_notification
# ---------------------------------------------------------------------------

def _scan_buffer_for_notification(buf):
    idx = 0
    while idx + 19 <= len(buf):
        if buf[idx:idx + 16] == b'\xff' * 16:
            length   = int.from_bytes(buf[idx + 16:idx + 18], 'big')
            msg_type = buf[idx + 18]
            if msg_type == 3:
                try:
                    if idx + 21 <= len(buf):
                        return True, buf[idx + 19], buf[idx + 20]
                except Exception:
                    pass
                return True, None, None
            if length < 19:
                break
            idx += length
        else:
            idx += 1
    return False, None, None


# ---------------------------------------------------------------------------
# execute_live_pipeline
# ---------------------------------------------------------------------------

def execute_live_pipeline(test_case):
    test_id      = test_case["test_id"]
    logger.info("--- Starting Test ID %s (RFC %s) ---", test_id, test_case["rfc_standard"])

    seq_category            = classify_sequence(test_case["sequence"])
    expect_fsm_notification = (seq_category == "PRE_HANDSHAKE")

    if expect_fsm_notification:
        logger.info(
            "[RUNNER] Test %s classified as PRE_HANDSHAKE — "
            "expecting FSM Error NOTIFICATION (code 5), not UPDATE error (code 3)",
            test_id
        )

    sessions               = {}
    session_buffers        = {}
    client_closed_sessions = set()
    current_session_id     = 0
    broken_sessions        = set()
    failure_actions        = {}
    captured_notification  = False
    notif_error_code       = None
    notif_error_subcode    = None
    tcp_refused            = False   
    sent_soft_mutation     = False

    for event_block in test_case["sequence"]:
        action = event_block["action_event"]

        if current_session_id in sessions and current_session_id not in broken_sessions:
            try:
                sessions[current_session_id].setblocking(False)
                check_bytes = sessions[current_session_id].recv(4096)
                if len(check_bytes) == 0:
                    broken_sessions.add(current_session_id)
                else:
                    session_buffers[current_session_id] += check_bytes
            except BlockingIOError:
                pass
            except (ConnectionResetError, BrokenPipeError, socket.error):
                broken_sessions.add(current_session_id)

            found, ec, esc = _scan_buffer_for_notification(
                session_buffers.get(current_session_id, b""))
            if found:
                captured_notification = True
                notif_error_code      = ec
                notif_error_subcode   = esc
                broken_sessions.add(current_session_id)

        if current_session_id in broken_sessions and action != "TCP_CONN_START":
            break

        try:
            if action == "TCP_CONN_START":
                if current_session_id in sessions:
                    try:
                        sessions[current_session_id].close()
                    except Exception:
                        pass
                    client_closed_sessions.add(current_session_id)
                current_session_id += 1
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3.0)
                sock.connect((target_ip, target_port))
                sock.settimeout(None)
                sessions[current_session_id]        = sock
                session_buffers[current_session_id] = b""
                time.sleep(0.05)

            elif action == "RCV_OPEN" and current_session_id in sessions:
                sessions[current_session_id].send(bytes(bgp_open))
                success, updated_buf = complete_bgp_handshake(
                    sessions[current_session_id],
                    session_buffers[current_session_id]
                )
                session_buffers[current_session_id] = updated_buf
                if not success:
                    broken_sessions.add(current_session_id)
                    failure_actions[current_session_id] = "HANDSHAKE_FAILED"

            elif action == "RCV_KEEPALIVE" and current_session_id in sessions:
                sessions[current_session_id].send(bytes(bgp_keepalive))
                time.sleep(0.05)

            elif action == "RCV_VALID_UPDATE" and current_session_id in sessions:
                sessions[current_session_id].send(bytes(bgp_valid_update))
                time.sleep(0.05)

            elif action == "RCV_UPDATE_MISSING_MANDATORY" and current_session_id in sessions:
                failure_actions[current_session_id] = "RCV_UPDATE_MISSING_MANDATORY"
                sessions[current_session_id].send(bytes(bgp_missing_mandatory))
                sent_soft_mutation = True
                time.sleep(0.05)

            elif action == "RCV_UPDATE_BAD_FLAGS" and current_session_id in sessions:
                failure_actions[current_session_id] = "RCV_UPDATE_BAD_FLAGS"
                sessions[current_session_id].send(bytes(bgp_bad_flags))
                sent_soft_mutation = True
                time.sleep(0.05)

            elif action == "RCV_UPDATE_BAD_LENGTH" and current_session_id in sessions:
                failure_actions[current_session_id] = "RCV_UPDATE_BAD_LENGTH"
                sessions[current_session_id].send(bytes(bgp_bad_length))
                time.sleep(0.05)

        except ConnectionRefusedError:
            tcp_refused = True
            broken_sessions.add(current_session_id)
            failure_actions[current_session_id] = "TCP_REFUSED"
            logger.error(
                "[RUNNER] Test %s: TCP connection refused on %s:%d — "
                "bgpd is not reachable. Aborting this test.",
                test_id, target_ip, target_port
            )
            break

        except (BrokenPipeError, ConnectionResetError, socket.error) as e:
            broken_sessions.add(current_session_id)
            if current_session_id not in failure_actions:
                failure_actions[current_session_id] = action

        if current_session_id > 0 and current_session_id not in broken_sessions:
            if event_block["resulting_state"] == "IDLE":
                time.sleep(0.05)
                try:
                    sessions[current_session_id].setblocking(False)
                    check_bytes = sessions[current_session_id].recv(4096)
                    if len(check_bytes) == 0:
                        broken_sessions.add(current_session_id)
                    else:
                        session_buffers[current_session_id] += check_bytes
                except BlockingIOError:
                    pass
                except (ConnectionResetError, BrokenPipeError, socket.error):
                    broken_sessions.add(current_session_id)

                found, ec, esc = _scan_buffer_for_notification(
                    session_buffers.get(current_session_id, b""))
                if found:
                    captured_notification = True
                    notif_error_code      = ec
                    notif_error_subcode   = esc
                    broken_sessions.add(current_session_id)

                if current_session_id not in broken_sessions:
                    failure_actions[current_session_id] = "SHOULD_HAVE_CLOSED"
                    broken_sessions.add(current_session_id)

    # Final pass drain loop
    time.sleep(0.05)
    for s_id, sock in sessions.items():
        if s_id in client_closed_sessions:
            continue
        try:
            sock.setblocking(False)
            while True:
                check_bytes = sock.recv(4096)
                if len(check_bytes) == 0:
                    broken_sessions.add(s_id)
                    break
                session_buffers[s_id] += check_bytes
        except BlockingIOError:
            pass
        except (ConnectionResetError, BrokenPipeError, socket.error):
            broken_sessions.add(s_id)

        found, ec, esc = _scan_buffer_for_notification(session_buffers.get(s_id, b""))
        if found:
            captured_notification = True
            notif_error_code      = ec
            notif_error_subcode   = esc
            broken_sessions.add(s_id)

    for sock in sessions.values():
        try:
            sock.close()
        except Exception:
            pass

    active_broken_sessions = broken_sessions - client_closed_sessions

    # -----------------------------------------------------------------------
    # Result evaluation
    # -----------------------------------------------------------------------

    if tcp_refused or any(failure_actions.get(s) == "TCP_REFUSED"
                          for s in active_broken_sessions):
        result = "INFRASTRUCTURE_TCP_REFUSED"

    elif active_broken_sessions:
        if any(failure_actions.get(s) == "HANDSHAKE_FAILED" for s in active_broken_sessions):
            result = "INFRASTRUCTURE_HANDSHAKE_ERROR"

        elif any(failure_actions.get(s) == "SHOULD_HAVE_CLOSED" for s in active_broken_sessions):
            result = "POTENTIAL_RFC_BUG"

        else:
            dropped_on_fatal = any(
                failure_actions.get(s) == "RCV_UPDATE_BAD_LENGTH"
                and is_fatal_framing_error(bgp_bad_length)
                for s in active_broken_sessions
            )
            if dropped_on_fatal:
                result = "EXPECTED_DISCONNECT"
            else:
                model_expected_drop = (test_case["sequence"][-1]["resulting_state"] == "IDLE")

                if model_expected_drop:
                    if captured_notification:
                        if expect_fsm_notification:
                            if notif_error_code == 5:
                                result = "EXPECTED_DISCONNECT"
                            elif notif_error_code == 3:
                                result = "WRONG_NOTIFICATION_CODE"
                                logger.warning(
                                    "[RUNNER] Test %s: PRE_HANDSHAKE received NOTIFICATION "
                                    "code 3 (UPDATE Error) — RFC 4271 §6.5 requires code 5 "
                                    "(FSM Error) for out-of-state messages.",
                                    test_id
                                )
                            else:
                                result = "EXPECTED_DISCONNECT"
                        else:
                            result = "EXPECTED_DISCONNECT"
                    else:
                        if expect_fsm_notification:
                            result = "MISSING_NOTIFICATION"
                            logger.warning(
                                "[RUNNER] Test %s: PRE_HANDSHAKE — server closed without "
                                "a BGP NOTIFICATION. RFC 4271 §6.5 requires one.",
                                test_id
                            )
                        else:
                            result = "UNEXPECTED_DISCONNECT"
                else:
                    if sent_soft_mutation:
                        result = "POTENTIAL_RFC_BUG"
                    else:
                        result = "DEEP_PASS"

    else:
        if current_session_id > 0:
            model_expected_drop = (test_case["sequence"][-1]["resulting_state"] == "IDLE")
            result = "POTENTIAL_RFC_BUG" if model_expected_drop else "DEEP_PASS"
        else:
            result = "DEEP_PASS"

    logger.info("--- Test ID %s Result: %s ---", test_id, result)
    return result


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    global CURRENT_RFC_STANDARD, SHUTDOWN_SERVER

    if not preflight_check(target_ip, target_port):
        print("\n[!] PREFLIGHT FAILED — no BGP daemon reachable at "
              f"{target_ip}:{target_port}. Aborting.")
        print("    Make sure FRR bgpd is running inside your Docker container:")
        print("      docker exec -it frr-lab /usr/lib/frr/bgpd -d -f /etc/frr/frr.conf")
        print("    And that port 179 is mapped: -p 179:179")
        sys.exit(1)

    try:
        suite_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "tests", "bgp_test_suite_formatted.json"
        )
        with open(suite_path, "r") as f:
            suite_data = json.load(f)
    except FileNotFoundError:
        print("Error: bgp_test_suite_formatted.json not found. Run format_tests.py first.")
        sys.exit(1)

    demo_cases = suite_data
    print(f"\nRunning {len(demo_cases)} test cases against FRR bgpd at "
          f"{target_ip}:{target_port} ...")

    deep_passes       = []
    expected_drops    = []
    rfc_bugs          = []
    handshake_errors  = []
    unexp_drops       = []
    wrong_notif_codes = []
    missing_notifs    = []
    tcp_refused_list  = []   

    for test_case in demo_cases:
        CURRENT_RFC_STANDARD = test_case["rfc_standard"]
        cat  = execute_live_pipeline(test_case)
        t_id = test_case["test_id"]

        if   cat == "DEEP_PASS":                     deep_passes.append(t_id)
        elif cat == "EXPECTED_DISCONNECT":           expected_drops.append(t_id)
        elif cat == "POTENTIAL_RFC_BUG":             rfc_bugs.append(t_id)
        elif cat == "INFRASTRUCTURE_HANDSHAKE_ERROR": handshake_errors.append(t_id)
        elif cat == "UNEXPECTED_DISCONNECT":         unexp_drops.append(t_id)
        elif cat == "WRONG_NOTIFICATION_CODE":       wrong_notif_codes.append(t_id)
        elif cat == "MISSING_NOTIFICATION":          missing_notifs.append(t_id)
        elif cat == "INFRASTRUCTURE_TCP_REFUSED":    tcp_refused_list.append(t_id)

        if cat == "INFRASTRUCTURE_TCP_REFUSED" and len(tcp_refused_list) >= 3:
            print("\n[!] 3 consecutive TCP_REFUSED results — bgpd appears to have stopped.")
            print("    Halting suite early to avoid misleading results.")
            break

    print("\n==================================================")
    print("     EXPANDED CONSTRAINT SUITE REPORT             ")
    print("==================================================")
    print(f"Total Test Cases Executed         : {len(demo_cases)}")
    print(f"Deep Passes (Safe Ingestion)      : {len(deep_passes)}")
    print(f"Expected Disconnects (Compliant)  : {len(expected_drops)}")
    print(f"Potential RFC Compliance Bugs     : {len(rfc_bugs)}")
    print(f"Unexpected Session Drops          : {len(unexp_drops)}")
    print(f"Wrong NOTIFICATION Code           : {len(wrong_notif_codes)}")
    print(f"Missing NOTIFICATION (raw close)  : {len(missing_notifs)}")
    print(f"Infrastructure Handshake Errors   : {len(handshake_errors)}")
    print(f"Infrastructure TCP Refused        : {len(tcp_refused_list)}")   
    print("==================================================")
    if rfc_bugs:
        print(f"\n[!] POTENTIAL RFC COMPLIANCE BUG TEST IDS:\n    {rfc_bugs}")
        print("==================================================")
    if unexp_drops:
        print(f"\n[!] UNEXPECTED SESSION DROP TEST IDS:\n    {unexp_drops}")
        print("==================================================")
    if wrong_notif_codes:
        print(f"\n[!] WRONG NOTIFICATION CODE (should be FSM Error 5/0):\n    {wrong_notif_codes}")
        print("==================================================")
    if missing_notifs:
        print(f"\n[!] MISSING NOTIFICATION (raw close, no BGP NOTIFICATION sent):\n    {missing_notifs}")
        print("==================================================")
    if tcp_refused_list:
        print(f"\n[!] TCP REFUSED (bgpd unreachable) TEST IDS:\n    {tcp_refused_list}")
        print("    Run: docker exec -it frr-lab /usr/lib/frr/bgpd -d -f /etc/frr/frr.conf")
        print("==================================================")


if __name__ == "__main__":
    main()