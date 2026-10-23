# BGP Formal Verification Parity Fuzzer

This module combines executable RFC models, symbolic and bounded test generation, and live conformance checks against FRRouting for the BGP error-handling rules in **RFC 4271**, **RFC 7606**, and **RFC 4724**. It establishes agreement for the generated cases, not a proof of correctness for every FRR behavior.

CrossHair and Z3 generate edge cases for bounded packet parameters in the earlier suites. Directed structural cases cover OPEN and UPDATE framing, while a finite Graceful Restart model explores route-state transitions. The live harness sends these packets to FRR and compares observable behavior with the applicable reference model.

## Core Architecture and File Explanations

In this repository, we construct a formal model that acts as a "source of truth", and then we compare the outputs of our model with a live implementation (e.g. FRRouting) by sending generated packets over a local socket.

How the pieces fit together for the **BGP Malformed Packets** project:
- **`generate_rfc4271_suite.py` / `generate_rfc7606_suite.py`**: CrossHair entry points with symbolic BGP attribute parameters. Solved examples are saved as dictionaries in `tests/` and later used to construct physical packets. Coverage reports show which modeled branches those examples actually exercise.
- **`generate_aspath_suite.py` / `generate_mpreach_suite.py` / `generate_opencap_suite.py`**: *Structural* generators. Instead of raw byte soup they declare bounded structural parameters - AS_PATH segment types/counts/ASN width, MP_REACH AFI/SAFI/nexthop framing, OPEN capability TLVs - so symbolic exploration stays cheap and test counts stay small.
- **`graceful_restart.py`**: Directed RFC 4724 OPEN capability cases with correct code 64 encoding, restart/time boundaries, AFI/SAFI forwarding flags, duplicates, truncated tuples, and an IPv4 End-of-RIB UPDATE after successful handshakes. These cases run on fresh sessions through the same OPEN oracle and parity runner.
- **`gr_stateful.py`**: Stateful GR helper scenarios that announce routes, disconnect, reconnect, refresh selected routes, send End-of-RIB, and check route retention and cleanup. The JSON report includes event order and wire hex for reproducing failures.
- **`gr_model.py`**: Pure finite reference model for absent/active/stale routes. The stateful suite derives expected RIB observations from this model; `check_bounded_invariants(4)` exhaustively explores 549,920 transitions over two-route event sequences.
- **`packet_builders.py`**: Single source of truth for turning dictionary arguments into wire structures. Both the generators (oracle side) and `run_parity_fuzzer.py` (wire side) import it, so what the oracle judges can never diverge from what FRR receives.
- **`seed_structural_suites.py`**: Enumerates each structural space exhaustively offline, deduplicates on `(wire bytes, oracle verdict)` and stride-samples per verdict class (`--max-per-class`). Ships runnable dictionaries immediately without waiting on CrossHair; CrossHair re-derivation remains the canonical source.
- **`bgp_oracle.py`**: The formal reference implementation (Oracle). It reads incoming BGP path attributes and models strict logical branching outlined by RFC 4271 and RFC 7606 (e.g., when to trigger a Session Reset vs Attribute Discard). Value-level checks cover ORIGIN values, NEXT_HOP martians, AS_PATH/AS4_PATH segment framing (2- vs 4-byte ASN), MP_REACH/MP_UNREACH structure, ATTR_SET inner length, PMSI_TUNNEL minimum size, OTC fixed length, and RFC 7606 §5 duplicate handling. Also hosts `parse_capabilities`, the RFC 5492 OPEN-parameter model.
- **`run_parity_fuzzer.py`**: The engine driving the parity checks. It loads generated test dictionaries from `tests/`, connects over a socket to a live FRR daemon (e.g. `127.0.0.1:1179`), performs a BGP handshake, and ships the fuzzed packets. Finally, it observes if FRR crashed, tore down the session, or gracefully discarded attributes, comparing these live results precisely against the `bgp_oracle.py` expectations.
- **`testing/coverage.py`**: Wraps the execution of `run_parity_fuzzer.py` using Python's `coverage` tool to measure branch coverage of the oracle.
- **`collect_c_coverage.sh`**: Runs the selected suite against the gcov-instrumented container (`setup_frr_coverage.sh` / `Dockerfile.coverage`), captures lcov data for `bgp_attr.c`, `bgp_fsm.c`, `bgp_packet.c`, `bgp_open.c`, and `bgp_route.c`, and renders HTML into `coverage_html_c/`. Use two lcov captures and `compare_c_coverage.py` for an incremental comparison.

