"""Seed the structural suites by exhaustive enumeration of their bounded
spaces, deduplicated on (wire bytes, oracle verdict), then stratified-capped
per verdict class so live runs stay practical.

This is the MBT anti-explosion pattern: the symbolic space each generator
declares is tiny and enumerable offline, so runnable dictionaries ship
immediately. Symbolic exploration is a separate workflow; crosshair watch
does not export these corpora automatically. Two cases
survive dedup only if they differ in what FRR sees on the wire or in the
RFC-mandated outcome; the cap then bounds each verdict class while stride
sampling keeps structural spread.

    PYTHONPATH=. python3 models/bgpd/malformed_packets/seed_structural_suites.py \
        [--max-per-class 80]
"""

import argparse
from itertools import product
from pathlib import Path

from models.bgpd.malformed_packets.packet_builders import (
    MP_AFIS, MP_SAFIS, MP_NH_LENS, ATTR_FLAG_CLASSES, CAP_CODES,
)
from models.bgpd.malformed_packets.bgp_oracle import parse_capabilities
from models.bgpd.malformed_packets.run_parity_fuzzer import (
    build_aspath_update, build_mpreach_update, build_opencap_open,
    _extract_opt_params, eval_aspath, eval_mpreach,
)

OUT_DIR = Path(__file__).resolve().parent / "tests"
CANONICAL_PREFIX_ID = 0   # fixed so wire bytes are comparable across cases

def verdict_of(suite, args):
    if suite == "aspath":
        return eval_aspath(build_aspath_update(args, CANONICAL_PREFIX_ID)[1], args)
    if suite == "mpreach":
        return eval_mpreach(build_mpreach_update(args, CANONICAL_PREFIX_ID)[1], args)
    return parse_capabilities(_extract_opt_params(build_opencap_open(args)))


def wire_of(suite, args):
    if suite == "aspath":
        return build_aspath_update(args, CANONICAL_PREFIX_ID)[0]
    if suite == "mpreach":
        return build_mpreach_update(args, CANONICAL_PREFIX_ID)[0]
    return build_opencap_open(args)


def enumerate_space():
    # AS_PATH: 5^4 x 2 x 2 x 7 = 17,500 raw points.
    for s1t, s1c, s2t, s2c in product(range(5), repeat=4):
        for asn4, with_as4 in product((0, 1), repeat=2):
            for extra in range(-3, 4):
                yield "aspath", {
                    "seg1_type": s1t, "seg1_count": s1c,
                    "seg2_type": s2t, "seg2_count": s2c,
                    "asn_4byte": asn4, "with_as4_path": with_as4,
                    "extra_len": extra,
                }

    # MP_REACH: 3x5x5x2x2x2x9 = 5,400 raw points.
    for afi, safi, nh_len in product(MP_AFIS, MP_SAFIS, MP_NH_LENS):
        for fill, resv, nlri_wf, flags in product(
                (0, 1), (0, 1), (0, 1), ATTR_FLAG_CLASSES):
            yield "mpreach", {
                "afi": afi, "safi": safi, "nh_len": nh_len,
                "fill_nh": fill, "reserved_present": resv,
                "nlri_wf": nlri_wf, "flags": flags,
            }

    # OPEN capabilities: cap1 space exhaustively; for two-cap cases fix a
    # well-formed cap1 (independent factors don't interact except when
    # framing breaks, which the interaction probes cover).
    n_codes = len(CAP_CODES)
    cap_points = [(code, ln, fill)
                  for code in range(n_codes)
                  for ln in range(7)
                  for fill in (0, 1)]
    for c1, l1, f1 in cap_points:                                   # single
        yield "opencap", {"num_caps": 1, "code1_idx": c1, "len1": l1,
                          "fill1": f1, "code2_idx": 0, "len2": 0, "fill2": 0}
    anchor = {"num_caps": 2, "code1_idx": CAP_CODES.index(65), "len1": 4, "fill1": 1}
    for c2, l2, f2 in cap_points:                                   # paired
        yield "opencap", {**anchor, "code2_idx": c2, "len2": l2, "fill2": f2}
    # Interaction probes: broken framing on one or both caps.
    for l1, f1, l2, f2 in ((6, 0, 6, 0), (6, 0, 4, 1), (4, 1, 6, 0)):
        yield "opencap", {"num_caps": 2, "code1_idx": 18, "len1": l1,
                          "fill1": f1, "code2_idx": 18, "len2": l2, "fill2": f2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-per-class", type=int, default=80,
                    help="cap per (suite, verdict) class; stride-sampled")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ns = ap.parse_args()
    if ns.max_per_class < 1:
        ap.error("max-per-class must be positive")
    ns.out_dir.mkdir(parents=True, exist_ok=True)

    seen = set()
    kept = {"aspath": [], "mpreach": [], "opencap": []}   # (args, verdict)
    total = 0

    for suite, args in enumerate_space():
        total += 1
        verdict = verdict_of(suite, args).name
        key = (suite, wire_of(suite, args).hex(), verdict)
        if key in seen:
            continue
        seen.add(key)
        kept[suite].append((args, verdict))

    files = {
        "aspath": "aspath_argdict.txt",
        "mpreach": "mpreach_argdict.txt",
        "opencap": "opencap_argdict.txt",
    }
    written_total = 0
    for suite, fname in files.items():
        classes = {}
        for idx, (args, verdict) in enumerate(kept[suite]):
            classes.setdefault(verdict, []).append((idx, args))

        chosen = []
        for verdict, items in sorted(classes.items()):
            cap = min(ns.max_per_class, len(items))
            stride = len(items) / cap if cap else 1
            picked = {items[min(int(i * stride), len(items) - 1)][0]
                      for i in range(cap)}
            # Include the last point while honoring the per-class cap.
            if items[-1][0] not in picked:
                picked.remove(max(picked))
            picked.add(items[-1][0])
            for idx, args in sorted(classes[verdict]):
                if idx in picked:
                    chosen.append((args, verdict))

        hist = {}
        for args, verdict in chosen:
            hist[verdict] = hist.get(verdict, 0) + 1

        path = ns.out_dir / fname
        with open(path, "w") as f:
            for args, _ in chosen:
                f.write(str(args) + "\n")
        written_total += len(chosen)
        print(f"[+] {suite}: {len(kept[suite])} unique -> {len(chosen)} written -> {path}")
        for v, n in sorted(hist.items()):
            print(f"      {v:<20} {n}")
    print(f"[i] enumerated {total} points; dedup kept "
          f"{sum(len(v) for v in kept.values())}; wrote {written_total}")


if __name__ == "__main__":
    main()
