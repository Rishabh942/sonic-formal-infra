"""Shared deterministic packet-structure builders.

Single source of truth used by BOTH sides of the parity engine:

* CrossHair generator entries (generate_*_suite.py) import these to build
  the same structure they feed to the oracle, so the symbolic verdict and
  the wire bytes can never diverge.
* run_parity_fuzzer.py imports them to construct the physical packets.

All builders are concrete-Python over small symbolic ints - cheap for Z3,
no test-case explosion: each suite explores a bounded structural space
instead of raw byte soup.
"""

import struct

from models.bgpd.malformed_packets.bgp_oracle import BGPPathAttr


def decode_update_attributes(packet):
    """Decode UPDATE framing back to oracle inputs without judging attributes.

    The adapter rejects truncated framing. Malformed attribute *values* are
    retained verbatim for parse_attributes to classify. Returns withdrawals,
    attributes, and announced NLRI as encoded, including empty EOR fields.
    """
    if (len(packet) < 23 or packet[:16] != b'\xff' * 16
            or int.from_bytes(packet[16:18], 'big') != len(packet)
            or packet[18] != 2):
        raise ValueError('invalid UPDATE framing')
    withdrawn_len = int.from_bytes(packet[19:21], 'big')
    offset = 21 + withdrawn_len
    if offset + 2 > len(packet):
        raise ValueError('truncated withdrawn-routes field')
    end = offset + 2 + int.from_bytes(packet[offset:offset + 2], 'big')
    if end > len(packet):
        raise ValueError('truncated path-attributes field')
    raw = packet[offset + 2:end]
    attrs = []
    while raw:
        if len(raw) < 3:
            raise ValueError('truncated attribute header')
        flags, code = raw[:2]
        header = 4 if flags & 0x10 else 3
        if len(raw) < header:
            raise ValueError('truncated extended attribute header')
        length = int.from_bytes(raw[2:header], 'big')
        if header + length > len(raw):
            raise ValueError('truncated attribute value')
        attrs.append(BGPPathAttr(flags, code, length, raw[header:header + length]))
        raw = raw[header + length:]
    return packet[21:offset], attrs, packet[end:]


def build_as4_path_attr(asn_4byte):
    """Shared companion attribute for symbolic generation and live encoding."""
    value = build_as_path_value(1, 1, 0, 0, asn_4byte, 0)
    return BGPPathAttr(0xC0, 17, len(value), value)

# Bounded AFI/SAFI universes for MP_* fuzzing (SMT-friendly small sets).
MP_AFIS = (0, 1, 2)            # 0 = invalid on purpose, 1=IPv4, 2=IPv6
MP_SAFIS = (0, 1, 2, 4, 128)   # 0 invalid, 1 unicast, 2 multicast, 4 mpls-vpn, 128 vpnv4
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
    4,    # Other capability code (outside this oracle's semantic checks)
    5,    # Capabilities Advertisement (obsolete, RFC 5492 §4.3)
    6,    # Multiple Routes to a Destination (obsolete)
    7,    # Extended Next Hop Encoding (RFC 5549)
    8,    # BGPsec (RFC 8205)
    9,    # Multiple Labels (RFC 8277)
    64,   # Graceful Restart (RFC 4724)
    65,   # 4-octet ASN (RFC 6793)
    69,   # FQDN? (historical draft; unknown-ish)
    70,   # Enhanced Route Refresh (RFC 7313)
    71,   # Long-lived Graceful Restart (draft)
    73,   # AddPath (RFC 7911)
    78,   # Hostname (draft-walton-bgp-hostname)
    79,   # BGP Role (RFC 9234)
    130,  # Prestandard SRv6 SAFI seen in the wild
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
        out = out[:-extra_len] if -extra_len < len(out) else b''
    return out


def _well_formed_nlri(afi: int, safi: int) -> bytes:
    """One parseable NLRI prefix for the (afi, safi) scope."""
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

    fill_nh=False truncates the nexthop field (framing error); when
    reserved_present is False the mandatory Reserved octet is omitted;
    nlri_wf selects empty NLRI vs one well-formed prefix for the scope."""
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


def build_graceful_restart_value(restart_flags: int, restart_time: int,
                                 families=()) -> bytes:
    """RFC 4724 capability 64: flags/time followed by four-byte AFI/SAFI tuples.

    Families are (afi, safi, flags). Reserved flag bits are preserved so the
    receiver's ignore behavior can be exercised, not filtered by the builder.
    """
    value = struct.pack('!H', ((restart_flags & 0xF) << 12) | (restart_time & 0xFFF))
    for afi, safi, flags in families:
        value += struct.pack('!HBB', afi, safi, flags)
    return value
