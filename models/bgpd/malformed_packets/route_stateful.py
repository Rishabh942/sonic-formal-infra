"""Run model-generated route competition inside the isolated Docker lab.

python -m models.bgpd.malformed_packets.route_stateful --dry-run
Use run_route_lab.sh for live execution; loopback peers run inside Linux.
"""

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import select
import subprocess
import time

from .route_model import Event, Route, State, explore, obligations
from .route_wire import ASNS, PEER_IPS, PREFIXES, Peer, message, open_message, update, oracle_transition
from .frr_backend import FRR, configure


def expected_export(state):
    rib = {}
    for prefix, name in enumerate(PREFIXES):
        peer = state.winner(prefix)
        if peer is not None:
            route = state.candidates(prefix)[peer]
            rib[name] = {'path': [65001] + [ASNS[peer]] * route.length,
                         'origin': route.origin}
    return rib


def read_rib():
    """Fail on observation errors; an unavailable CLI is never an empty RIB."""
    result = {}
    for prefix in PREFIXES:
        paths = []
        for path in FRR.paths(prefix):
            paths.append({'peer': path['peer']['peerId'],
                          'path': path['aspath']['string'],
                          'origin': path['origin'],
                          'valid': path.get('valid', False),
                          'best': path.get('bestpath', {}).get('overall', False)})
        result[prefix] = sorted(paths, key=lambda p: p['peer'])
    return result


def expected_rib(state):
    result = {}
    for prefix, name in enumerate(PREFIXES):
        result[name] = [
            {'peer': PEER_IPS[peer],
             'path': ' '.join([str(ASNS[peer])] * route.length),
             'origin': {0: 'IGP', 2: 'incomplete'}[route.origin],
             'valid': True, 'best': state.winner(prefix) == peer}
            for peer, route in enumerate(state.candidates(prefix)) if route is not None]
    return result


class Lab:
    def __init__(self, host, port, coverage_only, wire):
        self.peers = []
        self.wire = wire
        self.last_keepalive = 0
        self.coverage_only = coverage_only
        try:
            for index in range(3):
                peer = Peer(index, host, port)
                self.peers.append(peer)
                self.send(index, open_message(index))
                self.send(index, message(4))
            deadline = time.monotonic() + 5
            while not all(p.established for p in self.peers):
                self.pump()
                if time.monotonic() >= deadline:
                    raise TimeoutError('three-peer handshake did not complete')
        except Exception:
            self.close()
            raise

    def send(self, peer, packet):
        self.wire.append({'direction': 'sent', 'peer': peer, 'hex': packet.hex()})
        self.peers[peer].sock.sendall(packet)

    def pump(self):
        if time.monotonic() - self.last_keepalive > 10:
            for peer in self.peers:
                self.send(peer.index, message(4))
            self.last_keepalive = time.monotonic()
        readable, _, _ = select.select([p.sock for p in self.peers], [], [], 0.05)
        for peer in self.peers:
            if peer.sock in readable:
                chunk = peer.sock.recv(65536)
                self.wire.append({'direction': 'received-chunk', 'peer': peer.index,
                                  'hex': chunk.hex()})
                peer.feed(chunk)

    def converge(self, state, timeout=4):
        deadline = time.monotonic() + timeout
        stable_since = None
        actual_rib = None
        wanted_wire = expected_export(state)
        wanted_rib = expected_rib(state)
        while time.monotonic() < deadline:
            self.pump()
            if not self.coverage_only:
                actual_rib = read_rib()
            actual_wire = dict(self.peers[2].rib)
            matches = actual_wire == wanted_wire and (
                self.coverage_only or actual_rib == wanted_rib)
            if matches:
                if stable_since is None:
                    stable_since = time.monotonic()
                if time.monotonic() - stable_since >= 0.2:
                    return {'expected_rib': wanted_rib, 'actual_rib': actual_rib,
                            'expected_export': wanted_wire, 'actual_export': actual_wire}
            else:
                stable_since = None
        raise AssertionError(json.dumps({'expected_rib': wanted_rib,
                                        'actual_rib': actual_rib,
                                        'expected_export': wanted_wire,
                                        'actual_export': self.peers[2].rib}))

    def reset(self):
        for peer in range(2):
            for prefix in range(2):
                self.send(peer, update(Event('withdraw', peer, prefix)))
        return self.converge(State())

    def close(self):
        for peer in self.peers:
            peer.sock.close()


