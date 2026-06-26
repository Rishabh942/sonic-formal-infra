"""Model-writing primitives.
"""

import hashlib
import ipaddress
from collections import UserList
from enum import Enum
from typing import Iterable, NamedTuple, NewType


# ── Fixed-width integer types ────────────────────────────────────────────────
# Width hints for mirroring C struct fields. They are not enforced by Python.
# Use the clamp_u8 / clamp_u16 / clamp_u32 helpers below to bound symbolic values
# into range from builder code when needed.
uint8_t = NewType('uint8_t', int)
uint16_t = NewType('uint16_t', int)
uint32_t = NewType('uint32_t', int)


def clamp_u8(x: int) -> uint8_t:
    return uint8_t(x & 0xFF)


def clamp_u16(x: int) -> uint16_t:
    return uint16_t(x & 0xFFFF)


def clamp_u32(x: int) -> uint32_t:
    return uint32_t(x & 0xFFFFFFFF)


# ── Opaque types ─────────────────────────────────────────────────────────────
# opaque_prefix_t, opaque_addr_t, and str63_t are int aliases, not str. The model
# only does identity comparison on them, so an integer ID is semantically
# equivalent — and it avoids a solver's expensive symbolic-string reasoning.
# Concrete prefixes, host addresses, and names are derived from the integer values
# via to_ipv6_opaque_prefix / to_ipv6_opaque_address / to_short_name below.
#
# opaque_prefix_t is a route prefix (carries a /N mask); opaque_addr_t is a
# concrete host address (no mask) — typically a nexthop, endpoint, or resolved
# address; str63_t is a short name (e.g. an interface or VRF name).
opaque_prefix_t = NewType('opaque_prefix_t', int)
opaque_addr_t = NewType('opaque_addr_t', int)
str63_t = NewType('str63_t', int)


# ── Opaque renderers ─────────────────────────────────────────────────────────
# The model treats the opaque ID types above as opaque integers; these helpers map
# each ID to a deterministic concrete address for test harnesses that drive real
# software (FRR bgpd, gTest fixtures, etc.). The mapping is hash-derived (stdlib
# blake2b) — not confined to a documentation subnet — so coverage is broad and
# collisions are negligible; output is stable across runs and Python versions.
# IPv4 spans the full 32-bit space; IPv6 keeps 4 hextets (64 bits) of entropy and
# zeroes the rest, collapsing to a short '::' whose position varies per ID, for
# readability.
#
# A random address may land in a special range (multicast, link-local, loopback,
# etc.); mask the renderers if a harness rejects those.

# OPAQUE_ROOT renders to the unspecified address ('::' · 0.0.0.0) and the
# default-route prefix (::/0 · 0.0.0.0/0).
OPAQUE_ROOT = 0


def to_ipv6_opaque_prefix(p: opaque_prefix_t) -> str:
    """Deterministic IPv6 CIDR for an opaque_prefix_t identifier.

    to_ipv6_opaque_address(p) with a /128 host length. id 0 maps to ::/0, the
    IPv6 default-route prefix."""
    if p == OPAQUE_ROOT:
        return "::/0"
    return f"{to_ipv6_opaque_address(opaque_addr_t(p))}/128"


def to_ipv6_opaque_address(a: opaque_addr_t) -> str:
    """Deterministic IPv6 host address for an opaque_addr_t identifier. Keeps 4
    hextets (64 bits) of entropy and zeroes the other 4.
    Suitable for nexthop / endpoint / resolved fields.
    OPAQUE_ROOT (id 0) maps to '::', the IPv6 unspecified address."""
    if a == OPAQUE_ROOT:
        return "::"
    h = hashlib.blake2b(str(a).encode(), digest_size=16).hexdigest()
    hextets = [h[i:i + 4] for i in range(0, 16, 4)]  # 4 non-zero hextets
    front = int(h[16:18], 16) % 5  # how many sit before the gap
    groups = hextets[:front] + ['0', '0', '0', '0'] + hextets[front:]
    return str(ipaddress.IPv6Address(':'.join(groups)))


def to_ipv4_opaque_prefix(p: opaque_prefix_t) -> str:
    """Deterministic IPv4 CIDR for an opaque_prefix_t identifier.

    to_ipv4_opaque_address(p) with a /32 host length. id 0 maps to 0.0.0.0/0,
    the IPv4 default-route prefix."""
    if p == OPAQUE_ROOT:
        return "0.0.0.0/0"
    return f"{to_ipv4_opaque_address(opaque_addr_t(p))}/32"


