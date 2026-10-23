"""Stateful RFC 4724 probes: routes, disconnects, reconnects, and EoR.

The OPEN-only corpus reaches capability parsing; these scenarios exercise
the FRR helper state machine and verify actual RIB outcomes in a normal run.
Coverage mode sends the same wire sequences without vtysh queries, keeping
C coverage attributable to protocol traffic rather than inspection commands.
"""

import socket
import struct
import time

from models.bgpd.malformed_packets.graceful_restart import (
    IPV4_END_OF_RIB, build_graceful_restart_open,
)
from models.bgpd.malformed_packets.gr_model import GrState, step


SCENARIOS = (
    'stale-then-eor',
    'refresh-one-then-eor',
    'forwarding-bit-cleared',
    'restart-time-expired',
    'notification-clears-route',
    'no-gr-control',
)

CEASE_NOTIFICATION = b'\xff' * 16 + struct.pack('!HBBB', 21, 3, 6, 0)
ROUTE_ARGS = {'flags4': 0xC0, 'type4': 8, 'len4': 4,
              'payload_hex': '00010001'}


def _gr_open(restart=False, forwarding=True, restart_time=90):
    return build_graceful_restart_open({
        'flags': 8 if restart else 0,
        'time': restart_time,
        'families': [(1, 1, 0x80 if forwarding else 0)],
        'trim': 0, 'duplicate': False,
    })


def _connect(host, port, open_message):
    from models.bgpd.malformed_packets.run_parity_fuzzer import perform_bgp_handshake

    sock = socket.create_connection((host, port), timeout=3)
    sock.settimeout(3)
    try:
        if not perform_bgp_handshake(sock, open_message):
            raise ConnectionError('BGP handshake incomplete')
        return sock
    except Exception:
        sock.close()
        raise


def _send(sock, packet):
    from models.bgpd.malformed_packets.run_parity_fuzzer import send_update_and_monitor

    notified, active = send_update_and_monitor(sock, packet, fast=True)
    if notified or not active:
        raise ConnectionError('session reset after UPDATE')


def _route(prefix_id):
    from models.bgpd.malformed_packets.run_parity_fuzzer import build_legacy_update

    packet, _, prefix, _ = build_legacy_update(ROUTE_ARGS, 3, 4, prefix_id)
    return packet, prefix


def _check(results, stage, prefix, model, route, coverage_mode):
    if coverage_mode:
        return
    from models.bgpd.malformed_packets.run_parity_fuzzer import check_if_route_installed

    expected = model.present(route)
    actual = check_if_route_installed(prefix)
    results.append({'stage': stage, 'prefix': prefix, 'expected': expected,
                    'actual': actual, 'pass': actual == expected})


