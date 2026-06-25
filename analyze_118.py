import json
import os

SUITE_PATH = "/Users/rishabh/Github/sonic-formal-infra/examples/bgp_malformed_packets/tests/bgp_test_suite_formatted.json"
bug_ids = [17, 23, 31, 51, 70, 80, 81, 82, 99, 101, 107, 115, 118, 123, 126, 137, 138, 141, 144, 154, 155, 157, 161, 163, 165, 174, 176, 177, 180, 186, 188, 189, 192, 200, 210, 214, 218, 223, 227, 240, 241, 243, 244, 245, 249, 254, 261, 268, 272, 274, 284, 288, 295, 302, 303, 304, 306, 307, 310, 312, 315, 317, 321, 323, 327, 329, 330, 331, 333, 334, 335, 337, 339, 346, 348, 355, 357, 361, 364, 368, 370, 373, 378, 381, 384, 388, 389, 392, 393, 398, 405, 408, 413, 419, 422, 423, 425, 426, 428, 430, 438, 440, 443, 447, 448, 449, 450, 451, 454, 456, 458, 459, 461, 462, 465, 469, 471, 472]

with open(SUITE_PATH, "r") as f:
    suite = json.load(f)

established_bugs = []
other_bugs = []

for target_id in bug_ids:
    target_case = next((tc for tc in suite if tc["test_id"] == target_id), None)
    if not target_case:
        continue
    
    events = [step.get("action_event", "") for step in target_case["sequence"]]
    
    has_open = "RCV_OPEN" in events
    tcp_idx = events.index("TCP_CONN_START") if "TCP_CONN_START" in events else -1
    open_idx = events.index("RCV_OPEN") if has_open else -1
    
    update_events = ["RCV_UPDATE_MISSING_MANDATORY", "RCV_UPDATE_BAD_LENGTH", "RCV_UPDATE_BAD_FLAGS", "RCV_VALID_UPDATE"]
    
    first_update_after_tcp = -1
    for i, event in enumerate(events):
        if i > tcp_idx and event in update_events:
            first_update_after_tcp = i
            break
            
    if first_update_after_tcp != -1 and (not has_open or first_update_after_tcp < open_idx):
        pass # premature
    elif has_open and first_update_after_tcp > open_idx:
        established_bugs.append(target_case)
    else:
        other_bugs.append(target_case)

def print_case(tc):
    print(f"Test ID {tc['test_id']}: {' -> '.join([s['action_event'] for s in tc['sequence']])}")

print("--- Sample Established Bugs ---")
for tc in established_bugs[:3]:
    print_case(tc)

print("\n--- Sample Other Edge Cases ---")
for tc in other_bugs[:3]:
    print_case(tc)
