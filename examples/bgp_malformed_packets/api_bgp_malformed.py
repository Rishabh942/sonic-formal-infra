"""Executable model of BGP FSM state transitions under RFC 4271 and RFC 7606.

This replaces raw Z3 declarations with an executable Python spec. CrossHair
will symbolically execute this code to discover all paths (actions/states)
and generate test sequences.
"""

from dataclasses import dataclass
from enum import IntEnum

class BState(IntEnum):
    IDLE = 0
    CONNECT = 1
    OPENSENT = 2
    ESTABLISHED = 3

class BEvent(IntEnum):
    TCP_CONN_START = 10
    RCV_OPEN = 11
    RCV_VALID_UPDATE = 12
    RCV_KEEPALIVE = 13
    RCV_UPDATE_MISSING_MANDATORY = 14
    RCV_UPDATE_BAD_FLAGS = 15
    RCV_UPDATE_BAD_LENGTH = 16

class RFCStandard(IntEnum):
    RFC4271 = 4271
    RFC7606 = 7606

@dataclass
class BGPState:
    fsm_state: BState = BState.IDLE

    def transition(self, event: BEvent, rfc: RFCStandard) -> tuple[BState, str]:
        """Execute a single FSM state transition.
        
        Returns the new state and the action code.
        """
        if event == BEvent.TCP_CONN_START:
            return BState.CONNECT, "ESTABLISH_TCP"

        # Handshake progression
        if self.fsm_state == BState.IDLE:
            return BState.IDLE, "DROP_CONNECTION"
            
        elif self.fsm_state == BState.CONNECT:
            if event == BEvent.RCV_OPEN:
                return BState.OPENSENT, "SEND_OPEN_AND_KEEPALIVE"
            return BState.IDLE, "SEND_NOTIFICATION"
            
        elif self.fsm_state == BState.OPENSENT:
            if event == BEvent.RCV_KEEPALIVE:
                return BState.ESTABLISHED, "NONE"
            return BState.IDLE, "SEND_NOTIFICATION"
            
        elif self.fsm_state == BState.ESTABLISHED:
            if event == BEvent.RCV_VALID_UPDATE:
                return BState.ESTABLISHED, "UPDATE_RIB"
            elif event == BEvent.RCV_KEEPALIVE:
                return BState.ESTABLISHED, "NONE"
            
            # Malformed Packet Handling
            elif event == BEvent.RCV_UPDATE_MISSING_MANDATORY:
                if rfc == RFCStandard.RFC4271:
                    return BState.IDLE, "SEND_NOTIFICATION_AND_RESET"
                else:  # RFC 7606 (Treat-as-withdraw / Attribute Discard)
                    return BState.ESTABLISHED, "TREAT_AS_WITHDRAW"
                    
            elif event == BEvent.RCV_UPDATE_BAD_FLAGS:
                if rfc == RFCStandard.RFC4271:
                    return BState.IDLE, "SEND_NOTIFICATION_AND_RESET"
                else:  # RFC 7606 (Soft reset / discard)
                    return BState.ESTABLISHED, "DISCARD_ATTRIBUTE"
                    
            elif event == BEvent.RCV_UPDATE_BAD_LENGTH:
                # Fatal framing error breaks message boundaries; session must drop under both RFCs
                return BState.IDLE, "SEND_NOTIFICATION_AND_RESET"
                
        return BState.IDLE, "DROP_CONNECTION"
