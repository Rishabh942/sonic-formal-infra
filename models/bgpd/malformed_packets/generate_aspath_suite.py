"""Suite 4 - AS_PATH structural fuzzing via CrossHair.

Explores a *bounded structural* space instead of raw bytes: two segments
(type/count each), 2- vs 4-byte ASN mode, optional AS4_PATH companion, and
a small declared-length perturbation. Each solved point yields one
dictionary consumed by run_parity_fuzzer.py (suite "aspath").

    crosshair watch models/bgpd/malformed_packets/generate_aspath_suite.py
"""

from models.bgpd.malformed_packets.bgp_oracle import parse_attributes, BGPPathAttr
from models.bgpd.malformed_packets.packet_builders import build_as_path_value


def test_as_path_structure(
    seg1_type: int, seg1_count: int,
    seg2_type: int, seg2_count: int,
    asn_4byte: int,
    with_as4_path: int,
    extra_len: int,
) -> str:
    """Entry point for CrossHair. Returns the oracle verdict name."""
    if not (0 <= seg1_type <= 4 and 0 <= seg2_type <= 4):
        return "INVALID_INPUTS"
    if not (0 <= seg1_count <= 4 and 0 <= seg2_count <= 4):
        return "INVALID_INPUTS"
    if asn_4byte not in (0, 1) or with_as4_path not in (0, 1):
        return "INVALID_INPUTS"
    if not (-3 <= extra_len <= 3):
        return "INVALID_INPUTS"

    is4 = bool(asn_4byte)
    value = build_as_path_value(seg1_type, seg1_count, seg2_type, seg2_count, is4, extra_len)

    attrs = [
        BGPPathAttr(64, 1, 1, b'\x00'),                       # ORIGIN
        BGPPathAttr(64, 2, len(value), value),                # fuzzed AS_PATH
        BGPPathAttr(64, 3, 4, b'\x01\x01\x01\x01'),           # NEXT_HOP
    ]
    if with_as4_path:
        # Well-formed AS4_PATH companion (RFC 6793 interplay).
        as4 = build_as_path_value(1, 1, 0, 0, True, 0)
        attrs.append(BGPPathAttr(192, 17, len(as4), as4))

    res = parse_attributes(attrs, asn_4byte=is4, enforce_first_as=65002)
    return res.name
