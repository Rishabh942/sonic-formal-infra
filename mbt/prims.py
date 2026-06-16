"""Model-writing primitives.
"""

import hashlib
import ipaddress
from collections import UserList
from typing import Iterable, NewType

# ── Domain ID types ──────────────────────────────────────────────────────────
# prefix_t, addr_t, and str63_t are int aliases, not str. The model only does
# identity comparison on them, so an integer ID is semantically equivalent —
# and it avoids a solver's expensive symbolic-string reasoning. Concrete prefixes,
# host addresses, and names are derived from the integer values via
# to_ipv6_prefix / to_ipv6_address / to_short_name below.
#
# prefix_t is a route prefix (carries a /N mask); addr_t is a concrete host
# address (no mask) — typically a nexthop, endpoint, or resolved address;
# str63_t is a short name (e.g. an interface or VRF name).
prefix_t = NewType('prefix_t', int)
addr_t = NewType('addr_t', int)
str63_t = NewType('str63_t', int)

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


# ── Renderers ────────────────────────────────────────────────────────────────
# The model treats the ID types above as opaque integers; these helpers map each
# ID to a deterministic concrete address for test harnesses that drive real
# software (FRR bgpd, gTest fixtures, etc.). The mapping is hash-derived (stdlib
# blake2b) — not confined to a documentation subnet — so coverage is broad and
# collisions are negligible; output is stable across runs and Python versions.
# IPv4 spans the full 32-bit space; IPv6 keeps 4 hextets (64 bits) of entropy and
# zeroes the rest, collapsing to a short '::' whose position varies per ID, for
# readability. id 0 is the
# one reserved value: it renders to the default route / unspecified address via
# the *_ROOT_PREFIX / *_UNSPECIFIED sentinels.
#
# A random address may land in a special range (multicast, link-local, loopback,
# etc.); mask the renderers if a harness rejects those.

IPV6_ROOT_PREFIX = prefix_t(0)
IPV6_UNSPECIFIED = addr_t(0)
IPV4_ROOT_PREFIX = prefix_t(0)
IPV4_UNSPECIFIED = addr_t(0)


def to_ipv6_prefix(p: prefix_t) -> str:
    """Deterministic IPv6 route prefix for a prefix_t identifier.

    to_ipv6_address(p) with a /128 host length. IPV6_ROOT_PREFIX (id 0) maps to
    ::/0, the IPv6 default-route prefix."""
    if p == IPV6_ROOT_PREFIX:
        return "::/0"
    return f"{to_ipv6_address(addr_t(p))}/128"


def to_ipv6_address(a: addr_t) -> str:
    """Deterministic IPv6 host address for an addr_t identifier. Keeps 4 hextets
    (64 bits) of entropy and zeroes the other 4; the zero run sits at a per-ID
    position, so '::' lands leading, interior, or trailing rather than always at
    the tail. Suitable for nexthop / endpoint / resolved fields. IPV6_UNSPECIFIED
    (id 0) maps to '::', the IPv6 unspecified address."""
    if a == IPV6_UNSPECIFIED:
        return "::"
    h = hashlib.blake2b(str(a).encode(), digest_size=16).hexdigest()
    hextets = [h[i:i + 4] for i in range(0, 16, 4)]  # 4 non-zero hextets
    front = int(h[16:18], 16) % 5  # how many sit before the gap
    groups = hextets[:front] + ['0', '0', '0', '0'] + hextets[front:]
    return str(ipaddress.IPv6Address(':'.join(groups)))


def to_ipv4_prefix(p: prefix_t) -> str:
    """Deterministic IPv4 route prefix for a prefix_t identifier.

    to_ipv4_address(p) with a /32 host length. IPV4_ROOT_PREFIX (id 0) maps to
    0.0.0.0/0, the IPv4 default-route prefix."""
    if p == IPV4_ROOT_PREFIX:
        return "0.0.0.0/0"
    return f"{to_ipv4_address(addr_t(p))}/32"


def to_ipv4_address(a: addr_t) -> str:
    """Deterministic IPv4 host address for an addr_t identifier, over the full
    IPv4 space. Suitable for nexthop / endpoint / resolved fields.
    IPV4_UNSPECIFIED (id 0) maps to 0.0.0.0, the IPv4 unspecified address."""
    if a == IPV4_UNSPECIFIED:
        return "0.0.0.0"
    h = hashlib.blake2b(str(a).encode(), digest_size=4).digest()
    return f"{h[0]}.{h[1]}.{h[2]}.{h[3]}"


def to_short_name(s: str63_t) -> str:
    """Deterministic 12-char hex name for a str63_t identifier."""
    return hashlib.blake2b(str(s).encode(), digest_size=6).hexdigest()


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
