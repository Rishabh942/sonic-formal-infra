"""Core BGP UPDATE fuzzer: replay saved attribute mutations against FRR.

The earlier extended, soft-fault and community suites share wire builders,
the RFC oracle and live observations. Reports keep dry-run/coverage counts
separate from parity passes. JSON files are not runner inputs.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import socket
import struct
import subprocess
import time

from models.bgpd.malformed_packets.bgp_oracle import parse_attributes, BGPPathAttr, ParseResult
from models.bgpd.malformed_packets.packet_builders import encode_attr, normalize_payload


DEFAULT_HOST = "127.0.0.1"

DEFAULT_PORT = 1179

KEEPALIVE_MESSAGE = b'\xff' * 16 + b'\x00\x13\x04'

FRR_CONTAINER = "frr-lab"

OBS_RESET = "SESSION_RESET"

OBS_INSTALLED = "INSTALLED"

OBS_NOT_INSTALLED = "NOT_INSTALLED"

ALLOWED_OBSERVATIONS = {
    ParseResult.VALID: {OBS_INSTALLED},                 # best-path must install
    ParseResult.ATTRIBUTE_DISCARD: {OBS_INSTALLED},     # route kept, bad attr dropped
    ParseResult.TREAT_AS_WITHDRAW: {OBS_NOT_INSTALLED},
    # RFC 7606 §7.11: MP structural errors permit EITHER session reset or
    # AFI/SAFI disable - a conforming daemon may pick either.
    ParseResult.AFI_SAFI_DISABLE: {OBS_NOT_INSTALLED, OBS_RESET},
    ParseResult.SESSION_RESET: {OBS_RESET},
    ParseResult.IMPL_CHOICE: {OBS_RESET, OBS_INSTALLED, OBS_NOT_INSTALLED},
}

BASE_DIR = Path(__file__).resolve().parent

def clear_bgp_log(container="frr-lab"):
    subprocess.call(["docker", "exec", container, "sh", "-c", "> /tmp/bgpd.log"])

def get_bgp_log(container="frr-lab"):
    try:
        out = subprocess.check_output(["docker", "exec", container, "cat", "/tmp/bgpd.log"], stderr=subprocess.DEVNULL)
        lines = [l.split('] ')[-1].strip() for l in out.decode('utf-8').split('\n') if 'BGP:' in l and 'sockopt' not in l and 'TCP MD5' not in l and 'unrecognized capability' not in l]
        return "\n".join(lines)
    except Exception:
        return ""

def build_bgp_open(opt_params=None, asn=65002, router_id="192.168.1.1"):
    """OPEN message; default capabilities: MP-BGP IPv4, RR old+new,
    Enhanced RR, 4-byte ASN."""
    import socket as _sock
    if opt_params is None:
        opt_params = b''
        opt_params += struct.pack('!BB', 2, 6) + struct.pack('!BB', 1, 4) + struct.pack('!HBB', 1, 0, 1)
        opt_params += struct.pack('!BB', 2, 2) + struct.pack('!BB', 128, 0)
        opt_params += struct.pack('!BB', 2, 2) + struct.pack('!BB', 2, 0)
        opt_params += struct.pack('!BB', 2, 2) + struct.pack('!BB', 70, 0)
        opt_params += struct.pack('!BB', 2, 6) + struct.pack('!BB', 65, 4) + struct.pack('!I', asn)
    open_body = struct.pack('!BHH', 4, asn, 90) + _sock.inet_aton(router_id) \
        + struct.pack('!B', len(opt_params)) + opt_params
    msg_len = 16 + 2 + 1 + len(open_body)
    return b'\xff' * 16 + struct.pack('!HB', msg_len, 1) + open_body

def _mandatory_attrs():
    return [
        BGPPathAttr(flags=64, type_code=1, length=1, value=b'\x00'),
        BGPPathAttr(flags=64, type_code=2, length=6, value=b'\x02\x01\x00\x00\xfd\xea'),
        BGPPathAttr(flags=64, type_code=3, length=4, value=b'\x01\x01\x01\x01'),
    ]

def _attr_wire(attr: BGPPathAttr) -> bytes:
    return encode_attr(attr.flags, attr.type_code, attr.length) + attr.value

def validate_update_attributes(packet, attrs):
    """Independently decode the emitted UPDATE and compare the oracle input.

    This checks outer/header boundaries and values, not RFC correctness.
    It prevents a successful dry run from hiding wire/model disagreement.
    """
    if (len(packet) < 23 or packet[:16] != b'\xff' * 16 or packet[18] != 2
            or int.from_bytes(packet[16:18], 'big') != len(packet)):
        raise ValueError("invalid UPDATE frame")
    start = 21 + int.from_bytes(packet[19:21], 'big')
    if start + 2 > len(packet):
        raise ValueError("truncated withdrawn routes")
    end = start + 2 + int.from_bytes(packet[start:start + 2], 'big')
    pos = start + 2
    if end > len(packet):
        raise ValueError("attribute block exceeds UPDATE")
    decoded = []
    while pos < end:
        if pos + 3 > end:
            raise ValueError("truncated attribute header")
        flags, code = packet[pos:pos + 2]
        width = 2 if flags & 0x10 else 1
        if pos + 2 + width > end:
            raise ValueError("truncated extended attribute header")
        length = int.from_bytes(packet[pos + 2:pos + 2 + width], 'big')
        pos += 2 + width
        if pos + length > end:
            raise ValueError("attribute value exceeds block")
        decoded.append((flags, code, length, packet[pos:pos + length]))
        pos += length
    if decoded != [(a.flags, a.type_code, a.length, a.value) for a in attrs]:
        raise ValueError("emitted attributes differ from oracle input")

def _prefix_bytes(prefix_id: int):
    """Unique /24 per test case: NLRI [len=24, 10.a.b.0] with a.b derived
    from id. Isolates RIB state between cases (the old fixed 10.0.0.0/24
    leaked) - and the mask octet MUST be 24, or routes install under a
    different prefix than the one being verified."""
    a = (prefix_id >> 8) & 0xFF
    b = prefix_id & 0xFF
    return bytes((24, 10, a, b)), f"10.{a}.{b}.0/24"

class PrefixAllocator:
    def __init__(self):
        self._n = 0

    def next(self):
        self._n += 1
        return self._n

def build_legacy_update(args, version, slot, prefix_id):
    """Legacy suites: fuzzed attribute slotted among hard-coded mandatories."""
    f_flags = args[f"flags{slot}"]
    f_type = 1 if (version == 2 and slot == 1) else args[f"type{slot}"]
    f_len = args[f"len{slot}"]

    if f"payload_hex{slot}" in args:
        val_bytes = normalize_payload(args[f"payload_hex{slot}"], f_len)
    elif "payload_hex" in args:
        val_bytes = normalize_payload(args["payload_hex"], f_len)
    else:
        val_bytes = b'\x00' * f_len
    fuzz_obj = BGPPathAttr(flags=f_flags, type_code=f_type, length=f_len, value=val_bytes)

    origin_obj, as_path_obj, next_hop_obj = _mandatory_attrs()
    ordered = []
    if slot == 1:
        ordered.append(fuzz_obj)
    ordered.append(as_path_obj)
    if slot == 2:
        ordered.append(fuzz_obj)
    ordered.append(next_hop_obj)
    if slot == 3:
        ordered.append(fuzz_obj)
    if not (version == 2 and slot == 1):
        ordered.append(origin_obj)
    if slot == 4:
        ordered.append(fuzz_obj)

    attr_bytes = b''.join(_attr_wire(a) for a in ordered)
    attrs_for_oracle = list(ordered)

    pb, prefix_str = _prefix_bytes(prefix_id)
    update_len = 23 + len(attr_bytes) + len(pb)
    update_bytes = b'\xff' * 16 + struct.pack('!HB', update_len, 2) + b'\x00\x00' \
        + struct.pack('!H', len(attr_bytes)) + attr_bytes + pb
    return update_bytes, attrs_for_oracle, prefix_str, f"v{version}slot{slot}"

def expand_legacy_cases(raw_cases):
    """Expand legacy dicts across their slot positions exactly like the
    original engine: extended dicts at slots [1,2,3], soft dicts [1,4],
    semantic dicts [4]. Each expansion becomes its own test case."""
    expanded = []
    for args in raw_cases:
        placed = False
        for version, slots in ((1, (1, 2, 3)), (2, (1, 4)), (3, (4,))):
            for slot in slots:
                if f"type{slot}" in args or (version == 2 and slot == 1 and "flags1" in args):
                    expanded.append((args, version, slot))
                    placed = True
            if placed:
                break
        if not placed:
            expanded.append((args, 3, 4))
    return expanded

class BgpSession:
    """Reusable BGP session; re-handshakes automatically after a teardown."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def ensure(self):
        if self.sock is not None:
            return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        try:
            s.connect((self.host, self.port))
            if not perform_bgp_handshake(s):
                raise ConnectionError("BGP OPEN/KEEPALIVE exchange incomplete")
        except Exception:
            s.close()
            raise
        self.sock = s

    def invalidate(self):
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None

    def close(self):
        self.invalidate()

