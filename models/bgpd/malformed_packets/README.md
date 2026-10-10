# BGP malformed-packet model and parity fuzzer

This module models selected BGP attribute and OPEN error-handling rules and
replays generated inputs against FRRouting. The default release candidate
contains legacy attribute, AS_PATH/AS4_PATH, MP_REACH, OPEN capability, and
Route Refresh suites. Stateful Graceful Restart and route lifecycle work are
outside this cut.

## Pipeline and formal-methods scope

`bgp_oracle.py` is an executable RFC model. `generate_*_suite.py` entry points
expose bounded arguments for symbolic exploration with CrossHair.
`packet_builders.py` supplies shared structural byte builders.
`seed_structural_suites.py` enumerates a finite grid, deduplicates by wire bytes
and verdict, and samples each verdict class. Enumeration is exhaustive only
over that grid; the saved, capped corpus is a sample.

`run_parity_fuzzer.py` loads the committed dictionaries, constructs packets,
checks emitted UPDATE attributes against the oracle input, and evaluates the
model. Live mode then compares permitted outcomes with session/RIB observations.
These checks do not formally verify FRR's C implementation or prove complete RFC
compliance. Python branch coverage and FRR C coverage are separate measurements.

Active case files are `tests/*_argdict*.txt`: one Python literal dictionary per
line, parsed with `ast.literal_eval`. Historical JSON files are reference
artifacts and are not runner inputs. CrossHair output containing expressions
(such as assignment expressions) must be converted to literal dictionaries
before loading. `crosshair watch` analyzes contracts; it does not write these
corpora automatically.

## Offline release check

From the repository root, with Python 3.10+ (no Docker or solver required):

```bash
python3 -m unittest models.bgpd.malformed_packets.testing.test_release -v
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer \
  --suite all --dry-run --fail-on-deviation --out /tmp/bgp-release-dry-run.json
```

Dry runs build packets and evaluate the model. Their matrix has **zero parity
passes**, because no daemon was observed. Missing, empty, malformed, or
non-literal corpora fail the run. `--limit` caps each suite; `--limit 0` executes
zero cases. Reports include corpus row counts and SHA-256 hashes.

Regenerate the three structural corpora deterministically:

```bash
python3 -m models.bgpd.malformed_packets.seed_structural_suites --max-per-class 80
```

Use `--out-dir /tmp/bgp-seeds` to compare regeneration without replacing saved
files. Symbolic tools are optional for replay (`pip install crosshair-tool`);
the structural entry points return model verdicts for bounded inputs. A solver
run, its bounds, and its output must be recorded separately before claiming
symbolically derived coverage.

## Live parity

Docker is required. The setup scripts replace the container named `frr-lab`.
The standard lab uses `quay.io/frrouting/frr:10.0.1`, local port 1179 and peer
ASN 65002:

```bash
bash models/bgpd/malformed_packets/setup_frr_container.sh
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer \
  --suite all --fail-on-deviation --out /tmp/bgp-live-parity.json
```

The runner advertises four-octet ASN support. Two-octet AS_PATH cases are
executed offline and skipped live, with the skip count in the report. Session
establishment and RIB-query failures are harness errors, not evidence that FRR
crashed. Native IPv4 cases query `show ip bgp <prefix> json` and check for a
`paths` entry; this does not prove kernel forwarding or re-advertisement.
MP-only and Route Refresh cases check session survival only.

`--fail-on-deviation` exits nonzero for reported deviations and connection or
observation errors. A discrepancy needs reproduction and RFC review before
being escalated as an implementation defect.

## Coverage

Optional Python coverage (offline):

```bash
python3 -m pip install coverage
python3 -m models.bgpd.malformed_packets.testing.coverage
```

FRR C coverage (Linux Docker image built from FRR tag `frr-10.0.1`):

```bash
bash models/bgpd/malformed_packets/setup_frr_coverage.sh
bash models/bgpd/malformed_packets/collect_c_coverage.sh --baseline
bash models/bgpd/malformed_packets/collect_c_coverage.sh
```

The collector resets counters and injects up to 100 cases per suite in
`--coverage-mode`. This mode **skips parity assertions** and records zero passes.
It extracts `bgp_attr.c`, `bgp_open.c`, `bgp_packet.c`, and `bgp_route.c`, then
renders `coverage_html_c/`. Baseline comparisons require the same FRR revision
and file denominators. Create a local baseline; no historical coverage numbers
are presented as measurements of this release.

## Known limits and next cleanup

- Legacy dictionaries are expanded into individual attribute-slot mutations
  around valid mandatory attributes. These are derived tests, rather than
  exact replay of the original generator's whole attribute sequence. Old soft
  dictionaries lack the newer `val1`/`val4` arguments and use zero payloads.
- Payload normalization makes an attribute agree with its declared length;
  a case named “truncated” may therefore become a valid normalized payload.
- MP modeling covers selected header/nexthop framing, not full NLRI semantics.
  Labeled/VPN tails are stress inputs; family RIB state is not queried.
- OPEN modeling checks TLV framing and selected lengths, not every capability's
  contents or negotiation. Capability assignments follow the
  [IANA registry](https://www.iana.org/assignments/capability-codes/).
- Route Refresh seeds exercise AFI/SAFI combinations with correct message
  framing. They have a survival expectation, not a full refresh-state model.

Next work should unify legacy generation and replay around the same complete
wire case and context, regenerate those corpora, and add family-specific live
observations. This release keeps those limitations explicit instead of claiming
complete symbolic generation or full protocol verification.
