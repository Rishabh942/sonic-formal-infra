"""Finite reference model for RFC 4724 helper route retention.

The state is intentionally small: each route is absent, active, or stale.
An exhaustive bounded walk can check transition invariants independently of
the socket harness; live scenarios then compare FRR's RIB with this model.
"""

from dataclasses import dataclass
from enum import IntEnum
from itertools import product
from collections import deque


class RouteState(IntEnum):
    ABSENT = 0
    ACTIVE = 1
    STALE = 2


@dataclass(frozen=True)
class GrState:
    routes: tuple[RouteState, ...]
    gr_enabled: bool
    connected: bool = True

    @classmethod
    def initial(cls, gr_enabled: bool, route_count: int = 2):
        return cls((RouteState.ABSENT,) * route_count, gr_enabled)

    def present(self, index: int) -> bool:
        return self.routes[index] != RouteState.ABSENT


def step(state: GrState, event: str, route: int = 0) -> GrState:
    """Apply one wire-visible event to the expected helper state."""
    routes = list(state.routes)
    connected = state.connected
    if event in ('announce', 'refresh'):
        if connected:
            routes[route] = RouteState.ACTIVE
    elif event == 'disconnect':
        if connected:
            # RFC 4724 section 4.2: consecutive restarts must delete routes
            # already stale; only freshly learned/refreshed routes survive.
            routes = [RouteState.STALE if state.gr_enabled and r == RouteState.ACTIVE
                      else RouteState.ABSENT for r in routes]
        connected = False
    elif event == 'reconnect_f1':
        connected = True
    elif event == 'reconnect_f0':
        routes = [RouteState.ABSENT if r == RouteState.STALE else r
                  for r in routes]
        connected = True
    elif event in ('eor', 'timer'):
        routes = [RouteState.ABSENT if r == RouteState.STALE else r
                  for r in routes]
    elif event == 'notification':
        routes = [RouteState.ABSENT] * len(routes)
        connected = False
    else:
        raise ValueError(f'unknown GR event: {event}')
    return GrState(tuple(routes), state.gr_enabled, connected)


def check_bounded_invariants(depth: int = 4) -> tuple[int, int]:
    """Exhaustively explore all two-route event sequences through `depth`."""
    events = ('announce', 'refresh', 'disconnect', 'reconnect_f1',
              'reconnect_f0', 'eor', 'timer', 'notification')
    choices = tuple(product(events, (0, 1)))
    explored = 0
    visited = set()
    for gr in (False, True):
        for length in range(depth + 1):
            for sequence in product(choices, repeat=length):
                state = GrState.initial(gr)
                for event, route in sequence:
                    prior = state
                    state = step(state, event, route)
                    explored += 1
                    if event in ('eor', 'timer', 'reconnect_f0'):
                        assert RouteState.STALE not in state.routes
                    if event == 'notification':
                        assert all(r == RouteState.ABSENT for r in state.routes)
                    if event in ('announce', 'refresh') and prior.connected:
                        assert state.routes[1 - route] == prior.routes[1 - route]
                    visited.add(state)
    return explored, len(visited)


@dataclass(frozen=True)
class GrEvent:
    kind: str
    route: int = 0


def enabled_events(state):
    """Executable helper traces: packet events require an established session.

    Timer expiry is scoped to a disconnected helper with retained routes.
    Timer races after reconnect are outside this generated suite's model.
    Global events have one canonical route index, avoiding duplicate edges.
    """
    if state.connected:
        for route, status in enumerate(state.routes):
            yield GrEvent('announce' if status == RouteState.ABSENT else 'refresh', route)
        if any(state.present(i) for i in range(len(state.routes))):
            yield GrEvent('disconnect')
            yield GrEvent('notification')
        if RouteState.STALE in state.routes:
            yield GrEvent('eor')
    else:
        yield GrEvent('reconnect_f1')
        if RouteState.STALE in state.routes:
            yield GrEvent('reconnect_f0')
            yield GrEvent('timer')


def checked_step(state, event):
    if event not in tuple(enabled_events(state)):
        raise ValueError(f'event not enabled in GR state: {event}')
    after = step(state, event.kind, event.route)
    check_transition(state, event, after)
    return after


def check_transition(before, event, after):
    """Check cleanup scope, retention, frame, and connection postconditions."""
    if after.gr_enabled != before.gr_enabled:
        raise AssertionError('negotiated GR mode changed')
    expected_connected = (False if event.kind in ('disconnect', 'notification') else
                          True if event.kind.startswith('reconnect_') else before.connected)
    if after.connected != expected_connected:
        raise AssertionError('incorrect session state')
    for route, old in enumerate(before.routes):
        actual = after.routes[route]
        if event.kind in ('announce', 'refresh'):
            expected = RouteState.ACTIVE if route == event.route else old
        elif event.kind == 'notification' or (event.kind == 'disconnect' and not before.gr_enabled):
            expected = RouteState.ABSENT
        elif event.kind == 'disconnect':
            expected = RouteState.STALE if old == RouteState.ACTIVE else RouteState.ABSENT
        elif event.kind in ('eor', 'timer', 'reconnect_f0') and old == RouteState.STALE:
            expected = RouteState.ABSENT
        else:
            expected = old
        if actual != expected:
            raise AssertionError('GR route retention/cleanup property failed')


def gr_obligations(before, event, after):
    tag = f'gr{int(before.gr_enabled)}/{event.kind}'
    if event.kind in ('announce', 'refresh'):
        tag += f'/route{event.route}/{before.routes[event.route].name.lower()}'
    yield tag
    if event.kind in ('eor', 'timer', 'reconnect_f0', 'notification', 'disconnect'):
        yield tag + f'/active{before.routes.count(RouteState.ACTIVE)}/stale{before.routes.count(RouteState.STALE)}'


def generate_traces():
    """Explore only enabled edges to a fixed point and emit shortest witnesses.

    The older bounded-walk API remains for historical tests. These unique
    graph counts, unlike that walk's repeated execution count, describe the
    legal event abstraction used by the new live executor.
    """
    witnesses = {}
    states = edges = 0
    for gr in (False, True):
        initial = GrState.initial(gr)
        paths = {initial: ()}
        queue = deque([initial])
        while queue:
            before = queue.popleft()
            for event in enabled_events(before):
                after = checked_step(before, event)
                edges += 1
                trace = paths[before] + (event,)
                for goal in gr_obligations(before, event, after):
                    witnesses.setdefault(goal, (gr, trace))
                if after not in paths:
                    paths[after] = trace
                    queue.append(after)
        states += len(paths)
    traces = list(dict.fromkeys(witnesses.values()))
    return {'states': states, 'edges': edges, 'obligations': len(witnesses),
            'traces': traces, 'witnesses': witnesses}
