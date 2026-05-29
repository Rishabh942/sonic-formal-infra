"""Executable model of bgpd's nexthop-tracking callback (api_bgp_nh_update).

Demo for model-based testing (MBT). The model is the spec; a test harness
drives the real bgpd against the model and compares observable behavior.

The four MBT artifacts a tester uses:

* State        — BgpdNexthopState. What bgpd remembers between calls. It is
                 read from and written to by each call.
* Transition   — api_bgp_nh_update(api). The action under test. Its return
                 value is the set of downstream messages bgpd would emit
                 to zebra; it also updates the state.
* Precondition — api_bgp_nh_update_precondition(api). Guards the action.
                 Random/symbolic test generators use it to skip or shrink
                 infeasible inputs.
* Invariant    — Must hold at every state the model visits. Checked after each transition.

Scope: api_bgp_nh_update only. Route advertise/withdraw are out of scope;
the RIB is read-only state that this API re-evaluates. For the broader
(color/SRv6-TE-aware) model, see ref_model/bgpd/bgpd.py.
"""

from dataclasses import dataclass, field
from enum import IntEnum

from builtin import *


# ── Domain types ─────────────────────────────────────────────────────────────
# Abstract types that capture key fields relevant to bgpd's handling of nexthop updates.

class BOp(IntEnum):
    """Route operation conveyed to zebra (SET = route_add, DEL = route_del)."""
    SET = 1
    DEL = 2


@dataclass
class BgpdRouteEvent:
    """One outbound route message from bgpd to zebra."""
    op: BOp
    prefix: prefix_t
    nexthops: list[addr_t]


@dataclass
class BgpNexthopCache:
    """One entry in bgpd's nexthop-tracking cache. Models the C
    struct bgp_nexthop_cache: the cached nexthop is keyed by endpoint;
    `resolved` is the zebra-resolved next-hop address; `valid` is the
    BGP_NEXTHOP_VALID flag derived from zebra's last NHT reply."""
    endpoint: addr_t
    resolved: addr_t
    valid: bool


@dataclass
class BgpRibEntry:
    """One entry in bgpd's RIB: a prefix and the set of nexthops that reach it."""
    prefix: prefix_t
    nexthops: list[addr_t]


# ── API surface ──────────────────────────────────────────────────────────────
# The action under test takes a BApiNexthopUpdate (what zebra sends) and
# returns a DownstreamMsgs (what bgpd emits in response).

@dataclass
class BApiNexthopUpdate:
    """Input payload: zebra's nexthop-tracking notification."""
    endpoint: addr_t     # the tracked nexthop address
    resolved: addr_t     # resolved next-hop (== endpoint if directly connected)
    status_up: bool      # zebra-side reachability (drives BGP_NEXTHOP_VALID)


@dataclass
class DownstreamMsgs:
    """Output: messages bgpd emits while processing one nh update.

    Owns its insertion convention (newest-first via prepend) so the
    transition body doesn't have to know. Use emit_del / emit_add."""
    msgs: list[BgpdRouteEvent] = field(default_factory=list)

    def emit_del(self, prefix: prefix_t) -> None:
        prepend(self.msgs, BgpdRouteEvent(op=BOp.DEL, prefix=prefix, nexthops=[]))

    def emit_add(self, prefix: prefix_t, nexthops: list[addr_t]) -> None:
        prepend(self.msgs, BgpdRouteEvent(op=BOp.SET, prefix=prefix, nexthops=nexthops))


# ── Model: state, contract, transition ───────────────────────────────────────

@dataclass
class BgpdNexthopState:
    """The model's state. Both fields are observable bgpd state."""
    nexthop_cache_table: list[BgpNexthopCache] = field(default_factory=list)
    rib: list[BgpRibEntry] = field(default_factory=list)

    # ── Invariant ───────────────────────────────────────────────────────────
    def invariant(self) -> bool:
        """
        Three groups of constraints:
          1. Keys are unique within each table.
          2. RIB entries are well-formed (no duplicate / no empty nh lists).
          3. The cache and the RIB agree: every route nexthop is cached, and
             every cache entry is referenced by at least one route. In other
             words, the cache is exactly the union of route nexthops."""
        cache_unique = no_dup(bnc.endpoint for bnc in self.nexthop_cache_table)
        rib_keys_unique = no_dup(r.prefix for r in self.rib)
        rib_nhs_dedup = all(no_dup(r.nexthops) for r in self.rib)
        rib_nonempty = all(len(r.nexthops) > 0 for r in self.rib)
        all_rib_nhs_cached = all(
            any(bnc.endpoint == nh for bnc in self.nexthop_cache_table)
            for r in self.rib
            for nh in r.nexthops
        )
        cache_is_referenced = all(
            any(any(bnc.endpoint == nh for nh in r.nexthops) for r in self.rib)
            for bnc in self.nexthop_cache_table
        )
        return (
            cache_unique
            and rib_keys_unique
            and rib_nhs_dedup
            and rib_nonempty
            and all_rib_nhs_cached
            and cache_is_referenced
        )

    # ── Precondition ────────────────────────────────────────────────────────
    def api_bgp_nh_update_precondition(self, api: BApiNexthopUpdate) -> bool:
        """Action guard. The harness must only call api_bgp_nh_update when
        this returns True. This API has no input-shape requirements beyond
        the state invariant, so the guard reduces to invariant()."""
        return self.invariant()

    # ── Transition ──────────────────────────────────────────────────────────
    def api_bgp_nh_update(self, api: BApiNexthopUpdate) -> DownstreamMsgs:
        """Process one zebra nexthop-tracking update.

        Returns the messages bgpd would emit to zebra. After this call the
        state must still satisfy invariant() — the harness checks this."""
        res = DownstreamMsgs()

        # Unknown nexthop: zebra is telling us about something we don't
        # track. No state change, no downstream messages.
        if not any(bnc.endpoint == api.endpoint for bnc in self.nexthop_cache_table):
            return res

        # Update the cache entry. Early-out if (resolved, valid) didn't change.
        for bnc in self.nexthop_cache_table:
            if bnc.endpoint == api.endpoint:
                if bnc.resolved == api.resolved and bnc.valid == api.status_up:
                    return res
                bnc.valid = api.status_up
                bnc.resolved = api.resolved
                break

        # Re-evaluate every RIB entry that uses this nexthop. If the entry
        # now has no valid nexthops, withdraw the route (DEL); otherwise
        # re-announce with the surviving up-set (SET).
        for r in self.rib:
            if any(nh == api.endpoint for nh in r.nexthops):
                if self._all_nhs_down(r):
                    res.emit_del(r.prefix)
                else:
                    up_nexthops = [nh for nh in r.nexthops if self._is_valid_nh(nh)]
                    res.emit_add(r.prefix, up_nexthops)
        return res

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _is_valid_nh(self, nh: addr_t) -> bool:
        """True iff `nh` is cached and currently up."""
        return any(bnc.endpoint == nh and bnc.valid for bnc in self.nexthop_cache_table)

    def _is_invalid_nh(self, nh: addr_t) -> bool:
        """True iff `nh` is not cached, or is cached but down."""
        return all(bnc.endpoint != nh or not bnc.valid for bnc in self.nexthop_cache_table)

    def _all_nhs_down(self, r: BgpRibEntry) -> bool:
        """True iff none of the route's nexthops are currently up."""
        return all(self._is_invalid_nh(nh) for nh in r.nexthops)
