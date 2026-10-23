"""Small, strict BGP wire adapter for the bounded route-competition lab.

Only legacy IPv4 unicast and four-octet AS_SEQUENCE paths are supported.
TCP framing is buffered across reads; unexpected messages fail the run.
"""

import ipaddress
import socket
import struct

from models.bgpd.malformed_packets.bgp_oracle import ParseResult, parse_attributes
from models.bgpd.malformed_packets.packet_builders import decode_update_attributes, encode_attr

PREFIXES = ('198.18.0.0/24', '198.18.1.0/24')
PEER_IPS = ('127.0.0.2', '127.0.0.3', '127.0.0.4')
ASNS = (65002, 65003, 65004)
MARKER = b'\xff' * 16


def message(kind, body=b''):
    return MARKER + struct.pack('!HB', 19 + len(body), kind) + body


def open_message(peer):
    # AS4 only: no GR retention and no extra address-family behavior.
    capability = struct.pack('!BBBBI', 2, 6, 65, 4, ASNS[peer])
    return message(1, struct.pack('!BHH4sB', 4, ASNS[peer], 90,
                                  socket.inet_aton(f'192.0.2.{peer + 2}'),
                                  len(capability)) + capability)


def nlri(prefix):
    net = ipaddress.IPv4Network(prefix)
    return bytes([net.prefixlen]) + net.network_address.packed[:(net.prefixlen + 7) // 8]


def attribute(flags, code, value):
    return encode_attr(flags, code, len(value)) + value


def update(event):
    prefix = nlri(PREFIXES[event.prefix])
    if event.kind == 'withdraw':
        return message(2, struct.pack('!H', len(prefix)) + prefix + b'\x00\x00')
    length = event.route.length if event.route else 1
    origin = event.route.origin if event.route else 0
    path = b''.join(struct.pack('!I', ASNS[event.peer]) for _ in range(length))
    # Intact outer framing/NLRI, invalid attribute value/segment framing.
    aspath = bytes((2, length + (event.kind == 'bad_aspath'))) + path
    attrs = (attribute(0x40, 1, bytes((3 if event.kind == 'bad_origin' else origin,)))
             + attribute(0x40, 2, aspath)
             + attribute(0x40, 3, socket.inet_aton(f'192.0.2.{event.peer + 2}')))
    return message(2, b'\x00\x00' + struct.pack('!H', len(attrs)) + attrs + prefix)


def oracle_transition(state, event, packet):
    """Compose the existing packet oracle with the independent state model.

    State effects follow the verdict and decoded wire attributes. Compare
    with the abstract event too, so a builder/model disagreement cannot be
    silently accepted as a changed expectation for FRR.
    """
    from .route_model import Event, Route, step

    withdrawn, attrs, announced = decode_update_attributes(packet)
    target = nlri(PREFIXES[event.prefix])
    if event.kind == 'withdraw':
        if withdrawn != target or attrs or announced:
            raise ValueError('withdrawal wire/model disagreement')
        verdict = 'WITHDRAW'
        effect = event
    else:
        if withdrawn or announced != target:
            raise ValueError('announcement NLRI/model disagreement')
        result = parse_attributes(attrs, asn_4byte=True,
                                  enforce_first_as=ASNS[event.peer])
        verdict = result.name
        if result == ParseResult.TREAT_AS_WITHDRAW:
            effect = Event('withdraw', event.peer, event.prefix)
        elif result == ParseResult.VALID:
            values = {attr.type_code: attr.value for attr in attrs}
            path = values[2]
            if len(path) < 2 or path[0] != 2 or len(path) != 2 + 4 * path[1]:
                raise ValueError('valid AS path outside bounded route model')
            effect = Event('announce', event.peer, event.prefix,
                           Route(path[1], values[1][0]))
        else:
            raise ValueError(f'packet oracle verdict outside route model: {verdict}')
    after = step(state, effect)
    expected_verdict = ('WITHDRAW' if event.kind == 'withdraw' else
                        'VALID' if event.kind == 'announce' else 'TREAT_AS_WITHDRAW')
    if verdict != expected_verdict or after != step(state, event):
        raise AssertionError('packet oracle/wire/state-model disagreement')
    return verdict, after


def read_nlri(data):
    result = []
    while data:
        bits = data[0]
        size = (bits + 7) // 8
        if bits > 32 or len(data) < 1 + size:
            raise ValueError('invalid IPv4 NLRI')
        addr = ipaddress.IPv4Address(data[1:1 + size].ljust(4, b'\x00'))
        result.append(str(ipaddress.IPv4Network(f'{addr}/{bits}', strict=False)))
        data = data[1 + size:]
    return result


def parse_update(body, rib):
    """Apply an observer UPDATE, retaining AS path and ORIGIN for comparison."""
    if len(body) < 4:
        raise ValueError('short UPDATE')
    withdrawn_len = int.from_bytes(body[:2], 'big')
    offset = 2 + withdrawn_len
    if offset + 2 > len(body):
        raise ValueError('truncated withdrawal')
    withdrawn = read_nlri(body[2:offset])
    attr_len = int.from_bytes(body[offset:offset + 2], 'big')
    end = offset + 2 + attr_len
    if end > len(body):
        raise ValueError('truncated attributes')
    attrs = body[offset + 2:end]
    origin, path = None, None
    while attrs:
        if len(attrs) < 3:
            raise ValueError('short attribute header')
        flags, code = attrs[:2]
        header = 4 if flags & 0x10 else 3
        if len(attrs) < header:
            raise ValueError('short extended attribute header')
        size = int.from_bytes(attrs[2:header], 'big')
        if header + size > len(attrs):
            raise ValueError('short attribute payload')
        value = attrs[header:header + size]
        attrs = attrs[header + size:]
        if code == 1:
            if len(value) != 1 or value[0] > 2:
                raise ValueError('invalid exported ORIGIN')
            origin = value[0]
        if code == 2:
            path = []
            while value:
                if len(value) < 2 or value[0] != 2:
                    raise ValueError('expected AS_SEQUENCE')
                count = value[1]
                size = 2 + 4 * count
                if len(value) < size:
                    raise ValueError('truncated AS_SEQUENCE')
                path.extend(struct.unpack(f'!{count}I', value[2:size]))
                value = value[size:]
    announced = read_nlri(body[end:])
    if announced and (origin is None or path is None):
        raise ValueError('missing exported mandatory attributes')
    for prefix in withdrawn:
        rib.pop(prefix, None)
    for prefix in announced:
        rib[prefix] = {'path': path, 'origin': origin}


class Peer:
    def __init__(self, index, host, port):
        self.index = index
        self.sock = socket.socket()
        self.sock.settimeout(3)
        try:
            self.sock.bind((PEER_IPS[index], 0))
            self.sock.connect((host, port))
        except Exception:
            self.sock.close()
            raise
        self.buffer = b''
        self.opened = False
        self.established = False
        self.rib = {}

    def feed(self, chunk):
        if not chunk:
            raise ConnectionError(f'peer {self.index}: EOF')
        self.buffer += chunk
        messages = []
        while len(self.buffer) >= 19:
            if self.buffer[:16] != MARKER:
                raise ValueError('invalid BGP marker')
            size, kind = struct.unpack('!HB', self.buffer[16:19])
            if not 19 <= size <= 4096:
                raise ValueError('invalid BGP message length')
            if len(self.buffer) < size:
                break
            packet, self.buffer = self.buffer[:size], self.buffer[size:]
            body = packet[19:]
            messages.append(packet)
            if kind == 3:
                raise ConnectionError(f'peer {self.index}: NOTIFICATION {body.hex()}')
            if kind == 1:
                if len(body) < 10 or body[0] != 4 or int.from_bytes(body[1:3], 'big') != 65001:
                    raise ValueError('unexpected FRR OPEN')
                self.opened = True
            elif kind == 4:
                if body or not self.opened:
                    raise ValueError('unexpected KEEPALIVE')
                self.established = True
            elif kind == 2:
                parse_update(body, self.rib)
            else:
                raise ValueError(f'unexpected message type {kind}')
        return messages
