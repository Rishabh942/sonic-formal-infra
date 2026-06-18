"""CrossHair target for bgp_malformed_packets.

Defines the entry point for symbolic path coverage.
"""

from models.bgpd.malformed_packets.model import BGPState, BState, BEvent, RFCStandard

def execute_bgp_sequence(
    events: list[int],
    rfc_standard_val: int
) -> list[tuple[int, str]]:
    """Runs a sequence of events on the BGP state machine.
    
    Inputs are constrained to primitive types (lists of ints) to ensure
    efficient symbolic reasoning under Z3.
    """
    # Bound sequence length for symbolic execution speed (similar to steps=7)
    if len(events) < 1 or len(events) > 7:
        return []
        
    if rfc_standard_val not in (4271, 7606):
        return []
        
    # Restrict to valid BEvent integers
    valid_events = {10, 11, 12, 13, 14, 15, 16}
    for e in events:
        if e not in valid_events:
            return []
            
    rfc = RFCStandard(rfc_standard_val)
    state = BGPState(BState.IDLE)
    
    trace = []
    for e_val in events:
        event = BEvent(e_val)
        # Store state BEFORE the transition
        prev_state = state.fsm_state
        next_state, action = state.transition(event, rfc)
        trace.append((int(prev_state), action))
        state.fsm_state = next_state
        
    return trace
