# BGP Formal Verification Parity Fuzzer

This module provides a formal verification testing suite that mathematically proves whether an open-source BGP parser (FRRouting) complies with the error-handling specifications detailed in **RFC 4271 (BGP-4)** and **RFC 7606 (Revised Error Handling)**.

By leveraging an SMT solver (Z3 via CrossHair), we condensed the infinite space of malformed BGP Update payloads into a mathematically complete set of exact edge cases (Suites 1 & 2). We also included directed semantic fuzzing for Community attributes (Suite 3). This suite fires these payloads at a live FRR daemon and asserts that FRR's physical C-parser mimics our Python Oracle (RFC 7606).

## Core Architecture and File Explanations

In this repository, we construct a formal model that acts as a "source of truth", and then we compare the outputs of our model with a live implementation (e.g. FRRouting) by sending generated packets over a local socket.

How the pieces fit together for the **BGP Malformed Packets** project:
- **`bgp_oracle.py`**: The formal reference implementation (Oracle). It reads incoming BGP path attributes and models strict logical branching outlined by RFC 4271 and RFC 7606 (e.g., when to trigger a Session Reset vs Attribute Discard).
- **`run_parity_fuzzer.py`**: The engine driving the parity checks. It loads generated test dictionaries from `tests/`, connects over a socket to a live FRR daemon (e.g. `127.0.0.1:1179`), performs a BGP handshake, and ships the fuzzed packets. Finally, it observes if FRR crashed, tore down the session, or gracefully discarded attributes, comparing these live results precisely against the `bgp_oracle.py` expectations.
- **`testing/coverage.py`**: Wraps the execution of `run_parity_fuzzer.py` using Python's `coverage` tool configured for strict **branch coverage**. This ensures that generated test cases cover 100% of all possible `if/else` edges (both True and False paths) inside the `bgp_oracle.py` specification, validating the thoroughness of the fuzzer.

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

### Phase 2: Running the Master Fuzzer
To dynamically inject the mathematically synthesized payloads into the live FRR router and verify compliance, run the comprehensive fuzzer from the root of the repo:

```bash
cd ../../../ # Go back to sonic-formal-infra root
PYTHONPATH=. python3 models/bgpd/malformed_packets/run_parity_fuzzer.py
```

### Phase 3: Branch Coverage Verification
To prove that our fuzzing payloads rigorously exercise the logic inside the formal model, you can run the suite under strict branch coverage tracking. This ensures the fuzzer hits all possible True/False logical edges outlined by the RFCs:

```bash
cd ../../../ # Go back to sonic-formal-infra root
PYTHONPATH=. python3 -m models.bgpd.malformed_packets.testing.coverage
```

This will run all generated test cases against `bgp_oracle.py` and output a terminal coverage report.

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
Valid Updates                |      52 |      52 |       0
Strict Teardown (RFC 4271)   |    1120 |     860 |     260
Treat-as-Withdraw (RFC 7606) |     876 |     279 |     597
AFI/SAFI Disable (RFC 7606)  |       0 |       0 |       0
Attribute Discard (RFC 7606) |     286 |     286 |       0

--- Critical Metrics ---
Legitimate Route Installs : 306
Routes Illegally Installed: 92
FRR Parser Crashes        : 0
-----------------------------------------------------------------------
Unexpected Protocol Deviations: 857

=> VERDICT: 857 Protocol Deviations Found.
```

If the `RFC Compliance Deviations` counter increments, it means FRR's behavior deviates from strict RFC 7606 expectations (e.g., dropping the session instead of doing a Treat-As-Withdraw, or illegally installing a malformed optional attribute). The fuzzer will output the specific **Test IDs** (e.g., `V2-45`) so you can isolate and reproduce the exact broken payload. A detailed JSON file (`parity_report_comprehensive.json`) will also be generated containing the exact hex arguments used.
