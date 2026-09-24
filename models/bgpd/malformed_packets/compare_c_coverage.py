"""Compare two lcov captures and show C lines/functions added by a suite.

Run the existing suites on a fresh coverage container, save
/tmp/frr_target.info, then run the new suite against the same container and
compare the saved capture with the new /tmp/frr_target.info.
"""

import argparse
from pathlib import Path


def read_hits(path):
    hits = {}
    for section in Path(path).read_text().split('end_of_record'):
        lines = section.splitlines()
        source = next((line[3:] for line in lines if line.startswith('SF:')),
                      None)
        if source is None:
            continue
        name = Path(source).name
        covered_lines = {
            int(parts[0]) for line in lines if line.startswith('DA:')
            for parts in [line[3:].split(',')] if int(parts[1]) > 0
        }
        covered_functions = {
            line[5:].split(',', 1)[1] for line in lines
            if line.startswith('FNDA:') and int(line[5:].split(',', 1)[0]) > 0
        }
        hits[name] = covered_lines, covered_functions
    return hits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', help='saved lcov .info before new suite')
    parser.add_argument('after', help='lcov .info after new suite')
    args = parser.parse_args()
    before = read_hits(args.before)
    after = read_hits(args.after)
    added_lines = added_functions = 0
    for name in sorted(after):
        old_lines, old_functions = before.get(name, (set(), set()))
        new_lines, new_functions = after[name]
        lines = sorted(new_lines - old_lines)
        functions = sorted(new_functions - old_functions)
        added_lines += len(lines)
        added_functions += len(functions)
        print(f'{name}: +{len(lines)} lines, +{len(functions)} functions')
        if functions:
            print('  functions:', ', '.join(functions))
        if lines:
            print('  lines:', ', '.join(map(str, lines)))
    print(f'TOTAL: +{added_lines} lines, +{added_functions} functions')


if __name__ == '__main__':
    main()
