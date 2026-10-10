"""Suite 5 - MP_REACH_NLRI structural fuzzing via CrossHair.

Symbolic structure: AFI/SAFI drawn from small realistic universes,
nexthop length from {0,4,16,24,32}, truncation toggles for the nexthop and
the mandatory Reserved octet, plus a bounded NLRI tail. Each solved point
becomes one dictionary for run_parity_fuzzer.py (suite "mpreach"), which
sends a pure-MP UPDATE (no IPv4 NLRI, NEXT_HOP omitted - legal per
RFC 4760 §5).

    crosshair watch models/bgpd/malformed_packets/generate_mpreach_suite.py
"""

from models.bgpd.malformed_packets.bgp_oracle import parse_attributes, BGPPathAttr
from models.bgpd.malformed_packets.packet_builders import (
    build_mp_reach_value, MP_AFIS, MP_SAFIS, MP_NH_LENS, ATTR_FLAG_CLASSES,
)


def test_mp_reach_structure(
    afi: int, safi: int, nh_len: int,
    fill_nh: int, reserved_present: int,
    nlri_wf: int,
    flags: int,
) -> str:
    """Entry point for CrossHair. Returns the oracle verdict name."""
    if afi not in MP_AFIS or safi not in MP_SAFIS or nh_len not in MP_NH_LENS:
        return "INVALID_INPUTS"
    if flags not in ATTR_FLAG_CLASSES:
        return "INVALID_INPUTS"
    if fill_nh not in (0, 1) or reserved_present not in (0, 1):
        return "INVALID_INPUTS"
    if nlri_wf not in (0, 1):       # empty NLRI vs one well-formed prefix
        return "INVALID_INPUTS"

    value = build_mp_reach_value(afi, safi, nh_len,
                                 bool(fill_nh), bool(reserved_present),
                                 nlri_wf)

    attrs = [
        BGPPathAttr(64, 1, 1, b'\x00'),                       # ORIGIN
        BGPPathAttr(64, 2, 6, b'\x02\x01\x00\x00\xfd\xea'),   # AS_PATH (4-byte ASN)
        BGPPathAttr(flags, 14, len(value), value),            # fuzzed MP_REACH_NLRI
        # NEXT_HOP intentionally absent; has_ipv4_nlri=False below.
    ]
    res = parse_attributes(attrs,
                           asn_4byte=True,
                           has_ipv4_nlri=False)
    return res.name
