import json
from pathlib import Path
def generate():
    cases = []
    # Enumerate this bounded AFI/SAFI grid (not all protocol values).
    for afi in [1, 2, 25, 16384]:
        for safi in [1, 2, 128, 133]:
            cases.append({"afi": afi, "safi": safi})
    with (Path(__file__).resolve().parent / 'tests' / 'routerefresh_argdict.txt').open('w') as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")
if __name__ == "__main__":
    generate()
