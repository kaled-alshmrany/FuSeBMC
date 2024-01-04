import os
import sys

from fusebmc_util.goalsorting import GoalSorting
from fusebmc_ml.Feature import Feature, ModelType

ESBMC_EXE = './FuSeBMC_engines/ESBMC/esbmc '
ESBMC_CONCURRENCY_EXE = './FuSeBMC_engines/ESBMC_concurrency/esbmc '
ESBMC7_EXE = './FuSeBMC_engines/ESBMC7/esbmc '
ESBMC_SVCOMP = './FuSeBMC_engines/ESBMC_SVCOMP/esbmc '
ESBMC7_4_0_EXE = './FuSeBMC_engines/ESBMC7.4.0/bin/esbmc '

ESBMC_EXE = ESBMC_EXE
IS_DEBUG = True

MAX_NUM_OF_LINES_OUT = 50
MAX_NUM_OF_LINES_ERRS = 50

IS_TIME_OUT_ENABLED = True
MUST_COMPILE_INSTRUMENTED = False

MUST_GENERATE_RANDOM_TESTCASE = True
MUST_ADD_EXTRA_TESTCASE = True

MUST_APPLY_TIME_PER_GOAL = True
MUST_APPLY_LIGHT_INSTRUMENT_FOR_BIG_FILES = not True

MEM_LIMIT_BRANCHES_ESBMC = 10 # giga ; Zero or negative means unlimited. 
MEM_LIMIT_BRANCHES_MAP2CHECK = 1000 # miga

MEM_LIMIT_ERROR_CALL_ESBMC = 10
MEM_LIMIT_ERROR_CALL_MAP2CHECK = 1000 # miga
MEM_LIMIT_MEM_OVERFLOW_REACH_TERM_MAP2CHECK = 1000 # miga

MEM_LIMIT_ESBMC = 10 # GiGA: Memory limit for other properties.

#MAX_VIRTUAL_MEMORY = 8 #GIGA

BIG_FILE_LINES_COUNT = 8000

AFL_HOME_PATH = os.path.abspath('./FuSeBMC_engines/AFL/')

#MAP2CHECK_EXE = os.path.abspath('./map2check/map2check ')
MAP2CHECK_EXE = os.path.abspath('./map2check-fuzzer/map2check ')
#MAP2CHECK_TIMEOUT= 150 #seconds
MAP2CHECK_ERRORCALL_SYMEX_TIMEOUT = 40 #seconds
MAP2CHECK_ERRORCALL_FUZZER_TIMEOUT = 150 #seconds

MAP2CHECK_ERRORCALL_SYMEX_ENABLED = False
MAP2CHECK_ERRORCALL_FUZZER_ENABLED = False

MAP2CHECK_COVERBRANCHES_ENABLED = not True 
MAP2CHECK_COVERBRANCHES_TIMEOUT = 70 #seconds

MAP2CHECK_MEM_OVERFLOW_REACH_TERM_ENABLED = not True
MAP2CHECK_MEM_OVERFLOW_REACH_TERM_FUZZER_TIMEOUT = 150 #seconds


FUSEBMC_INSTRUMENT_EXE_PATH = os.path.abspath('./FuSeBMC_instrument/FuSeBMC_instrument')

C_COMPILER = 'gcc'



#for ESBMC, Fuzzer and SeedGen.
#ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED = True
#ERRORCALL_INFINITE_WHILE_LOOP_LIMIT = 20


#for ESBMC, Fuzzer and Tracer.

#COVERBRANCHES_INFINITE_WHILE_LOOP_LIMIT = 20

COVERBRANCHES_HANDLE_REPEATED_TESTCASES_ENABLED =  True

MEM_OVERFLOW_REACH_TERM_RUNTWICE_ENABLED = not True



FuSeBMC_GoalTracer_CC = 'gcc' 
FuSeBMC_GoalTracer_CC_PARAMS = ''
FuSeBMC_GoalTracer_MEM_LIMIT = 5 # Giga


