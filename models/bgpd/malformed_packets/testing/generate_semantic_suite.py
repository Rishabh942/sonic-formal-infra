import json

def generate_semantic_communities():
    suite = []
    
    # Standard properties for optional transitive community attributes
    # flags=0xC0 (Optional=1, Transitive=1)
    
    # 1. Type 8: Communities (RFC 1997)
    # 4 byte payloads.
    t8_payloads = [
        "00000000", # Reserved
        "0000FFFF", # Reserved boundary
        "FFFF0000", # Reserved boundary
        "FFFFFFFF", # Reserved
        "FFFFFF01", # NO_EXPORT (Well-known)
        "FFFFFF02", # NO_ADVERTISE (Well-known)
        "FFFFFF03", # NO_EXPORT_SUBCONFED (Well-known)
        "12345678", # Random Standard
    ]
    for p in t8_payloads:
        suite.append({
            "flags4": 0xC0,
            "type4": 8,
            "len4": 4,
            "payload_hex": p
        })
        
    # 2. Type 16: Extended Communities (RFC 4360, 5668, 7153)
    # 8 byte payloads. First 1-2 bytes are Type/Sub-Type.
    # RFC 4360 Types: 0x00 (2-octet AS), 0x01 (IPv4), 0x02 (4-octet AS - RFC 5668)
    t16_payloads = [
        "0000000000000000", # All zeros
        "0002123456789012", # Type 0x00 (2-octet AS), SubType 0x02 (Route Target)
        "01020A0000010001", # Type 0x01 (IPv4), SubType 0x02 (Route Target) - 10.0.0.1:1
        "0202112233440001", # Type 0x02 (4-octet AS - RFC 5668), SubType 0x02 (Route Target)
        "0600000000000000", # EVPN (Type 0x06) Mac Mobility (SubType 0x00)
        "8000000000000000", # Non-transitive bit set in Type (0x80)
        "FF00000000000000", # IANA Reserved Type (0xFF)
        "02FF000000000000", # Valid Type 0x02, Invalid/Reserved SubType 0xFF
        "0300123456789012", # Opaque (Type 0x03)
    ]
    for p in t16_payloads:
        suite.append({
            "flags4": 0xC0,
            "type4": 16,
            "len4": 8,
            "payload_hex": p
        })

    # 3. Type 32: Large Communities (RFC 8092)
    # 12 byte payloads. (4-byte Global Admin, 4-byte Local Data 1, 4-byte Local Data 2)
    t32_payloads = [
        "000000000000000000000000", # All zeros
        "FFFFFFFFFFFFFFFFFFFFFFFF", # All F's
        "112233445566778899AABBCC", # Random Valid
    ]
    for p in t32_payloads:
        suite.append({
            "flags4": 0xC0,
            "type4": 32,
            "len4": 12,
            "payload_hex": p
        })
        
    # Edge Cases: Incorrect Lengths (Truncated payloads)
    suite.append({
        "flags4": 0xC0,
        "type4": 16,
        "len4": 8,          # Claims 8 bytes
        "payload_hex": "00" # Only provides 1 byte
    })
    
    suite.append({
        "flags4": 0xC0,
        "type4": 8,
        "len4": 4,          # Claims 4 bytes
        "payload_hex": "0000000000000000" # Provides 8 bytes
    })

    out_path = "models/bgpd/malformed_packets/tests/attr_argdict_semantic.txt"
    with open(out_path, "w") as f:
        for args in suite:
            f.write(str(args) + "\n")
            
    print(f"[+] Wrote {len(suite)} semantic test cases to {out_path}")

if __name__ == "__main__":
    generate_semantic_communities()
