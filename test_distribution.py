from models.bgpd.malformed_packets.attribute_model_extended import parse_attributes, BGPPathAttr, ParseResult

test_args = []
with open("models/bgpd/malformed_packets/tests/attr_argdict_soft.txt", "r") as f:
    for line in f:
        if not line.strip(): continue
        test_args.append(eval(line.strip()))

tally = {
    ParseResult.VALID: 0,
    ParseResult.SESSION_RESET: 0,
    ParseResult.AFI_SAFI_DISABLE: 0,
    ParseResult.TREAT_AS_WITHDRAW: 0,
    ParseResult.ATTRIBUTE_DISCARD: 0
}

for args in test_args:
    attrs = []
    # slot 1
    attrs.append(BGPPathAttr(flags=args["flags1"], type_code=1, length=args["len1"]))
    # slot 2 is fixed
    attrs.append(BGPPathAttr(flags=64, type_code=2, length=4))
    # slot 3 is fixed
    attrs.append(BGPPathAttr(flags=64, type_code=3, length=4))
    # slot 4
    attrs.append(BGPPathAttr(flags=args["flags4"], type_code=args["type4"], length=args["len4"]))

    res = parse_attributes(attrs)
    tally[res] += 1

print("Oracle Distribution:")
for k, v in tally.items():
    print(f"{k.name}: {v}")