## Draft: stateful suites integrated with the parity fuzzer

The stateful expansion now uses the same **`run_parity_fuzzer.py` entry point,
packet oracle, parity matrix, JSON report, dry-run/coverage modes, and failure
exit convention** as the existing suites. It adds these suite names:

| Suite | Generation and checks | Lab |
| --- | --- | --- |
| `grrestart` | Existing 29 directed OPEN cases through `parse_capabilities` | Legacy or combined |
| `grstate` | Existing six GR scenarios retained as regressions | Legacy or combined |
| `grgenerated` | 33 legal model-generated traces; check absent/active/stale route states | Legacy or combined |
| `routecompetition` | 88 generated traces; check candidates, selected route, and observer UPDATEs | Combined |
| `generated` | `grgenerated` plus `routecompetition` | Combined |
| `all_existing` | Earlier packet suites plus `grrestart` and `grstate` | Legacy or combined |
| `all` | Earlier suites plus `grgenerated`; also includes `routecompetition` with the combined profile | Profile-dependent |

`route_model.py` specifies two candidate peers, two prefixes, AS-path lengths
of one or two, and ORIGIN values IGP or incomplete. The finite graph has
**625 states and 17,500 labeled transitions**, checked for candidate isolation,
replacement/withdrawal behavior, and preference/eligibility. Breadth-first
exploration derives shortest witnesses for **102 behavioral targets**,
deduplicated to **88 traces**. Those traces are a selected subset of model
paths; the live daemon does not execute every model edge.

The route wire adapter decodes its actual UPDATE bytes with the shared
`decode_update_attributes`, calls **`bgp_oracle.parse_attributes`** with the
negotiated AS width and peer first-AS policy, and derives the state effect
from that verdict and the decoded attributes. It also compares with the
independent abstract event: an encoder or oracle disagreement fails the run
instead of silently changing the expectation for FRR. Explicit withdrawals
and EOR are handled as protocol events rather than attribute-bearing UPDATEs.

`gr_model.generate_traces()` explores **18 unique states and 64 enabled
transitions**, producing **33 traces for 40 targets**. Guards prevent actions
such as sending UPDATEs while disconnected. Generated GR OPENs and route
announcements are checked by the existing capability/attribute oracles before
replay. The live checks distinguish absent, active, and stale routes and
include selective refresh followed by EOR. The original bounded GR walk and
six regression scenarios remain available; its historical 549,920 execution
count includes repeated paths and is not a unique graph-edge count.

