"""Shared attribute header and payload framing for core replay."""

import struct

from models.bgpd.malformed_packets.bgp_oracle import BGPPathAttr


def build_as_path_value(seg1_type: int, seg1_count: int,
                        seg2_type: int, seg2_count: int,
                        extra_len: int = 0) -> bytes:
    """Build a four-byte-ASN AS_PATH from two bounded segments.

    Type zero omits a segment. Nonzero types are kept on the wire so the
    oracle and FRR can judge malformed types and counts. A length adjustment
    changes the attribute value, not its enclosing UPDATE framing.
    """
    out = bytearray()
    asn = (65002).to_bytes(4, 'big')
    for seg_type, count in ((seg1_type, seg1_count), (seg2_type, seg2_count)):
        if seg_type:
            out.extend((seg_type, count))
            out.extend(asn * count)
    if extra_len > 0:
        out.extend(b'\x00' * extra_len)
    elif extra_len < 0:
        del out[max(0, len(out) + extra_len):]
    return bytes(out)


def build_as4_path_attr() -> BGPPathAttr:
    """Optional transitive AS4_PATH companion used by model and replay."""
    value = build_as_path_value(2, 1, 0, 0)
    return BGPPathAttr(0xC0, 17, len(value), value)

def encode_attr(flags: int, type_code: int, length: int) -> bytes:
    """Attribute header honoring the Extended Length flag (RFC 4271 §4.3)."""
    hdr = struct.pack('!BB', flags, type_code)
    if flags & 0x10:
        hdr += struct.pack('!H', length)
    else:
        hdr += struct.pack('!B', length)
    return hdr


def normalize_payload(payload_hex: str, declared_len: int) -> bytes:
    """Make the wire self-consistent with the declared attribute length.

    The legacy harness appended raw payload bytes regardless of `len`,
    desynchronizing FRR's parser (it consumed the following attributes as
    payload). The oracle must see exactly what FRR reads: pad short
    payloads with zeros, truncate long ones."""
    raw = bytes.fromhex(payload_hex)
    if len(raw) < declared_len:
        raw = raw + b'\x00' * (declared_len - len(raw))
    return raw[:declared_len]
