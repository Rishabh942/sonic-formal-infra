import socket, struct, time, json
with open("models/bgpd/malformed_packets/tests/attr_argdict_extended.txt") as f:
    args = eval(f.readline().strip())

for k in args.keys():
    if 'len' in k and (args[k.replace('len', 'flags')] & 0x10):
        args[k] = args[k] & 0xFFFF
    elif 'len' in k or 'type' in k or 'flags' in k:
        args[k] = args[k] & 0xFF

attr_bytes = b''
for i in range(1, 4):
    attr_bytes += struct.pack('!BB', args[f"flags{i}"], args[f"type{i}"])
    if args[f"flags{i}"] & 0x10:
        attr_bytes += struct.pack('!H', args[f"len{i}"])
    else:
        attr_bytes += struct.pack('!B', args[f"len{i}"])
    attr_bytes += b'\x00' * args[f"len{i}"]

nlri = b'\x18\xc0\xa8\x01'
update_len = 23 + len(attr_bytes) + len(nlri)
update_bytes = b'\xff'*16 + struct.pack('!HB', update_len, 2) + b'\x00\x00' + struct.pack('!H', len(attr_bytes)) + attr_bytes + nlri

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2.0)
s.connect(("127.0.0.1", 1179))
s.sendall(b'\xff'*16 + b'\x00\x3b\x01\x04\xfd\xea\x00\x5a\x00\x00\x00\x00\x1e\x02\x06\x01\x04\x00\x01\x00\x01\x02\x02\x80\x00\x02\x02\x02\x00\x02\x02\x46\x00\x02\x06\x41\x04\x00\x00\xfd\xea')
try:
    print("Received after OPEN:", s.recv(4096))
except Exception as e:
    print("OPEN error", e)

s.sendall(b'\xff'*16 + b'\x00\x13\x04')
print("Sending UPDATE...")
s.sendall(update_bytes)

time.sleep(0.5)

while True:
    try:
        data = s.recv(4096)
        if not data:
            print("Socket closed gracefully by FRR")
            break
        print(f"Received chunk ({len(data)} bytes):", data)
    except socket.timeout:
        print("Socket timed out waiting for more data.")
        break
    except Exception as e:
        print("Error reading:", e)
        break

s.close()
