import os

test_cases = [
    # AS_PATH (type 2) segment length overrun
    # flags=64, type=2, len=3, value=b'\x02\x05\x00'
    {"flags1": 64, "len1": 1, "payload_hex1": "00", "flags4": 64, "type4": 2, "len4": 3, "payload_hex": "020500"},
    # AS_PATH (type 2) invalid segment type
    # flags=64, type=2, len=3, value=b'\x05\x00\x00'
    {"flags1": 64, "len1": 1, "payload_hex1": "00", "flags4": 64, "type4": 2, "len4": 3, "payload_hex": "050000"},
    # MP_REACH_NLRI (type 14) short value
    # flags=144, type=14, len=4, value=b'\x00\x01\x01\x04'
    {"flags1": 64, "len1": 1, "payload_hex1": "00", "flags4": 144, "type4": 14, "len4": 4, "payload_hex": "00010104"},
    # MP_REACH_NLRI (type 14) bad next hop length framing
    # flags=144, type=14, len=6, value=b'\x00\x01\x01\x04\x01\x02'
    {"flags1": 64, "len1": 1, "payload_hex1": "00", "flags4": 144, "type4": 14, "len4": 6, "payload_hex": "000101040102"},
    # MP_UNREACH_NLRI (type 15) short value
    # flags=144, type=15, len=2, value=b'\x00\x01'
    {"flags1": 64, "len1": 1, "payload_hex1": "00", "flags4": 144, "type4": 15, "len4": 2, "payload_hex": "0001"},
]

with open("models/bgpd/malformed_packets/tests/attr_argdict_soft.txt", "a") as f:
    for tc in test_cases:
        f.write(repr(tc) + "\n")

print("Added complex test cases.")
