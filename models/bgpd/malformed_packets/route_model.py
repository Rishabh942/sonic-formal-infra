"""Finite IPv4 route competition model and shortest conformance witnesses.

Scope: two established eBGP peers, two prefixes, equal weight/local-pref,
reachable next hops, no policy/GR/multipath. Rank by AS_SEQUENCE length,
ORIGIN, then router ID (compare-routerid enabled). Peer 0 has the lower ID.
RFC 7606 sections 7.1/7.2 require treat-as-withdraw for the two malformed
replacements in this alphabet. This is an abstraction, not all of BGP.
"""

from collections import deque
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True, order=True)
class Route:
    length: int
    origin: int


@dataclass(frozen=True)
class Event:
    kind: str
    peer: int
    prefix: int
    route: Route | None = None


@dataclass(frozen=True)
class State:
    # prefix-major: p0/peer0, p0/peer1, p1/peer0, p1/peer1
    routes: tuple = (None, None, None, None)

    def candidates(self, prefix):
        return self.routes[2 * prefix:2 * prefix + 2]

    def winner(self, prefix):
        eligible = [(route.length, route.origin, peer)
                    for peer, route in enumerate(self.candidates(prefix))
                    if route is not None]
        return min(eligible)[2] if eligible else None


ROUTES = tuple(Route(length, origin) for length, origin in product((1, 2), (0, 2)))
EVENTS = tuple(
    event for peer, prefix in product(range(2), repeat=2)
    for event in (
        *(Event('announce', peer, prefix, route) for route in ROUTES),
        Event('withdraw', peer, prefix),
        Event('bad_origin', peer, prefix),
        Event('bad_aspath', peer, prefix),
    )
)


def step(state, event):
    if event not in EVENTS:
        raise ValueError(f'outside bounded event alphabet: {event}')
    routes = list(state.routes)
    routes[2 * event.prefix + event.peer] = (
        event.route if event.kind == 'announce' else None)
    return State(tuple(routes))


def check_properties(before, event, after):
    """Frame, withdrawal, eligibility, and preference properties.

    Preference is checked pairwise, independently of winner's sorting code.
    Exceptions remain enabled even under python -O.
    """
    changed = 2 * event.prefix + event.peer
    for index, old in enumerate(before.routes):
        if index != changed and after.routes[index] != old:
            raise AssertionError('an unrelated candidate changed')
    expected = event.route if event.kind == 'announce' else None
    if after.routes[changed] != expected:
        raise AssertionError('replacement/withdrawal postcondition failed')
    for prefix in range(2):
        candidates = after.candidates(prefix)
        winner = after.winner(prefix)
        if winner is None:
            if any(route is not None for route in candidates):
                raise AssertionError('eligible routes have no winner')
            continue
        chosen = candidates[winner]
        if chosen is None:
            raise AssertionError('selected an absent candidate')
        other = candidates[1 - winner]
        if other is not None:
            if chosen.length > other.length:
                raise AssertionError('longer AS path selected')
            if chosen.length == other.length:
                if chosen.origin > other.origin:
                    raise AssertionError('worse ORIGIN selected')
                if chosen.origin == other.origin and winner != 0:
                    raise AssertionError('router ID tie-break violated')


def obligations(before, event, after):
    """Observable semantic targets, not a count of repeated path prefixes."""
    prefix = event.prefix
    old, new = before.winner(prefix), after.winner(prefix)
    tag = f'p{prefix}/peer{event.peer}/{event.kind}'
    yield tag + '/basic'
    if before.candidates(prefix)[event.peer] is not None:
        yield tag + '/replace-existing'
    if old == event.peer and new == 1 - event.peer:
        yield tag + '/selected-to-backup'
    if old == event.peer and new is None:
        yield tag + '/last-route-removed'
    if old == 1 - event.peer and new == old:
        yield tag + '/other-winner-preserved'
    if before.winner(1 - prefix) is not None:
        yield tag + '/other-prefix-preserved'
    candidates = after.candidates(prefix)
    if event.kind == 'announce' and all(r is not None for r in candidates):
        a, b = candidates
        decision = ('path-length' if a.length != b.length else
                    'origin' if a.origin != b.origin else 'router-id')
        yield f'p{prefix}/selection/{decision}/winner{new}'


def explore():
    """Explore reachable state graph to a fixed point; retain shortest witnesses.

    All 625 states and 17,500 state/event edges in this abstraction are
    checked. Live execution uses one witness per semantic obligation, not
    every model edge. These two coverage scopes must be reported separately.
    """
    initial = State()
    paths = {initial: ()}
    queue = deque([initial])
    witnesses = {}
    edges = 0
    while queue:
        before = queue.popleft()
        for event in EVENTS:
            after = step(before, event)
            check_properties(before, event, after)
            edges += 1
            path = paths[before] + (event,)
            for goal in obligations(before, event, after):
                witnesses.setdefault(goal, path)
            if after not in paths:
                paths[after] = path
                queue.append(after)
    # A witness may satisfy multiple goals; replay its wire trace only once.
    traces = list(dict.fromkeys(witnesses.values()))
    return {'states': len(paths), 'edges': edges,
            'obligations': len(witnesses), 'traces': traces,
            'witnesses': witnesses}
