import json
def generate():
    cases = []
    # Exhaustive AFI/SAFI fuzzing for Route Refresh
    for afi in [1, 2, 25, 16384]:
        for safi in [1, 2, 128, 133]:
            cases.append({"afi": afi, "safi": safi})
    with open("models/bgpd/malformed_packets/tests/routerefresh_argdict.txt", "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")
if __name__ == "__main__":
    generate()
