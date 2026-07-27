from models.bgpd.malformed_packets.bgp_oracle import parse_attributes, BGPPathAttr

def test_attribute_sequence_soft(
    flags1: int, len1: int,
    flags4: int, type4: int, len4: int
) -> str:
    """Entry point for CrossHair to test Treat-as-Withdraw by hardcoding perfect AS_PATH and NEXT_HOP."""
    
    if not (0 <= flags1 <= 255) or not (0 <= flags4 <= 255):
        return "INVALID_INPUTS"
        
    if not (1 <= type4 <= 128):
        return "INVALID_INPUTS"
        
    if not (0 <= len1 <= 12) or not (0 <= len4 <= 12):
        return "INVALID_INPUTS"
        
    attrs = [
        BGPPathAttr(flags1, 1, len1),       # ORIGIN: Type 1
        BGPPathAttr(64, 2, 4),              # AS_PATH: Type 2, flags=64 (valid), len=4 (2-byte ASN)
        BGPPathAttr(64, 3, 4),              # NEXT_HOP: Type 3, flags=64 (valid), len=4
        BGPPathAttr(flags4, type4, len4)    # OPTIONAL/4th attribute
    ]
    res = parse_attributes(attrs)
    if res.name == "INVALID_INPUTS":
        return "INVALID_INPUTS"
    return res.name
