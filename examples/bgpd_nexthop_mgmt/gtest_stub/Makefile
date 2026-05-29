CXX      ?= clang++
CXXFLAGS := -std=c++17 -Wall -Wextra -O0 -g
LDLIBS   := -ljson-c

# json-c lives under Homebrew on macOS. Detect either an Apple-silicon
# (/opt/homebrew) or Intel (/usr/local) prefix at build time.
JSON_C_PREFIX := $(shell brew --prefix json-c 2>/dev/null)
ifneq ($(JSON_C_PREFIX),)
  CXXFLAGS += -I$(JSON_C_PREFIX)/include
  LDFLAGS  += -L$(JSON_C_PREFIX)/lib
endif

SRC := json_reader.cpp main.cpp
OBJ := $(SRC:.cpp=.o)
BIN := read_tests

all: $(BIN)

$(BIN): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS) $(LDLIBS)

%.o: %.cpp common_data.h json_reader.h
	$(CXX) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJ) $(BIN)

.PHONY: all clean
