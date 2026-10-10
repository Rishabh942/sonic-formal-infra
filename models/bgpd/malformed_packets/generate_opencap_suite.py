"""Suite 6 - BGP OPEN capability fuzzing via CrossHair.

Drives RFC 5492 capability parsing on the daemon (a large, previously
untested chunk of C: bgp_open_capability / bgp_capability_parse). The
symbolic space is bounded: one or two capability TLVs with codes drawn
from a fixed realistic universe and lengths 0..6.

Each solved point becomes a dictionary for run_parity_fuzzer.py
(suite "opencap"); the runner crafts the OPEN message from it and expects
Established (VALID) vs NOTIFICATION (SESSION_RESET) per the oracle.

    crosshair watch models/bgpd/malformed_packets/generate_opencap_suite.py
"""

from models.bgpd.malformed_packets.bgp_oracle import parse_capabilities
from models.bgpd.malformed_packets.packet_builders import (
    build_capability_value,
    wrap_capability,
    CAP_CODES,
)


def test_open_capabilities(
    num_caps: int,
    code1_idx: int, len1: int, fill1: int,
    code2_idx: int, len2: int, fill2: int,
) -> str:
    """Entry point for CrossHair. Returns the oracle verdict name."""
    if num_caps not in (1, 2):
        return "INVALID_INPUTS"
    if not (0 <= code1_idx < len(CAP_CODES)) or not (0 <= code2_idx < len(CAP_CODES)):
        return "INVALID_INPUTS"
    if not (0 <= len1 <= 6) or not (0 <= len2 <= 6):
        return "INVALID_INPUTS"
    if fill1 not in (0, 1) or fill2 not in (0, 1):
        return "INVALID_INPUTS"

    opt_params = b''
    opt_params += wrap_capability(
        build_capability_value(CAP_CODES[code1_idx], len1, bool(fill1)))
    if num_caps == 2:
        opt_params += wrap_capability(
            build_capability_value(CAP_CODES[code2_idx], len2, bool(fill2)))

    res = parse_capabilities(opt_params)
    return res.name
