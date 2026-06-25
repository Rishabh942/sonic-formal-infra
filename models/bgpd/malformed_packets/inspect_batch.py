import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
SUITE_PATH = os.path.join(_HERE, "tests", "bgp_test_suite_formatted.json")

with open(SUITE_PATH, "r") as f:
    suite = json.load(f)

for target_id in [17, 23, 31, 51, 70]:
    target_case = next((tc for tc in suite if tc["test_id"] == target_id), None)
    if target_case:
        print(f"\n=========================================================================")
        print(f"=== TRACE ANALYSIS FOR TEST ID {target_case['test_id']} ===")
        print(f"Target Compliance Context: {target_case.get('rfc_standard', 'Unknown')}")
        print(f"=========================================================================")
        for step in target_case["sequence"]:
            print(f"  Step {step.get('step', '?')}:")
            print(f"    Current State   : [{step.get('expected_state', '?')}]")
            print(f"    Event Received  : {step.get('action_event', '?')}")
            print(f"    Resulting State : [{step.get('resulting_state', '?')}]")
            print(f"    Action Taken    : {step.get('action_taken', '?')}")
            print("-" * 50)
