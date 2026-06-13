import json
import os
import sys

# Path to the formatted test suite JSON
_HERE = os.path.dirname(os.path.abspath(__file__))
SUITE_PATH = os.path.join(_HERE, "tests", "bgp_test_suite_formatted.json")

try:
    with open(SUITE_PATH, "r") as f:
        suite = json.load(f)
except FileNotFoundError:
    print(f"Error: {SUITE_PATH} dataset not found. Run your generator and formatter first.")
    sys.exit(1)

print(f"Loaded database containing {len(suite)} generated test vectors.")
user_input = input("Enter the Test ID number you want to inspect: ").strip()

try:
    target_id = int(user_input)
except ValueError:
    print("Error: Input must be a valid integer.")
    sys.exit(1)

# Search the array for the matching test id dict object
target_case = next((tc for tc in suite if tc["test_id"] == target_id), None)

if target_case:
    print(f"\n=========================================================================")
    print(f"=== TRACE ANALYSIS FOR TEST ID {target_case['test_id']} ===")
    print(f"Target Compliance Context: RFC {target_case['rfc_standard']}")
    print(f"=========================================================================")
    
    for step in target_case["sequence"]:
        print(f"  Step {step['step']}:")
        print(f"    Current State   : [{step['expected_state']}]")
        print(f"    Event Received  : {step['action_event']}")
        print(f"    Resulting State : [{step['resulting_state']}]")
        print(f"    Action Taken    : {step['action_taken']}")
        print("-" * 50)
    print("=========================================================================")
else:
    print(f"Error: Test ID {target_id} was not found inside the current test suite boundaries.")
