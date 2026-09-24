"""Wire-level checks for the Graceful Restart corpus and OPEN oracle."""

import struct
import unittest

from models.bgpd.malformed_packets.bgp_oracle import (
    ParseResult, parse_capabilities, scan_as_path,
)
from models.bgpd.malformed_packets.gr_model import (
    GrState, RouteState, check_bounded_invariants, step,
)
from models.bgpd.malformed_packets.graceful_restart import (
    IPV4_END_OF_RIB, build_graceful_restart_open, graceful_restart_cases,
)
from models.bgpd.malformed_packets.packet_builders import wrap_capability
from models.bgpd.malformed_packets.run_parity_fuzzer import (
    _extract_opt_params, build_aspath_update,
)


class GracefulRestartTests(unittest.TestCase):
    def test_capability_codes_and_tuple_boundary(self):
        valid = (b'\x00\x5a', b'\x80\x5a\x00\x01\x01\x80')
        invalid = (b'', b'\x00', b'\x00\x5a\x00', b'\x00\x5a\x00\x01\x01')
        for body in valid:
            with self.subTest(body=body):
                self.assertEqual(parse_capabilities(wrap_capability(
                    bytes((64, len(body))) + body)), ParseResult.VALID)
        for body in invalid:
            with self.subTest(body=body):
                self.assertEqual(parse_capabilities(wrap_capability(
                    bytes((64, len(body))) + body)), ParseResult.SESSION_RESET)
        self.assertEqual(parse_capabilities(wrap_capability(b'\x41\x04\x00\x00\xfd\xea')),
                         ParseResult.VALID)  # code 65 is four-octet ASN
        self.assertEqual(parse_capabilities(wrap_capability(b'\x41\x02\x00\x00')),
                         ParseResult.SESSION_RESET)

    def test_corpus_wire_is_self_consistent(self):
        cases = graceful_restart_cases()
        self.assertEqual(len({case['name'] for case in cases}), len(cases))
        self.assertGreaterEqual(len(cases), 25)
        results = set()
        for case in cases:
            with self.subTest(case=case['name']):
                msg = build_graceful_restart_open(case)
                self.assertEqual(struct.unpack('!H', msg[16:18])[0], len(msg))
                self.assertEqual(msg[18], 1)
                self.assertEqual(msg[28], len(msg) - 29)
                results.add(parse_capabilities(_extract_opt_params(msg)))
        self.assertEqual(results, {ParseResult.VALID, ParseResult.SESSION_RESET})

    def test_end_of_rib_is_minimal_update(self):
        self.assertEqual(len(IPV4_END_OF_RIB), 23)
        self.assertEqual(IPV4_END_OF_RIB[18], 2)
        self.assertEqual(IPV4_END_OF_RIB[19:], b'\x00' * 4)

    def test_as4_path_flags_and_lab_first_as_policy(self):
        args = {'seg1_type': 2, 'seg1_count': 1, 'seg2_type': 0,
                'seg2_count': 0, 'asn_4byte': 1,
                'with_as4_path': 1, 'extra_len': 0}
        _, attrs, _, _ = build_aspath_update(args, 1)
        self.assertEqual(attrs[-1].type_code, 17)
        self.assertEqual(attrs[-1].flags, 0xC0)  # optional transitive
        self.assertTrue(scan_as_path(attrs[1].value, 4, False, 65002))
        self.assertFalse(scan_as_path(b'\x01\x01\x00\x00\xfd\xea',
                                      4, False, 65002))

    def test_bounded_gr_reference_model(self):
        transitions, states = check_bounded_invariants(4)
        self.assertGreater(transitions, 500000)
        self.assertGreater(states, 10)
        model = GrState.initial(True)
        model = step(step(model, 'announce', 0), 'disconnect')
        self.assertEqual(model.routes[0], RouteState.STALE)
        model = step(step(model, 'reconnect_f1'), 'eor')
        self.assertEqual(model.routes[0], RouteState.ABSENT)


if __name__ == '__main__':
    unittest.main()