def run_report(args):
    graph = explore()
    traces = graph['traces']
    if args.baseline:
        traces = [(Event('announce', 0, 0, Route(1, 0)),
                   Event('announce', 0, 1, Route(1, 0)),
                   Event('withdraw', 0, 0), Event('withdraw', 0, 1))]
    if args.limit is not None:
        traces = traces[:args.limit]
    report = {'model': {k: graph[k] for k in ('states', 'edges', 'obligations')},
              'mode': 'dry-run' if args.dry_run else (
                  'coverage-only' if args.coverage_only else 'conformance'),
              'baseline': args.baseline, 'traces': [], 'wire': [],
              'error': None, 'live_obligations_passed': []}
    report['source_sha256'] = {
        name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
        for name in ('route_model.py', 'route_wire.py', 'route_stateful.py', 'route_lab.conf',
                     'bgp_oracle.py', 'packet_builders.py')}
    lab = None
    covered = set()
    try:
        if not args.dry_run:
            report['frr_version'] = subprocess.check_output(
                ['/usr/lib/frr/bgpd', '--version'], text=True, timeout=2).strip()
            lab = Lab(args.host, args.port, args.coverage_only, report['wire'])
        for index, trace in enumerate(traces):
            entry = {'id': index, 'events': [], 'status': 'running'}
            report['traces'].append(entry)
            if lab:
                entry['reset'] = lab.reset()
            state = State()
            for event in trace:
                before = state
                packet = update(event)
                verdict, state = oracle_transition(state, event, packet)
                record = {'event': asdict(event), 'wire': packet.hex(), 'oracle_verdict': verdict,
                          'expected_state': asdict(state)}
                entry['events'].append(record)
                if lab:
                    lab.send(event.peer, packet)
                    record['observation'] = lab.converge(state)
                    if not args.coverage_only:
                        covered.update(obligations(before, event, state))
            entry['status'] = 'generated' if args.dry_run else (
                'coverage-only' if args.coverage_only else 'passed')
            if lab and (index + 1) % 10 == 0:
                print(f'Completed {index + 1}/{len(traces)} traces', flush=True)
        if lab:
            lab.reset()
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        if report['traces'] and report['traces'][-1]['status'] == 'running':
            report['traces'][-1]['status'] = 'failed'
        log = Path('/tmp/route-lab.log')
        if log.exists():
            report['frr_log_tail'] = log.read_text(errors='replace')[-24000:]
    finally:
        if lab:
            lab.close()
    report['live_obligations_passed'] = sorted(covered)
    return report


def run_scenarios(host, port, limit=None, coverage_mode=False, dry_run=False,
                  baseline=False):
    from types import SimpleNamespace
    report = run_report(SimpleNamespace(host=host, port=port, limit=limit,
                                       coverage_only=coverage_mode,
                                       dry_run=dry_run, baseline=baseline))
    results = []
    for trace in report['traces']:
        failed = trace['status'] in ('running', 'failed')
        results.append({'name': f"trace-{trace['id']}", 'pass': not failed,
                        'status': trace['status'], 'checks': [
                            e['observation'] for e in trace['events'] if 'observation' in e],
                        'events': trace['events'],
                        'wire': [e['wire'] for e in trace['events']],
                        'error': report['error'] if failed else None})
    if report['error'] and not any(not r['pass'] for r in results):
        results.append({'name': 'setup-or-cleanup', 'pass': False, 'checks': [],
                        'events': [], 'wire': [], 'error': report['error']})
    metadata = {k: v for k, v in report.items() if k != 'traces'}
    return results, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=1179)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--baseline', action='store_true', help='single-advertiser control')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--coverage-only', action='store_true', help='omit vtysh observations')
    parser.add_argument('--out', default='/tmp/route-stateful.json')
    args = parser.parse_args()
    if args.limit is not None and args.limit < 0:
        parser.error('--limit must be nonnegative')
    from .run_parity_fuzzer import execute_comprehensive_suite
    configure(local=True, log_path='/tmp/route-lab.log')
    execute_comprehensive_suite(
        suite='routecompetition', host=args.host, port=args.port, limit=args.limit,
        out_path=args.out, dry_run=args.dry_run, coverage_mode=args.coverage_only,
        fail_on_deviation=True, lab_profile='combined', route_baseline=args.baseline)


if __name__ == '__main__':
    main()
