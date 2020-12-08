CLANG_BASE = /home/kaled/Downloads/clang_base
LLVM_BASE = /mnt/sda2/llvm-6.0.0
CXX = $(CLANG_BASE)/bin/clang++
#CXX= clang++
#
CXXFLAGS = -Wall -Wextra -W -std=c++11 -I./include
CXXFLAGS += -I$(CLANG_BASE)/include -I$(LLVM_BASE)/include  -fno-rtti  -Wno-unsequenced -Wno-unused-parameter
LDFLAGS = -L$(CLANG_BASE)/lib -L$(LLVM_BASE)/lib
LDLIBS = -lclangFrontend -lclangParse -lclangSema -lclangEdit -lclangAnalysis -lclangAST -lclangLex -lclangBasic -lclangDriver \
		-lclangSerialization -lpthread -lclangRewrite -lLLVMOption -lLLVMProfileData -lLLVMMCParser -lLLVMMC -lLLVMBitReader -lLLVMCore -lLLVMBinaryFormat -lLLVMSupport
EXE = FuSeBMC_inustrment
SRC_DIR = src
INCLUDE_DIR = include
OBJ_DIR = obj
HEADER = $(wildcard $(INCLUDE_DIR)/*.h)
SRC = $(wildcard $(SRC_DIR)/*.cpp)
OBJ = $(SRC:$(SRC_DIR)/%.cpp=$(OBJ_DIR)/%.o)
.PHONY: all clean debug release
debug: CXXFLAGS += -g -o0 -DMYDEBUG
debug: all

release: CXXFLAGS += -o3 -os
release: all
all: $(EXE)
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp $(INCLUDE_DIR)/%.h
	$(CXX) $(CXXFLAGS) $(CFLAGS) -c $< -o $@
$(EXE): $(OBJ)
	$(CXX) $(LDFLAGS) $^ $(LDLIBS) -o $@

clean:
	rm -f $(OBJ_DIR)/*.o
	rm -f $(EXE)
