"""Check bounded AS_PATH rules and reproduce the saved replay cases.

All 5^4 * 2 * 7 input points are checked. The saved cases are a deterministic
sample of distinct wire/verdict pairs, not the whole bounded space.
"""

import argparse
from itertools import product
from pathlib import Path

from models.bgpd.malformed_packets.generate_aspath_suite import test_as_path_structure
from models.bgpd.malformed_packets.run_parity_fuzzer import (
    build_aspath_update, eval_aspath, validate_update_attributes,
)


CORPUS = Path(__file__).parent / 'tests' / 'aspath_argdict.txt'


def build_corpus(max_per_verdict=80):
    if max_per_verdict < 1:
        raise ValueError('max_per_verdict must be positive')
    distinct = []
    seen = set()
    without_companion = {}
    checked = 0
    for s1t, s1c, s2t, s2c, companion, adjustment in product(
            range(5), range(5), range(5), range(5), (0, 1), range(-3, 4)):
        args = dict(seg1_type=s1t, seg1_count=s1c,
                    seg2_type=s2t, seg2_count=s2c,
                    with_as4_path=companion, extra_len=adjustment)
        verdict = test_as_path_structure(**args)
        if adjustment == 0:
            # An independent, bounded RFC 7606 framing/first-AS condition.
            segments = [(t, c) for t, c in ((s1t, s1c), (s2t, s2c)) if t]
            valid = (bool(segments) and segments[0][0] == 2
                     and all(t in (1, 2) and c > 0 for t, c in segments))
            expected = ('TREAT_AS_WITHDRAW' if not valid else
                        'ATTRIBUTE_DISCARD' if companion else 'VALID')
            if verdict != expected:
                raise AssertionError(f'RFC AS_PATH rule mismatch: {args}')
        key_without_companion = (s1t, s1c, s2t, s2c, adjustment)
        if companion:
            base = without_companion[key_without_companion]
            expected = ('TREAT_AS_WITHDRAW' if base == 'TREAT_AS_WITHDRAW'
                        else 'ATTRIBUTE_DISCARD')
            if verdict != expected:
                raise AssertionError(f'AS4 companion rule mismatch: {args}')
        else:
            if verdict not in ('VALID', 'TREAT_AS_WITHDRAW'):
                raise AssertionError(f'unexpected base AS_PATH verdict: {args}')
            without_companion[key_without_companion] = verdict
        packet, attrs, _, _ = build_aspath_update(args, 1)
        validate_update_attributes(packet, attrs)
        if eval_aspath(attrs, args).name != verdict:
            raise AssertionError(f'generator/wire oracle disagreement: {args}')
        checked += 1
        key = (packet, verdict)
        if key not in seen:
            seen.add(key)
            distinct.append((args, verdict))

    classes = {}
    for index, (_, verdict) in enumerate(distinct):
        classes.setdefault(verdict, []).append(index)
    selected = set()
    for indices in classes.values():
        count = min(max_per_verdict, len(indices))
        selected.update(indices[int(i * len(indices) / count)] for i in range(count))
        selected.add(indices[-1])
    cases = [distinct[i][0] for i in sorted(selected)]
    return checked, len(distinct), cases


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true',
                        help='replace the saved corpus; default checks it')
    parser.add_argument('--max-per-verdict', type=int, default=80)
    args = parser.parse_args(argv)
    checked, distinct, cases = build_corpus(args.max_per_verdict)
    data = ''.join(f'{case!r}\n' for case in cases)
    if args.write:
        CORPUS.write_text(data)
    elif not CORPUS.exists() or CORPUS.read_text() != data:
        parser.exit(1, 'saved AS_PATH corpus differs; run with --write\n')
    print(f'checked {checked} bounded inputs; {distinct} distinct wire/verdict '
          f'pairs; {len(cases)} saved cases')


if __name__ == '__main__':
    main()
