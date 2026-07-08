import struct
attr_bytes = struct.pack('!BBB', 64, 2, 6) + b'\x02\x01\x00\x00\xfd\xea'
attr_bytes += struct.pack('!BBB', 64, 3, 4) + b'\x01\x01\x01\x01'
attr_bytes += struct.pack('!BBB', 64, 1, 1) + b'\x00'

fuzzed = struct.pack('!BBB', 0, 1, 0)
attr_bytes += fuzzed
nlri_bytes = b'\x18\x0a\x00\x00'
update_len = 23 + len(attr_bytes) + len(nlri_bytes)
packet = b'\xff'*16 + struct.pack('!HB', update_len, 2) + b'\x00\x00' + struct.pack('!H', len(attr_bytes)) + attr_bytes + nlri_bytes

print(' '.join(f'{b:02x}' for b in packet))
