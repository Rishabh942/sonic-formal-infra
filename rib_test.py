import socket
import time
import subprocess
import json

from scapy.all import *
from scapy.contrib.bgp import *

target_ip = "127.0.0.1"
target_port = 1179

bgp_open = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="OPEN") / \
           BGPOpen(version=4, my_as=65002, hold_time=180, bgp_id="1.1.1.1", opt_params=[])

bgp_keepalive = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="KEEPALIVE")

setORIGIN   = BGPPathAttr(type_flags=0x40, type_code="ORIGIN", attribute=BGPPAOrigin(origin="IGP"))
setAS_valid = BGPPathAttr(type_flags=0x40, type_code="AS_PATH", attribute=BGPPAASPath(segments=[BGPPAASPath.ASPathSegment(segment_type=2, segment_value=[65002])]))
setNEXTHOP  = BGPPathAttr(type_flags=0x40, type_code="NEXT_HOP", attribute=[BGPPANextHop(next_hop="2.2.2.2")])

pkt = BGPHeader(marker=0xffffffffffffffffffffffffffffffff, type="UPDATE") / \
      BGPUpdate(withdrawn_routes_len=0, path_attr=[setORIGIN, setAS_valid, setNEXTHOP], nlri=[BGPNLRI_IPv4(prefix="11.0.0.0/24")])
if BGPHeader in pkt:  del pkt[BGPHeader].len
if BGPUpdate in pkt:  del pkt[BGPUpdate].path_attr_len
bgp_valid_update = bytes(pkt)

s = socket.socket()
s.connect((target_ip, target_port))
s.sendall(bytes(bgp_open))
s.recv(4096) # Recv OPEN
s.sendall(bytes(bgp_keepalive))
s.recv(4096) # Recv KEEPALIVE
s.sendall(bgp_valid_update)
time.sleep(1)

out = subprocess.check_output(["docker", "exec", "frr-lab", "vtysh", "-c", "show bgp ipv4 unicast json"])
print(out.decode())

s.close()
