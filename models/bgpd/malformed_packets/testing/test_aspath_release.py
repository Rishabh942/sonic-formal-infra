"""Direct AS_PATH wire-builder and RFC oracle checks."""

import unittest

from models.bgpd.malformed_packets import run_parity_fuzzer as runner
from models.bgpd.malformed_packets.bgp_oracle import (
    BGPPathAttr, ParseResult, parse_attributes,
)
from models.bgpd.malformed_packets.packet_builders import build_as_path_value


class AsPathReleaseTests(unittest.TestCase):
    def test_length_adjustment_removes_bytes_from_end(self):
        value = build_as_path_value(2, 1, 0, 0)
        self.assertEqual(value, b'\x02\x01\x00\x00\xfd\xea')
        self.assertEqual(build_as_path_value(2, 1, 0, 0, -1), value[:-1])
        self.assertEqual(build_as_path_value(2, 1, 0, 0, 2), value + b'\x00\x00')

    def test_first_as_and_as4_path_failures(self):
        origin, _, next_hop = runner._mandatory_attrs()
        good = BGPPathAttr(64, 2, 6, build_as_path_value(2, 1, 0, 0))
        bad_first = BGPPathAttr(64, 2, 6, b'\x02\x01\x00\x00\xfd\xeb')
        self.assertEqual(parse_attributes([origin, good, next_hop],
                                          asn_4byte=True, enforce_first_as=65002),
                         ParseResult.VALID)
        self.assertEqual(parse_attributes([origin, bad_first, next_hop],
                                          asn_4byte=True, enforce_first_as=65002),
                         ParseResult.TREAT_AS_WITHDRAW)
        malformed_as4 = BGPPathAttr(0xC0, 17, 2, b'\x02\x01')
        self.assertEqual(parse_attributes([origin, good, next_hop, malformed_as4],
                                          asn_4byte=True, enforce_first_as=65002),
                         ParseResult.ATTRIBUTE_DISCARD)

if __name__ == '__main__':
    unittest.main()