def to_ipv4_opaque_address(a: opaque_addr_t) -> str:
    """Deterministic IPv4 host address for an opaque_addr_t identifier, over the
    full IPv4 space. Suitable for nexthop / endpoint / resolved fields.
    OPAQUE_ROOT (id 0) maps to 0.0.0.0, the IPv4 unspecified address."""
    if a == OPAQUE_ROOT:
        return "0.0.0.0"
    h = hashlib.blake2b(str(a).encode(), digest_size=4).digest()
    return f"{h[0]}.{h[1]}.{h[2]}.{h[3]}"


def to_short_name(s: str63_t) -> str:
    """Deterministic 12-char hex name for a str63_t identifier."""
    return hashlib.blake2b(str(s).encode(), digest_size=6).hexdigest()


# ── Structured prefix and addresses ──────────────────────────────────────────
# addr_t and prefix_t are the structural counterparts of the opaque types above;
# use them only when a model needs structural reasoning, e.g. prefix_match.
addr_t = NewType('addr_t', int)


# prefix_t is a NamedTuple — a flat (addr, length) tuple with named fields — so
# CrossHair keeps exploring the cheap two-int representation while model code
# reads p.addr / p.length. length is the mask width in bits (0 = default route).
class prefix_t(NamedTuple):
    addr: addr_t
    length: int


IPV6_ROOT_PREFIX = prefix_t(addr_t(0), 0)
IPV4_ROOT_PREFIX = prefix_t(addr_t(0), 0)


def to_ipv6_prefix(p: prefix_t) -> str:
    return f"{to_ipv6_address(p.addr)}/{p.length}"


def to_ipv6_address(a: addr_t) -> str:
    return str(ipaddress.IPv6Address(a))


def to_ipv4_prefix(p: prefix_t) -> str:
    return f"{to_ipv4_address(p.addr)}/{p.length}"


def to_ipv4_address(a: addr_t) -> str:
    return str(ipaddress.IPv4Address(a))


class IPProto(Enum):
    """IP protocol version. Its value is the address width in bits, which selects
    the netmask space for prefix operations."""
    IPv4 = 32
    IPv6 = 128


# Block size per mask length, one table per protocol. _BLOCK[IPProto.IPv4],
# indexed by prefix length, is (2**32, 2**31, ..., 256, ..., 4, 2, 1) — i.e.
# /0 spans 2**32 addresses, /24 spans 256, /32 spans 1.
# This constant array simplifies symbolic execution.
_BLOCK = {
    proto: tuple(1 << (proto.value - length) for length in range(proto.value + 1))
    for proto in IPProto
}


def prefix_match(prefix: prefix_t, addr: addr_t, proto: IPProto = IPProto.IPv6) -> bool:
    """True iff `addr` is in [prefix.addr, prefix.addr + block), block =
    2 ** (width - prefix.length). proto picks the width (default IPv6/128);
    requires a canonical prefix.addr and 0 <= prefix.length <= proto.value."""
    block = _BLOCK[proto][prefix.length]
    return prefix.addr <= addr < prefix.addr + block


def prefix_well_formed(prefix: prefix_t, proto: IPProto = IPProto.IPv6) -> bool:
    """True iff `prefix` is a valid CIDR for `proto`: length in [0, width], addr in
    [0, 2 ** width), and addr canonical (host bits below the mask zero)."""
    width = proto.value
    return (0 <= prefix.length <= width
            and 0 <= prefix.addr < (1 << width)
            and prefix.addr % _BLOCK[proto][prefix.length] == 0)


# ── Collections ──────────────────────────────────────────────────────────────

class UList[T](UserList[T]):
    """Unordered list. Backed by a Python list (via UserList), but mypy treats
    it as a distinct type so plain `list[T]` and `UList[T]` cannot be freely
    interchanged."""
    pass


def ulist_eq(a: UList, b: UList) -> bool:
    """Multiset equality: same length and each element occurs the same number
    of times in both. Order is ignored; duplicates are respected."""
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        ca = 0
        for j in range(len(a)):
            if a[j] == a[i]:
                ca += 1
        cb = 0
        for j in range(len(b)):
            if b[j] == a[i]:
                cb += 1
        if ca != cb:
            return False
    return True


# ── Predicates & helpers ─────────────────────────────────────────────────────

def no_dup(l: Iterable) -> bool:
    items = list(l)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return False
    return True


def prepend(l: list, a) -> None:
    l.insert(0, a)
