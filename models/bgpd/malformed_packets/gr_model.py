"""Finite reference model for RFC 4724 helper route retention.

The state is intentionally small: each route is absent, active, or stale.
An exhaustive bounded walk can check transition invariants independently of
the socket harness; live scenarios then compare FRR's RIB with this model.
"""

from dataclasses import dataclass
from enum import IntEnum
from itertools import product


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
            routes = [RouteState.STALE if state.gr_enabled and r != RouteState.ABSENT
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