FuSeBMCFuzzerLib_ERRORCALL_USE_SEED_FROM_ESBMC1 = True

#FuSeBMCFuzzerLib_ERRORCALL_FORCE_RUN2 : run Fuzzer2 ignoring result from Fuzzer1
#FuSeBMCFuzzerLib_ERRORCALL_FORCE_RUN2 = False and FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED
FuSeBMCFuzzerLib_ERRORCALL_FORCE_RUN2 = False
FuSeBMCFuzzerLib_ERRORCALL_SEED_EXPAND_MAX_SIZE = 256 # 0  is disabled


#FuSeBMCFuzzerLib_ERRORCALL_CC = AFL_HOME_PATH+ '/afl-gcc'
FuSeBMCFuzzerLib_ERRORCALL_CC = AFL_HOME_PATH+ '/afl-gcc'
FuSeBMCFuzzerLib_ERRORCALL_CC_PARAMS = ''

FuSeBMCFuzzerLib_ERRORCALL_SELECTIVE_INPUTS_ITERATIONS = 500

FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_CC = 'gcc'
FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_CC_PARAMS = FuSeBMCFuzzerLib_ERRORCALL_CC_PARAMS

FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_MEM_LIMIT = 5 # Giga

FuSeBMCFuzzerLib_ERRORCALL_FUSEBMC_STAGE_ITERATION_INFINITE_WHILE = 100
#FuSeBMCFuzzerLib_ERRORCALL_FUSEBMC_STAGE_ITERATION_NON_INFINITE_WHILE = 2
FuSeBMCFuzzerLib_ERRORCALL_EXTRACT_SINGLEVAL_MAXLEN_FROM_TC = True
#SF = Selective Fuzzer
FuSeBMCFuzzerLib_ERRORCALL_FUSEBMC_SF_STAGE_ITERATION = 3
FuSeBMCFuzzerLib_ERRORCALL_FUZZED_APP_TIMEOUT = '120000+' # string; millisecond;+ means tolerence
FuSeBMCFuzzerLib_ERRORCALL_FUZZED_APP_MEM_LIMIT = '5G' # string

#ERRORCALL_INFINITE_WHILE_TIME_INCREMENT = 10 #seconds
#

################## COVER-BRANCHES ###############################


FuSeBMCFuzzerLib_COVERBRANCHES_SEED_EXPAND_MAX_SIZE = 256 # 0  is disabled



#FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES = 0 #Don't change it; The number og generated testcases from cover-Branches.We have lstFuzzerSeeds
#xxxx
FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_SEEDS_NUM_MIN = 4 # minimum Number of seeds for the second run of AFL
FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_SEEDS_NUM_MAX = 7 
FuSeBMCFuzzerLib_COVERBRANCHES_BYTES_PER_NUMBER = 8 


FuSeBMCFuzzerLib_COVERBRANCHES_DEFAULT_AFL_MIN_LENGTH = 36 # bytes ; you can change it ; -1: different lengths
FuSeBMCFuzzerLib_COVERBRANCHES_NUM_BYTES_TO_ADD_TO_TC = 8 # bytes to add to each testcase 
#FuSeBMCFuzzerLib_COVERBRANCHES_LOAD_EXTRAS_ENABLED = not True


FuSeBMCFuzzerLib_COVERBRANCHES_FUSEBMC_STAGE_ITERATION_INFINITE_WHILE = 100
#FuSeBMCFuzzerLib_COVERBRANCHES_FUSEBMC_STAGE_ITERATION_NON_INFINITE_WHILE = 2

# You can use clang with -fbracket-depth=100000 
FuSeBMCFuzzerLib_COVERBRANCHES_CC = AFL_HOME_PATH+ '/afl-gcc'
FuSeBMCFuzzerLib_COVERBRANCHES_CC_PARAMS = ''

