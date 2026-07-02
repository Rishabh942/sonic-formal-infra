# BGP Formal Verification Parity Fuzzer

This module provides a formal verification testing suite that mathematically proves whether an open-source BGP parser (FRRouting) complies with the error-handling specifications detailed in **RFC 4271 (BGP-4)** and **RFC 7606 (Revised Error Handling)**.

By leveraging an SMT solver (Z3 via CrossHair), we condensed the infinite space of malformed BGP Update payloads into a mathematically complete set of 1,041 exact edge cases. This suite fires those payloads at a live FRR daemon and asserts that FRR's physical C-parser perfectly mimics our mathematical Python Oracle.

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
- Downloads the `frrouting/frr:latest` Docker image.
- Spins up a container named `frr-lab` and exposes BGP port `179` to `1179` on your localhost.
- Automatically injects the necessary configuration to enable `bgpd` and configures it to peer with our Python fuzzer via AS 65002.

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
To dynamically inject the 1,041 mathematically synthesized payloads into the live FRR router and verify compliance, run the comprehensive fuzzer from the root of the repo:

```bash
cd ../../../ # Go back to sonic-formal-infra root
PYTHONPATH=. python3 models/bgpd/malformed_packets/run_parity_fuzzer.py
```

### 📊 Understanding the Output
The fuzzer runs in real-time, executing roughly 100 payloads per minute. It checks whether FRR responds with a strict `SESSION_RESET`, or correctly degrades the route via `Treat-as-Withdraw` / `AFI_SAFI_DISABLE`.

Upon completion, you will see a comprehensive parity report:
```text
==================================================
      COMPREHENSIVE EMPIRICAL RESULTS SUMMARY     
==================================================
Total Tests Executed      : 1041

--- Strict Enforcement (RFC 4271) ---
[PASS] Session Teardowns  : 520

--- Graceful Degradation (RFC 7606) ---
[PASS] Soft Faults        : 472
[PASS] AFI/SAFI Disable   : 49
[PASS] Attribute Discard  : 0

--- Critical Metrics ---
Routes Illegally Installed: 0
FRR Parser Crashes        : 0
--------------------------------------------------
RFC Compliance Deviations : 0

=> VERDICT: 100% PERFECT PARITY. FRR complies with all RFC bounds.
```

If a future update to FRR introduces a parser bug or a non-compliant behavior, the `RFC Compliance Deviations` counter will increment, and the fuzzer will output the specific **Test IDs** (e.g., `V2-45`) so you can isolate and reproduce the exact broken payload. A detailed JSON file (`parity_report_comprehensive.json`) will also be generated containing the exact hex arguments used.
