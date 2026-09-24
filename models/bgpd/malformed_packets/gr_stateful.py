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
    selected = SCENARIOS[:limit] if limit else SCENARIOS
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
