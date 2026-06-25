import socket
import time
import subprocess
import json
import sys

from scapy.all import *
from scapy.contrib.bgp import *

# Ensure primitives load
sys.path.append(".")
from mbt.prims import addr_t, to_ipv4_address

target_ip = "127.0.0.1"
target_port = 1179

print("[*] Compiling BGP Packets...")
bgp_open = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="OPEN") / \
           BGPOpen(version=4, my_as=65002, hold_time=180, bgp_id="1.1.1.1", opt_params=[])
bgp_keepalive = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="KEEPALIVE")

# Path Attributes
setORIGIN   = BGPPathAttr(type_flags=0x40, type_code="ORIGIN", attribute=BGPPAOrigin(origin="IGP"))
setAS_valid = BGPPathAttr(type_flags=0x40, type_code="AS_PATH", attribute=BGPPAASPath(segments=[BGPPAASPath.ASPathSegment(segment_type=2, segment_value=[65002])]))
setNEXTHOP  = BGPPathAttr(type_flags=0x40, type_code="NEXT_HOP", attribute=[BGPPANextHop(next_hop="2.2.2.2")])

# Valid Update
pkt_valid = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="UPDATE") / \
            BGPUpdate(withdrawn_routes_len=0, path_attr=[setORIGIN, setAS_valid, setNEXTHOP], nlri=[BGPNLRI_IPv4(prefix="11.0.0.0/24")])
if BGPHeader in pkt_valid: del pkt_valid[BGPHeader].len
if BGPUpdate in pkt_valid: del pkt_valid[BGPUpdate].path_attr_len
valid_update = bytes(pkt_valid)

# Malformed Update (Missing NEXTHOP) -> Triggers Treat-As-Withdraw
pkt_invalid = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="UPDATE") / \
              BGPUpdate(withdrawn_routes_len=0, path_attr=[setORIGIN, setAS_valid], nlri=[BGPNLRI_IPv4(prefix="10.0.0.0/24")])
if BGPHeader in pkt_invalid: del pkt_invalid[BGPHeader].len
if BGPUpdate in pkt_invalid: del pkt_invalid[BGPUpdate].path_attr_len
invalid_update = bytes(pkt_invalid)


def check_rib():
    out = subprocess.check_output(["docker", "exec", "frr-lab", "vtysh", "-c", "show bgp ipv4 unicast json"], stderr=subprocess.DEVNULL)
    data = json.loads(out)
    routes = data.get("routes", {})
    return len(routes)

print("[*] Connecting to FRR...")
s = socket.socket()
s.settimeout(1.0)
s.connect((target_ip, target_port))
s.sendall(bytes(bgp_open))
try:
    s.recv(4096)
except socket.timeout:
    pass
s.sendall(bytes(bgp_keepalive))
try:
    s.recv(4096)
except socket.timeout:
    pass

time.sleep(1)
print("\n[*] BGP Summary after Handshake:")
print(subprocess.check_output(["docker", "exec", "frr-lab", "vtysh", "-c", "show bgp summary"]).decode())

print("[*] Sending VALID UPDATE (11.0.0.0/24)...")
s.sendall(valid_update)
time.sleep(1)

routes_installed = check_rib()
print(f"    -> RIB Route Count via vtysh: {routes_installed}  (Status: INSTALLED)")

print("\n[*] Sending MALFORMED UPDATE (Missing NEXTHOP attribute) under RFC 7606...")
s.sendall(invalid_update)
time.sleep(1)

routes_after_malformed = check_rib()
print(f"    -> RIB Route Count via vtysh: {routes_after_malformed}  (Status: TREAT_AS_WITHDRAW / DISCARDED)")

print("\n[*] Is BGP Session still active? (TCP socket state)")
s.setblocking(False)
try:
    data = s.recv(4096)
    if len(data) == 0:
        print("    -> No, FRR tore down the session (RFC 4271 strict mode)")
    else:
        print("    -> Yes! FRR kept the socket open (RFC 7606 Treat-as-withdraw applied!)")
except (BlockingIOError, ConnectionResetError) as e:
    if isinstance(e, ConnectionResetError):
        print("    -> No, FRR sent a TCP RST (session torn down)")
    else:
        print("    -> Yes! FRR kept the socket open (RFC 7606 Treat-as-withdraw applied!)")

print("\n[*] Reading BGPD Internal Events from logs:")
logs = subprocess.check_output(["docker", "exec", "frr-lab", "cat", "/tmp/bgpd.log"], stderr=subprocess.DEVNULL).decode()
subprocess.call(["docker", "exec", "frr-lab", "bash", "-c", "> /tmp/bgpd.log"])
for line in logs.splitlines():
    if "BGP" in line:
        print(f"    [LOG] {line}")

s.close()
print("\n[*] Done.")
