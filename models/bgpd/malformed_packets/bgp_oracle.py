from typing import List
from dataclasses import dataclass
from enum import IntEnum

class ParseResult(IntEnum):
    VALID = 0
    SESSION_RESET = 1
    AFI_SAFI_DISABLE = 2
    TREAT_AS_WITHDRAW = 3
    ATTRIBUTE_DISCARD = 4

@dataclass
class BGPPathAttr:
    flags: int
    type_code: int
    length: int

def parse_attributes(attrs: List[BGPPathAttr]) -> ParseResult:
    """Simulates comprehensive FRR bgp_attr_parse() logical branches for RFC 4271/7606."""
    seen_origin = False
    seen_as_path = False
    seen_nexthop = False
    
    final_result = ParseResult.VALID
    
    def escalate(new_result: ParseResult):
        nonlocal final_result
        if new_result == ParseResult.SESSION_RESET:
            final_result = ParseResult.SESSION_RESET
        elif new_result == ParseResult.AFI_SAFI_DISABLE and final_result not in (ParseResult.SESSION_RESET,):
            final_result = ParseResult.AFI_SAFI_DISABLE
        elif new_result == ParseResult.TREAT_AS_WITHDRAW and final_result not in (ParseResult.SESSION_RESET, ParseResult.AFI_SAFI_DISABLE):
            final_result = ParseResult.TREAT_AS_WITHDRAW
        elif new_result == ParseResult.ATTRIBUTE_DISCARD and final_result == ParseResult.VALID:
            final_result = ParseResult.ATTRIBUTE_DISCARD

    # SMT-friendly duplicate check
    for i, attr in enumerate(attrs):
        is_duplicate = False
        for j in range(i):
            if attrs[j].type_code == attr.type_code:
                is_duplicate = True
                break
        
        if is_duplicate:
            # Duplicate mandatory attributes (1, 2, 3) and MP_REACH/UNREACH (14, 15) must session reset
            if attr.type_code in (1, 2, 3, 14, 15):
                escalate(ParseResult.SESSION_RESET)
            else:
                escalate(ParseResult.ATTRIBUTE_DISCARD)
            continue

        is_optional = (attr.flags & 0x80) != 0
        is_transitive = (attr.flags & 0x40) != 0

        if attr.type_code == 1:
            seen_origin = True
            if is_optional or not is_transitive or attr.length != 1:
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 2:
            seen_as_path = True
            if is_optional or not is_transitive:
                escalate(ParseResult.SESSION_RESET)
        elif attr.type_code == 3:
            seen_nexthop = True
            if is_optional or not is_transitive or attr.length != 4:
                escalate(ParseResult.SESSION_RESET)
        elif attr.type_code == 4:
            if not is_optional or is_transitive or attr.length != 4:
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 5:
            if is_optional or not is_transitive or attr.length != 4:
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 6:
            if is_optional or not is_transitive or attr.length != 0:
                escalate(ParseResult.ATTRIBUTE_DISCARD)
        elif attr.type_code == 7:
            if not is_optional or not is_transitive or attr.length != 6:
                escalate(ParseResult.ATTRIBUTE_DISCARD)
        elif attr.type_code == 8:
            if not is_optional or not is_transitive or (attr.length % 4 != 0):
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 9:
            if not is_optional or is_transitive or attr.length != 4:
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 10:
            if not is_optional or is_transitive or (attr.length % 4 != 0):
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 14:
            if not is_optional or is_transitive:
                escalate(ParseResult.SESSION_RESET)
        elif attr.type_code == 15:
            if not is_optional or is_transitive:
                escalate(ParseResult.SESSION_RESET)
        elif attr.type_code == 16:
            if not is_optional or not is_transitive or (attr.length % 8 != 0):
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 17:
            if not is_optional or not is_transitive:
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 18:
            if not is_optional or not is_transitive or attr.length != 8:
                escalate(ParseResult.ATTRIBUTE_DISCARD)
        elif attr.type_code == 22:
            if not is_optional or not is_transitive:
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 32:
            if not is_optional or not is_transitive:
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        elif attr.type_code == 128:
            if not is_optional:
                escalate(ParseResult.SESSION_RESET)
            elif not is_transitive:
                escalate(ParseResult.TREAT_AS_WITHDRAW)
        else:
            # Unknown attribute handling (RFC 7606 revised from RFC 4271)
            if not is_optional:
                escalate(ParseResult.SESSION_RESET)
            elif not is_transitive:
                escalate(ParseResult.ATTRIBUTE_DISCARD)

    # Validate that mandatory attributes exist (RFC 7606)
    if not seen_origin or not seen_as_path or not seen_nexthop:
        escalate(ParseResult.TREAT_AS_WITHDRAW)
        
    return final_result