def perform_bgp_handshake(s, open_msg=None):
    """Send OPEN, consume peer OPEN+KEEPALIVE (handling TCP fragmentation),
    answer KEEPALIVE. Returns False if the exchange did not complete;
    raises ConnectionError if the peer sent a NOTIFICATION."""
    s.sendall(open_msg if open_msg is not None else build_bgp_open())

    got_open = False
    got_keepalive = False
    deadline = time.monotonic() + 3.0
    buf = b''
    while time.monotonic() < deadline and not (got_open and got_keepalive):
        try:
            chunk = s.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            return False
        buf += chunk
        idx = 0
        while idx + 19 <= len(buf):
            if buf[idx:idx + 16] != b'\xff' * 16:
                idx += 1
                continue
            r_len = struct.unpack('!H', buf[idx + 16:idx + 18])[0]
            if not 19 <= r_len <= 4096:
                return False
            if idx + r_len > len(buf):
                break          # incomplete message: wait for more bytes
            r_type = buf[idx + 18]
            if r_type == 1:
                got_open = True
                s.sendall(build_bgp_keepalive())
            elif r_type == 4:
                got_keepalive = True
            elif r_type == 3:
                err = buf[idx + 19] if idx + 20 <= len(buf) else -1
                sub = buf[idx + 20] if idx + 21 <= len(buf) else -1
                raise ConnectionError(f"peer NOTIFICATION error={err} subcode={sub}")
            idx += r_len
        buf = buf[idx:]
        if len(buf) > 65536:
            return False

    return got_open and got_keepalive

