#include "json_reader.h"

#include <cstring>
#include <iostream>
#include <stdexcept>

extern "C" {
#include <json-c/json.h>
}

static BOp parse_bop(const char* s) {
    if (std::strcmp(s, "SET") == 0) return BOp::SET;
    if (std::strcmp(s, "DEL") == 0) return BOp::DEL;
    throw std::runtime_error(std::string("Unknown BOp value: ") + s);
}

static std::vector<addr_t> parse_addr_list(json_object* arr) {
    std::vector<addr_t> out;
    size_t n = json_object_array_length(arr);
    out.reserve(n);
    for (size_t i = 0; i < n; ++i) {
        out.emplace_back(json_object_get_string(json_object_array_get_idx(arr, i)));
    }
    return out;
}

static BgpNexthopCache parse_cache_entry(json_object* obj) {
    BgpNexthopCache out{};
    json_object_object_foreach(obj, key, val) {
        if      (std::strcmp(key, "endpoint") == 0) out.endpoint = json_object_get_string(val);
        else if (std::strcmp(key, "resolved") == 0) out.resolved = json_object_get_string(val);
        else if (std::strcmp(key, "valid")    == 0) out.valid    = json_object_get_boolean(val);
        else std::cerr << "Unhandled key in cache entry: " << key << "\n";
    }
    return out;
}

static BgpRibEntry parse_rib_entry(json_object* obj) {
    BgpRibEntry out{};
    json_object_object_foreach(obj, key, val) {
        if      (std::strcmp(key, "prefix")   == 0) out.prefix   = json_object_get_string(val);
        else if (std::strcmp(key, "nexthops") == 0) out.nexthops = parse_addr_list(val);
        else std::cerr << "Unhandled key in rib entry: " << key << "\n";
    }
    return out;
}

static BgpdNexthopState parse_state(json_object* obj) {
    BgpdNexthopState out{};
    json_object_object_foreach(obj, key, val) {
        if (std::strcmp(key, "nexthop_cache_table") == 0) {
            size_t n = json_object_array_length(val);
            out.nexthop_cache_table.reserve(n);
            for (size_t i = 0; i < n; ++i) {
                out.nexthop_cache_table.push_back(
                    parse_cache_entry(json_object_array_get_idx(val, i)));
            }
        } else if (std::strcmp(key, "rib") == 0) {
            size_t n = json_object_array_length(val);
            out.rib.reserve(n);
            for (size_t i = 0; i < n; ++i) {
                out.rib.push_back(
                    parse_rib_entry(json_object_array_get_idx(val, i)));
            }
        } else {
            std::cerr << "Unhandled key in state: " << key << "\n";
        }
    }
    return out;
}

static BApiNexthopUpdate parse_api_param(json_object* obj) {
    BApiNexthopUpdate out{};
    json_object_object_foreach(obj, key, val) {
        if      (std::strcmp(key, "endpoint")  == 0) out.endpoint  = json_object_get_string(val);
        else if (std::strcmp(key, "resolved")  == 0) out.resolved  = json_object_get_string(val);
        else if (std::strcmp(key, "status_up") == 0) out.status_up = json_object_get_boolean(val);
        else std::cerr << "Unhandled key in api param: " << key << "\n";
    }
    return out;
}

static BgpdRouteEvent parse_route_event(json_object* obj) {
    BgpdRouteEvent out{};
    json_object_object_foreach(obj, key, val) {
        if      (std::strcmp(key, "op")       == 0) out.op       = parse_bop(json_object_get_string(val));
        else if (std::strcmp(key, "prefix")   == 0) out.prefix   = json_object_get_string(val);
        else if (std::strcmp(key, "nexthops") == 0) out.nexthops = parse_addr_list(val);
        else std::cerr << "Unhandled key in route event: " << key << "\n";
    }
    return out;
}

static DownstreamMsgs parse_downstream_msgs(json_object* arr) {
    DownstreamMsgs out;
    size_t n = json_object_array_length(arr);
    out.reserve(n);
    for (size_t i = 0; i < n; ++i) {
        out.push_back(parse_route_event(json_object_array_get_idx(arr, i)));
    }
    return out;
}

static TestCase parse_test_case(json_object* obj) {
    TestCase out{};
    json_object_object_foreach(obj, key, val) {
        if      (std::strcmp(key, "TestId")         == 0) out.test_id         = json_object_get_int(val);
        else if (std::strcmp(key, "Op")             == 0) out.op              = json_object_get_string(val);
        else if (std::strcmp(key, "InitialState")   == 0) out.initial_state   = parse_state(val);
        else if (std::strcmp(key, "ApiParam")       == 0) out.api_param       = parse_api_param(val);
        else if (std::strcmp(key, "FinalState")     == 0) out.final_state     = parse_state(val);
        else if (std::strcmp(key, "DownstreamMsgs") == 0) out.downstream_msgs = parse_downstream_msgs(val);
        else std::cerr << "Unhandled key in test case: " << key << "\n";
    }
    return out;
}

std::vector<TestCase> read_test_cases(const std::string& path) {
    json_object* root = json_object_from_file(path.c_str());
    if (!root) {
        throw std::runtime_error("Failed to load JSON: " + path);
    }
    if (!json_object_is_type(root, json_type_array)) {
        json_object_put(root);
        throw std::runtime_error("Expected top-level JSON array in: " + path);
    }
    size_t n = json_object_array_length(root);
    std::vector<TestCase> out;
    out.reserve(n);
    for (size_t i = 0; i < n; ++i) {
        out.push_back(parse_test_case(json_object_array_get_idx(root, i)));
    }
    json_object_put(root);
    return out;
}
