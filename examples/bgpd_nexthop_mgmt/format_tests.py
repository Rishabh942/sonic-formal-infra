"""Format script for CrossHair arg_dictionary test inputs.

Reads tests/nh_update_argdict.txt (or any arg_dictionary-format file from
`crosshair cover`), canonicalizes and dedupes inputs, re-executes the
model on each canonical input, and writes a JSON file of fully-populated
test cases that can compare against actual bgpd execution.

Run from anywhere:
    python3 path/to/format_tests.py [INPUT] [-o OUTPUT]
"""

import argparse
import copy
import json
import os
import sys
from dataclasses import dataclass
from typing import Iterator

# Bootstrap sys.path so this script runs from any cwd without needing
# PYTHONPATH=.:lib. Anchors examples/ and examples/lib/ via __file__.
_HERE = os.path.dirname(os.path.abspath(__file__))      # examples/bgpd_nexthop_mgmt/
_EXAMPLES = os.path.dirname(_HERE)                       # examples/
sys.path.insert(0, os.path.join(_EXAMPLES, "lib"))
sys.path.insert(0, _EXAMPLES)

from builtin import to_ipv6_address, to_ipv6_prefix
from bgpd_nexthop_mgmt.api_bgp_nh_update import (
    BApiNexthopUpdate,
    BgpdNexthopState,
    DownstreamMsgs,
)
# Reaching for the underscore-prefixed helpers from crosshair_target.
# They're the canonical "normalize + build" trio; reusing them here keeps
# the postprocessor exactly in sync with the symbolic entry point.
from bgpd_nexthop_mgmt.crosshair_target import (
    _build_cache_seed,
    _build_state_and_api,
    _dedup_rib_seed,
)


DEFAULT_INPUT = os.path.join(_HERE, "tests", "nh_update_argdict.txt")
DEFAULT_OUTPUT = os.path.join(_HERE, "tests", "nh_update_formatted.json")


@dataclass
class TestCase:
    """One row from a CrossHair arg_dictionary file, plus slots that the
    processing step fills in.

    After read_and_dedup_argdict, only test_id and inputs are populated.
    After format_test_case (which calls evaluate), all six are populated."""
    test_id: int                                # sequential, starts at 1
    inputs: dict                                # canonicalized kwargs
    initial_state: BgpdNexthopState | None = None
    api_param: BApiNexthopUpdate | None = None
    final_state: BgpdNexthopState | None = None
    downstream_msgs: DownstreamMsgs | None = None


def read_argdict(path: str) -> Iterator[TestCase]:
    """Stream TestCases from a CrossHair arg_dictionary output file.

    Each non-blank line is one Python expression (a dict of kwargs).
    Only the input side of TestCase is populated; computed fields stay None."""
    with open(path) as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            # eval, not ast.literal_eval: CrossHair emits walrus aliases
            # (e.g., `v1:=(0, [])`) which ast rejects. Restricted __builtins__
            # keeps this safe for our trusted-but-walrus-containing input.
            inputs = eval(line, {"__builtins__": {}}, {})
            yield TestCase(test_id=line_no, inputs=inputs)


def canonicalize(inputs: dict) -> dict:
    """Run the same seed coercions the symbolic wrapper applies.

    After this pass, two raw inputs that map to the same model behavior
    become byte-identical, which lets us dedupe."""
    rib_seed = _dedup_rib_seed(inputs["rib_seed"])
    cache_seed = _build_cache_seed(rib_seed, inputs["cache_seed"])
    return {
        "rib_seed": rib_seed,
        "cache_seed": cache_seed,
        "api_endpoint": inputs["api_endpoint"],
        "api_resolved": inputs["api_resolved"],
        "api_status_up": inputs["api_status_up"],
    }


def _hash_key(canonical: dict) -> tuple:
    """Hashable fingerprint of canonical inputs (lists become tuples)."""
    return (
        tuple((p, tuple(nhs)) for p, nhs in canonical["rib_seed"]),
        tuple(canonical["cache_seed"]),
        canonical["api_endpoint"],
        canonical["api_resolved"],
        canonical["api_status_up"],
    )


