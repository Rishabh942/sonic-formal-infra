"""Require malformed UPDATEs to withdraw a route already installed for the same prefix."""

import argparse
from collections import OrderedDict
import json
from pathlib import Path
import time

from models.bgpd.malformed_packets import run_parity_fuzzer as replay


GOOD_ASPATH = dict(seg1_type=2, seg1_count=1, seg2_type=0, seg2_count=0,
                   with_as4_path=0, extra_len=0)


def distinct_withdrawal_cases():
    """Use emitted attribute bytes to avoid repeating identical mutations."""
    cases = OrderedDict()
    for suite, name in replay.CORPUS_FILES.items():
        raw = replay.load_argdict(replay.BASE_DIR / 'tests' / name)
        for args, version, slot in replay.expand_legacy_cases(raw):
            _, attrs, _, _ = replay.build_legacy_update(args, version, slot, 1)
            if replay.eval_legacy(attrs, args).name == 'TREAT_AS_WITHDRAW':
                signature = b''.join(replay._attr_wire(attr) for attr in attrs)
                cases.setdefault(signature, (suite, args, version, slot))
    raw = replay.load_argdict(replay.BASE_DIR / 'tests' / replay.ASPATH_FILE)
    for args in raw:
        _, attrs, _, _ = replay.build_aspath_update(args, 1)
        if replay.eval_aspath(attrs, args).name == 'TREAT_AS_WITHDRAW':
            signature = b''.join(replay._attr_wire(attr) for attr in attrs)
            cases.setdefault(signature, ('aspath', args, None, None))
    return list(cases.values())


def wait_for_route(prefix, present, container, timeout=2):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if replay.check_if_route_installed(prefix, retries=0,
                                           container=container) == present:
            return True
        time.sleep(0.05)
    return False


def run(container, host, port, out):
    cases = distinct_withdrawal_cases()
    if not cases:
        raise ValueError('no treat-as-withdraw cases in the saved corpus')
    failures = []
    session = replay.BgpSession(host, port)
    try:
        for index, (suite, args, version, slot) in enumerate(cases, 1):
            prefix_id = 52000 + index
            prefix = None
            try:
                session.ensure()
                good_packet, good_attrs, prefix, _ = replay.build_aspath_update(
                    GOOD_ASPATH, prefix_id)
                replay.validate_update_attributes(good_packet, good_attrs)
                notification, active = replay.send_update_and_monitor(
                    session.sock, good_packet)
                if notification or not active or not wait_for_route(prefix, True, container):
                    raise RuntimeError('valid setup route did not install')

                if suite == 'aspath':
                    bad_packet, bad_attrs, _, _ = replay.build_aspath_update(args, prefix_id)
                    verdict = replay.eval_aspath(bad_attrs, args)
                else:
                    bad_packet, bad_attrs, _, _ = replay.build_legacy_update(
                        args, version, slot, prefix_id)
                    verdict = replay.eval_legacy(bad_attrs, args)
                if verdict.name != 'TREAT_AS_WITHDRAW':
                    raise RuntimeError(f'unexpected oracle verdict: {verdict.name}')
                replay.validate_update_attributes(bad_packet, bad_attrs)
                notification, active = replay.send_update_and_monitor(
                    session.sock, bad_packet)
                if notification or not active or not wait_for_route(prefix, False, container):
                    raise RuntimeError(f'route did not withdraw; '
                                       f'notification={notification}, active={active}')
            except Exception as exc:
                failures.append(dict(index=index, suite=suite, prefix=prefix,
                                     args=args, error=str(exc)))
                session.invalidate()
            if index % 20 == 0 or index == len(cases):
                print(f'{index}/{len(cases)} distinct withdrawal cases checked; '
                      f'{len(failures)} failures', flush=True)
    finally:
        session.close()

    result = dict(total=len(cases), passed=len(cases) - len(failures),
                  failures=failures)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(f'Report: {out}')
    if failures:
        raise RuntimeError('strict withdrawal check failed; see the JSON report')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--container', default=replay.FRR_CONTAINER)
    parser.add_argument('--host', default=replay.DEFAULT_HOST)
    parser.add_argument('--port', type=int, default=replay.DEFAULT_PORT)
    parser.add_argument('--out', type=Path, default=replay.BASE_DIR / 'withdrawal_report_latest.json')
    args = parser.parse_args(argv)
    try:
        run(args.container, args.host, args.port, args.out)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.exit(1, f'error: {exc}\n')


if __name__ == '__main__':
    main()
