from typing import List
from dataclasses import dataclass
from enum import IntEnum

class ParseResult(IntEnum):
    VALID = 0
    SESSION_RESET = 1
    TREAT_AS_WITHDRAW = 2
    ATTRIBUTE_DISCARD = 3

@dataclass
class BGPPathAttr:
    flags: int
    type_code: int
    length: int

def parse_attributes(attrs: List[BGPPathAttr]) -> ParseResult:
    """Simulates FRR bgp_attr_parse() logical branches for RFC 4271/7606."""
    seen_origin = False
    seen_as_path = False
    seen_nexthop = False
    
    final_result = ParseResult.VALID
    
    def escalate(new_result: ParseResult):
        nonlocal final_result
        if new_result == ParseResult.SESSION_RESET:
            final_result = ParseResult.SESSION_RESET
        elif new_result == ParseResult.TREAT_AS_WITHDRAW and final_result != ParseResult.SESSION_RESET:
            final_result = ParseResult.TREAT_AS_WITHDRAW
        elif new_result == ParseResult.ATTRIBUTE_DISCARD and final_result == ParseResult.VALID:
            final_result = ParseResult.ATTRIBUTE_DISCARD

    for attr in attrs:
        is_optional = (attr.flags & 0x80) != 0
        is_transitive = (attr.flags & 0x40) != 0
        well_known_flags_valid = (not is_optional) and is_transitive
        
        if attr.type_code == 1: # ORIGIN
            if seen_origin:
                escalate(ParseResult.ATTRIBUTE_DISCARD)
            seen_origin = True
            if not well_known_flags_valid or attr.length != 1:
                escalate(ParseResult.TREAT_AS_WITHDRAW)
                
        elif attr.type_code == 2: # AS_PATH
            if seen_as_path:
                escalate(ParseResult.ATTRIBUTE_DISCARD)
            seen_as_path = True
            if not well_known_flags_valid:
                escalate(ParseResult.SESSION_RESET)
                
        elif attr.type_code == 3: # NEXT_HOP
            if seen_nexthop:
                escalate(ParseResult.ATTRIBUTE_DISCARD)
            seen_nexthop = True
            if not well_known_flags_valid or attr.length != 4:
                escalate(ParseResult.SESSION_RESET)
                
    if not seen_origin or not seen_as_path or not seen_nexthop:
        escalate(ParseResult.SESSION_RESET)
        
    return final_result
