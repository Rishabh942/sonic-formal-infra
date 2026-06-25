import json

with open("models/bgpd/malformed_packets/parity_report_soft.json", "r") as f:
    deviations = json.load(f)

print(f"Total Deviations: {len(deviations)}")

# Group by reason
groups = {}
for dev in deviations:
    args = dev["payload_args"]
    flags1 = args.get("flags1", 0)
    len1 = args.get("len1", 0)
    flags4 = args.get("flags4", 0)
    type4 = args.get("type4", 0)
    len4 = args.get("len4", 0)
    
    # Check flags4 Optional bit
    opt_bit = bool(flags4 & 0x80)
    trans_bit = bool(flags4 & 0x40)
    
    key = (type4, opt_bit, trans_bit)
    if key not in groups:
        groups[key] = {"count": 0, "sample": dev}
    groups[key]["count"] += 1

print("\nGroups by (type4, optional_bit, transitive_bit):")
for k, v in groups.items():
    print(f"Type: {k[0]}, Optional: {k[1]}, Transitive: {k[2]} -> Count: {v['count']}")
    print(f"  Sample: {v['sample']['rfc_expected']} vs {v['sample']['frr_actual']}")

