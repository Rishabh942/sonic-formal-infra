#ifndef JSON_READER_H
#define JSON_READER_H

#include <string>
#include <vector>

#include "common_data.h"

// Read a formatted test-case JSON file (the artifact emitted by
// examples/bgpd_nexthop_mgmt/format_tests.py). Returns the cases in
// file order. Throws std::runtime_error on file-load failure or
// malformed top-level structure.
std::vector<TestCase> read_test_cases(const std::string& path);

#endif // JSON_READER_H
