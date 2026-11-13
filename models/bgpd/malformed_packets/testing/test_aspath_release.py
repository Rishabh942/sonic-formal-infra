"""AS_PATH cut gates for reproducible inputs and model/wire agreement."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from models.bgpd.malformed_packets import run_parity_fuzzer as runner
from models.bgpd.malformed_packets.bgp_oracle import (
    BGPPathAttr, ParseResult, parse_attributes,
)
from models.bgpd.malformed_packets.generate_aspath_suite import test_as_path_structure
from models.bgpd.malformed_packets.packet_builders import build_as_path_value
from models.bgpd.malformed_packets.seed_aspath_suite import build_corpus


class AsPathReleaseTests(unittest.TestCase):
    def test_length_adjustment_removes_bytes_from_end(self):
        value = build_as_path_value(2, 1, 0, 0)
        self.assertEqual(value, b'\x02\x01\x00\x00\xfd\xea')
        self.assertEqual(build_as_path_value(2, 1, 0, 0, -1), value[:-1])
        self.assertEqual(build_as_path_value(2, 1, 0, 0, 2), value + b'\x00\x00')

    def test_bounded_generation_and_saved_corpus_agree(self):
        checked, distinct, expected = build_corpus()
        self.assertEqual((checked, distinct, len(expected)), (8750, 5552, 153))
        saved = runner.load_argdict(runner.BASE_DIR / 'tests' / runner.ASPATH_FILE)
        self.assertEqual(saved, expected)
        for index, args in enumerate(saved, 1):
            packet, attrs, _, _ = runner.build_aspath_update(args, index)
            runner.validate_update_attributes(packet, attrs)
            self.assertEqual(test_as_path_structure(**args),
                             runner.eval_aspath(attrs, args).name)

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

    def test_dry_run_records_no_empirical_passes(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            out = Path(tmp) / 'aspath.json'
            runner.execute_comprehensive_suite(suite='aspath', dry_run=True,
                                                fail_on_deviation=True, out_path=out)
            summary = json.loads(out.read_text())['summary']
            self.assertEqual(summary['total'], 153)
            self.assertEqual(summary['deviations'], 0)
            self.assertEqual(sum(row['PASS'] for row in summary['matrix'].values()), 0)
            self.assertEqual(summary['corpus'][runner.ASPATH_FILE]['rows'], 153)


if __name__ == '__main__':
    unittest.main()