FuSeBMCFuzzerLib_COVERBRANCHES_SELECTIVE_INPUTS_ITERATIONS = 500
FuSeBMCFuzzerLib_COVERBRANCHES_EXTRACT_SINGLEVAL_MAXLEN_FROM_TC = True
#SF = Selective Fuzzer
FuSeBMCFuzzerLib_COVERBRANCHES_FUSEBMC_SF_STAGE_ITERATION = 3
FuSeBMCFuzzerLib_COVERBRANCHES_FUZZED_APP_TIMEOUT = '30000+' # string; millisecond;+ means tolerence
FuSeBMCFuzzerLib_COVERBRANCHES_FUZZED_APP_MEM_LIMIT = '5G' # string



FuSeBMCFuzzerLib_TESTCASE_GEN_CC = 'gcc'
FuSeBMCFuzzerLib_TESTCASE_GEN_CC_PARAMS = ''

#FuSeBMCFuzzerLib_COVERBRANCHES_CC = 'clang'
#FuSeBMCFuzzerLib_COVERBRANCHES_CC_PARAMS = '-fbracket-depth=100000'

COVERBRANCHES_SHOW_UNIQUE_TESTCASES = not True




#goalSorting = GoalSorting.SEQUENTIAL
#goalSorting = GoalSorting.TYPE_THEN_DEPTH


goalSorting_IF_first = False # valid by DEPTH_THEN_TYPE
goalSorting_EMPTYELSE_last = True # valid by DEPTH_THEN_TYPE
goalSorting_AFTERLOOP_last = True # valid by DEPTH_THEN_TYPE
goalSorting_END_OF_FUN_last = True # valid by DEPTH_THEN_TYPE

################### our options for leatest Pre-run (12/11/2021) #############
MUST_APPLY_LIGHT_INSTRUMENT_FOR_BIG_FILES = not True
#FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT = 200 # second
#FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT = 250 # second
#FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED = True and FuSeBMCFuzzerLib_ERRORCALL_ENABLED



#ERRORCALL_ESBMC_RUN1_TIMEOUT = 60 # seconds timeout for light ESBMC



