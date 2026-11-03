"""Shared attribute header and payload framing for core replay."""

import struct

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
