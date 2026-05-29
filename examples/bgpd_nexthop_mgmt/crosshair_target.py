"""CrossHair target for api_bgp_nh_update.

The entry point for test generation is `api_bgp_nh_update_with_precondition`.
It takes the minimum set of primitive-typed inputs, so that CrossHair and Z3
could efficiently explore diverse input combinations.

Pre-processings like `_dedup_rib_seed`, `_build_cache_seed`, and `_build_state_and_api`
ensures the actual input to the target (`api_bgp_nh_update`) satisfies
`api_bgp_nh_update_precondition`. This pattern supplies custom pre-conditions
to CrossHair.
"""

from builtin import addr_t, prefix_t
from bgpd_nexthop_mgmt.api_bgp_nh_update import (
    BApiNexthopUpdate,
    BgpNexthopCache,
    BgpRibEntry,
    BgpdNexthopState,
    DownstreamMsgs,
)


def _dedup_rib_seed(
    rib_seed: list[tuple[int, list[int]]],
) -> list[tuple[int, list[int]]]:
    """Enforce rib_keys_unique, rib_nhs_dedup, rib_nonempty on the seed.

    Drops tuples with duplicate prefixes and tuples whose nexthop list
    becomes empty after dedup."""
    out: list[tuple[int, list[int]]] = []
    seen_prefixes: list = []
    for prefix, nhs in rib_seed:
        if any(prefix == p for p in seen_prefixes):
            continue
        deduped: list[int] = []
        for nh in nhs:
            if all(nh != d for d in deduped):
                deduped.append(nh)
        if len(deduped) == 0:
            continue
        out.append((prefix, deduped))
        seen_prefixes.append(prefix)
    return out


def _build_cache_seed(
    rib_seed: list[tuple[int, list[int]]],
    symbolic_cache_seed: list[tuple[int, int, bool]],
) -> list[tuple[int, int, bool]]:
    """Build the cache seed as exactly the union of RIB nexthops.

    For each unique RIB-referenced endpoint, take (resolved, valid) from
    the symbolic cache_seed if any tuple there has the matching endpoint;
    otherwise default to (endpoint, False)."""
    endpoints: list[int] = []
    for _, nhs in rib_seed:
        for nh in nhs:
            if all(nh != e for e in endpoints):
                endpoints.append(nh)

    out: list[tuple[int, int, bool]] = []
    for ep in endpoints:
        match: tuple[int, int, bool] | None = None
        for cs_ep, cs_resolved, cs_valid in symbolic_cache_seed:
            if cs_ep == ep:
                match = (ep, cs_resolved, cs_valid)
                break
        if match is not None:
            out.append(match)
        else:
            out.append((ep, ep, False))
    return out


def _build_state_and_api(
    rib_seed: list[tuple[int, list[int]]],
    cache_seed: list[tuple[int, int, bool]],
    api_endpoint: int,
    api_resolved: int,
    api_status_up: bool,
) -> tuple[BgpdNexthopState, BApiNexthopUpdate]:
    """Construct the model state and API param from already-canonical inputs.

    Both the symbolic entry point and the postprocessor go through here,
    so the dataclass plumbing lives in one place. Callers must have already
    run _dedup_rib_seed / _build_cache_seed on the seeds."""
    state = BgpdNexthopState(
        rib=[
            BgpRibEntry(prefix=prefix_t(p), nexthops=[addr_t(nh) for nh in nhs])
            for p, nhs in rib_seed
        ],
        nexthop_cache_table=[
            BgpNexthopCache(endpoint=addr_t(e), resolved=addr_t(r), valid=v)
            for e, r, v in cache_seed
        ],
    )
    api = BApiNexthopUpdate(
        endpoint=addr_t(api_endpoint),
        resolved=addr_t(api_resolved),
        status_up=api_status_up,
    )
    return state, api


def api_bgp_nh_update_with_precondition(
    rib_seed: list[tuple[int, list[int]]],
    cache_seed: list[tuple[int, int, bool]],
    api_endpoint: int,
    api_resolved: int,
    api_status_up: bool,
) -> DownstreamMsgs:
    rib_seed = _dedup_rib_seed(rib_seed)
    cache_seed = _build_cache_seed(rib_seed, cache_seed)
    state, api = _build_state_and_api(
        rib_seed, cache_seed, api_endpoint, api_resolved, api_status_up,
    )
    return state.api_bgp_nh_update(api)
