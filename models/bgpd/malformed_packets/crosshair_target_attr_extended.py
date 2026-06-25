from models.bgpd.malformed_packets.attribute_model_extended import BGPPathAttr, parse_attributes

def test_attribute_sequence_extended(
    flags1: int, type1: int, len1: int,
    flags2: int, type2: int, len2: int,
    flags3: int, type3: int, len3: int
) -> str:
    """Entry point for CrossHair to generate valid/malformed attribute sequences across all RFC 7606 types."""
    
    # Constrain inputs to ensure fast symbolic resolution and avoid infinite spaces
    if not (0 <= flags1 <= 255) or not (0 <= flags2 <= 255) or not (0 <= flags3 <= 255):
        return "INVALID_INPUTS"
        
    # Bounding between 1 and 128 is an SMT-friendly constraint for all known types
    if not (1 <= type1 <= 128) or not (1 <= type2 <= 128) or not (1 <= type3 <= 128):
        return "INVALID_INPUTS"
        
    if not (0 <= len1 <= 12) or not (0 <= len2 <= 12) or not (0 <= len3 <= 12):
        return "INVALID_INPUTS"
        
    attrs = [
        BGPPathAttr(flags1, type1, len1),
        BGPPathAttr(flags2, type2, len2),
        BGPPathAttr(flags3, type3, len3)
    ]
    
    res = parse_attributes(attrs)
    return res.name