def run_scenario(name, host, port, prefix_id, coverage_mode=False):
    """Run one isolated sequence and return each observable RIB assertion."""
    from models.bgpd.malformed_packets.run_parity_fuzzer import build_bgp_open

    checks = []
    sock = None
    packet1, prefix1 = _route(prefix_id)
    packet2, prefix2 = _route(prefix_id + 1)
    second_route = name == 'refresh-one-then-eor'
    gr = name != 'no-gr-control'
    restart_time = 1 if name == 'restart-time-expired' else 90
    initial_open = (_gr_open(restart_time=restart_time)
                    if gr else build_bgp_open())
    wire = {'initial_open': initial_open.hex(),
            'route_1': packet1.hex(),
            'route_2': packet2.hex() if second_route else None,
            'restart_open': None,
            'end_of_rib': IPV4_END_OF_RIB.hex(),
            'cease': CEASE_NOTIFICATION.hex()}
    events = []
    model = GrState.initial(gr)

    try:
        sock = _connect(host, port, initial_open)
        events.append('established')
        _send(sock, packet1)
        model = step(model, 'announce', 0)
        events.append('route_1_announced')
        if second_route:
            _send(sock, packet2)
            model = step(model, 'announce', 1)
            events.append('route_2_announced')
        time.sleep(0.25)
        _check(checks, 'announced', prefix1, model, 0, coverage_mode)
        if second_route:
            _check(checks, 'announced-second', prefix2, model, 1,
                   coverage_mode)

        if name == 'notification-clears-route':
            sock.sendall(CEASE_NOTIFICATION)
            model = step(model, 'notification')
            events.append('cease_sent')
        else:
            model = step(model, 'disconnect')
        sock.close()
        sock = None
        events.append('connection_closed')
        time.sleep(0.35)
        _check(checks, 'after-disconnect', prefix1, model, 0, coverage_mode)

        if name == 'restart-time-expired':
            time.sleep(1.4)
            model = step(model, 'timer')
            _check(checks, 'after-restart-timer', prefix1, model, 0,
                   coverage_mode)
        elif name not in ('notification-clears-route', 'no-gr-control'):
            forwarding = name != 'forwarding-bit-cleared'
            restart_open = _gr_open(restart=True, forwarding=forwarding)
            wire['restart_open'] = restart_open.hex()
            sock = _connect(host, port, restart_open)
            model = step(model, 'reconnect_f1' if forwarding else 'reconnect_f0')
            events.append('reestablished')
            time.sleep(0.2)
            _check(checks, 'reconnected', prefix1, model, 0, coverage_mode)
            if second_route:
                _send(sock, packet1)
                model = step(model, 'refresh', 0)
                events.append('route_1_refreshed')
            _send(sock, IPV4_END_OF_RIB)
            model = step(model, 'eor')
            events.append('end_of_rib_sent')
            time.sleep(0.25)
            _check(checks, 'after-eor', prefix1, model, 0, coverage_mode)
            if second_route:
                _check(checks, 'stale-second-after-eor', prefix2, model, 1,
                       coverage_mode)
            sock.sendall(CEASE_NOTIFICATION)
            events.append('cease_sent')

        return {'name': name, 'checks': checks,
                'pass': all(check['pass'] for check in checks), 'error': None,
                'events': events, 'wire': wire}
    except (OSError, ConnectionError) as exc:
        return {'name': name, 'checks': checks, 'pass': False,
                'error': str(exc), 'events': events, 'wire': wire}
    finally:
        if sock is not None:
            sock.close()
        time.sleep(0.2)  # let a dynamic neighbor leave the collision window


def run_scenarios(host, port, limit=None, coverage_mode=False, dry_run=False):
    selected = SCENARIOS[:limit] if limit is not None else SCENARIOS
    if dry_run:
        for index, _ in enumerate(selected):
            _gr_open()
            _gr_open(restart=True)
            _route(55000 + index * 2)
        return [{'name': name, 'checks': [], 'pass': True, 'error': None,
                 'events': [], 'wire': {}}
                for name in selected]
    return [run_scenario(name, host, port, 55000 + index * 2, coverage_mode)
            for index, name in enumerate(selected)]


def validate_packet(packet):
    """Use the shared oracle on the actual encoded OPEN/UPDATE."""
    from .bgp_oracle import ParseResult, parse_attributes, parse_capabilities
    from .packet_builders import decode_update_attributes
    from .run_parity_fuzzer import _extract_opt_params

    if packet[18] == 1:
        verdict = parse_capabilities(_extract_opt_params(packet))
    elif packet == IPV4_END_OF_RIB:
        # EOR has no advertised NLRI and therefore no mandatory attributes.
        return 'END_OF_RIB'
    elif packet[18] == 2:
        withdrawn, attrs, announced = decode_update_attributes(packet)
        if withdrawn or not announced:
            raise ValueError('expected a GR route announcement')
        verdict = parse_attributes(attrs, asn_4byte=True, enforce_first_as=65002)
    elif packet == CEASE_NOTIFICATION:
        return 'CEASE'
    else:
        raise ValueError('packet outside generated GR alphabet')
    if verdict != ParseResult.VALID:
        raise AssertionError(f'GR packet/oracle disagreement: {verdict.name}')
    return verdict.name


def observe_gr(prefixes, expected, timeout=3):
    from .frr_backend import FRR
    wanted = [status.name for status in expected.routes]
    deadline = time.monotonic() + timeout
    stable = None
    observed = []
    while time.monotonic() < deadline:
        observed = []
        for prefix in prefixes:
            paths = FRR.paths(prefix)
            if len(paths) > 1:
                observed.append('MULTIPLE_CANDIDATES')
            else:
                observed.append('ABSENT' if not paths else
                                'STALE' if paths[0].get('stale', False) else 'ACTIVE')
        if observed == wanted:
            if stable is None:
                stable = time.monotonic()
            if time.monotonic() - stable >= 0.1:
                return {'prefixes': prefixes, 'expected': wanted,
                        'actual': observed, 'pass': True}
        else:
            stable = None
        time.sleep(0.05)
    raise AssertionError(f'GR RIB mismatch: expected {wanted}, observed {observed}')


