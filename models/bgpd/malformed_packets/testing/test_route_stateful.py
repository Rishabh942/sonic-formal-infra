"""Independent properties and adversarial adapter checks for route competition."""

import json
import unittest
from unittest.mock import patch

from models.bgpd.malformed_packets.route_model import (
    Event, Route, State, check_properties, explore, obligations, step,
)
from models.bgpd.malformed_packets.route_stateful import expected_export, read_rib
from models.bgpd.malformed_packets.route_wire import (
    PREFIXES, Peer, message, parse_update, update,
)


class RouteModelTests(unittest.TestCase):
    def test_complete_graph_and_generated_witnesses(self):
        graph = explore()
        # Four independent candidate slots, each absent or one of four routes.
        self.assertEqual(graph['states'], 5 ** 4)
        self.assertEqual(graph['edges'], 5 ** 4 * 28)
        achieved = set()
        for trace in graph['traces']:
            state = State()
            for event in trace:
                after = step(state, event)
                achieved.update(obligations(state, event, after))
                state = after
        self.assertEqual(achieved, set(graph['witnesses']))
        for peer in range(2):
            for kind in ('withdraw', 'bad_origin', 'bad_aspath'):
                self.assertIn(f'p0/peer{peer}/{kind}/selected-to-backup', achieved)

    def test_malformed_replacement_preserves_other_candidates(self):
        before = State((Route(1, 0), Route(2, 0), Route(2, 2), Route(1, 0)))
        for kind in ('bad_origin', 'bad_aspath'):
            event = Event(kind, 0, 0)
            after = step(before, event)
            self.assertEqual(after.routes, (None, Route(2, 0), Route(2, 2), Route(1, 0)))
            self.assertEqual(after.winner(0), 1)
            self.assertEqual(expected_export(after)[PREFIXES[0]]['path'],
                             [65001, 65003, 65003])

    def test_properties_detect_wrong_winner_and_overbroad_cleanup(self):
        before = State((Route(1, 2), Route(2, 0), Route(1, 0), None))
        event = Event('announce', 0, 0, Route(1, 2))
        with patch.object(State, 'winner', return_value=1):
            with self.assertRaisesRegex(AssertionError, 'longer AS path'):
                check_properties(before, event, before)
        event = Event('withdraw', 0, 0)
        with self.assertRaisesRegex(AssertionError, 'unrelated'):
            check_properties(before, event, State())


class RouteWireTests(unittest.TestCase):
    def test_fragmented_and_coalesced_updates_and_withdrawal(self):
        # Exercise stream decoder without opening sockets.
        peer = Peer.__new__(Peer)
        peer.index, peer.buffer, peer.rib = 2, b'', {}
        peer.opened, peer.established = True, True
        announce = update(Event('announce', 0, 0, Route(2, 2)))
        withdraw = update(Event('withdraw', 0, 0))
        for byte in announce:
            peer.feed(bytes((byte,)))
        self.assertEqual(peer.rib[PREFIXES[0]], {'path': [65002, 65002], 'origin': 2})
        peer.feed(message(4) + withdraw + message(4))
        self.assertEqual(peer.rib, {})

    def test_malformed_packets_keep_outer_framing_and_fail_attribute_decode(self):
        for kind, error in [('bad_origin', 'ORIGIN'), ('bad_aspath', 'AS_SEQUENCE')]:
            packet = update(Event(kind, 0, 0))
            self.assertEqual(int.from_bytes(packet[16:18], 'big'), len(packet))
            self.assertEqual(packet[-4:], bytes((24, 198, 18, 0)))
            with self.assertRaisesRegex(ValueError, error):
                parse_update(packet[19:], {})

    def test_observation_error_is_not_route_absence(self):
        with patch('subprocess.check_output', return_value=b'% daemon unavailable'):
            with self.assertRaisesRegex(RuntimeError, 'non-JSON'):
                read_rib()
        with patch('subprocess.check_output', return_value=b'{"error": "unavailable"}'):
            with self.assertRaisesRegex(ValueError, 'unexpected RIB'):
                read_rib()
        with patch('subprocess.check_output', return_value=json.dumps({}).encode()):
            self.assertEqual(read_rib(), dict.fromkeys(PREFIXES, []))


if __name__ == '__main__':
    unittest.main()