def build_bgp_keepalive():
    return KEEPALIVE_MESSAGE

def send_update_and_monitor(s, update_bytes, fast=False):
    """Send one UPDATE; classify transport-level outcome."""
    notification_received = False
    is_active = True
    try:
        s.sendall(update_bytes)
    except Exception as e:
        print(f"[-] Failed to send UPDATE packet: {e}")
        return False, False

    s.settimeout(0.01 if fast else 0.3)
    buf = b''
    try:
        while True:
            data = s.recv(4096)
            if not data:
                is_active = False
                break
            buf += data
            idx = 0
            while idx <= len(buf) - 19:
                if buf[idx:idx + 16] == b'\xff' * 16:
                    msg_len = struct.unpack('!H', buf[idx + 16:idx + 18])[0]
                    if not 19 <= msg_len <= 4096:
                        raise ConnectionError("invalid peer BGP message length")
                    if idx + msg_len > len(buf):
                        break
                    if buf[idx + 18] == 3:
                        notification_received = True
                        is_active = False
                    idx += msg_len
                else:
                    idx += 1
            buf = buf[idx:]
            if len(buf) > 65536:
                raise ConnectionError("peer receive buffer exceeded")
    except socket.timeout:
        pass
    except (ConnectionResetError, BrokenPipeError, OSError):
        is_active = False
    return notification_received, is_active

def check_if_route_installed(prefix, retries=2, container=FRR_CONTAINER):
    for attempt in range(retries + 1):
        try:
            out = subprocess.check_output(
                ["docker", "exec", container, "vtysh", "-c",
                 f"show ip bgp {prefix} json"],
                stderr=subprocess.DEVNULL)
            data = json.loads(out)
            if data.get("paths"):
                return True
        except (subprocess.SubprocessError, OSError, ValueError) as exc:
            raise RuntimeError(f"RIB observation failed for {prefix}") from exc
        if attempt < retries:
            time.sleep(0.12)
    return False

def classify_observation(notification_received, is_active, installed):
    if notification_received or not is_active:
        return OBS_RESET
    return OBS_INSTALLED if installed else OBS_NOT_INSTALLED

def evaluate_case(test_id, oracle_res, observed, args, tally, discrepancies,
                  allowed=None, frr_log=''):
    tally["TOTAL_EXECUTED"] += 1
    key = oracle_res.name
    tally["MATRIX"].setdefault(key, {"TOTAL": 0, "PASS": 0, "FAIL": 0})
    tally["MATRIX"][key]["TOTAL"] += 1

    if observed in ("DRY_RUN", "COVERAGE_ONLY"):
        return                      # offline mode: builders + oracle only

    if allowed is None:
        allowed = ALLOWED_OBSERVATIONS[oracle_res]
    if observed in allowed:
        tally["MATRIX"][key]["PASS"] += 1
    else:
        tally["MATRIX"][key]["FAIL"] += 1
        discrepancies.append({
            "test_id": test_id,
            "payload_args": args,
            "rfc_allowed": sorted(allowed),
            "frr_observed": observed,
            "oracle_state": oracle_res.name, "frr_log": frr_log,
        })

