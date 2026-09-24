"""Bounded RFC 4724 OPEN and End-of-RIB probes for the parity harness.

These cases target the capability-64 parser, including the two-byte header,
four-byte AFI/SAFI tuples, reserved flags, duplicates, and truncated tuples.
Each case starts a fresh BGP session. Successful sessions send the IPv4
End-of-RIB UPDATE, which exercises the receive side beyond OPEN parsing.
"""

import struct

from models.bgpd.malformed_packets.packet_builders import (
    build_graceful_restart_value, wrap_capability,
)


IPV4_UNICAST = (1, 1, 0)
IPV4_FORWARDING = (1, 1, 0x80)
IPV6_FORWARDING = (2, 1, 0x80)


def graceful_restart_cases():
    """Small directed corpus with boundary values and independent factors."""
    cases = []
    def add(name, **kwargs):
        cases.append({"name": name, "flags": 0, "time": 90,
                      "families": [IPV4_UNICAST], "trim": 0,
                      "duplicate": False, **kwargs})

    add("helper-only", families=[])
    add("ipv4-unicast")
    add("restart-state", flags=8)
    add("reserved-restart-flags", flags=7)
    add("restart-and-reserved", flags=15)
    add("forwarding-state", families=[IPV4_FORWARDING])
    add("reserved-family-flags", families=[(1, 1, 0x7f)])
    add("ipv4-ipv6", families=[IPV4_FORWARDING, IPV6_FORWARDING])
    add("unsupported-family", families=[(65535, 255, 0x80)])
    add("duplicate-family", families=[IPV4_UNICAST, IPV4_FORWARDING])
    add("duplicate-capability", duplicate=True)
    for restart_time in (0, 1, 4095):
        add(f"time-{restart_time}", time=restart_time)
    for cut in (1, 2, 3, 4, 5, 6):
        add(f"truncated-{cut}", trim=cut)
    for family in ([], [IPV4_UNICAST], [IPV4_UNICAST, IPV6_FORWARDING]):
        for extra in (1, 2, 3):
            add(f"partial-tuple-{len(family)}-{extra}", families=family,
                extra_len=extra)
    return cases


def build_graceful_restart_open(args):
    """Build the actual OPEN that is passed to both FRR and the oracle."""
    # Local import avoids a cycle with the runner, which owns OPEN framing.
    from models.bgpd.malformed_packets.run_parity_fuzzer import build_bgp_open

    value = build_graceful_restart_value(args["flags"], args["time"],
                                         args["families"])
    value += b'\x42' * args.get("extra_len", 0)
    if args["trim"]:
        value = value[:-args["trim"]]

    # Negotiate MP IPv4/IPv6 and AS4 on every case. GR is a separate optional
    # parameter, so a bad GR body cannot silently corrupt the other TLVs.
    opt = wrap_capability(bytes((1, 4, 0, 1, 0, 1)))
    opt += wrap_capability(bytes((1, 4, 0, 2, 0, 1)))
    opt += wrap_capability(bytes((65, 4)) + struct.pack('!I', 65002))
    gr = wrap_capability(bytes((64, len(value))) + value)
    opt += gr
    if args["duplicate"]:
        opt += gr
    return build_bgp_open(opt_params=opt)


IPV4_END_OF_RIB = b'\xff' * 16 + struct.pack('!HBHH', 23, 2, 0, 0)
