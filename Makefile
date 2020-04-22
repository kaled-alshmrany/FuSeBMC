CLANG_BASE = /home/kaled/Downloads/clang_base
LLVM_BASE = /mnt/sda2/llvm-6.0.0

CXX = $(CLANG_BASE)/bin/clang++
CXXFLAGS = -g -fPIC -DPIC  -Wall -Wextra -W -std=c++11 -MD -MP  -pthread -std=c++11 -I./include
CXXFLAGS += -I$(CLANG_BASE)/include -I$(LLVM_BASE)/include  -fvisibility-inlines-hidden -Werror=date-time -Wno-unused-parameter -Wwrite-strings -Wcast-qual -Wno-missing-field-initializers -pedantic -Wno-long-long  -Wno-uninitialized -Wdelete-non-virtual-dtor -Wno-comment -fno-exceptions -fno-rtti -D_GNU_SOURCE -D_DEBUG -D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_LIMIT_MACROS 
#CXXFLAGS += 
#LLVM_LINK_COMPONENTS = support
#LDFLAGS = -g -lz -lrt -ldl -ltinfo -lpthread -lm -m64 
#-L/usr/lib/x86_64-linux-gnu
LDFLAGS = -fPIC -DPIC -L$(CLANG_BASE)/lib -L$(LLVM_BASE)/lib  -g -O2
#/mnt/sda2/llvm-6.0.0/bin/llvm-config --cxxflags
#/mnt/sda2/llvm-6.0.0/bin/llvm-config --ldflags --libs
#LDFLAGS += -L/home/kaled/esbmc-6.0/src/esbmc/.libs 
#LDFLAGS += -L/home/kaled/esbmc-6.0/src/boolector/boolector/build
#LDFLAGS += -L/home/kaled/mathsat-5.5.4-linux-x86_64/lib 
#LDFLAGS += -L/home/kaled/clang_base/lib -L/mnt/sda2/llvm-6.0.0/lib
#LDLIBS = -lpthread -lLLVMCore -lLLVMLTO -lLLVMPasses -lLLVMObjCARCOpts -lLLVMMIRParser -lLLVMSymbolize -lLLVMDebugInfoPDB \
	-lLLVMDebugInfoDWARF -lLLVMCoverage -lLLVMTableGen -lLLVMDlltoolDriver -lLLVMOrcJIT  \
	-lLLVMXCoreDisassembler -lLLVMXCoreCodeGen -lLLVMXCoreDesc -lLLVMXCoreInfo -lLLVMXCoreAsmPrinter \
	-lLLVMSystemZDisassembler -lLLVMSystemZCodeGen -lLLVMSystemZAsmParser -lLLVMSystemZDesc -lLLVMSystemZInfo \
	-lLLVMSystemZAsmPrinter -lLLVMSparcDisassembler -lLLVMSparcCodeGen -lLLVMSparcAsmParser -lLLVMSparcDesc \
	-lLLVMSparcInfo -lLLVMSparcAsmPrinter -lLLVMPowerPCDisassembler -lLLVMPowerPCCodeGen -lLLVMPowerPCAsmParser \
	-lLLVMPowerPCDesc -lLLVMPowerPCInfo -lLLVMPowerPCAsmPrinter -lLLVMNVPTXCodeGen -lLLVMNVPTXDesc -lLLVMNVPTXInfo  \
	-lLLVMNVPTXAsmPrinter -lLLVMMSP430CodeGen -lLLVMMSP430Desc -lLLVMMSP430Info -lLLVMMSP430AsmPrinter  \
	-lLLVMMipsDisassembler -lLLVMMipsCodeGen -lLLVMMipsAsmParser -lLLVMMipsDesc -lLLVMMipsInfo -lLLVMMipsAsmPrinter  \
	-lLLVMLanaiDisassembler -lLLVMLanaiCodeGen -lLLVMLanaiAsmParser -lLLVMLanaiDesc -lLLVMLanaiAsmPrinter  \
	-lLLVMLanaiInfo -lLLVMHexagonDisassembler -lLLVMHexagonCodeGen -lLLVMHexagonAsmParser -lLLVMHexagonDesc  \
	-lLLVMHexagonInfo -lLLVMBPFDisassembler -lLLVMBPFCodeGen -lLLVMBPFAsmParser -lLLVMBPFDesc -lLLVMBPFInfo  \
	-lLLVMBPFAsmPrinter -lLLVMARMDisassembler -lLLVMARMCodeGen -lLLVMARMAsmParser -lLLVMARMDesc -lLLVMARMInfo  \
	-lLLVMARMAsmPrinter -lLLVMARMUtils -lLLVMAMDGPUDisassembler -lLLVMAMDGPUCodeGen -lLLVMAMDGPUAsmParser  \
	-lLLVMAMDGPUDesc -lLLVMAMDGPUInfo -lLLVMAMDGPUAsmPrinter -lLLVMAMDGPUUtils -lLLVMAArch64Disassembler  \
	-lLLVMAArch64CodeGen -lLLVMAArch64AsmParser -lLLVMAArch64Desc -lLLVMAArch64Info -lLLVMAArch64AsmPrinter  \
	-lLLVMAArch64Utils -lLLVMObjectYAML -lLLVMLibDriver -lLLVMOption -lLLVMWindowsManifest -lLLVMFuzzMutate \
	-lLLVMX86Disassembler -lLLVMX86AsmParser -lLLVMX86CodeGen -lLLVMGlobalISel -lLLVMSelectionDAG -lLLVMAsmPrinter  \
	-lLLVMDebugInfoCodeView -lLLVMDebugInfoMSF -lLLVMX86Desc -lLLVMMCDisassembler -lLLVMX86Info -lLLVMX86AsmPrinter -lLLVMX86Utils \
	-lLLVMMCJIT -lLLVMLineEditor -lLLVMInterpreter -lLLVMExecutionEngine -lLLVMRuntimeDyld -lLLVMCodeGen -lLLVMTarget  \
	-lLLVMCoroutines -lLLVMipo -lLLVMInstrumentation -lLLVMVectorize -lLLVMScalarOpts -lLLVMLinker -lLLVMIRReader -lLLVMAsmParser \
	-lLLVMInstCombine -lLLVMTransformUtils -lLLVMBitWriter -lLLVMAnalysis -lLLVMProfileData -lLLVMObject -lLLVMMCParser -lLLVMMC  \
	-lLLVMBitReader -lLLVMCore -lLLVMBinaryFormat -lLLVMSupport -lLLVMDemangle 
	#-lgtest_main -lgtest -lLLVMTestingSupport
	
