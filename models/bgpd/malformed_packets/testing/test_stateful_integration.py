"""Guard packet/state oracle composition and shared runner/report semantics."""

from contextlib import redirect_stdout
from io import StringIO
from itertools import product
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from models.bgpd.malformed_packets.bgp_oracle import ParseResult
from models.bgpd.malformed_packets.generate_aspath_suite import test_as_path_structure
from models.bgpd.malformed_packets.gr_model import (
    GrEvent, GrState, RouteState, checked_step, enabled_events, generate_traces,
    gr_obligations, check_transition,
)
from models.bgpd.malformed_packets.packet_builders import decode_update_attributes
from models.bgpd.malformed_packets.route_model import EVENTS, Event, Route, State
from models.bgpd.malformed_packets.route_wire import oracle_transition, update
from models.bgpd.malformed_packets.run_parity_fuzzer import (
    build_aspath_update, eval_aspath, execute_comprehensive_suite, record_stateful_results,
)


class PacketOracleIntegrationTests(unittest.TestCase):
    def test_symbolic_entry_and_live_builder_agree(self):
        # Boundary/structural partitions including optional AS4_PATH and
        # first-AS rejection of AS_SET, with two- and four-byte encodings.
        for values in product(range(5), (0, 1, 4), (0, 2), (0, 1), (0, 1), (0, 1), (-3, 0, 3)):
            args = dict(zip(('seg1_type', 'seg1_count', 'seg2_type', 'seg2_count',
                             'asn_4byte', 'with_as4_path', 'extra_len'), values))
            packet, attrs, _, _ = build_aspath_update(args, 1)
            self.assertEqual(decode_update_attributes(packet)[1], attrs)
            self.assertEqual(test_as_path_structure(**args), eval_aspath(attrs, args).name)

    def test_all_route_event_encodings_use_existing_oracle(self):
        for event in EVENTS:
            verdict, _ = oracle_transition(State(), event, update(event))
            self.assertEqual(verdict, 'WITHDRAW' if event.kind == 'withdraw' else
                             'VALID' if event.kind == 'announce' else 'TREAT_AS_WITHDRAW')

    def test_builder_or_oracle_drift_is_rejected(self):
        event = Event('announce', 0, 0, Route(1, 0))
        wrong_wire = update(Event('announce', 0, 0, Route(2, 0)))
        with self.assertRaisesRegex(AssertionError, 'disagreement'):
            oracle_transition(State(), event, wrong_wire)
        bad = Event('bad_origin', 0, 0)
        with patch('models.bgpd.malformed_packets.route_wire.parse_attributes',
                   return_value=ParseResult.VALID):
            with self.assertRaises((ValueError, AssertionError)):
                oracle_transition(State(), bad, update(bad))
        packet = bytearray(update(event))
        packet[21:23] = (65535).to_bytes(2, 'big')
        with self.assertRaisesRegex(ValueError, 'truncated'):
            decode_update_attributes(bytes(packet))


class GeneratedGrTests(unittest.TestCase):
    def test_all_generated_traces_are_enabled_and_cover_reported_goals(self):
        graph = generate_traces()
        reached = set()
        for gr, trace in graph['traces']:
            state = GrState.initial(gr)
            for event in trace:
                self.assertIn(event, tuple(enabled_events(state)))
                after = checked_step(state, event)
                reached.update(gr_obligations(state, event, after))
                state = after
        self.assertEqual(reached, set(graph['witnesses']))
        self.assertIn('gr1/eor/active1/stale1', reached)
        self.assertIn('gr1/timer/active0/stale2', reached)
        self.assertIn('gr0/disconnect/active2/stale0', reached)

    def test_illegal_event_and_overbroad_cleanup_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'not enabled'):
            checked_step(GrState.initial(True), GrEvent('reconnect_f1'))
        before = GrState((RouteState.ACTIVE, RouteState.STALE), True)
        with self.assertRaisesRegex(AssertionError, 'cleanup'):
            check_transition(before, GrEvent('eor'), GrState.initial(True))

    def test_consecutive_restart_discards_old_stale_and_retains_refreshed_route(self):
        # RFC 4724 section 4.2: do not retain the same stale route indefinitely.
        before = GrState((RouteState.STALE, RouteState.ACTIVE), True)
        after = checked_step(before, GrEvent('disconnect'))
        self.assertEqual(after.routes, (RouteState.ABSENT, RouteState.STALE))
        self.assertFalse(after.connected)


class SharedRunnerTests(unittest.TestCase):
    def test_main_runner_writes_failure_and_exits_nonzero_on_oracle_disagreement(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            output = Path(directory) / 'report.json'
            with patch('models.bgpd.malformed_packets.route_wire.parse_attributes',
                       return_value=ParseResult.SESSION_RESET):
                with self.assertRaises(SystemExit) as failure:
                    execute_comprehensive_suite(suite='routecompetition', dry_run=True,
                                                limit=1, out_path=str(output),
                                                fail_on_deviation=True)
            self.assertEqual(failure.exception.code, 1)
            report = json.loads(output.read_text())
            self.assertEqual(report['summary']['deviations'], 1)
            self.assertEqual(report['summary']['matrix']['ROUTE_COMPETITION']['FAIL'], 1)
            self.assertIn('packet oracle verdict', report['discrepancies'][0]['error'])

    def test_dry_run_has_shared_schema_and_no_empirical_passes(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            output = Path(directory) / 'report.json'
            execute_comprehensive_suite(suite='generated', dry_run=True, limit=2,
                                        out_path=str(output), fail_on_deviation=True)
            report = json.loads(output.read_text())
            self.assertEqual(report['summary']['total'], 4)
            for row in report['summary']['matrix'].values():
                self.assertEqual(row, {'TOTAL': 2, 'PASS': 0, 'FAIL': 0})
            self.assertEqual({r['suite'] for r in report['stateful_results']},
                             {'routecompetition', 'grgenerated'})
            for result in report['stateful_results']:
                self.assertTrue(all('oracle_verdict' in e for e in result['events']))
            execute_comprehensive_suite(suite='generated', dry_run=True, limit=0,
                                        out_path=str(output), fail_on_deviation=True)
            self.assertEqual(json.loads(output.read_text())['summary']['total'], 0)

    def test_dry_run_and_coverage_errors_are_not_suppressed(self):
        for dry, coverage in ((True, False), (False, True)):
            tally = {'TOTAL_EXECUTED': 0, 'MATRIX': {}}
            failures, results = [], []
            record_stateful_results('routecompetition', 'ROUTE_COMPETITION',
                                    [{'name': 'bad', 'pass': False, 'error': 'oracle mismatch'}],
                                    tally, failures, results, dry, coverage)
            self.assertEqual(tally['MATRIX']['ROUTE_COMPETITION']['FAIL'], 1)
            self.assertEqual(len(failures), 1)


if __name__ == '__main__':
    unittest.main()
