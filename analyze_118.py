import json

SUITE_PATH = "/Users/rishabh/Github/sonic-formal-infra/models/bgpd/malformed_packets/tests/bgp_test_suite_formatted.json"
bug_ids = [17, 23, 31, 51, 70, 80, 81, 82, 99, 101, 107, 115, 118, 123, 126, 137, 138, 141, 144, 154, 155, 157, 161, 163, 165, 174, 176, 177, 180, 186, 188, 189, 192, 200, 210, 214, 218, 223, 227, 240, 241, 243, 244, 245, 249, 254, 261, 268, 272, 274, 284, 288, 295, 302, 303, 304, 306, 307, 310, 312, 315, 317, 321, 323, 327, 329, 330, 331, 333, 334, 335, 337, 339, 346, 348, 355, 357, 361, 364, 368, 370, 373, 378, 381, 384, 388, 389, 392, 393, 398, 405, 408, 413, 419, 422, 423, 425, 426, 428, 430, 438, 440, 443, 447, 448, 449, 450, 451, 454, 456, 458, 459, 461, 462, 465, 469, 471, 472]

with open(SUITE_PATH, "r") as f:
    suite = json.load(f)

rfc_4271_count = 0
rfc_7606_count = 0

for target_id in bug_ids:
    target_case = next((tc for tc in suite if tc["test_id"] == target_id), None)
    if not target_case:
        continue
    
    rfc = str(target_case.get("rfc_standard", ""))
    if "4271" in rfc:
        rfc_4271_count += 1
    elif "7606" in rfc:
        rfc_7606_count += 1

print(f"Total POTENTIAL_RFC_BUGs: {len(bug_ids)}")
print(f"RFC 4271 Cases: {rfc_4271_count}")
print(f"RFC 7606 Cases: {rfc_7606_count}")