Generated replay exposed a missing consecutive-restart rule in the earlier
GR model. The corrected model deletes previously stale routes on a second
disconnect while retaining freshly learned routes as stale, as required by
[RFC 4724 section 4.2](https://www.rfc-editor.org/rfc/rfc4724.html#section-4.2).
An explicit regression checks that distinction; FRR followed the RFC in the
observed discrepancy.

These new stateful generators use exhaustive finite-state exploration, not
CrossHair/Z3. Existing symbolic generators remain in place. AS4_PATH now uses
one companion-attribute builder in both `generate_aspath_suite.py` and the
live runner, including matching first-AS policy. Tests compare their verdicts
and decoded wire attributes across structural partitions.

From the repository root:

```bash
# All generated traces: build actual packets, invoke the oracle, check models.
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer \
  --suite generated --dry-run --fail-on-deviation --out /tmp/generated-dry.json
python3 -m unittest models.bgpd.malformed_packets.testing.test_stateful_integration

# Provision the isolated combined lab and invoke the main parity fuzzer.
# Requires the already-built frr-coverage-lab image; no host ports are exposed.
bash models/bgpd/malformed_packets/run_route_lab.sh
bash models/bgpd/malformed_packets/run_route_lab.sh --suite routecompetition
bash models/bgpd/malformed_packets/run_route_lab.sh --suite all_existing --limit 6
bash models/bgpd/malformed_packets/run_route_lab.sh --suite all

# Common baseline: previous corpus (limit 100 per suite) + topology control,
# then the new generated suites, with cumulative C coverage on the same build.
bash models/bgpd/malformed_packets/run_route_lab.sh --measure

# The existing coverage entry point dispatches these suites to that same lab.
bash models/bgpd/malformed_packets/collect_c_coverage.sh --suite generated
```

The wrapper passes `--frr-local --lab-profile combined` to the main runner;
`frr_backend.py` provides the shared local-or-Docker CLI and log access.
Outside that wrapper, the existing Docker `frr-lab` observation backend is
still the default. `route_stateful.py` remains a compatibility entry point
that delegates to the main runner. `--limit 0` selects zero cases.

The combined lab uses a fourth, single-client neighbor for the earlier
packet/GR suites, two route advertisers, and an observing peer. It enables
GR for the GR suites; route-competition peers do not negotiate GR. Route
competition assumes equal weight/local-pref, no route policy/multipath,
IPv4 unicast, and `compare-routerid` for deterministic ties. The daemon runs
with `-Z`, without forwarding-plane checks. Combining GR with competing
routes in one state model, timer races after reconnect, additional address
families, and failure-trace minimization remain outside this draft.

Reports retain `summary`, `discrepancies`, and `stateful_results`, and add
`suite_metadata` for graph counts and source/traffic evidence. Dry runs and
coverage runs do not count as empirical passes; adapter/model failures still
fail those runs. Observation errors fail explicitly rather than appearing
as absent routes. Live observations use bounded convergence checks; this is
not a general liveness proof or a proof of the FRR C implementation.

The wrapper prints a unique `/tmp/frr-route-draft.*` directory and removes
its container on exit. Measurement mode saves `baseline.json`, `control.json`,
`report.json`, both raw lcov captures, and the per-file line/function delta.
It omits CLI observations and uses cumulative counters. This new common
baseline supersedes the earlier draft's single-advertiser-only comparison;
never add those different deltas together. Timing/startup activity can still
contribute hits. Branch summaries now read lcov's `BRH` field correctly.

## 🚀 Prerequisites

To replicate these tests on your machine, you must have the following installed:
- **Python 3.10+** (Required for CrossHair AST evaluation)
- **Docker** (Required to spin up the FRRouting container)
- **Z3 Theorem Prover** and **CrossHair** (`pip install crosshair-tool`)

---

## 🛠️ Installation & Setup

We have provided a fully automated setup script to deploy the exact FRR testing environment used in our verification.

```bash
# 1. Clone the repository and enter this directory
git clone https://github.com/Rishabh942/sonic-formal-infra.git
cd sonic-formal-infra/models/bgpd/malformed_packets

# 2. Run the automated Docker setup script
./setup_frr_container.sh
```

**What the setup script does:**
- Downloads the `quay.io/frrouting/frr:10.0.1` Docker image.
- Spins up a container named `frr-lab` and exposes BGP port `179` to `1179` on your localhost.
- Automatically injects the necessary configuration to enable `bgpd` and configures it to peer with our Python fuzzer via AS 65002. (Note: `setup_frr_legacy.sh` is provided for FRR v7.5.0, but `setup_frr_container.sh` includes `disable-connected-check` and `ebgp-multihop 255` configurations required for the latest FRR versions to successfully accept fuzzed eBGP connections).

---

## 🔬 Replicating the Results

The core of this module is split into two phases: **Generation** (Oracle Prediction) and **Execution** (Fuzzing).

### Phase 1: Generating the Formal Dictionaries (Optional)
*Note: We have pre-committed the generated dictionaries (`tests/attr_argdict_extended.txt` and `tests/attr_argdict_soft.txt`), so you can skip this step if you just want to run the fuzzer.*

If you want to re-run the Z3 solver to verify our mathematical constraints from scratch:
```bash
# 1. Generate the RFC 4271 (Strict Teardown) Suite:
crosshair watch generate_rfc4271_suite.py

# 2. Generate the RFC 7606 (Soft Fault) Suite:
crosshair watch generate_rfc7606_suite.py
```
This commands Z3 to analyze `bgp_oracle.py` and output every unique variable combination required to achieve 100% path coverage.

For the structural suites (AS_PATH / MP_REACH / OPEN capabilities), either seed them by grid enumeration (instant, offline):

```bash
PYTHONPATH=. python3 models/bgpd/malformed_packets/seed_structural_suites.py --max-per-class 80
```

or solve them symbolically:

```bash
crosshair watch models/bgpd/malformed_packets/generate_aspath_suite.py
crosshair watch models/bgpd/malformed_packets/generate_mpreach_suite.py
crosshair watch models/bgpd/malformed_packets/generate_opencap_suite.py
```

### Phase 2: Running the Master Fuzzer
To dynamically inject the mathematically synthesized payloads into the live FRR router and verify compliance, run the comprehensive fuzzer from the root of the repo:

```bash
cd ../../../ # Go back to sonic-formal-infra root

# Interactive menu:
PYTHONPATH=. python3 models/bgpd/malformed_packets/run_parity_fuzzer.py

# Or scripted - all suites, or a single one, with a bounded case count:
PYTHONPATH=. python3 models/bgpd/malformed_packets/run_parity_fuzzer.py --suite all
PYTHONPATH=. python3 models/bgpd/malformed_packets/run_parity_fuzzer.py --suite aspath --limit 50
PYTHONPATH=. python3 models/bgpd/malformed_packets/run_parity_fuzzer.py --suite grrestart
PYTHONPATH=. python3 models/bgpd/malformed_packets/run_parity_fuzzer.py --suite grstate --fail-on-deviation --out /tmp/grstate-live.json

# Offline sanity check (builds every packet + runs the oracle, no daemon):
PYTHONPATH=. python3 models/bgpd/malformed_packets/run_parity_fuzzer.py --suite all --dry-run
```

Suites: `legacy` (attribute dictionaries), `aspath`, `mpreach`, `opencap`, `routerefresh`, `grrestart`, `grstate`, `all`. `all_no_gr` is the measurement control.

The Graceful Restart suite has 29 directed cases. Its two valid capability
length classes are 2 bytes (helper only) and `2 + 4*n` bytes (AFI/SAFI
tuples); truncated or partial tuples exercise OPEN error handling. The live
runner additionally sends the four-byte IPv4 End-of-RIB UPDATE body after a
successful handshake. The setup scripts enable `bgp graceful-restart` so FRR
negotiates the feature during these tests. This suite checks parsing and
End-of-RIB acceptance; it does not simulate retained routes across a daemon
restart.

The `grstate` suite checks stale-route retention, selective refresh, F-bit
handling on reconnect, restart-time expiration, NOTIFICATION cleanup, and a
non-GR control. A live FRR 10.0.1 run passed all six scenarios. Coverage mode
sends the same wire traffic but skips `vtysh` assertions; use the normal live
run to establish behavior. `--fail-on-deviation` exits nonzero on a mismatch
or failed FRR connection. The JSON report retains the scenario's checks,
event order, and wire hex for reproducing a failure.

### Phase 3: Branch Coverage Verification
To measure which oracle branches the current corpus exercises, run:

```bash
cd ../../../ # Go back to sonic-formal-infra root
PYTHONPATH=. python3 -m models.bgpd.malformed_packets.testing.coverage
```

This will run all generated test cases against `bgp_oracle.py` and output a terminal coverage report.

### Phase 4: C Coverage on the Real Parser (gcov/lcov)

```bash
./models/bgpd/malformed_packets/setup_frr_coverage.sh     # builds FRR 10.0.1 with --enable-gcov
./models/bgpd/malformed_packets/collect_c_coverage.sh     # fuzzer + lcov capture + HTML
./models/bgpd/malformed_packets/collect_c_coverage.sh --suite grrestart --limit 29
```

Run `collect_c_coverage.sh --baseline` to record `coverage_baseline.json`; subsequent runs print the delta for lines/functions when the tracked file scope matches and write browsable HTML under `coverage_html_c/`.
For a comparable delta, use the same `--suite` and `--limit` and the same lab
configuration for baseline and follow-up runs. The committed baseline predates
this expansion and was collected under different harness behavior, so its
printed delta is not an isolated measure of the new GR cases.
For a controlled before/after measurement on one FRR build, run
`all_no_gr --limit 100`, save `/tmp/frr_target.info`, then run
`grstate --limit 6` and `grrestart --limit 29` and compare the captures with
`compare_c_coverage.py`. See [GR_C_COVERAGE_REPORT.md](GR_C_COVERAGE_REPORT.md)
for the measured result and exact commands, or [MEETING_BRIEF.md](MEETING_BRIEF.md)
for a one-page summary.

### 📊 Understanding the Output
The fuzzer runs in real-time, executing roughly 100 payloads per minute. It checks whether FRR responds with a strict `SESSION_RESET`, or correctly degrades the route via `Treat-as-Withdraw` / `AFI_SAFI_DISABLE`.

Upon completion, you will see a comprehensive parity report similar to this example:
```text
=======================================================================
                COMPREHENSIVE EMPIRICAL RESULTS SUMMARY                
=======================================================================
Total Tests Executed      : 2334

--- Test Categorization (By Expected Behavior) ---
Category                     |   Total |    PASS |    FAIL
-------------------------------------------------------
Valid Updates                |      22 |      20 |       2
Strict Teardown (RFC 4271)   |     110 |     110 |       0
Treat-as-Withdraw (RFC 7606) |    1719 |    1719 |       0
AFI/SAFI Disable (RFC 7606)  |       0 |       0 |       0
Attribute Discard (RFC 7606) |     483 |     483 |       0

--- Critical Metrics ---
Legitimate Route Installs : 503
Routes Illegally Installed: 0
FRR Parser Crashes        : 0
-----------------------------------------------------------------------
Unexpected Protocol Deviations: 2

=> VERDICT: 2 Protocol Deviations Found.
```

If the `RFC Compliance Deviations` counter increments, it means FRR's behavior deviates from strict RFC 7606 expectations (e.g., dropping the session instead of doing a Treat-As-Withdraw, or illegally installing a malformed optional attribute). The fuzzer will output the specific **Test IDs** (e.g., `V2-45`) so you can isolate and reproduce the exact broken payload. A detailed JSON file (`parity_report_comprehensive.json`) will also be generated containing the exact hex arguments used.

### Harness correctness invariants

These are load-bearing properties of the current engine; do not regress them:

1. **Wire/oracle sync** - payload bytes are padded/truncated to the declared
   attribute length before they hit either side, so FRR's parser consumes
   exactly what the oracle models. (Earlier revisions appended raw payloads,
   desynchronizing the parser and poisoning results.)
2. **Unique NLRI per case** - every test case sends its own `10.a.b.0/24`
   prefix, so RIB state never leaks between cases.
3. **Honest observation model** - observed behavior is classified first
   (`SESSION_RESET` / `INSTALLED` / `NOT_INSTALLED`) and compared against
   the RFC-permitted outcome set; it is never derived from the oracle
   verdict itself.
4. **4-byte ASN awareness** - our OPEN advertises AS4, so AS_PATH framing is
   judged with 4-byte ASN stride on every suite.
