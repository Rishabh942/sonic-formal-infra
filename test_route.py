import socket
import struct
import time
import subprocess
import json
from models.bgpd.malformed_packets.run_parity_fuzzer import build_bgp_open, build_bgp_keepalive, get_rib_route_count

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 1179))
s.sendall(build_bgp_open())
time.sleep(0.5)
s.sendall(build_bgp_keepalive())
time.sleep(0.5)

attr_bytes = struct.pack('!BBB', 64, 2, 6) + b'\x02\x01\x00\x00\xfd\xea'
attr_bytes += struct.pack('!BBB', 64, 3, 4) + b'\x01\x01\x01\x01'
attr_bytes += struct.pack('!BBB', 64, 1, 1) + b'\x00'

nlri_bytes = b'\x18\x0a\x00\x00'
update_len = 23 + len(attr_bytes) + len(nlri_bytes)
update_bytes = b'\xff'*16 + struct.pack('!HB', update_len, 2) + b'\x00\x00' + struct.pack('!H', len(attr_bytes)) + attr_bytes + nlri_bytes

s.sendall(update_bytes)
time.sleep(1)

count = get_rib_route_count()
print(f"Route count: {count}")

s.close()