def read_and_dedup_argdict(path: str) -> Iterator[TestCase]:
    """Read, canonicalize, and dedupe.

    Yields the first occurrence of each canonical key, with `inputs` replaced
    by its canonical form. `test_id` is preserved from the source line so the
    survivor still points back to its original row in the input file."""
    seen: set[tuple] = set()
    for tc in read_argdict(path):
        canonical = canonicalize(tc.inputs)
        key = _hash_key(canonical)
        if key in seen:
            continue
        seen.add(key)
        yield TestCase(test_id=tc.test_id, inputs=canonical)


def evaluate(
    canonical: dict,
) -> tuple[BgpdNexthopState, BApiNexthopUpdate, BgpdNexthopState, DownstreamMsgs]:
    """Re-execute the model on canonical inputs.

    Returns (initial_state, api_param, final_state, downstream_msgs).
    `initial_state` is the freshly-built pre-state; `final_state` is a
    deep copy mutated by the transition.

    Asserts the invariant before and after — before is a sanity check on
    canonicalize() (its job is to produce invariant-satisfying states);
    after is the model's claimed property. Each test case is thus also
    an invariant check."""
    initial_state, api = _build_state_and_api(**canonical)
    assert initial_state.invariant(), (
        f"canonicalized inputs produced a non-invariant state: {canonical!r}"
    )
    final_state = copy.deepcopy(initial_state)
    msgs = final_state.api_bgp_nh_update(api)
    assert final_state.invariant(), (
        f"transition broke invariant; inputs={canonical!r}, msgs={msgs!r}"
    )
    return initial_state, api, final_state, msgs


def _state_to_dict(s: BgpdNexthopState) -> dict:
    return {
        "nexthop_cache_table": [
            {
                "endpoint": to_ipv6_address(b.endpoint),
                "resolved": to_ipv6_address(b.resolved),
                "valid": b.valid,
            }
            for b in s.nexthop_cache_table
        ],
        "rib": [
            {
                "prefix": to_ipv6_prefix(r.prefix),
                "nexthops": [to_ipv6_address(nh) for nh in r.nexthops],
            }
            for r in s.rib
        ],
    }


def _api_to_dict(a: BApiNexthopUpdate) -> dict:
    return {
        "endpoint": to_ipv6_address(a.endpoint),
        "resolved": to_ipv6_address(a.resolved),
        "status_up": a.status_up,
    }


def _msgs_to_dict(m: DownstreamMsgs) -> list[dict]:
    return [
        {
            "op": e.op.name,
            "prefix": to_ipv6_prefix(e.prefix),
            "nexthops": [to_ipv6_address(nh) for nh in e.nexthops],
        }
        for e in m.msgs
    ]


def format_test_case(tc: TestCase) -> dict:
    """Re-execute the model and produce the formatted output dict.

    Populates tc.initial_state / api_param / final_state / downstream_msgs
    in place so in-memory consumers see a fully-formed TestCase."""
    initial_state, api, final_state, msgs = evaluate(tc.inputs)
    tc.initial_state = initial_state
    tc.api_param = api
    tc.final_state = final_state
    tc.downstream_msgs = msgs
    return {
        "TestId": tc.test_id,
        "Op": "api_bgp_nh_update",
        "InitialState": _state_to_dict(initial_state),
        "ApiParam": _api_to_dict(api),
        "FinalState": _state_to_dict(final_state),
        "DownstreamMsgs": _msgs_to_dict(msgs),
    }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Read a CrossHair arg_dictionary file, canonicalize + dedupe inputs, "
            "re-execute the model, and emit JSON test cases."
        ),
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=DEFAULT_INPUT,
        help=f"Path to arg_dictionary file (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT,
        help=f"Path to output JSON file (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    raw = sum(1 for _ in read_argdict(args.input))
    cases = list(read_and_dedup_argdict(args.input))
    formatted = [format_test_case(tc) for tc in cases]

    with open(args.output, "w") as f:
        json.dump(formatted, f, indent=2)

    print(f"path:     {args.input}")
    print(f"raw:      {raw} inputs")
    print(f"deduped:  {len(cases)} test cases")
    print(f"output:   {args.output}")


if __name__ == "__main__":
    main()
