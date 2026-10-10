#!/bin/bash
# Measure C-side (gcov) coverage of bgpd reached by the parity fuzzer.
#
# Requires the coverage-instrumented container:
#   ./setup_frr_coverage.sh
#
# Usage:
#   PYTHONPATH=. ./collect_c_coverage.sh [--baseline]
#
# --baseline saves coverage_baseline.json for later comparison; without it a
# summary is printed and diffed against an existing baseline.
#
# How it works (each step matters):
#   1. /frr must be world-writable - bgpd drops privileges to user "frr",
#      and gcov silently fails to write .gcda into a root-owned tree.
#   2. After the fuzzer finishes, bgpd is SIGTERMed: gcov counters are
#      flushed to .gcda on process exit, not continuously.
#   3. All lcov/genhtml steps run INSIDE the container (the host may not
#      have lcov installed).

set -euo pipefail
cd "$(dirname "$0")/../../.."   # repo root

MODE="${1:-run}"
if [[ "$MODE" != "run" && "$MODE" != "--baseline" ]]; then
  echo "Usage: $0 [--baseline]" >&2
  exit 2
fi
FILES='*/bgpd/bgp_attr.c */bgpd/bgp_open.c */bgpd/bgp_packet.c */bgpd/bgp_route.c'

echo "[*] Fixing gcda write permissions..."
docker exec frr-lab chmod -R a+rwX /frr
docker exec frr-lab lcov --zerocounters --directory /frr

echo "[*] Running fuzzer against coverage-instrumented bgpd..."
PYTHONPATH=. python3 -m models.bgpd.malformed_packets.run_parity_fuzzer --suite all --limit 100 --coverage-mode --fail-on-deviation

echo "[*] Stopping bgpd gracefully to flush gcov counters..."
docker exec frr-lab pkill -TERM bgpd || true
sleep 4
docker start frr-lab >/dev/null && sleep 3

echo "[*] Capturing + extracting via lcov (in-container)..."
docker exec frr-lab bash -ec "\
  lcov --capture --directory /frr --output-file /tmp/coverage.info --rc lcov_branch_coverage=1 2>/dev/null >/dev/null; \
  lcov --extract /tmp/coverage.info $FILES --output-file /tmp/target.info --rc lcov_branch_coverage=1 >/dev/null 2>&1; \
  genhtml /tmp/target.info --output-directory /tmp/coverage_html_c --rc lcov_branch_coverage=1 >/dev/null 2>&1"
docker cp frr-lab:/tmp/target.info /tmp/frr_target.info
docker cp frr-lab:/tmp/coverage_html_c models/bgpd/malformed_packets/ >/dev/null

FRR_REVISION=$(docker exec frr-lab git -C /frr rev-parse HEAD)
python3 - "$MODE" "$FRR_REVISION" <<'EOF'
import json, re, sys
mode = sys.argv[1]
txt = open("/tmp/frr_target.info").read()
rows = []
for sec in txt.split("end_of_record"):
    m = re.search(r"^SF:(.+)$", sec, re.M)
    if not m:
        continue
    def g(p):
        mm = re.search(p, sec, re.M)
        return int(mm.group(1)) if mm else 0
    rows.append(dict(name=m.group(1).split("/")[-1], lf=g(r"LF:(\d+)"), lh=g(r"LH:(\d+)"),
                     bf=g(r"BRF:(\d+)"), bh=g(r"BRH:(\d+)"), fn=g(r"FNF:(\d+)"), fh=g(r"FNH:(\d+)")))
if {r['name'] for r in rows} != {'bgp_attr.c', 'bgp_open.c', 'bgp_packet.c', 'bgp_route.c'}:
    raise SystemExit('Missing or unexpected target files in lcov capture')
tot = lambda k1, k2: (sum(r[k1] for r in rows), sum(r[k2] for r in rows))
tl, tlf = tot("lh", "lf"); tb, tbf = tot("bh", "bf"); tf, tfn = tot("fh", "fn")
snap = {"files": rows, "frr_revision": sys.argv[2], "mode": "coverage-only",
        "total": {"lines": tl, "lines_total": tlf,
                  "branches": tb, "branches_total": tbf,
                  "funcs": tf, "funcs_total": tfn}}
for r in sorted(rows, key=lambda x: x["name"]):
    print(f"  {r['name']:<16} lines {r['lh']}/{r['lf']} ({100*r['lh']/max(r['lf'],1):.1f}%)  "
          f"branches {r['bh']}/{r['bf']} ({100*r['bh']/max(r['bf'],1):.1f}%)  "
          f"funcs {r['fh']}/{r['fn']}")
t = snap["total"]
print(f"  {'TOTAL':<16} lines {tl}/{tlf} ({100*tl/max(tlf,1):.1f}%)  "
      f"branches {tb}/{tbf} ({100*tb/max(tbf,1):.1f}%)  "
      f"funcs {tf}/{tfn} ({100*tf/max(tfn,1):.1f}%)")
base_path = "models/bgpd/malformed_packets/coverage_baseline.json"
if mode == "--baseline":
    json.dump(snap, open(base_path, "w"), indent=1)
    print("[+] baseline saved:", base_path)
else:
    from pathlib import Path
    if not Path(base_path).exists():
        print('[i] No baseline; rerun with --baseline on the same FRR build for a comparison.')
        sys.exit(0)
    base = json.load(open(base_path))
    signature = lambda data: sorted((r['name'], r['lf'], r['bf'], r['fn']) for r in data['files'])
    if base.get('frr_revision') != snap['frr_revision'] or signature(base) != signature(snap):
        raise SystemExit('Baseline build/denominators differ; no comparable coverage delta')
    bt = base["total"]
    print(f"[i] baseline: lines {bt['lines']}/{bt['lines_total']}, "
          f"funcs {bt['funcs']}/{bt['funcs_total']}")
    print(f"[+] delta: lines {100*(tl-bt['lines'])/+max(tlf,1):+.1f}pp, "
          f"funcs {100*(tf-bt['funcs'])/max(tfn,1):+.1f}pp")
EOF
