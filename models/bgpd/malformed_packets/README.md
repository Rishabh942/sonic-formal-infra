# BGP malformed-packet tests

An executable RFC oracle and packet fuzzer for FRRouting. Suites cover path
attributes, AS_PATH/AS4_PATH, MP_REACH, OPEN capabilities and Route Refresh.
Stateful GR and route lifecycle tests are excluded from this release.

Requires **Python 3.10+**. Live tests also require a running **Docker** daemon
with Linux containers. Run the Python commands below from the repository root.
The shell scripts work from any directory and support `--help`.

## Offline check

```bash
python3 -m unittest models.bgpd.malformed_packets.testing.test_release models.bgpd.malformed_packets.testing.test_scripts
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer \
  --suite all --dry-run --fail-on-deviation --out /tmp/bgp-dry-run.json
```

This builds every saved packet and evaluates the oracle without Docker.
Dry-run PASS/FAIL counters stay at zero because no daemon was observed.
Missing or malformed case files fail the run.

## Live tests

```bash
bash models/bgpd/malformed_packets/setup_frr_container.sh
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer \
  --suite all --limit 20 --fail-on-deviation --out /tmp/bgp-parity.json
```

Setup uses FRR **10.0.1**, container `frr-lab`, local port `1179`, and peer ASN
`65002`. It sets router ID `10.0.0.1`, waits for BGP, and prints the next command. An existing
container is preserved unless you pass `--replace` to setup.
FRR receives `NET_ADMIN` and `SYS_ADMIN` capabilities inside the container.

`--limit` caps each suite; omit it to run the full saved corpus. `--suite`
accepts `all`, `legacy`, `aspath`, `mpreach`, `opencap`, or `routerefresh`.
`--fail-on-deviation` returns a nonzero exit code for mismatches and harness
errors. Review a mismatch's packet and RFC rule before treating it as an FRR bug.

For a separate lab, pass `--container bgp-test --port 11790` to both setup and
the fuzzer. Stop it afterward with `docker stop bgp-test`; remove it with
`docker rm bgp-test`. For the default lab, use `frr-lab` instead.

## C coverage

The first command builds FRR with gcov; the first build can take several minutes.
Use `--replace` when switching an existing standard lab to coverage mode.

```bash
bash models/bgpd/malformed_packets/setup_frr_coverage.sh --replace
bash models/bgpd/malformed_packets/collect_c_coverage.sh --baseline
bash models/bgpd/malformed_packets/collect_c_coverage.sh
```

The collector clears counters with bgpd stopped, starts a fresh daemon, waits
for its observer peer, and injects up to 100 cases per suite. It then stops bgpd
to flush counters, captures them, and restarts the lab. Startup is included in
the measurement. It measures
`bgp_attr.c`, `bgp_open.c`, `bgp_packet.c`, and `bgp_route.c`.
Coverage mode skips parity checks; it does not report compliance passes.

Results are under `models/bgpd/malformed_packets/coverage_html_c/`:
`index.html`, raw `target.info`, metrics `summary.json`, injection `parity.json`,
and `baseline.json`. Later runs compare line, branch and function percentages
with the baseline. Comparisons require the same FRR revision, case limit and
file denominators. The collector accepts `--container`, `--port`, `--limit`,
and `--out DIR`.
Live scheduling can change coverage between runs; a small delta alone is not
evidence of a testing improvement.

## Model and generation

`bgp_oracle.py` defines selected RFC error-handling rules. Structural
`generate_*_suite.py` functions expose bounded inputs for CrossHair;
`packet_builders.py` supplies shared byte builders. The runner checks emitted
UPDATE attributes against its oracle inputs before sending them.

Saved cases in `tests/*.txt` are Python literal dictionaries, one per line,
loaded with `ast.literal_eval`. Historical JSON files are not runner inputs.
Regenerate the bounded structural sample separately:

```bash
python3 -m models.bgpd.malformed_packets.seed_structural_suites --out-dir /tmp/bgp-seeds
```

This enumerates a finite grid and samples each verdict class. It does not
re-run an SMT solver. CrossHair exploration and case export are separate steps;
`crosshair watch` does not write these files automatically. Neither enumeration
nor replay proves complete RFC compliance or formally verifies FRR's C code.

## Limits

- Legacy rows become individual slot mutations, rather than whole-sequence
  generator replay. Payloads are padded/truncated to their declared length.
- Two-octet AS_PATH cases run offline and are skipped in the AS4 live session.
- Native IPv4 tests check BGP `paths`, not kernel forwarding. MP and Route
  Refresh tests check session survival, not family-specific route state.
- MP modeling omits full NLRI semantics; OPEN modeling checks selected TLV
  lengths, not every capability's contents or negotiation.

Optional Python oracle coverage: install `coverage` with
`python3 -m pip install coverage`, then run
`python3 -m models.bgpd.malformed_packets.testing.coverage` from the repository root.
The historical `setup_frr_legacy.sh` uses FRR 7.5; the default workflow uses 10.0.1.