###############################################################################
class FuSeBMCParams:
	SVCOMP24_PRE_RUN = True
	ESBMC_Version = 6
	benchmark = ''
	arch = '32'
	propertyFile = ''
	strategy = ''
	solver = ''
	encoding = '--foatbv'
	concurrency = False
	#timeout = 890
	time_out_s = 890
	ResultDir = None
	WRAPPER_Output_Dir ='./fusebmc_output/'
	INSTRUMENT_Output_File = ''
	INSTRUMENT_Output_Goals_File = ''
	INSTRUMENT_Output_Dir = ''
	TestSuite_Dir = ''
	esbmc_dargs = ''
	is_ctrl_c = False
	forceStop = False
	version = False
	RunTestCov = False
	SHOW_ME_OUTPUT = True
	
	FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED = True
	FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED = True
	FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT = 250 # second
	FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT_2 = 600 # second
	
	FuSeBMC_GoalTracer_ENABLED = True
	goalSorting = GoalSorting.DEPTH_THEN_TYPE
	FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH = True
	FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL = 1
	
	FuSeBMCFuzzerLib_ERRORCALL_ENABLED = True
	FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED = True
	FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT = 500 # second
	FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT_2 = 100 # second
	ERRORCALL_RUNTWICE_ENABLED = True
	ERRORCALL_ESBMC_RUN1_TIMEOUT = 60 # seconds timeout for light ESBMC
	FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_SEEDS_NUM = 1 # Number of seeds to be generated
	ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED = True
	ERRORCALL_INFINITE_WHILE_TIME_INCREMENT = 10 #seconds
	
	ML = Feature.NONE
	MLModel = ModelType.DTC
	
	COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED = True
	COVERBRANCHES_INFINITE_WHILE_TIME_INCREMENT = 10 #seconds
	
	COVERBRANCHES_SELECTIVE_INPUTS_ENABLED = True
	COVERBRANCHES_SELECTIVE_INPUTS_TIME_INCREMENT = 550 #seconds
	
	ERRORCALL_SELECTIVE_INPUTS_ENABLED = True
	ERRORCALL_SELECTIVE_INPUTS_TIME_INCREMENT = 460 #seconds
	
	MAX_K_STEP = -1 # -1:unlimited; -2:default; else the given value
	UNWIND = 1
	k_step = 5
	COVERBRANCHES_ADD_GOAL_END_FUNC = False
	
	contextBound = 2
	contextBoundStep = 5
	maxContextBound = 15 #-1 --unlimited-context-bound 
	
	maxInductiveStep = 3
	addSymexValueSets = 0 # 0 disabled; 1 enabled
	
	@staticmethod
	def LoadDefaultValues():
		FuSeBMCParams.ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED = True
		FuSeBMCParams.ERRORCALL_INFINITE_WHILE_TIME_INCREMENT = 10 #seconds
		FuSeBMCParams.COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED = True
		FuSeBMCParams.COVERBRANCHES_INFINITE_WHILE_TIME_INCREMENT = 10 #seconds
		FuSeBMCParams.COVERBRANCHES_SELECTIVE_INPUTS_ENABLED = True
		FuSeBMCParams.COVERBRANCHES_SELECTIVE_INPUTS_TIME_INCREMENT = 500 #seconds
		FuSeBMCParams.ERRORCALL_SELECTIVE_INPUTS_ENABLED = True
		FuSeBMCParams.ERRORCALL_SELECTIVE_INPUTS_TIME_INCREMENT = 600 #seconds
		FuSeBMCParams.k_step = 5
		FuSeBMCParams.contextBound = 2
		FuSeBMCParams.maxInductiveStep = 3
		
	
	@staticmethod
	def SetupValues():
		FuSeBMCParams.INSTRUMENT_Output_File = FuSeBMCParams.WRAPPER_Output_Dir + '/fusebmc_instrument_output/instrumented.c'
		FuSeBMCParams.INSTRUMENT_Output_Dir = FuSeBMCParams.WRAPPER_Output_Dir + '/fusebmc_instrument_output/'
		FuSeBMCParams.INSTRUMENT_Output_Goals_File = FuSeBMCParams.INSTRUMENT_Output_Dir+'/goals.txt'
		FuSeBMCParams.TestSuite_Dir = FuSeBMCParams.WRAPPER_Output_Dir + "/test-suite/"
		FuSeBMCParams.benchmark = os.path.abspath(FuSeBMCParams.benchmark)
		FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED = FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED and FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED
		FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED = FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED and FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_ENABLED
		
########### LOCAL -  RUN #####################
#FuSeBMCFuzzerLib_ERRORCALL_SELECTIVE_INPUTS_ITERATIONS = 5000

#ERRORCALL_ESBMC_RUN1_TIMEOUT = 60
#MEM_LIMIT_BRANCHES_ESBMC = 2 # Giga
#MEM_LIMIT_ERROR_CALL_ESBMC = 2 #Giga
#FuSeBMCFuzzerLib_ERRORCALL_FORCE_RUN2 = True
#FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED = False
#SHOW_ME_OUTPUT = False
########### PRE - RUN #####################

FuSeBMCParams.SHOW_ME_OUTPUT = False
IS_DEBUG = False
MEM_LIMIT_BRANCHES_ESBMC = 8 # Giga
MEM_LIMIT_ERROR_CALL_ESBMC = 8 #Giga


########### BEGIN - MACHINE_LEARNING #####################
'''
MEM_LIMIT_BRANCHES_ESBMC = 7 # Giga
MEM_LIMIT_ERROR_CALL_ESBMC = 7 #Giga
MEM_LIMIT_ESBMC = 7 #Giga
'''
########### END   - MACHINE_LEARNING #####################