def run_generated_trace(gr, trace, host, port, index, coverage_mode=False, dry_run=False):
    from dataclasses import asdict
    from .gr_model import checked_step, gr_obligations
    from .run_parity_fuzzer import build_bgp_open

    routes = [_route(60000 + 2 * index + route) for route in range(2)]
    prefixes = [prefix for _, prefix in routes]
    restart_time = 2 if any(e.kind == 'timer' for e in trace) else 90
    initial = _gr_open(restart_time=restart_time) if gr else build_bgp_open()
    result = {'name': f'generated-{index}', 'checks': [], 'events': [],
              'wire': {'initial_open': initial.hex(), 'events': []},
              'pass': True, 'error': None, 'covered_obligations': []}
    state = GrState.initial(gr)
    sock = None
    covered = set()
    try:
        result['initial_oracle_verdict'] = validate_packet(initial)
        if not dry_run:
            sock = _connect(host, port, initial)
        for event in trace:
            before = state
            after = checked_step(state, event)
            packet = None
            if event.kind in ('announce', 'refresh'):
                packet = routes[event.route][0]
            elif event.kind == 'eor':
                packet = IPV4_END_OF_RIB
            elif event.kind == 'notification':
                packet = CEASE_NOTIFICATION
            elif event.kind.startswith('reconnect_'):
                packet = (_gr_open(restart=True, forwarding=event.kind == 'reconnect_f1',
                                   restart_time=restart_time) if gr else build_bgp_open())
            verdict = validate_packet(packet) if packet else 'SESSION_EVENT'
            record = {'event': asdict(event), 'oracle_verdict': verdict,
                      'expected_state': [r.name for r in after.routes],
                      'wire': packet.hex() if packet else None}
            result['events'].append(record)
            result['wire']['events'].append(record['wire'])
            if not dry_run:
                if event.kind in ('announce', 'refresh', 'eor'):
                    _send(sock, packet)
                elif event.kind == 'notification':
                    sock.sendall(packet)
                    sock.close()
                    sock = None
                elif event.kind == 'disconnect':
                    sock.close()
                    sock = None
                elif event.kind.startswith('reconnect_'):
                    sock = _connect(host, port, packet)
                elif event.kind == 'timer':
                    time.sleep(restart_time + 0.3)
                if coverage_mode:
                    time.sleep(0.2)
                else:
                    result['checks'].append(observe_gr(prefixes, after))
                    covered.update(gr_obligations(before, event, after))
            state = after
    except Exception as exc:
        result['pass'], result['error'] = False, f'{type(exc).__name__}: {exc}'
    finally:
        if not dry_run:
            try:
                # Do not leave helper-retained routes between generated traces.
                if sock is None and any(state.present(i) for i in range(2)):
                    sock = _connect(host, port, _gr_open(restart=True, forwarding=False)
                                    if gr else build_bgp_open())
                if sock is not None:
                    sock.sendall(CEASE_NOTIFICATION)
                if not coverage_mode:
                    observe_gr(prefixes, GrState.initial(gr))
            except Exception as exc:
                result['pass'] = False
                result['error'] = (result['error'] or '') + f'; cleanup: {exc}'
            finally:
                if sock is not None:
                    sock.close()
                time.sleep(0.2)
    result['covered_obligations'] = sorted(covered)
    return result


def run_generated_scenarios(host, port, limit=None, coverage_mode=False, dry_run=False):
    from .gr_model import generate_traces
    graph = generate_traces()
    selected = graph['traces'] if limit is None else graph['traces'][:limit]
    results = []
    for index, (gr, trace) in enumerate(selected):
        results.append(run_generated_trace(gr, trace, host, port, index, coverage_mode, dry_run))
        if not dry_run and (index + 1) % 10 == 0:
            print(f'GR generated: {index + 1}/{len(selected)} traces', flush=True)
        if not results[-1]['pass']:
            break
    metadata = {key: graph[key] for key in ('states', 'edges', 'obligations')}
    metadata['generated_traces'] = len(graph['traces'])
    metadata['live_obligations_passed'] = sorted({
        goal for result in results for goal in result['covered_obligations']})
    return results, metadata
