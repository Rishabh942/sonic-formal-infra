"""Core release gates for framing, model context and honest observations."""
import contextlib
import io
import json
from pathlib import Path
import socket
import struct
import tempfile
import unittest
from unittest.mock import Mock, patch

from models.bgpd.malformed_packets import run_parity_fuzzer as runner
from models.bgpd.malformed_packets.bgp_oracle import BGPPathAttr, ParseResult, parse_attributes
from models.bgpd.malformed_packets.generate_rfc7606_suite import test_attribute_sequence_soft
from models.bgpd.malformed_packets.dummy_peer import build_open
from models.bgpd.malformed_packets.testing.c_coverage import main as coverage_main, read_lcov


class CoreReleaseTests(unittest.TestCase):
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
            self.assertEqual(report['total'], 3)
            self.assertEqual(sum(r['PASS'] for r in report['matrix'].values()), 0)
            self.assertEqual(len(report['corpus']), 3)
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
            self.assertEqual(summary['total'], 3)
            self.assertTrue(summary['coverage_mode'])
            self.assertEqual(sum(r['PASS'] for r in summary['matrix'].values()), 0)

    def test_connection_failure_cannot_pass_release_gate(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(runner, 'BgpSession') as session, patch.object(runner.time, 'sleep'):
            session.return_value.ensure.side_effect = ConnectionError('refused')
            out = Path(tmp) / 'report.json'
            with self.assertRaises(RuntimeError):
                runner.execute_comprehensive_suite(suite='extended', limit=1,
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
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / 'target.info'
            fixture.write_text(''.join(
                f'SF:/frr/bgpd/{name}\nLF:10\nLH:5\nBRF:8\nBRH:3\nFNF:2\nFNH:1\nend_of_record\n'
                for name in ('bgp_attr.c', 'bgp_open.c', 'bgp_packet.c', 'bgp_route.c')))
            parity = root / 'parity.json'
            parity.write_text(json.dumps({'summary': {'coverage_mode': True, 'dry_run': False,
                'connection_failures': 0, 'observation_errors': 0, 'total': 5,
                'run_context': {'limit': 1}, 'corpus': {}}}))
            options = ['--info', str(fixture), '--parity', str(parity),
                       '--out', str(root), '--revision', 'fixture-revision']
            with contextlib.redirect_stdout(io.StringIO()):
                coverage_main(options + ['--baseline'])
            baseline = json.loads((root / 'baseline.json').read_text())
            self.assertEqual(baseline['total']['bh'], 12)
            self.assertEqual(baseline['total']['bf'], 32)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
                with self.assertRaises(SystemExit) as failure:
                    coverage_main(options[:-1] + ['different-revision'])
            self.assertEqual(failure.exception.code, 1)
            self.assertIn('no comparable coverage delta', err.getvalue())

    def test_lcov_missing_or_duplicate_records_fail_closed(self):
        text = 'SF:/frr/bgpd/bgp_attr.c\nLF:10\nLH:5\nBRF:8\nBRH:3\nFNF:2\nFNH:1\nend_of_record\n'
        for bad in (text, text * 4, text.replace('BRH:3\n', '')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                read_lcov(bad)

    def test_full_core_corpus_matches_emitted_bytes(self):
        total = 0
        for name in runner.CORPUS_FILES.values():
            cases = runner.expand_legacy_cases(runner.load_argdict(runner.BASE_DIR / 'tests' / name))
            for args, version, slot in cases:
                total += 1
                packet, attrs, _, _ = runner.build_legacy_update(args, version, slot, total)
                runner.validate_update_attributes(packet, attrs)
                runner.eval_legacy(attrs, args)
        self.assertEqual(total, 2344)

    def test_as_path_uses_negotiated_asn_width(self):
        for payload, width, expected in (
            (b'\x02\x01\x00\x00\xfd\xea', True, ParseResult.VALID),
            (b'\x02\x01\xfd\xea', False, ParseResult.VALID),
            (b'\x02\x01\xfd\xea', True, ParseResult.TREAT_AS_WITHDRAW),
            (b'\x02\x00', True, ParseResult.TREAT_AS_WITHDRAW),
            (b'\x02\x01\x00\x00\xfd', True, ParseResult.TREAT_AS_WITHDRAW),
        ):
            attrs = [BGPPathAttr(64, 1, 1, b'\x00'),
                     BGPPathAttr(64, 2, len(payload), payload),
                     BGPPathAttr(64, 3, 4, b'\x01\x01\x01\x01')]
            with self.subTest(payload=payload, asn4=width):
                self.assertEqual(parse_attributes(attrs, asn_4byte=width), expected)

    def test_generator_and_slot_replay_share_core_rules(self):
        # Keep ORIGIN valid and isolate the fourth attribute's length rule.
        for length in range(13):
            args = dict(flags1=64, len1=1, flags4=192, type4=8, len4=length)
            _, attrs, _, _ = runner.build_legacy_update(args, 2, 4, 1)
            self.assertEqual(test_attribute_sequence_soft(**args), runner.eval_legacy(attrs, args).name)

    def test_wire_mismatch_rejected(self):
        args = dict(flags4=192, type4=8, len4=4, payload_hex='00010203')
        packet, attrs, _, _ = runner.build_legacy_update(args, 3, 4, 1)
        mutated = bytearray(packet)
        mutated[26] ^= 1
        with self.assertRaises(ValueError):
            runner.validate_update_attributes(bytes(mutated), attrs)
        with self.assertRaises(ValueError):
            runner.validate_update_attributes(packet[:-1], attrs)


if __name__ == '__main__':
    unittest.main()
