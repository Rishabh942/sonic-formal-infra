from typing import List
from dataclasses import dataclass
from enum import IntEnum

class ParseResult(IntEnum):
    VALID = 0
    SESSION_RESET = 1
    AFI_SAFI_DISABLE = 2
    TREAT_AS_WITHDRAW = 3
    ATTRIBUTE_DISCARD = 4
    IMPL_CHOICE = 5  # RFC allows flexible choice (e.g. Session Reset vs AFI/SAFI disable)

@dataclass
class BGPPathAttr:
    flags: int
    type_code: int
    length: int

def escalate(new_result: ParseResult, current_result: ParseResult) -> ParseResult:
    if new_result == ParseResult.SESSION_RESET:
        return ParseResult.SESSION_RESET
    elif new_result == ParseResult.AFI_SAFI_DISABLE and current_result not in (ParseResult.SESSION_RESET,):
        return ParseResult.AFI_SAFI_DISABLE
    elif new_result == ParseResult.TREAT_AS_WITHDRAW and current_result not in (ParseResult.SESSION_RESET, ParseResult.AFI_SAFI_DISABLE):
        return ParseResult.TREAT_AS_WITHDRAW
    elif new_result == ParseResult.ATTRIBUTE_DISCARD and current_result == ParseResult.VALID:
        return ParseResult.ATTRIBUTE_DISCARD
    elif new_result == ParseResult.IMPL_CHOICE and current_result not in (ParseResult.SESSION_RESET, ParseResult.AFI_SAFI_DISABLE, ParseResult.TREAT_AS_WITHDRAW):
        # IMPL_CHOICE is lower precedence than explicit error actions
        return ParseResult.IMPL_CHOICE
    return current_result

def parse_attributes(attrs: List[BGPPathAttr], is_ibgp: bool = False) -> ParseResult:
    """Simulates comprehensive FRR bgp_attr_parse() logical branches for RFC 4271/7606."""
    seen_origin = False
    seen_as_path = False
    seen_nexthop = False
    
    final_result = ParseResult.VALID
    
    # SMT-friendly duplicate check
    for i, attr in enumerate(attrs):
        is_duplicate = False
        for j in range(i):
            if attrs[j].type_code == attr.type_code:
                is_duplicate = True
                break
        
        if is_duplicate:
            # Under RFC 7606, duplicate MP_REACH/UNREACH (14, 15) MUST session reset.
            # Other duplicate attributes, including mandatory ones (1, 2, 3), should be ATTRIBUTE_DISCARD.
            if attr.type_code in (14, 15):
                final_result = escalate(ParseResult.SESSION_RESET, final_result)
            else:
                final_result = escalate(ParseResult.ATTRIBUTE_DISCARD, final_result)
            continue

        is_optional = (attr.flags & 0x80) != 0
        is_transitive = (attr.flags & 0x40) != 0

        if attr.type_code == 1: # ORIGIN
            seen_origin = True
            if is_optional or not is_transitive or attr.length != 1:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 2: # AS_PATH
            seen_as_path = True
            if is_optional or not is_transitive:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 3: # NEXT_HOP
            seen_nexthop = True
            if is_optional or not is_transitive or attr.length != 4:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 4: # MULTI_EXIT_DISC (MED)
            if not is_optional or is_transitive or attr.length != 4:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 5: # LOCAL_PREF
            if is_optional or not is_transitive or attr.length != 4:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
            elif not is_ibgp:
                # RFC 4271: If received from eBGP, it shall be ignored.
                pass
        elif attr.type_code == 6: # ATOMIC_AGGREGATE
            if is_optional or not is_transitive or attr.length != 0:
                final_result = escalate(ParseResult.ATTRIBUTE_DISCARD, final_result)
        elif attr.type_code == 7: # AGGREGATOR
            if not is_optional or not is_transitive or attr.length != 6:
                final_result = escalate(ParseResult.ATTRIBUTE_DISCARD, final_result)
        elif attr.type_code == 8: # COMMUNITY
            if not is_optional or not is_transitive or (attr.length % 4 != 0):
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 9: # ORIGINATOR_ID
            if not is_optional or is_transitive or attr.length != 4:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 10: # CLUSTER_LIST
            if not is_optional or is_transitive or (attr.length % 4 != 0):
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 14: # MP_REACH_NLRI
            if not is_optional or is_transitive:
                final_result = escalate(ParseResult.IMPL_CHOICE, final_result)
        elif attr.type_code == 15: # MP_UNREACH_NLRI
            if not is_optional or is_transitive:
                final_result = escalate(ParseResult.IMPL_CHOICE, final_result)
        elif attr.type_code == 16: # EXTENDED_COMMUNITIES
            if not is_optional or not is_transitive or (attr.length % 8 != 0):
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 17: # AS4_PATH
            if not is_optional or not is_transitive:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 18: # AS4_AGGREGATOR
            if not is_optional or not is_transitive or attr.length != 8:
                final_result = escalate(ParseResult.ATTRIBUTE_DISCARD, final_result)
        elif attr.type_code == 22: # PMSI_TUNNEL
            if not is_optional or not is_transitive:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 32: # LARGE_COMMUNITY
            if not is_optional or not is_transitive:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        elif attr.type_code == 128: # ATTR_SET (RFC 6368)
            if not is_optional:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
            elif not is_transitive:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
        else:
            # Unknown attribute handling (RFC 7606 revised from RFC 4271)
            if not is_optional:
                final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
            elif not is_transitive:
                final_result = escalate(ParseResult.ATTRIBUTE_DISCARD, final_result)
            else:
                # If it is optional and transitive, it's just forwarded to peers.
                # We don't discard or treat as withdraw. Safe to ignore.
                pass

    # Validate that mandatory attributes exist (RFC 7606)
    if not seen_origin or not seen_as_path or not seen_nexthop:
        final_result = escalate(ParseResult.TREAT_AS_WITHDRAW, final_result)
    else:
        # All mandatory attributes exist. No action needed.
        pass
        
    return final_result
