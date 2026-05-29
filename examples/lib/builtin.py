import hashlib
from collections import UserList
from typing import NewType, Iterable


class UList[T](UserList[T]):
    """Unordered list. Backed by a Python list (via UserList), but mypy treats
    it as a distinct type so plain `list[T]` and `UList[T]` cannot be freely
    interchanged."""
    pass


# prefix_t, addr_t, and str63_t are int aliases, not str. The model only
# does identity comparison on them, so an integer ID is semantically
# equivalent — and it avoids Z3's expensive symbolic-string reasoning.
# Concrete prefixes, host addresses, and names are derived from the integer
# values via to_ipv6_prefix / to_ipv6_address / to_short_name below.
#
# prefix_t is a route prefix (carries a /N mask); addr_t is a concrete host
# address (no mask) — typically a nexthop, endpoint, or resolved address.
prefix_t = NewType('prefix_t', int)
addr_t = NewType('addr_t', int)
str63_t = NewType('str63_t', int)

# These int width hints are not enforced by Python, nor by CrossHair / Z3.
# Use the clamp_u8 / clamp_u16 / clamp_u32 helpers below to bound symbolic
# values into range from builder code when needed.
uint8_t = NewType('uint8_t', int)
uint16_t = NewType('uint16_t', int)
uint32_t = NewType('uint32_t', int)


def clamp_u8(x: int) -> uint8_t:
    return uint8_t(x & 0xFF)


def clamp_u16(x: int) -> uint16_t:
    return uint16_t(x & 0xFFFF)


def clamp_u32(x: int) -> uint32_t:
    return uint32_t(x & 0xFFFFFFFF)


IPV6_ROOT_PREFIX = prefix_t(0)
IPV6_UNSPECIFIED = addr_t(0)


# Concrete-representation generators. The model treats prefix_t and str63_t
# as opaque integer IDs; these helpers map each ID to a deterministic,
# random-looking concrete string for use in test harnesses that need to
# drive real software (FRR bgpd, gTest fixtures, etc.). The mapping is
# hash-derived (stdlib blake2b), so output is stable across runs and
# Python versions while looking unrelated for adjacent IDs.

def to_ipv6_prefix(p: prefix_t) -> str:
    """Deterministic IPv6 route prefix for a prefix_t identifier.

    Returns an address under RFC 3849's documentation range 2001:db8::/32,
    with /128 host length. IPV6_ROOT_PREFIX (id 0) maps to ::/0, the IPv6
    default-route prefix."""
    if p == IPV6_ROOT_PREFIX:
        return "::/0"
    h = hashlib.blake2b(str(p).encode(), digest_size=6).hexdigest()
    return f"2001:db8:{h[0:4]}:{h[4:8]}::{h[8:12]}/128"


def to_ipv6_address(a: addr_t) -> str:
    """Deterministic IPv6 host address for an addr_t identifier.

    Same address space as to_ipv6_prefix, but without the /N suffix —
    appropriate for nexthop / endpoint / resolved fields. IPV6_UNSPECIFIED
    (id 0) maps to '::', the IPv6 unspecified address."""
    if a == IPV6_UNSPECIFIED:
        return "::"
    h = hashlib.blake2b(str(a).encode(), digest_size=6).hexdigest()
    return f"2001:db8:{h[0:4]}:{h[4:8]}::{h[8:12]}"


def to_short_name(s: str63_t) -> str:
    """Deterministic 12-char hex name for a str63_t identifier."""
    return hashlib.blake2b(str(s).encode(), digest_size=6).hexdigest()


def no_dup(l: Iterable) -> bool:
    items = list(l)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return False
    return True


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


def prepend(l: list, a) -> None:
    l.insert(0, a)


def branch(a):
    return a
