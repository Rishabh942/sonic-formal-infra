"""Offline release gates for packet/model correspondence and harness failures."""
import contextlib
import io
import json
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from models.bgpd.malformed_packets import run_parity_fuzzer as runner
from models.bgpd.malformed_packets.bgp_oracle import ParseResult, parse_capabilities
from models.bgpd.malformed_packets.dummy_peer import build_open
from models.bgpd.malformed_packets.generate_aspath_suite import test_as_path_structure
from models.bgpd.malformed_packets.generate_mpreach_suite import test_mp_reach_structure
from models.bgpd.malformed_packets.generate_opencap_suite import test_open_capabilities
from models.bgpd.malformed_packets.packet_builders import (
    build_as_path_value, build_capability_value, wrap_capability,
)
from models.bgpd.malformed_packets.seed_structural_suites import (
    enumerate_space, verdict_of, wire_of,
)


class ReleaseTests(unittest.TestCase):
    def test_aspath_truncation_removes_requested_suffix(self):
        for asn4 in (False, True):
            value = build_as_path_value(2, 3, 1, 2, asn4)
            for count in range(1, len(value) + 3):
                with self.subTest(asn4=asn4, count=count):
                    shortened = build_as_path_value(2, 3, 1, 2, asn4, -count)
                    self.assertEqual(len(shortened), max(0, len(value) - count))
                    self.assertTrue(value.startswith(shortened))

    def test_structural_grid_matches_generator_and_wire(self):
        counts = {name: 0 for name in ('aspath', 'mpreach', 'opencap')}
        for suite, args in enumerate_space():
            counts[suite] += 1
            verdict = verdict_of(suite, args).name
            if suite == 'aspath':
                generated = test_as_path_structure(**args)
                packet, attrs, _, _ = runner.build_aspath_update(args, 1)
                runner.validate_update_attributes(packet, attrs)
            elif suite == 'mpreach':
                generated = test_mp_reach_structure(**args)
                packet, attrs, _, _ = runner.build_mpreach_update(args, 1)
                runner.validate_update_attributes(packet, attrs)
            else:
                generated = test_open_capabilities(**args)
            if generated != verdict:
                self.fail(f'{suite} mismatch for {args}: {generated} != {verdict}')
        self.assertEqual(counts, {'aspath': 17500, 'mpreach': 5400, 'opencap': 535})

    def test_registry_capability_lengths(self):
        valid_lengths = {64: {2, 6}, 65: {4}, 69: {4}, 9: {1}}
        for code, lengths in valid_lengths.items():
            for length in range(7):
                with self.subTest(code=code, length=length):
                    wire = wrap_capability(build_capability_value(code, length, True))
                    expected = ParseResult.VALID if length in lengths else ParseResult.SESSION_RESET
                    self.assertEqual(parse_capabilities(wire), expected)

    def test_as4_flags_and_first_as_policy(self):
        args = dict(seg1_type=2, seg1_count=1, seg2_type=0, seg2_count=0,
                    asn_4byte=1, with_as4_path=1, extra_len=0)
        _, attrs, _, _ = runner.build_aspath_update(args, 1)
        self.assertEqual(runner.eval_aspath(attrs, args), ParseResult.VALID)
        attrs[-1].flags = 128
        self.assertEqual(runner.eval_aspath(attrs, args), ParseResult.TREAT_AS_WITHDRAW)
        args['with_as4_path'] = 0
        args['seg1_type'] = 1
        _, attrs, _, _ = runner.build_aspath_update(args, 2)
        self.assertEqual(runner.eval_aspath(attrs, args), ParseResult.TREAT_AS_WITHDRAW)

    def test_wire_mismatch_rejected(self):
        args = dict(seg1_type=2, seg1_count=1, seg2_type=0, seg2_count=0,
                    asn_4byte=1, with_as4_path=0, extra_len=0)
        packet, attrs, _, _ = runner.build_aspath_update(args, 1)
        mutated = bytearray(packet)
        mutated[26] = 2  # emitted ORIGIN value disagrees with the model
        with self.assertRaises(ValueError):
            runner.validate_update_attributes(bytes(mutated), attrs)
        with self.assertRaises(ValueError):
            runner.validate_update_attributes(packet[:-1], attrs)

    def test_loader_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'cases.txt'
            with self.assertRaises(FileNotFoundError):
                runner.load_argdict(path)
            for bad in ('', '[]\n', "__import__('os').getcwd()\n", '{bad\n'):
                path.write_text(bad)
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    runner.load_argdict(path)
            path.write_text("{'x': 1, 'value': b'abc'}\n")
            self.assertEqual(runner.load_argdict(path), [{'x': 1, 'value': b'abc'}])

    def test_dry_run_has_no_live_calls_or_passes(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(runner.socket, 'socket', side_effect=AssertionError('live socket')), \
                patch.object(runner.subprocess, 'check_output', side_effect=AssertionError('docker')):
            out = Path(tmp) / 'report.json'
            runner.execute_comprehensive_suite(dry_run=True, limit=1, out_path=out,
                                               fail_on_deviation=True)
            report = json.loads(out.read_text())['summary']
            self.assertEqual(report['total'], 5)
            self.assertEqual(sum(r['PASS'] for r in report['matrix'].values()), 0)
            self.assertEqual(len(report['corpus']), 7)
            runner.execute_comprehensive_suite(dry_run=True, limit=0, out_path=out)
            self.assertEqual(json.loads(out.read_text())['summary']['total'], 0)

    def test_invalid_run_options_rejected(self):
        for options in ({'suite': 'missing'}, {'limit': -1},
                        {'dry_run': True, 'coverage_mode': True}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                runner.execute_comprehensive_suite(**options)

    def test_coverage_mode_reaches_all_suites_without_parity(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(runner, 'BgpSession'), patch.object(runner.socket, 'socket'), \
                patch.object(runner, 'perform_bgp_handshake', return_value=True), \
                patch.object(runner, 'send_update_and_monitor', return_value=(False, True)), \
                patch.object(runner, 'check_if_route_installed', side_effect=AssertionError('RIB check')), \
                patch.object(runner, 'get_bgp_log', side_effect=AssertionError('log check')), \
                patch.object(runner, 'clear_bgp_log'), patch.object(runner.time, 'sleep'):
            out = Path(tmp) / 'report.json'
            runner.execute_comprehensive_suite(coverage_mode=True, limit=1, out_path=out,
                                               fail_on_deviation=True)
            summary = json.loads(out.read_text())['summary']
            self.assertEqual(summary['total'], 5)
            self.assertTrue(summary['coverage_mode'])
            self.assertEqual(sum(r['PASS'] for r in summary['matrix'].values()), 0)

    def test_connection_failure_cannot_pass_release_gate(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(runner, 'BgpSession') as session, patch.object(runner.time, 'sleep'):
            session.return_value.ensure.side_effect = ConnectionError('refused')
            out = Path(tmp) / 'report.json'
            with self.assertRaises(RuntimeError):
                runner.execute_comprehensive_suite(suite='routerefresh', limit=1,
                                                   out_path=out, fail_on_deviation=True)
            self.assertEqual(json.loads(out.read_text())['summary']['connection_failures'], 1)

    def test_fragmented_handshake_and_notification(self):
        peer_open = runner.build_bgp_open(asn=65001)
        keepalive = runner.build_bgp_keepalive()
        stream = peer_open + keepalive
        for split in range(1, len(stream)):
            sock = Mock()
            sock.recv.side_effect = [stream[:split], stream[split:]]
            self.assertTrue(runner.perform_bgp_handshake(sock))
        sock = Mock()
        sock.recv.side_effect = [peer_open, keepalive]  # exactly 19 bytes
        self.assertTrue(runner.perform_bgp_handshake(sock))
        notification = b'\xff' * 16 + struct.pack('!HB', 21, 3) + b'\x03\x01'
        for split in range(1, len(notification)):
            sock = Mock()
            sock.recv.side_effect = [notification[:split], notification[split:], socket.timeout()]
            self.assertEqual(runner.send_update_and_monitor(sock, keepalive), (True, False))

    def test_incomplete_handshake_closes_socket(self):
        with patch.object(runner.socket, 'socket') as factory, \
                patch.object(runner, 'perform_bgp_handshake', return_value=False):
            session = runner.BgpSession('localhost', 1179)
            with self.assertRaises(ConnectionError):
                session.ensure()
            factory.return_value.close.assert_called_once()
            self.assertIsNone(session.sock)

    def test_rib_query_failure_is_not_route_absence(self):
        with patch.object(runner.subprocess, 'check_output', side_effect=OSError('docker missing')):
            with self.assertRaises(RuntimeError):
                runner.check_if_route_installed('10.0.1.0/24')

    def test_observer_peer_matches_configuration(self):
        packet = build_open()
        self.assertEqual(int.from_bytes(packet[16:18], 'big'), len(packet))
        self.assertEqual(int.from_bytes(packet[20:22], 'big'), 65003)
        self.assertEqual(int.from_bytes(packet[22:24], 'big'), 0)

    def test_lcov_branch_hits_and_baseline_compatibility(self):
        script = (runner.BASE_DIR / 'collect_c_coverage.sh').read_text()
        source = script.split("<<'EOF'\n", 1)[1].rsplit('\nEOF', 1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'models/bgpd/malformed_packets').mkdir(parents=True)
            fixture = root / 'target.info'
            fixture.write_text(''.join(
                f'SF:/frr/bgpd/{name}\nLF:10\nLH:5\nBRF:8\nBRH:3\nFNF:2\nFNH:1\nend_of_record\n'
                for name in ('bgp_attr.c', 'bgp_open.c', 'bgp_packet.c', 'bgp_route.c')))
            source = source.replace('/tmp/frr_target.info', str(fixture))
            result = subprocess.run([sys.executable, '-c', source, '--baseline', 'fixture-revision'],
                                    cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            baseline = json.loads((root / 'models/bgpd/malformed_packets/coverage_baseline.json').read_text())
            self.assertEqual(baseline['total']['branches'], 12)
            self.assertEqual(baseline['total']['branches_total'], 32)
            changed = subprocess.run([sys.executable, '-c', source, 'run', 'different-revision'],
                                     cwd=root, capture_output=True, text=True)
            self.assertNotEqual(changed.returncode, 0)
            self.assertIn('no comparable coverage delta', changed.stderr)


if __name__ == '__main__':
    unittest.main()
