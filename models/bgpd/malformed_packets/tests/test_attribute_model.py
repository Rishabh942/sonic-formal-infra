from models.bgpd.malformed_packets.attribute_model import BGPPathAttr, parse_attributes, ParseResult

def test_valid_attributes():
    attrs = [
        BGPPathAttr(flags=0x40, type_code=1, length=1), # ORIGIN
        BGPPathAttr(flags=0x40, type_code=2, length=0), # AS_PATH
        BGPPathAttr(flags=0x40, type_code=3, length=4)  # NEXT_HOP
    ]
    assert parse_attributes(attrs) == ParseResult.VALID

def test_flag_18_resolution():
    # 18 = 0x12 = Extended Length + Reserved. Missing Transitive (0x40).
    attrs = [
        BGPPathAttr(flags=0x40, type_code=1, length=1), # ORIGIN
        BGPPathAttr(flags=18,   type_code=2, length=0), # AS_PATH with flag 18
        BGPPathAttr(flags=0x40, type_code=3, length=4)  # NEXT_HOP
    ]
    res = parse_attributes(attrs)
    assert res == ParseResult.BAD_FLAGS, f"Expected BAD_FLAGS for flag 18 on AS_PATH, got {res}"

def test_duplicate_origin():
    # Two ORIGIN attributes in the same update
    attrs = [
        BGPPathAttr(flags=0x40, type_code=1, length=1), # ORIGIN 1
        BGPPathAttr(flags=0x40, type_code=2, length=0), # AS_PATH
        BGPPathAttr(flags=0x40, type_code=3, length=4), # NEXT_HOP
        BGPPathAttr(flags=0x40, type_code=1, length=1)  # ORIGIN 2
    ]
    res = parse_attributes(attrs)
    assert res == ParseResult.DUPLICATE_ATTRIBUTE, f"Expected DUPLICATE_ATTRIBUTE, got {res}"

if __name__ == "__main__":
    test_valid_attributes()
    test_flag_18_resolution()
    test_duplicate_origin()
    print("All unit tests passed perfectly! Oracle bit math and duplicate logic is mathematically sound.")
