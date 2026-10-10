# BGP UPDATE attribute tests

Core release of the malformed-packet fuzzer from PR #3, using the August 20
feature scope. It tests extended path attributes, soft faults and community
payloads against an executable RFC oracle. Later standalone AS_PATH, MP_REACH,
OPEN, Route Refresh and stateful GR/route suites are outside this cut.

Requires **Python 3.10+**. Live tests require **Docker with Linux containers**.
Run Python commands from the repository root. Shell scripts work from any
working directory and support `--help`.

## Offline check

```bash
python3 -m unittest models.bgpd.malformed_packets.testing.test_core_release models.bgpd.malformed_packets.testing.test_scripts
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer \
  --dry-run --fail-on-deviation --out /tmp/bgp-core-dry.json
```

The dry run builds every saved packet and evaluates the oracle. It reports
zero parity passes because no daemon was observed. Missing or malformed
argument files fail the run.

## Live replay

```bash
bash models/bgpd/malformed_packets/setup_frr_container.sh
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer \
  --limit 20 --fail-on-deviation --out /tmp/bgp-core-live.json
```

Setup pins FRR **10.0.1**, creates `frr-lab`, binds BGP to `127.0.0.1:1179`,
and waits for readiness. The router ASN is 65001 and the fuzzer ASN is 65002.
The container receives `NET_ADMIN` and `SYS_ADMIN`. An existing container is
preserved unless you pass `--replace`.

Omit `--limit` to replay the full corpus. It caps packet mutations **per suite**.
`--suite` accepts `all` (default), `extended`, `soft`, or `semantic`.
`--fail-on-deviation` returns nonzero for unexpected daemon behavior or harness
errors. Reports distinguish route presence, session reset and route absence;
a mismatch needs packet/RFC analysis before being reported as an FRR bug.

For a separate lab, pass `--container bgp-test --port 11790` to setup and the
fuzzer. Stop it with `docker stop bgp-test`; remove it with `docker rm bgp-test`.
The historical `setup_frr_legacy.sh` selects FRR 7.5.

## C coverage

The initial build takes several minutes. Use `--replace` to switch an existing
standard lab to the coverage image.

```bash
bash models/bgpd/malformed_packets/setup_frr_coverage.sh --replace
bash models/bgpd/malformed_packets/collect_c_coverage.sh --baseline
bash models/bgpd/malformed_packets/collect_c_coverage.sh
```

The collector clears counters with bgpd stopped, starts a fresh daemon, waits
for the observer peer, injects up to 100 mutations per suite, then flushes and
captures counters before restarting. **Startup is included.** Coverage mode
records injections without assigning parity passes.

Results under `models/bgpd/malformed_packets/coverage_html_c/` include HTML,
raw `target.info`, `summary.json`, injection `parity.json` and `baseline.json`.
The four measured files are `bgp_attr.c`, `bgp_open.c`, `bgp_packet.c` and
`bgp_route.c`. Comparisons require matching FRR revisions, counter scope, limits
and denominators. The collector accepts `--container`, `--port`, `--limit`,
and `--out DIR`. Small changes between captures can reflect scheduling.
To cover all 2,344 saved packets, use `--limit 2000` on both collector calls.

## Model and arguments

`bgp_oracle.py` retains the earlier flag/length/duplicate rules and adds
payload-aware AS_PATH framing with the negotiated ASN width. The runner uses
the same oracle and checks decoded UPDATE attributes against its model inputs.
`generate_rfc4271_suite.py`, `generate_rfc7606_suite.py` and
`testing/generate_semantic_suite.py` retain the core model entry points.

For example, `flags4=192`, `type4=8`, `len4=4` and
`payload_hex='00010203'` produce a COMMUNITY attribute:
`c0 08 04 00 01 02 03`. Flags, type and length are bounded generator variables;
replay uses their concrete values. The payload is padded or truncated to the
declared length. Saved `tests/*.txt` rows are Python literal dictionaries,
loaded with `ast.literal_eval`. Historical JSON files are not replay inputs.

The original dictionaries expand into individual slot mutations around valid
mandatory attributes; they are not full-sequence generator replay. The oracle
models selected RFC rules, not every attribute value or NLRI semantic. Native
IPv4 observations check BGP `paths`, not kernel forwarding. The core keeps the
earlier flag-first handling; later peer-first oracle changes are deferred.
RFC precedence between eBGP attribute flags and peer-specific discard rules
is still under review. Attribute-discard outcomes check route retention;
AFI/SAFI-disable outcomes allow route absence or session reset. Per-attribute
removal and family-state changes require separate checks.

Replay does not require CrossHair. Symbolic exploration and case export are
separate steps; `crosshair watch` does not export these files automatically.
Saved-case replay does not prove complete RFC compliance or formally verify
FRR's C implementation.

Optional Python oracle branch coverage: install `coverage` with
`python3 -m pip install coverage`, then run
`python3 -m models.bgpd.malformed_packets.testing.coverage`.
