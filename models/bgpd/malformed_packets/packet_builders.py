"""Shared deterministic packet-structure builders.

Single source of truth used by BOTH sides of the parity engine:

* CrossHair generator entries (generate_*_suite.py) import these to build
  structure they feed to the oracle. Regression tests check that the runner
  decodes the same attributes from the emitted wire bytes.
* run_parity_fuzzer.py imports them to construct the physical packets.

All builders are concrete-Python over small symbolic ints - cheap for Z3,
no test-case explosion: each suite explores a bounded structural space
instead of raw byte soup.
"""

import struct

# Bounded AFI/SAFI universes for MP_* fuzzing (SMT-friendly small sets).
MP_AFIS = (0, 1, 2)            # 0 = invalid on purpose, 1=IPv4, 2=IPv6
MP_SAFIS = (0, 1, 2, 4, 128)   # 0 invalid, 1 unicast, 2 multicast, 4 labeled, 128 VPN
MP_NH_LENS = (0, 4, 16, 24, 32)

# Representative attribute-flag byte classes: the oracle (and FRR's flag
# checker) distinguish only Optional(0x80) x Transitive(0x40); Extended-
# Length(0x10) changes wire framing; Partial(0x20) is re-advertisement
# stress. Enumerating these 9 instead of all 256 values prevents explosion.
ATTR_FLAG_CLASSES = (0x00, 0x10, 0x40, 0x50, 0x80, 0x90, 0xC0, 0xD0, 0xF0)

# Capability codes exercised by the OPEN-capability suite (RFC 5492 + friends).
CAP_CODES = (
    1,    # MP-BGP (RFC 4760)
    2,    # Route Refresh (RFC 2918)
    3,    # Outbound Route Filtering (RFC 5291)
    4,    # Multiple routes to a destination (deprecated)
    5,    # Extended Next Hop Encoding (RFC 8950)
    6,    # Extended Message (RFC 8654)
    7,    # BGPsec (RFC 8205)
    8,    # Multiple Labels (RFC 8277)
    9,    # BGP Role (RFC 9234)
    64,   # Graceful Restart (RFC 4724), TLV framing only
    65,   # 4-octet ASN (RFC 6793)
    69,   # ADD-PATH (RFC 7911)
    70,   # Enhanced Route Refresh (RFC 7313)
    71,   # Long-lived Graceful Restart (RFC 9494), TLV framing only
    73,   # FQDN (draft-walton-bgp-hostname-capability)
    78,   # Edge Metadata (temporary registration)
    79,   # Unassigned
    130,  # Prestandard Outbound Route Filtering (deprecated)
    255,  # Unassigned / reserved edge
)


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


def build_as_path_value(seg1_type: int, seg1_count: int,
                        seg2_type: int, seg2_count: int,
                        asn_4byte: bool,
                        extra_len: int = 0) -> bytes:
    """Concrete AS_PATH value from bounded symbolic parameters.

    seg types: 0 => segment absent, else AS_SET(1)/AS_SEQUENCE(2)/
    AS_CONFED_SEQUENCE(3)/AS_CONFED_SET(4). extra_len pads (+) or truncates
    (-) the value so declared-length games stay in-band and parser-safe.

    ASNs are filled with our peer ASN 65002 - zero-filled ASNs would trip
    FRR's enforce-first-as check (leftmost AS must equal peer AS) before
    framing ever matters, masking the behavior under test."""
    asn_size = 4 if asn_4byte else 2
    asn = (b'\x00\x00\xfd\xea') if asn_4byte else b'\xfd\xea'
    out = b''
    for seg_type, count in ((seg1_type, seg1_count), (seg2_type, seg2_count)):
        if seg_type == 0:
            continue
        out += bytes((seg_type & 0xFF, count & 0xFF))
        out += asn * (count & 0xFF)
    if extra_len > 0:
        out += b'\x00' * extra_len
    elif extra_len < 0:
        out = out[:extra_len]
    return out


def _well_formed_nlri(afi: int, safi: int) -> bytes:
    """Representative NLRI tail; only unicast IP encoding is complete.

    Labeled/VPN tails are stress inputs, not validated route advertisements.
    The current MP oracle checks header/nexthop framing, not NLRI semantics.
    """
    rd = b'\x00\x02\x00\x00\xfd\xea\x00\x01'          # RD: ASN 65002, 1
    if afi == 2:
        v6 = bytes((64,)) + b'\x20\x01\x0d\xb8\x00\x00\x00\x00'   # 2001:db8::/64
        return rd + v6 if safi == 128 else v6
    v4 = bytes((24,)) + b'\x0a\x10\x01'               # 10.16.1.0/24
    return rd + v4 if safi == 128 else v4


def build_mp_reach_value(afi: int, safi: int, nh_len: int,
                         fill_nh: bool, reserved_present: bool,
                         nlri_wf: int) -> bytes:
    """RFC 4760 §7 MP_REACH_NLRI value from bounded symbolic parameters.

    fill_nh=False omits nexthop bytes (later fields can be consumed as data); when
    reserved_present is False the mandatory Reserved octet is omitted;
    nlri_wf selects empty NLRI vs a representative tail for the scope."""
    out = struct.pack('!HBB', afi & 0xFFFF, safi & 0xFF, nh_len & 0xFF)
    out += (b'\x11' * nh_len) if fill_nh else b''
    if reserved_present:
        out += b'\x00'
    if nlri_wf:
        out += _well_formed_nlri(afi, safi)
    return out


def build_capability_value(code: int, cap_len: int, fill: bool) -> bytes:
    """One RFC 5492 capability TLV body (without the 2-byte opt-param
    wrapper): Code(1) Len(1) Value(Len). fill=False truncates the value."""
    body = (b'\x42' * cap_len) if fill else b''
    return bytes((code & 0xFF, cap_len & 0xFF)) + body


def wrap_capability(cap_body: bytes) -> bytes:
    """Wrap a capability body into an optional parameter (type 2)."""
    return struct.pack('!BB', 2, len(cap_body)) + cap_body