def summarize_and_report(tally, discrepancies, out_path, dry_run, coverage_mode,
                         corpus, run_context):
    mode = "dry run" if dry_run else "coverage only" if coverage_mode else "live parity"
    print(f"\nBGP results ({mode})")
    print(f"Cases processed: {tally['TOTAL_EXECUTED']}")

    print("\nResults by oracle verdict:")
    print(f"{'Oracle Verdict':<28} | {'Total':>7} | {'PASS':>7} | {'FAIL':>7}")
    print("-" * 55)
    for key in ("VALID", "SESSION_RESET", "TREAT_AS_WITHDRAW",
                "AFI_SAFI_DISABLE", "ATTRIBUTE_DISCARD", "IMPL_CHOICE"):
        row = tally["MATRIX"].get(key)
        if row:
            print(f"{key:<28} | {row['TOTAL']:>7} | {row['PASS']:>7} | {row['FAIL']:>7}")

    print(f"\nConnection/handshake errors: {tally['CONNECTION_FAILURES']}")
    print(f"RIB observation errors: {tally['OBSERVATION_ERRORS']}")
    print(f"Unexpected outcomes: {len(discrepancies)}")

    if discrepancies:
        print("\nCases with unexpected outcomes:")
        for idx, d in enumerate(discrepancies):
            if idx > 15:
                print("... (truncated)")
                break
            print(f"  - {d['test_id']} (allowed {d['rfc_allowed']}, got {d['frr_observed']})")

    with open(out_path, "w") as f:
        json.dump({"summary": {
            "total": tally["TOTAL_EXECUTED"],
            "deviations": len(discrepancies),
            "matrix": tally["MATRIX"],
            "dry_run": dry_run,
            "coverage_mode": coverage_mode,
            "connection_failures": tally["CONNECTION_FAILURES"],
            "observation_errors": tally["OBSERVATION_ERRORS"],
            "skipped_asn2_cases": tally["SKIPPED_ASN2"],
            "corpus": corpus,
            "run_context": run_context,
        }, "discrepancies": discrepancies}, f, indent=2)
    print(f"Report: {out_path}")

def load_argdict(path):
    cases = []
    with open(path, "r") as f:
        for number, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                case = ast.literal_eval(line.strip())
            except (ValueError, SyntaxError) as exc:
                raise ValueError(f"{path}:{number}: expected a literal argument dictionary") from exc
            if not isinstance(case, dict):
                raise ValueError(f"{path}:{number}: expected a dictionary")
            cases.append(case)
    if not cases:
        raise ValueError(f"{path}: corpus is empty")
    return cases

def run_update_suite(cases, builder, oracle_eval, label, tally, discrepancies,
                     alloc, session, dry_run, limit, coverage_mode=False,
                     container=FRR_CONTAINER):
    """Generic runner for UPDATE-carrying suites. `builder(case, prefix_id)`
    returns (update_bytes, attrs_for_oracle, prefix_str|None, tag);
    `oracle_eval(attrs, case)` returns the ParseResult."""
    total = min(len(cases), limit) if limit is not None else len(cases)
    print(f"\n[*] Running suite: {label} ({total} cases)")
    for i, args in enumerate(cases[:total]):
        if (i + 1) % 10 == 0 or (i + 1) == total:
            print(f"    -> Progress: {i + 1} / {total} cases processed...", flush=True)

        update_bytes, attrs, prefix_str, tag = builder(args, alloc.next())
        if update_bytes[18] == 2:
            validate_update_attributes(update_bytes, attrs)
        oracle_res = oracle_eval(attrs, args)

        test_id = f"{label}-{i}-{tag}"
        if dry_run:
            evaluate_case(test_id, oracle_res, "DRY_RUN", args, tally, discrepancies)
            continue

        try:
            session.ensure()
        except Exception:
            tally["CONNECTION_FAILURES"] += 1
            session.invalidate()
            time.sleep(0.2)          # let FRR tear the dead peer down cleanly
            continue

        if not coverage_mode:
            clear_bgp_log(container)
        notif, active = send_update_and_monitor(session.sock, update_bytes, fast=coverage_mode)
        if not active:
            session.invalidate()
            time.sleep(0.15)         # avoid BGP connection-collision on reconnect

        installed = False
        if not coverage_mode and active and not notif and prefix_str is not None:
            time.sleep(0.05)
            try:
                installed = check_if_route_installed(prefix_str, container=container)
            except RuntimeError:
                tally["OBSERVATION_ERRORS"] += 1
                session.invalidate()
                continue
        observed = classify_observation(notif, active, installed)
        frr_log = get_bgp_log(container) if not dry_run and not coverage_mode else ''
        allowed = ALLOWED_OBSERVATIONS[oracle_res]
        evaluate_case(test_id, oracle_res, "COVERAGE_ONLY" if coverage_mode else observed,
                      args, tally, discrepancies, allowed=allowed, frr_log=frr_log)
        time.sleep(0.01)

