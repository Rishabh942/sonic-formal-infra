# BGP UPDATE attribute tests

The malformed UPDATE core from PR #8 tests extended path attributes, soft
faults and community payloads against an executable RFC oracle. This draft
adds bounded AS_PATH/AS4_PATH structure in four-byte-ASN sessions. MP_REACH,
OPEN, Route Refresh and stateful GR/route suites are outside this cut.

Requires **Python 3.10+**. Live tests require **Docker with Linux containers**.
Run Python commands from the repository root. Shell scripts work from any
working directory and support `--help`.

## Offline check

```bash
python3 -m unittest models.bgpd.malformed_packets.testing.test_core_release models.bgpd.malformed_packets.testing.test_scripts models.bgpd.malformed_packets.testing.test_aspath_release
python3 -m models.bgpd.malformed_packets.seed_aspath_suite
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
`--suite` accepts `all` (default), `extended`, `soft`, `semantic`, or `aspath`.
`--fail-on-deviation` returns nonzero for unexpected daemon behavior or harness
errors. Reports distinguish route presence, notified session reset, unnotified
disconnect and route absence; an unsent UPDATE is a harness error.
a mismatch needs packet/RFC analysis before being reported as an FRR bug.

For a separate lab, pass `--container bgp-test --port 11790` to setup and the
fuzzer. Stop it with `docker stop bgp-test`; remove it with `docker rm bgp-test`.
The historical `setup_frr_legacy.sh` selects FRR 7.5.

## AS_PATH draft cut

`generate_aspath_suite.py` bounds two segment types and counts, optional
AS4_PATH, and a small value-length adjustment. The seed command above checks
all 8,750 bounded inputs for generator/wire/oracle agreement, then checks the
saved 153-case sample. To regenerate that sample, run the same command with
`--write`. The saved cases are Python literal dictionaries like the core
corpus. Both the generator and replay call `parse_attributes` with the lab's
four-byte ASN negotiation and first-AS policy.

To replay only this suite, add `--suite aspath` to the live command above.
The default `all` run includes it. Two-byte-ASN sessions need a separate peer
that does not negotiate AS4; this draft makes no live claim about them. A dry
run checks packet construction and model results, not FRR behavior.

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
`bgp_route.c`. Comparisons require matching FRR revisions, counter scope, limits,
corpus hashes and denominators. The collector accepts `--container`, `--port`, `--limit`,
and `--out DIR`. Small changes between captures can reflect scheduling.
To cover all 2,497 saved packets, use `--limit 2000` on both collector calls.

## Model and arguments

`bgp_oracle.py` retains the earlier flag/length/duplicate rules and adds
payload-aware AS_PATH framing with the negotiated ASN width. The runner uses
the same oracle and checks decoded UPDATE attributes against its model inputs.
`generate_rfc4271_suite.py`, `generate_rfc7606_suite.py`,
`testing/generate_semantic_suite.py` and `generate_aspath_suite.py` are the
model entry points in this cut.

For example, `flags4=192`, `type4=8`, `len4=4` and
`payload_hex='00010203'` produce a COMMUNITY attribute:
`c0 08 04 00 01 02 03`. Flags, type and length are bounded generator variables;
replay uses their concrete values. The payload is padded or truncated to the
declared length. Saved `tests/*.txt` rows are Python literal dictionaries,
loaded with `ast.literal_eval`. Historical JSON files are not replay inputs.

The original dictionaries expand into individual slot mutations around valid
mandatory attributes; they are not full-sequence generator replay. The oracle
models selected RFC rules, not every attribute value or NLRI semantic.
Types 23, 25, 26, 29, 35, 39 and 40 are assigned path attributes whose
semantics are not modeled here. The symbolic entry points exclude them instead
of applying the generic unknown-attribute rule. One historical extended-suite
packet uses type 23; its replay is not a test of type-23-specific semantics.
Native IPv4 observations check BGP `paths`, not kernel forwarding. The core
keeps the earlier flag-first handling; later peer-first changes are deferred.
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