#LDLIBS += -lclangTooling -lclangBasic -lclangASTMatchers  -lclangFrontend -lclangSerialization -lclangDriver \
           -lclangRewriteFrontend -lclangRewrite -lclangParse -lclangSema -lclangAnalysis \
           -lclangAST -lclangASTMatchers -lclangEdit -lclangLex -lclangBasic
#LDLIBS += -lclangTooling -lclangFrontendTool -lclangFrontend -lclangDriver -lclangSerialization -lclangCodeGen -lclangParse  \
	  -lclangSema   -lclangEdit  -lclangAnalysis -lclangDriver -lclangSerialization -lclangIndex -lclangRewrite \
	-lclangAST -lclangLex -lclangBasic 
#-lclangChecker -lgmp
LDLIBS = -lgomp  -lclangTooling -lclangFrontend -lclangParse -lclangSema -lclangEdit -lclangAnalysis -lclangAST -lclangLex -lclangBasic -lclangDriver -lclangASTMatchers \
	-lclangSerialization -lLLVMProfileData -lLLVMBitReader -lLLVMCore -lLLVMBinaryFormat -lLLVMOption -lLLVMMCParser -lLLVMMC -lLLVMSupport -lLLVMDemangle -lz -lrt -ldl -ltinfo -lpthread -lm -lclangTooling  -lclangRewrite  -lLLVMCore -lLLVMLTO -lLLVMPasses -lLLVMObjCARCOpts -lLLVMMIRParser -lLLVMSymbolize -lLLVMDebugInfoPDB \
	-lLLVMDebugInfoDWARF -lLLVMCoverage -lLLVMTableGen -lLLVMDlltoolDriver -lLLVMOrcJIT  \
	-lLLVMXCoreDisassembler -lLLVMXCoreCodeGen -lLLVMXCoreDesc -lLLVMXCoreInfo -lLLVMXCoreAsmPrinter \
	-lLLVMSystemZDisassembler -lLLVMSystemZCodeGen -lLLVMSystemZAsmParser -lLLVMSystemZDesc -lLLVMSystemZInfo \
	-lLLVMSystemZAsmPrinter -lLLVMSparcDisassembler -lLLVMSparcCodeGen -lLLVMSparcAsmParser -lLLVMSparcDesc \
	-lLLVMSparcInfo -lLLVMSparcAsmPrinter -lLLVMPowerPCDisassembler -lLLVMPowerPCCodeGen -lLLVMPowerPCAsmParser \
	-lLLVMPowerPCDesc -lLLVMPowerPCInfo -lLLVMPowerPCAsmPrinter -lLLVMNVPTXCodeGen -lLLVMNVPTXDesc -lLLVMNVPTXInfo  \
	-lLLVMNVPTXAsmPrinter -lLLVMMSP430CodeGen -lLLVMMSP430Desc -lLLVMMSP430Info -lLLVMMSP430AsmPrinter  \
	-lLLVMMipsDisassembler -lLLVMMipsCodeGen -lLLVMMipsAsmParser -lLLVMMipsDesc -lLLVMMipsInfo -lLLVMMipsAsmPrinter  \
	-lLLVMLanaiDisassembler -lLLVMLanaiCodeGen -lLLVMLanaiAsmParser -lLLVMLanaiDesc -lLLVMLanaiAsmPrinter  \
	-lLLVMLanaiInfo -lLLVMHexagonDisassembler -lLLVMHexagonCodeGen -lLLVMHexagonAsmParser -lLLVMHexagonDesc  \
	-lLLVMHexagonInfo -lLLVMBPFDisassembler -lLLVMBPFCodeGen -lLLVMBPFAsmParser -lLLVMBPFDesc -lLLVMBPFInfo  \
	-lLLVMBPFAsmPrinter -lLLVMARMDisassembler -lLLVMARMCodeGen -lLLVMARMAsmParser -lLLVMARMDesc -lLLVMARMInfo  \
	-lLLVMARMAsmPrinter -lLLVMARMUtils -lLLVMAMDGPUDisassembler -lLLVMAMDGPUCodeGen -lLLVMAMDGPUAsmParser  \
	-lLLVMAMDGPUDesc -lLLVMAMDGPUInfo -lLLVMAMDGPUAsmPrinter -lLLVMAMDGPUUtils -lLLVMAArch64Disassembler  \
	-lLLVMAArch64CodeGen -lLLVMAArch64AsmParser -lLLVMAArch64Desc -lLLVMAArch64Info -lLLVMAArch64AsmPrinter  \
	-lLLVMAArch64Utils -lLLVMObjectYAML -lLLVMLibDriver -lLLVMOption -lLLVMWindowsManifest -lLLVMFuzzMutate \
	-lLLVMX86Disassembler -lLLVMX86AsmParser -lLLVMX86CodeGen -lLLVMGlobalISel -lLLVMSelectionDAG -lLLVMAsmPrinter  \
	-lLLVMDebugInfoCodeView -lLLVMDebugInfoMSF -lLLVMX86Desc -lLLVMMCDisassembler -lLLVMX86Info -lLLVMX86AsmPrinter -lLLVMX86Utils \
	-lLLVMMCJIT -lLLVMLineEditor -lLLVMInterpreter -lLLVMExecutionEngine -lLLVMRuntimeDyld -lLLVMCodeGen -lLLVMTarget  \
	-lLLVMCoroutines -lLLVMipo -lLLVMInstrumentation -lLLVMVectorize -lLLVMScalarOpts -lLLVMLinker -lLLVMIRReader -lLLVMAsmParser \
	-lLLVMInstCombine -lLLVMTransformUtils -lLLVMBitWriter -lLLVMAnalysis -lLLVMProfileData -lLLVMObject -lLLVMMCParser -lLLVMMC  \
	-lLLVMBitReader -lLLVMCore -lLLVMBinaryFormat -lLLVMSupport -lLLVMDemangle
EXE = my_instrument

SRC_DIR = src
INCLUDE_DIR = include
OBJ_DIR = obj

HEADER = $(wildcard $(INCLUDE_DIR)/*.h)
SRC = $(wildcard $(SRC_DIR)/*.cpp)
OBJ = $(SRC:$(SRC_DIR)/%.cpp=$(OBJ_DIR)/%.o)

.PHONY: all clean
all: $(EXE)

$(EXE): $(OBJ)
	$(CXX) $(LDFLAGS) $^ $(LDLIBS) -o $@

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp $(INCLUDE_DIR)/%.h
	$(CXX) $(CXXFLAGS) $(CFLAGS) -c $< -o $@



#clean:
#	$(RM) $(OBJ)

my:
	#@echo $(CXX) $(LDFLAGS) $^ $(LDLIBS)
	@echo $(HEADER)
	@echo $(OBJ)
clean:
	rm -f $(OBJ_DIR)/*.o
	rm -f $(EXE)