def eval_legacy(attrs, args):
    # The OPEN advertises AS4; concrete AS_PATH payloads use four-byte ASNs.
    return parse_attributes(attrs, asn_4byte=True)

CORPUS_FILES = {
    "extended": "attr_argdict_extended.txt",
    "soft": "attr_argdict_soft.txt",
    "semantic": "attr_argdict_semantic.txt",
}


def execute_comprehensive_suite(suite="all", host=DEFAULT_HOST, port=DEFAULT_PORT,
                                limit=None, out_path=None, dry_run=False,
                                coverage_mode=False, fail_on_deviation=False,
                                container=FRR_CONTAINER):
    if suite not in ("all", *CORPUS_FILES):
        raise ValueError(f"unknown suite: {suite}")
    if limit is not None and limit < 0:
        raise ValueError("limit must be nonnegative")
    if dry_run and coverage_mode:
        raise ValueError("dry-run and coverage-mode are separate run modes")
    tally = {"TOTAL_EXECUTED": 0, "CONNECTION_FAILURES": 0,
             "OBSERVATION_ERRORS": 0, "SKIPPED_ASN2": 0, "MATRIX": {}}
    discrepancies, corpus = [], {}
    out_path = out_path or BASE_DIR / "parity_report_latest.json"
    session = None if dry_run else BgpSession(host, port)
    alloc = PrefixAllocator()

    def builder(case, prefix_id):
        args, version, slot = case
        return build_legacy_update(args, version, slot, prefix_id)

    def oracle(attrs, case):
        return eval_legacy(attrs, case[0])

    try:
        for label, name in CORPUS_FILES.items():
            if suite != "all" and suite != label:
                continue
            path = BASE_DIR / "tests" / name
            raw = load_argdict(path)
            corpus[name] = {"rows": len(raw),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            run_update_suite(expand_legacy_cases(raw), builder, oracle, label,
                             tally, discrepancies, alloc, session, dry_run, limit,
                             coverage_mode, container)
    finally:
        if session is not None:
            session.close()
    summarize_and_report(tally, discrepancies, out_path, dry_run, coverage_mode, corpus,
                         {"suite": suite, "host": host, "port": port,
                          "container": container, "limit": limit})
    if fail_on_deviation and (discrepancies or tally["CONNECTION_FAILURES"]
                              or tally["OBSERVATION_ERRORS"]):
        raise RuntimeError("parity run failed; see the JSON report for deviations/errors")
    return discrepancies


def main(argv=None):
    ap = argparse.ArgumentParser(description="Core BGP UPDATE parity fuzzer")
    ap.add_argument("--suite", choices=["all", *CORPUS_FILES], default="all")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--container", default=FRR_CONTAINER,
                    help="Docker container used for RIB/log queries (default: frr-lab)")
    ap.add_argument("--limit", type=int, help="max slot mutations per suite")
    ap.add_argument("--out", help="JSON path (default: parity_report_latest.json)")
    ap.add_argument("--coverage-mode", action="store_true", help="inject without parity checks")
    ap.add_argument("--dry-run", action="store_true", help="evaluate saved cases without Docker")
    ap.add_argument("--fail-on-deviation", action="store_true",
                    help="exit nonzero for mismatches or harness errors")
    ns = ap.parse_args(argv)
    try:
        execute_comprehensive_suite(suite=ns.suite, host=ns.host, port=ns.port,
                                    limit=ns.limit, out_path=ns.out, dry_run=ns.dry_run,
                                    coverage_mode=ns.coverage_mode,
                                    fail_on_deviation=ns.fail_on_deviation, container=ns.container)
    except (ValueError, OSError, RuntimeError) as exc:
        ap.exit(1, f"error: {exc}\n")


if __name__ == '__main__':
    main()
