"""Summarize the collector's lcov output and compare compatible baselines."""
import argparse
import json
from pathlib import Path

TARGETS = {'bgp_attr.c', 'bgp_open.c', 'bgp_packet.c', 'bgp_route.c'}


def read_lcov(text):
    rows = []
    fields = {'LF': 'lf', 'LH': 'lh', 'BRF': 'bf', 'BRH': 'bh', 'FNF': 'fn', 'FNH': 'fh'}
    for record in text.split('end_of_record'):
        row = {}
        for line in record.splitlines():
            key, sep, value = line.partition(':')
            if key == 'SF':
                row['name'] = Path(value).name
            elif key in fields:
                row[fields[key]] = int(value)
        if row:
            if set(row) != {'name', *fields.values()}:
                raise ValueError('lcov record is missing line, branch or function totals')
            for hit, found in (('lh', 'lf'), ('bh', 'bf'), ('fh', 'fn')):
                if not 0 <= row[hit] <= row[found]:
                    raise ValueError(f"invalid lcov counts for {row['name']}")
            rows.append(row)
    if len(rows) != 4 or {r['name'] for r in rows} != TARGETS:
        raise ValueError('lcov capture must contain each of the four target files once')
    if any(r['lf'] == 0 or r['fn'] == 0 for r in rows):
        raise ValueError('lcov capture has empty line/function denominators')
    return sorted(rows, key=lambda r: r['name'])


def signature(snapshot):
    return (snapshot['frr_revision'], snapshot['limit'],
            [(r['name'], r['lf'], r['bf'], r['fn']) for r in snapshot['files']])


def percent(hit, total):
    return 100 * hit / total if total else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--info', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--parity', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args(argv)
    try:
        run = json.loads(args.parity.read_text())['summary']
        if (not run['coverage_mode'] or run['dry_run'] or run['connection_failures']
                or run['observation_errors'] or run['total'] == 0):
            raise ValueError('coverage injection report is not a successful live coverage run')
        rows = read_lcov(args.info.read_text())
        total = {key: sum(r[key] for r in rows) for key in ('lf', 'lh', 'bf', 'bh', 'fn', 'fh')}
        snap = {'frr_revision': args.revision, 'mode': 'coverage-only',
                'limit': run['run_context']['limit'], 'corpus': run['corpus'],
                'files': rows, 'total': total}
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / 'summary.json').write_text(json.dumps(snap, indent=2) + '\n')
        for row in [*rows, {'name': 'TOTAL', **total}]:
            print(f"{row['name']:<16} lines {row['lh']}/{row['lf']} ({percent(row['lh'], row['lf']):.1f}%)  "
                  f"branches {row['bh']}/{row['bf']} ({percent(row['bh'], row['bf']):.1f}%)  "
                  f"functions {row['fh']}/{row['fn']} ({percent(row['fh'], row['fn']):.1f}%)")
        baseline = args.out / 'baseline.json'
        if args.baseline:
            baseline.write_text(json.dumps(snap, indent=2) + '\n')
            print(f'Baseline saved: {baseline}')
        elif baseline.exists():
            old = json.loads(baseline.read_text())
            if signature(old) != signature(snap):
                raise ValueError('baseline build, case limit or denominators differ; no comparable coverage delta')
            changes = []
            for label, hit, found in (('lines', 'lh', 'lf'), ('branches', 'bh', 'bf'), ('functions', 'fh', 'fn')):
                delta = percent(total[hit], total[found]) - percent(old['total'][hit], old['total'][found])
                changes.append(f'{label} {delta:+.2f}pp')
            print('Change from baseline: ' + ', '.join(changes))
        else:
            print('No baseline. Use --baseline to save one for the next run.')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'error: {exc}\n')


if __name__ == '__main__':
    main()
