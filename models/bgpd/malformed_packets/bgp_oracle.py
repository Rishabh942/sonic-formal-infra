"""Executable RFC oracle for BGP UPDATE path-attribute parsing.

Reference model ("the spec") for the error handling a conforming BGP-4
speaker must apply to received path attributes:

* RFC 4271 - BGP-4 (wire format, mandatory attributes)
* RFC 7606 - Revised Error Handling (the five actions and per-attribute
  mapping; this is the backbone of the model)
* RFC 4760 - MP_REACH_NLRI / MP_UNREACH_NLRI structure
* RFC 6793 - 4-byte ASN (AS4_PATH / AS4_AGGREGATOR)
* RFC 5065 - AS_CONFED_* segment types
* RFC 6368 - ATTR_SET
* RFC 8092 - Large Communities
* RFC 9234 - OTC (Role / Only-To-Customer)

The five RFC 7606 actions are ranked by severity in ParseResult so that
combining several errors collapses into min() (most severe wins).

Design constraints (MBT): every check is SMT-friendly - bounded loops over
the attribute list, integer/bytes comparisons only, no unbounded parsing.
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import IntEnum

class ParseResult(IntEnum):
    # Numbered by severity (1 = most severe, 6 = least severe);
    # keep_most_severe() is therefore a min().
    # Conceptual mapping to FRR bgp_attr_parse_ret values noted inline.
    SESSION_RESET = 1      # RFC 4271 teardown / FRR: BGP_ATTR_PARSE_ERROR_NOTIFYPLS
    AFI_SAFI_DISABLE = 2   # RFC 7606 soft fault / FRR: BGP_ATTR_PARSE_ERROR (afisafi scope)
    TREAT_AS_WITHDRAW = 3  # RFC 7606 soft fault / FRR: BGP_ATTR_PARSE_WITHDRAW
    ATTRIBUTE_DISCARD = 4  # RFC 7606 soft fault / FRR: proceed, drop attribute
    IMPL_CHOICE = 5        # RFC leaves implementation choice open
    VALID = 6              # no error / FRR: BGP_ATTR_PARSE_PROCEED

class MP_NLRI_Result(IntEnum):
    SESSION_RESET = ParseResult.SESSION_RESET
    TREAT_AS_WITHDRAW = ParseResult.TREAT_AS_WITHDRAW

@dataclass(frozen=True)
class ImplChoice:
    """Resolution of points where the RFCs explicitly allow either of two
    actions (e.g. RFC 4760 flag errors on MP_REACH/MP_UNREACH)."""
    mp_nlri_choice: MP_NLRI_Result

@dataclass
class BGPPathAttr:
    flags: int
    type_code: int
    length: int
    value: Optional[bytes] = None

def keep_most_severe(new_result: ParseResult, current_result: ParseResult) -> ParseResult:
    """Keep the most severe of two results. Enum values are severity-ranked,
    so this is min()."""
    return min(new_result, current_result)

# ── Flag bits (RFC 4271 §4.3) ────────────────────────────────────────────────
FLAG_OPTIONAL = 0x80
FLAG_TRANSITIVE = 0x40
FLAG_EXTENDED_LEN = 0x10

def _attr_well_known(flags: int) -> bool:
    return not (flags & FLAG_OPTIONAL)

def _attr_transitive(flags: int) -> bool:
    return bool(flags & FLAG_TRANSITIVE)

# ── Structural helpers ───────────────────────────────────────────────────────

def scan_as_path(value: bytes, asn_size: int, allow_confed: bool,
                 enforce_first_as: Optional[int] = None) -> bool:
    """RFC 4271 §4.3 AS_PATH framing walk; asn_size is 2 or 4 bytes per ASN.

    Segment types: AS_SET(1), AS_SEQUENCE(2), AS_CONFED_SEQUENCE(3),
    AS_CONFED_SET(4). Confed segments from a non-confederation peer mean the
    route leaked out of a confed - treat-as-withdraw (RFC 5065 §4.2 /
    RFC 7606 §7.4)."""
    if enforce_first_as is not None:
        if (len(value) < 2 + asn_size or value[0] != 2 or value[1] == 0
                or int.from_bytes(value[2:2 + asn_size], 'big') != enforce_first_as):
            return False
    idx = 0
    while idx < len(value):
        if idx + 2 > len(value):
            return False
        seg_type = value[idx]
        seg_count = value[idx + 1]
        idx += 2
        if seg_type not in (1, 2, 3, 4):
            return False
        if seg_count == 0:
            return False          # §7.2: Path Segment Length of zero is malformed
        if seg_type in (3, 4) and not allow_confed:
            return False
        if idx + seg_count * asn_size > len(value):
            return False
        idx += seg_count * asn_size
    return True

def _mp_reach_structurally_valid(value: bytes) -> bool:
    """RFC 4760 §7 framing + per-(AFI, SAFI) nexthop-length semantics.

    Framing: AFI(2) SAFI(1) NH_Len(1) NextHop(NH_Len) Reserved(1) NLRI...
    Nexthop widths follow RFC 4760 §6.1, RFC 2545 (IPv6 dual-stack),
    RFC 4364 (VPN RD-prefixed), RFC 8277 (labeled unicast). An unrecognized
    AFI/SAFI combination or a width outside the table means the attribute
    is unusable for that scope => AFI/SAFI disable under RFC 7606 §7.6."""
    if len(value) < 4:
        return False
    afi = (value[0] << 8) | value[1]
    safi = value[2]
    nh_len = value[3]
    allowed = _MP_NH_LENGTHS.get((afi, safi))
    if allowed is None:
        return False
    if nh_len not in allowed:
        return False
    return len(value) >= 4 + nh_len + 1

_MP_NH_LENGTHS = {
    (1, 1): (4,),           # IPv4 unicast
    (1, 2): (4,),           # IPv4 multicast
    (2, 1): (16, 32),       # IPv6 unicast (+ link-local form, RFC 2545)
    (2, 2): (16, 32),
    (1, 128): (12,),        # VPNv4: 8-byte RD + 4
    (2, 128): (24,),        # VPNv6: 8-byte RD + 16
    (1, 4): (4, 12),        # labeled unicast (RFC 8277)
    (2, 4): (16,),
}

def _attr_set_structurally_valid(value: bytes) -> bool:
    """RFC 6368 §3 ATTR_SET framing: Flags(1) TypeCode(1) Length(2) AttrValue;
    the embedded Length must equal outer length minus 4."""
    if len(value) < 4:
        return False
    inner_len = (value[2] << 8) | value[3]
    return inner_len == len(value) - 4

# ── The model ────────────────────────────────────────────────────────────────

def parse_attributes(attrs: List[BGPPathAttr],
                     is_ibgp: bool = False,
                     impl_choice: Optional[ImplChoice] = None,
                     asn_4byte: bool = False,
                     has_ipv4_nlri: bool = True,
                     allow_confed: bool = False,
                     enforce_first_as: Optional[int] = None) -> ParseResult:
    """Model RFC 4271 §6.3 / RFC 7606 UPDATE attribute processing.

    asn_4byte       peer negotiated 4-byte ASN (RFC 6793); AS_PATH carries
                    4-byte ASNs.
    has_ipv4_nlri   UPDATE carries IPv4-unicast NLRI in the withdrawn-routes
                    or NLRI field; NEXT_HOP is then mandatory unless
                    MP_REACH provides it (RFC 4760 §5: when MP_REACH is used
                    for a route, NEXT_HOP SHALL be ignored / not required).
    allow_confed    peer is inside our confederation (AS_CONFED_* legal).
    enforce_first_as optional eBGP peer ASN policy; disabled for generic callers.

    value=None means "length-only test case" - value-level checks are
    skipped (mirrors the legacy argdict suites)."""
    seen_origin = False
    seen_as_path = False
    seen_next_hop = False
    seen_mp_reach = False

    final_result = ParseResult.VALID

    def fault(res: ParseResult) -> None:
        nonlocal final_result
        final_result = keep_most_severe(res, final_result)

    # RFC 7606 §3.g duplicate detection (O(n^2) scan keeps Z3 cheap).
    for i, attr in enumerate(attrs):
        is_duplicate = any(attrs[j].type_code == attr.type_code for j in range(i))

        if is_duplicate:
            if attr.type_code in (14, 15):
                # Duplicated MP_REACH/MP_UNREACH: NOTIFICATION Malformed
                # Attribute List (RFC 7606 §3.g).
                fault(ParseResult.SESSION_RESET)
            else:
                # §3.g: ALL other duplicated attributes - mandatory ones
                # included - have every occurrence after the first simply
                # discarded, and processing continues.
                pass
            continue



        is_optional = bool(attr.flags & FLAG_OPTIONAL)
        is_transitive = _attr_transitive(attr.flags)

        tc = attr.type_code
        val = attr.value

        if tc == 1:  # ORIGIN - well-known mandatory; malformed => withdraw (7606 §7.4)
            seen_origin = True
            if is_optional or not is_transitive or attr.length != 1:
                fault(ParseResult.TREAT_AS_WITHDRAW)
            elif val is not None and (len(val) < 1 or val[0] > 2):
                # Origin values: IGP(0) EGP(1) INCOMPLETE(2) - RFC 4271 §4.3.
                fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 2:  # AS_PATH - well-known mandatory; malformed => withdraw
            seen_as_path = True
            if is_optional or not is_transitive:
                fault(ParseResult.TREAT_AS_WITHDRAW)
            elif val is not None:
                if not scan_as_path(val, 4 if asn_4byte else 2, allow_confed,
                                    enforce_first_as):
                    fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 3:  # NEXT_HOP - well-known mandatory; malformed => withdraw
            seen_next_hop = True
            if is_optional or not is_transitive or attr.length != 4:
                fault(ParseResult.TREAT_AS_WITHDRAW)
            elif val is not None and len(val) == 4:
                if val == b'\x00\x00\x00\x00' or (val[0] & 0xF0) >= 0xE0:
                    # 0.0.0.0 or class D/E (multicast/reserved) next hop is
                    # unusable - RFC 4271 §6.3; FRR martian-checks these.
                    fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 4:  # MULTI_EXIT_DISC - optional non-transitive; withdraw (7606 §7.4)
            if not is_optional or is_transitive or attr.length != 4:
                fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 5:  # LOCAL_PREF (RFC 7606 §7.5)
            if not is_ibgp:
                # Received from an external neighbor: SHALL be discarded.
                fault(ParseResult.ATTRIBUTE_DISCARD)
            elif is_optional or not is_transitive or attr.length != 4:
                fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 6:  # ATOMIC_AGGREGATE - well-known discretionary; discard (7606 §7.4)
            if is_optional or not is_transitive or attr.length != 0:
                fault(ParseResult.ATTRIBUTE_DISCARD)
        elif tc == 7:  # AGGREGATOR (RFC 7606 §7.7)
            # Length depends on AS4 negotiation: 8 when the 4-octet ASN
            # capability is both advertised and received, else 6.
            expected_len = 8 if asn_4byte else 6
            if not is_optional or not is_transitive or attr.length != expected_len:
                fault(ParseResult.ATTRIBUTE_DISCARD)
        elif tc == 8:  # COMMUNITY (RFC 7606 §7.8)
            # §7.8 is explicit: malformed => treat-as-withdraw.
            if not is_optional or not is_transitive or attr.length == 0 or (attr.length % 4 != 0):
                fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 9:  # ORIGINATOR_ID (RFC 7606 §7.9)
            if not is_ibgp:
                # From an external neighbor: SHALL be discarded (§7.9).
                fault(ParseResult.ATTRIBUTE_DISCARD)
            elif not is_optional or is_transitive or attr.length != 4:
                fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 10:  # CLUSTER_LIST (RFC 7606 §7.10)
            if not is_ibgp:
                fault(ParseResult.ATTRIBUTE_DISCARD)   # §7.10 eBGP clause
            elif not is_optional or is_transitive or attr.length == 0 or (attr.length % 4 != 0):
                fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 14:  # MP_REACH_NLRI (RFC 4760)
            seen_mp_reach = True
            if not is_optional or is_transitive:
                # Flag violation: RFC 4760 era => session reset; revised
                # practice allows AFI/SAFI disable - impl choice (7606 §7.6).
                choice = ParseResult(impl_choice.mp_nlri_choice.value) if impl_choice else ParseResult.IMPL_CHOICE
                fault(choice)
            if val is not None and not _mp_reach_structurally_valid(val):
                # Framing damage scoped to the AFI/SAFI (RFC 7606 §7.6).
                fault(ParseResult.AFI_SAFI_DISABLE)
        elif tc == 15:  # MP_UNREACH_NLRI (RFC 4760)
            if not is_optional or is_transitive:
                choice = ParseResult(impl_choice.mp_nlri_choice.value) if impl_choice else ParseResult.IMPL_CHOICE
                fault(choice)
            if val is not None and len(val) < 3:
                # Minimum AFI(2)+SAFI(1) framing (RFC 4760 §7 / 7606 §7.6).
                fault(ParseResult.AFI_SAFI_DISABLE)
        elif tc == 16:  # EXTENDED_COMMUNITIES (RFC 7606 §7.14)
            # §7.14 is explicit: malformed => treat-as-withdraw.
            if not is_optional or not is_transitive or attr.length == 0 or (attr.length % 8 != 0):
                fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 25:  # IPv6-addr-specific ext-community (RFC 7606 §7.15)
            if not is_optional or is_transitive or attr.length == 0 or (attr.length % 20 != 0):
                fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 17:  # AS4_PATH (RFC 6793) - optional transitive
            if not is_optional or not is_transitive:
                fault(ParseResult.TREAT_AS_WITHDRAW)  # RFC 7606 §3.c
            elif val is not None:
                if not scan_as_path(val, 4, allow_confed):
                    # Malformed AS4_PATH: discard the attribute, keep the
                    # route (RFC 6793 §5 "treat as not present").
                    fault(ParseResult.ATTRIBUTE_DISCARD)
        elif tc == 18:  # AS4_AGGREGATOR (RFC 6793) - optional transitive; discard
            if not is_optional or not is_transitive or attr.length != 8:
                fault(ParseResult.ATTRIBUTE_DISCARD)
        elif tc == 22:  # PMSI_TUNNEL (RFC 6514) - optional transitive
            # Flags(1) Type(1) Label(3) => 5 octets minimum.
            if not is_optional or not is_transitive or attr.length < 5:
                fault(ParseResult.ATTRIBUTE_DISCARD)
        elif tc == 32:  # LARGE_COMMUNITIES (RFC 8092) - optional transitive
            # Sibling of Community/Ext-Community: malformed => withdraw.
            if not is_optional or not is_transitive or attr.length == 0 or (attr.length % 12 != 0):
                fault(ParseResult.TREAT_AS_WITHDRAW)
        elif tc == 33:  # OTC (RFC 9234) - optional transitive
            # Fixed 4-octet AS; malformed => RFC 7606 default: discard (§4).
            if not is_optional or not is_transitive or attr.length != 4:
                fault(ParseResult.ATTRIBUTE_DISCARD)
        elif tc == 128:  # ATTR_SET (RFC 6368, revised by RFC 7606 §7.16)
            if not is_optional or not is_transitive:
                fault(ParseResult.TREAT_AS_WITHDRAW)
            elif val is not None and not _attr_set_structurally_valid(val):
                fault(ParseResult.TREAT_AS_WITHDRAW)   # §7.16: withdraw
        else:
            # Unrecognized attributes (RFC 7606 §7.3, revised from 4271):
            # well-known => withdraw; optional non-transitive => discard;
            # optional transitive => keep & forward.
            # RFC 7606 §4: zero length is a syntax error => withdraw for unrecognized attrs.
            if attr.length == 0:
                fault(ParseResult.TREAT_AS_WITHDRAW)
            elif not is_optional:
                fault(ParseResult.TREAT_AS_WITHDRAW)
            elif not is_transitive:
                fault(ParseResult.ATTRIBUTE_DISCARD)
            else:
                pass

    # Missing mandatory attributes (RFC 7606 §7.4): treat-as-withdraw.
    # NEXT_HOP is only required when IPv4 NLRI is carried natively and
    # MP_REACH does not supply reachability for the route (RFC 4760 §5).
    need_next_hop = has_ipv4_nlri and not seen_mp_reach
    if not seen_origin or not seen_as_path or need_next_hop and not seen_next_hop:
        fault(ParseResult.TREAT_AS_WITHDRAW)

    return final_result


# ── OPEN / capability model (RFC 5492) ───────────────────────────────────────

# Semantic body requirements for RECOGNIZED capabilities. RFC 5492 §5
# mandates graceful ignorance only for unknown codes; a recognized
# capability too short to carry its mandatory fields makes the whole OPEN
# malformed (OPEN Message Error, RFC 4271 §6.2). Minimums:
#   1  MP-BGP          (RFC 4760 §8): 4-octet records -> len >= 4, len % 4 == 0
#   64 GracefulRestart (RFC 4724 §3): 2 octets + zero or more 4-octet tuples
#   65 AS4             (RFC 6793 §4): exactly 4 octets
#   69 AddPath         (RFC 7911):    4-octet records -> len >= 4, len % 4 == 0
#   9  Role            (RFC 9234 §4): exactly 1 octet
_CAP_SEMANTIC_LEN = {
    1: lambda n: n >= 4 and n % 4 == 0,
    64: lambda n: n >= 2 and (n - 2) % 4 == 0,
    65: lambda n: n == 4,
    69: lambda n: n >= 4 and n % 4 == 0,
    9: lambda n: n == 1,
}

def parse_capabilities(opt_params: bytes) -> ParseResult:
    """Model OPEN optional-parameter processing (RFC 5492 §4).

    Framing rule: every optional parameter must fit inside the OPEN
    message; overrun => OPEN parse failure => session reset (RFC 4271 §4.2,
    §6.4). Unknown capability codes are ignored gracefully (RFC 5492 §5);
    recognized capabilities with impossible body lengths => session reset."""
    idx = 0
    while idx < len(opt_params):
        if idx + 2 > len(opt_params):
            return ParseResult.SESSION_RESET
        param_type = opt_params[idx]
        param_len = opt_params[idx + 1]
        idx += 2
        if param_type == 2:  # Capabilities Advertisement
            if idx + param_len > len(opt_params) or param_len < 2:
                return ParseResult.SESSION_RESET
            cap_end = idx + param_len
            cidx = idx
            while cidx < cap_end:
                if cidx + 2 > cap_end:
                    return ParseResult.SESSION_RESET
                cap_code = opt_params[cidx]
                cap_len = opt_params[cidx + 1]
                cidx += 2 + cap_len
                if cidx > cap_end:
                    return ParseResult.SESSION_RESET
                check = _CAP_SEMANTIC_LEN.get(cap_code)
                if check is not None and not check(cap_len):
                    return ParseResult.SESSION_RESET
            idx = cap_end
        else:
            if idx + param_len > len(opt_params):
                return ParseResult.SESSION_RESET
            idx += param_len
    return ParseResult.VALID
