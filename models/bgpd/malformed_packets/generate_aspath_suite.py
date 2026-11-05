"""Bounded AS_PATH/AS4_PATH oracle entry point for four-byte BGP sessions.

The same arguments are consumed by the replay builder. Two-byte sessions
require a separately negotiated peer and are outside this release cut.
"""

from models.bgpd.malformed_packets.bgp_oracle import BGPPathAttr, parse_attributes
from models.bgpd.malformed_packets.packet_builders import (
    build_as4_path_attr, build_as_path_value,
)


def test_as_path_structure(seg1_type: int, seg1_count: int,
                           seg2_type: int, seg2_count: int,
                           with_as4_path: int, extra_len: int) -> str:
    """Return the modeled outcome for a bounded structural AS_PATH input."""
    if not (0 <= seg1_type <= 4 and 0 <= seg2_type <= 4
            and 0 <= seg1_count <= 4 and 0 <= seg2_count <= 4
            and with_as4_path in (0, 1) and -3 <= extra_len <= 3):
        return "INVALID_INPUTS"

    value = build_as_path_value(seg1_type, seg1_count,
                                seg2_type, seg2_count, extra_len)
    attrs = [BGPPathAttr(64, 1, 1, b'\x00'),
             BGPPathAttr(64, 2, len(value), value),
             BGPPathAttr(64, 3, 4, b'\x01\x01\x01\x01')]
    if with_as4_path:
        attrs.append(build_as4_path_attr())
    return parse_attributes(attrs, asn_4byte=True,
                            enforce_first_as=65002).name
