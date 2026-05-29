#include "json_reader.h"

#include <algorithm>
#include <iostream>
#include <string>

static const char* bop_str(BOp op) {
    switch (op) {
        case BOp::SET: return "SET";
        case BOp::DEL: return "DEL";
    }
    return "?";
}

static void print_addr_list(const std::vector<addr_t>& xs) {
    std::cout << "[";
    for (size_t i = 0; i < xs.size(); ++i) {
        if (i) std::cout << ", ";
        std::cout << xs[i];
    }
    std::cout << "]";
}

static void print_state(const BgpdNexthopState& s, const char* indent) {
    std::cout << indent << "nexthop_cache_table (" << s.nexthop_cache_table.size() << "):\n";
    for (const auto& b : s.nexthop_cache_table) {
        std::cout << indent << "  endpoint=" << b.endpoint
                  << " resolved=" << b.resolved
                  << " valid=" << (b.valid ? "true" : "false") << "\n";
    }
    std::cout << indent << "rib (" << s.rib.size() << "):\n";
    for (const auto& r : s.rib) {
        std::cout << indent << "  prefix=" << r.prefix << " nexthops=";
        print_addr_list(r.nexthops);
        std::cout << "\n";
    }
}

static void print_test_case(const TestCase& tc) {
    std::cout << "TestId=" << tc.test_id << " Op=" << tc.op << "\n";
    std::cout << "  InitialState:\n";
    print_state(tc.initial_state, "    ");
    std::cout << "  ApiParam: endpoint=" << tc.api_param.endpoint
              << " resolved=" << tc.api_param.resolved
              << " status_up=" << (tc.api_param.status_up ? "true" : "false") << "\n";
    std::cout << "  FinalState:\n";
    print_state(tc.final_state, "    ");
    std::cout << "  DownstreamMsgs (" << tc.downstream_msgs.size() << "):\n";
    for (const auto& m : tc.downstream_msgs) {
        std::cout << "    op=" << bop_str(m.op)
                  << " prefix=" << m.prefix
                  << " nexthops=";
        print_addr_list(m.nexthops);
        std::cout << "\n";
    }
}

int main(int argc, char** argv) {
    std::string path = (argc > 1)
        ? std::string(argv[1])
        : std::string("../tests/nh_update_formatted.json");

    std::cout << "Reading " << path << " ...\n";
    std::vector<TestCase> cases;
    try {
        cases = read_test_cases(path);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    std::cout << "Loaded " << cases.size() << " test cases.\n\n";

    // Print a small sample to confirm the shape.
    size_t sample_n = std::min<size_t>(2, cases.size());
    for (size_t i = 0; i < sample_n; ++i) {
        std::cout << "----- sample [" << i << "] -----\n";
        print_test_case(cases[i]);
        std::cout << "\n";
    }

    // Aggregate stat: how many cases produced at least one downstream msg?
    size_t nonempty_msgs = 0;
    for (const auto& tc : cases) {
        if (!tc.downstream_msgs.empty()) ++nonempty_msgs;
    }
    std::cout << "Summary: " << nonempty_msgs << " / " << cases.size()
              << " cases emit downstream messages.\n";

    return 0;
}
