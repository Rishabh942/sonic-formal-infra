#ifndef COMMON_DATA_H
#define COMMON_DATA_H

#include <cstdint>
#include <string>
#include <vector>

// Type aliases mirror NewType('prefix_t', int) / NewType('addr_t', int) in
// examples/lib/builtin.py. The wire format on the C++ side is the IPv6
// string produced by to_ipv6_prefix / to_ipv6_address — i.e., prefixes
// carry a "/N" suffix (e.g. "2001:db8:...::xxxx/128", "::/0"); addresses
// don't (e.g. "2001:db8:...::xxxx", "::").
using prefix_t = std::string;
using addr_t   = std::string;

// Mirrors BOp(IntEnum) in api_bgp_nh_update.py.
enum class BOp : std::uint8_t {
    SET = 1,
    DEL = 2,
};

struct BgpdRouteEvent {
    BOp                 op;
    prefix_t            prefix;
    std::vector<addr_t> nexthops;
};

struct BgpNexthopCache {
    addr_t endpoint;
    addr_t resolved;
    bool   valid;
};

struct BgpRibEntry {
    prefix_t            prefix;
    std::vector<addr_t> nexthops;
};

struct BgpdNexthopState {
    std::vector<BgpNexthopCache> nexthop_cache_table;
    std::vector<BgpRibEntry>     rib;
};

struct BApiNexthopUpdate {
    addr_t endpoint;
    addr_t resolved;
    bool   status_up;
};

// In Python this is a dataclass with a single `msgs: list[...]` field.
// The JSON serializer flattens it to a bare array, so the C++ analog is
// the bare vector — no wrapping struct.
using DownstreamMsgs = std::vector<BgpdRouteEvent>;

struct TestCase {
    int               test_id;
    std::string       op;              // currently always "api_bgp_nh_update"
    BgpdNexthopState  initial_state;
    BApiNexthopUpdate api_param;
    BgpdNexthopState  final_state;
    DownstreamMsgs    downstream_msgs;
};

#endif // COMMON_DATA_H
