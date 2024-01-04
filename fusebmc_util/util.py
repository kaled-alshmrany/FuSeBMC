import os
#import sys
#import zipfile
import hashlib
import string
import random
import struct
from datetime import datetime
import traceback
import argparse
from decimal import Decimal
from .consts import *
from .inputtype import InputType
from .tcolors import TColors


class FuSeBMCProcessName:
	Afl_fuzz = 1
	Tracer_EXE = 2
	Instrument = 3
	SeedGen = 4
	
class Result:
	success = 1
	fail_deref = 2
	fail_memtrack = 3
	fail_free = 4
	fail_reach = 5
	fail_overflow = 6
	err_timeout = 7
	err_memout = 8
	err_unwinding_assertion = 9
	force_fp_mode = 10
	unknown = 11
	fail_memcleanup = 12
	fail_termination = 13
	#20.05.2020
	fail_cover_error_call = 14
	fail_cover_branches = 15
	
	@staticmethod
	def is_fail(res):
		if res == Result.fail_deref:
			return True
		if res == Result.fail_free:
			return True
		if res == Result.fail_memtrack:
			return True
		if res == Result.fail_overflow:
			return True
		if res == Result.fail_reach:
			return True
		if res == Result.fail_memcleanup:
			return True
		if res == Result.fail_termination:
			return True
		return False

	@staticmethod
	def is_out(res):
		if res == Result.err_memout:
			return True
		if res == Result.err_timeout:
			return True
		if res == Result.unknown:
			return True
		return False

class MyTimeOutException(Exception): pass
class Property:
	unreach_call = 1
	memsafety = 2
	overflow = 3
	termination = 4
	memcleanup = 5
	cover_branches = 6
	cover_error_call = 7
	no_data_race = 8

def parse_result(the_output, prop):
	# Parse output
	#if prop == Property.cover_error_call or prop == Property.cover_branches:
	#	raise Exception("Don't use parse_result for cover_error_call, cover_branches.!!")
	if "Timed out" in the_output:
		return Result.err_timeout
	if "Out of memory" in the_output:
		return Result.err_memout
	
	if "Chosen solver doesn\'t support floating-point numbers" in the_output:
		return Result.force_fp_mode

	# Error messages:
	memory_leak = "dereference failure: forgotten memory"
	invalid_pointer = "dereference failure: invalid pointer"
	access_out = "dereference failure: Access to object out of bounds"
	dereference_null = "dereference failure: NULL pointer"
	expired_variable = "dereference failure: accessed expired variable pointer"
	invalid_object = "dereference failure: invalidated dynamic object"
	invalid_object_free = "dereference failure: invalidated dynamic object freed"
	invalid_pointer_free = "dereference failure: invalid pointer freed"
	free_error = "dereference failure: free() of non-dynamic memory"
	bounds_violated = "array bounds violated"
	free_offset = "Operand of free must have zero pointer offset"
	if "VERIFICATION FAILED" in the_output:
		if "unwinding assertion loop" in the_output:
			return Result.err_unwinding_assertion
		
		if prop == Property.memcleanup:
			if memory_leak in the_output:
				return Result.fail_memcleanup
		if prop == Property.termination:
			return Result.fail_termination
		if prop == Property.memsafety:
			if memory_leak in the_output:
				return Result.fail_memtrack
			if invalid_pointer_free in the_output:
				return Result.fail_free
			if invalid_object_free in the_output:
				return Result.fail_free
			if expired_variable in the_output:
				return Result.fail_deref
			if invalid_pointer in the_output:
				return Result.fail_deref
			if dereference_null in the_output:
				return Result.fail_deref
			if free_error in the_output:
				return Result.fail_free
			if access_out in the_output:
				return Result.fail_deref
			if invalid_object in the_output:
				return Result.fail_deref
			if bounds_violated in the_output:
				return Result.fail_deref
			if free_offset in the_output:
				return Result.fail_free
			if " Verifier error called" in the_output:
				return Result.success
		if prop == Property.overflow:
			return Result.fail_overflow
		if prop == Property.unreach_call:
			return Result.fail_reach
	if "VERIFICATION SUCCESSFUL" in the_output:
		return Result.success
	return Result.unknown

def get_result_string(the_result):
	if the_result == Result.fail_memcleanup: return "FALSE_MEMCLEANUP"
	if the_result == Result.fail_memtrack: return "FALSE_MEMTRACK"
	if the_result == Result.fail_free: return "FALSE_FREE"
	if the_result == Result.fail_deref: return "FALSE_DEREF"
	if the_result == Result.fail_overflow: return "FALSE_OVERFLOW"
	if the_result == Result.fail_reach: return "FALSE_REACH"
	if the_result == Result.fail_termination: return "FALSE_TERMINATION"
	if the_result == Result.success: return "TRUE"
	if the_result == Result.err_timeout: return "Timed out"
	if the_result == Result.err_unwinding_assertion: return "Unknown"
	if the_result == Result.err_memout: return "Unknown"
	if the_result == Result.unknown: return "Unknown"
	exit(0)
'''
def get_result_string(the_result):
	# TODO: What is the output
	if the_result == Result.fail_cover_error_call: return "FAIL_COVER_ERROR_CALL"
	if the_result == Result.fail_cover_branches: return "FAIL_COVER_BRANCHES"
	if the_result == Result.fail_memcleanup: return "FALSE_MEMCLEANUP"
	
	if the_result == Result.fail_memtrack: return "Unknown" #return "FALSE_MEMTRACK"
	if the_result == Result.fail_free: return "Unknown" #return "FALSE_FREE"
	if the_result == Result.fail_deref: return "Unknown" #return "FALSE_DEREF"
	
	if the_result == Result.fail_overflow: return "FALSE_OVERFLOW"
	if the_result == Result.fail_reach: return "FALSE_REACH"
	if the_result == Result.fail_termination: return "FALSE_TERMINATION"
	if the_result == Result.success: return "TRUE" #return "DONE"
	if the_result == Result.err_timeout: return "Timed out"
	if the_result == Result.err_unwinding_assertion: return "Unknown"
	if the_result == Result.err_memout: return "Unknown"
	if the_result == Result.unknown: return "Unknown"
	exit(0)
'''
'''
def get_result_string(the_result):
	if the_result == Result.fail_memcleanup: return "FALSE_MEMCLEANUP"
	if the_result == Result.fail_memtrack: return "FALSE_MEMTRACK"
	if the_result == Result.fail_free: return "FALSE_FREE"
	if the_result == Result.fail_deref: return "FALSE_DEREF"
	if the_result == Result.fail_overflow: return "FALSE_OVERFLOW"
	if the_result == Result.fail_reach: return "DONE"
	if the_result == Result.success: return "DONE"
	if the_result == Result.err_timeout: return "Timed out"
	if the_result == Result.err_unwinding_assertion: return "Unknown"
	
	# TODO: What is the output
	if the_result == Result.fail_cover_error_call: return "FAIL_COVER_ERROR_CALL"	
	if the_result == Result.fail_cover_branches: return "FAIL_COVER_BRANCHES"
	if the_result == Result.err_memout: return "Unknown"
	if the_result == Result.unknown: return "TIMEOUT"
	exit(0)
'''
def GetPropertyFromFile(property_file):
	f = open(property_file, 'r')
	property_file_content = f.read()
	if "CHECK( init(main()), LTL(G valid-free) )" in property_file_content:
		return Property.memsafety, property_file_content
	elif "CHECK( init(main()), LTL(G valid-memcleanup) )" in property_file_content:
		return Property.memcleanup,property_file_content
	elif "CHECK( init(main()), LTL(G ! overflow) )" in property_file_content:
		return Property.overflow,property_file_content
	#elif "CHECK( init(main()), LTL(G ! call(__VERIFIER_error())) )" in property_file_content:
	elif "CHECK( init(main()), LTL(G ! call(reach_error())) )" in property_file_content:
		return Property.unreach_call,property_file_content
	elif "CHECK( init(main()), LTL(F end) )" in property_file_content:
		return Property.termination,property_file_content
	#20.05.2020 TODO : remove reach
	#elif "COVER( init(main()), FQL(COVER EDGES(@CALL(__VERIFIER_error))) )" in property_file_content:
	#	category_property = Property.cover_error_call
	elif "COVER( init(main()), FQL(COVER EDGES(@CALL(reach_error))) )" in property_file_content:
		return Property.cover_error_call,property_file_content
	#elif "COVER( init(main()), FQL(COVER EDGES(@CALL(__VERIFIER_error))) )" in property_file_content:
	#	category_property = Property.unreach_call
	elif "COVER( init(main()), FQL(COVER EDGES(@DECISIONEDGE)) )" in property_file_content:
		return Property.cover_branches,property_file_content
	elif "CHECK( init(main()), LTL(G ! data-race) )" in property_file_content:
		return Property.no_data_race, property_file_content
	else:
		print ("Unsupported Property",property_file)
		return None,property_file_content

def getLinesCountInFile(pFilePath):
	line_count = 0
	file = open(pFilePath, 'r')
	for line in file:
		if line != '\n' : line_count += 1
	file.close()
	return line_count

def GetSH1ForFile(fil):
	BUF_SIZE = 32768
	sha1 = hashlib.sha1()
	with open(fil, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			sha1.update(data)
		return sha1.hexdigest()
	return ''
#https://stackoverflow.com/questions/10501247/best-way-to-generate-random-file-names-in-python?lq=1
def GenerateRondomFileName():
	return ''.join(random.choice(string.ascii_letters) for _ in range(5))

'''
def AddFileToArchive(full_file_name, zip_file_name):
	if not os.path.isfile(full_file_name): return
	os.makedirs(os.path.dirname(os.path.abspath(zip_file_name)), exist_ok=True)
	appendOrCreate='w'
	if os.path.isfile(zip_file_name): appendOrCreate='a'
	zipf = zipfile.ZipFile(zip_file_name, appendOrCreate , zipfile.ZIP_DEFLATED)
	zipf.write(os.path.abspath(full_file_name),os.path.basename(os.path.abspath(full_file_name)))
	zipf.close()
'''

'''def ZipDir(path, zip_file_name):
	os.makedirs(os.path.dirname(os.path.abspath(zip_file_name)), exist_ok=True)
	#RemoveFileIfExists(zip_file_name)
	zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
	for root, dirs, files in os.walk(os.path.abspath(path)):
		for file in files:
			zipf.write(os.path.join(root,file),file)
	zipf.close()
'''
def MakeFolderEmptyORCreate(flder):
	if os.path.isdir(flder):
		for file_loop in os.listdir(flder):
			file_to_del=os.path.join(flder, file_loop)
			if os.path.isfile(file_to_del):
				os.remove(file_to_del)
	else:
		os.mkdir(flder)

def RemoveFileIfExists(fil):
	if os.path.isfile(fil): os.remove(fil)

#is str a float 
def isfloat(p_str):
	try:
		a = float(p_str)
	except (TypeError, ValueError): return False
	else: return True

#is str an Int
def isint(p_str):
	try:
		a = float(p_str) ; b = int(p_str)
	except (TypeError, ValueError): return False
	else: return a == b

def GetGoalListFromFile(file_path):
	'''
	Returns a list of goals as int from the file.
	'''
	lstGoalsInFile = []
	if os.path.isfile(file_path):
		with open(file_path,'r') as f_covered:
			for line in f_covered:
				if line.startswith('#'):continue
				line_int = int(line)
				lstGoalsInFile.append(line_int)
	return lstGoalsInFile

def HandleException(ex, msg = '' ,mustExit = False):
	import traceback
	traceback.print_exc()
	now_s = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	if IS_DEBUG:
		print(TColors.FAIL)
		if msg != '' : print(msg)
		print(ex)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		if exc_tb is not None:
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
		print(TColors.ENDC)
		with open('./errorlog.log','a') as f:
			f.write(now_s+'\n')
			#f.write(benchmark +' '+str(arch)+' '+ str(category_property)+'\n')
			f.write(' '.join(sys.argv[0:])+'\n')
			if msg != '' : f.write(msg+'\n')
			f.write(str(ex)+'\n')
			if exc_tb is not None:
				f.write(str(exc_type)+' '+ fname + ' ' + str(exc_tb.tb_lineno)+'\n')
			f.write('******************************************\n')
		if mustExit : exit(1)
	#exit(0)

def WriteListInSeedFile(lst,seed_filename,numOfBytes = 4, p_signed = True):
	with open (seed_filename,'wb') as seed_f:
		for inp in lst:
			seed_f.write(inp.to_bytes(numOfBytes, byteorder=sys.byteorder, signed=p_signed))

def WriteTestcaseInSeedFile(assump_lst,seed_filename,arch):
	'''
	Write a Testcase (that is a list of nonDeterministicCall) in seed file stream.
	@Return: The size of the seed. 
	'''
	testcaseSize = 0
	try:
		with open(seed_filename, 'wb') as seed_f:
			for nonDeterministicCall in assump_lst:
				is_signed = not InputType.IsUnSigned(nonDeterministicCall.inputType)
				if nonDeterministicCall.inputType == InputType._string:
					bytesNum = len(nonDeterministicCall.value)
				else:
					bytesNum = InputType.GeSizeForDataType(nonDeterministicCall.inputType, arch)
				testcaseSize += bytesNum
				if(isint(nonDeterministicCall.value)):
					try:
						seed_f.write((int(nonDeterministicCall.value)).to_bytes(bytesNum, byteorder=sys.byteorder, signed=is_signed))
					except Exception as ex:
						HandleException(ex,'value='+str(nonDeterministicCall.value)+' bytesNum='+str(bytesNum),False)
						try:
							seed_f.write((int(nonDeterministicCall.value)).to_bytes(bytesNum, byteorder=sys.byteorder, signed=False))
						except Exception as ex:
							seed_f.write((int(0)).to_bytes(bytesNum, byteorder=sys.byteorder, signed=is_signed))
				elif (isfloat(nonDeterministicCall.value)):
					try:
						
						bytes_per_component = bytesNum / 4
						if bytes_per_component != 1 or bytes_per_component != 2 : bytes_per_component = 2
						for byte in struct.pack('!f' , float(nonDeterministicCall.value)):
							seed_f.write((int(byte)).to_bytes(bytes_per_component, byteorder=sys.byteorder, signed=False))
						
					except Exception as ex:
						HandleException(ex,f"write to seed, val={nonDeterministicCall.value}",False)
						try:
							b=struct.pack('@d' , Decimal(nonDeterministicCall.value))
							seed_f.write(b)
						except Exception as ex:
							seed_f.write((int(0)).to_bytes(bytesNum, byteorder=sys.byteorder, signed=is_signed))
						
				else:
					input_str = nonDeterministicCall.value + ''
					if input_str and not isinstance(input_str , bytes): input_str = input_str.encode()
					seed_f.write(input_str)
					if FuSeBMCFuzzerLib_COVERBRANCHES_NUM_BYTES_TO_ADD_TO_TC > 0 :
						for _ in range(0,FuSeBMCFuzzerLib_COVERBRANCHES_NUM_BYTES_TO_ADD_TO_TC):
							seed_f.write((int(0)).to_bytes(1, byteorder=sys.byteorder, signed=True))
							testcaseSize += 1
	except Exception as ex2: HandleException(ex2,'write to seed',False)
	return testcaseSize

def getArgs(pCmdLine = None):
	def check_positive(value: int)-> int:
		ivalue = int(value)
		if ivalue <= 0:
			raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
		return ivalue
	def check_max_k_step(value: int)-> int:
		ivalue = int(value)
		if ivalue < -2:
			raise argparse.ArgumentTypeError("%s is an invalid value: [-1:unlimited; -2;default; else the givien value]" % value)
		return ivalue
	# Options
	parser = argparse.ArgumentParser()
	parser.add_argument("-a", "--arch", help="Either 32 or 64 bits",type=int, choices=[32, 64], default=FuSeBMCParams.arch)
	parser.add_argument("-v", "--version",help="Prints ESBMC's version", action='store_true')
	parser.add_argument("-p", "--propertyfile", help="Path to the property file")
	parser.add_argument("benchmark", nargs='?', help="Path to the benchmark")
	#parser.add_argument("-s", "--strategy", help="ESBMC's strategy",choices=["kinduction", "falsi", "incr"], default="incr")
	#parser.add_argument("-z", "--zip_path", help="the tesuite Zip file to generate", default=None)
	parser.add_argument("-o", "--output", help="the output for of this run", default=None)
	#parser.add_argument("-t", "--timeout", help="time out seconds",type=float)
	parser.add_argument('--timeout', dest='time_out_s', help="Timeout in seconds", type=int, default=FuSeBMCParams.time_out_s)
	parser.add_argument("-s", "--strategy", help="ESBMC's strategy", choices=["kinduction", "falsi", "incr", "fixed"], default="fixed")
	parser.add_argument("-c", "--concurrency", help="Set concurrency flags", action='store_true')
	parser.add_argument("--run-testcov", dest='RunTestCov', help="Run TestCov Verifier", action='store_true', default=FuSeBMCParams.RunTestCov)
	parser.add_argument("--verbose", dest='SHOW_ME_OUTPUT', help="Show messages verbose (default: False)", action='store_true', default=FuSeBMCParams.SHOW_ME_OUTPUT)
	parser.add_argument("--result-dir", dest='ResultDir', help="Set the results output directory", default=FuSeBMCParams.ResultDir)
	parser.add_argument("--encoding", dest='encoding', help="ESBMC's encoding", choices=["floatbv", "fixedbv"], default="floatbv")
	parser.add_argument("--solver",dest='solver', help="ESBMC's solver", choices=["boolector", "z3"], default="boolector")
	
	
	parser.add_argument("--fuzzer-cover-branches-1", dest='FuzzerCoverBranches1', help="Enable Fuzzer 1 in CoverBranches", choices=["0", "1"], default=FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED)
	parser.add_argument('--fuzzer-cover-branches-1-time', dest='FuzzerCoverBranches1Time', help="Time of Fuzzer 1 in CoverBranches", type=int, default=FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT)
	
	parser.add_argument("--fuzzer-cover-branches-2", dest='FuzzerCoverBranches2', help="Enable Fuzzer 2 in CoverBranches", choices=["0", "1"], default=FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED)
	parser.add_argument('--fuzzer-cover-branches-2-time', dest='FuzzerCoverBranches2Time', help="Time of Fuzzer 2 in CoverBranches", type=int, default=FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT_2)
	
	parser.add_argument('--goal-tracer', dest='GoalTracer', help="Enable GoalTracer in CoverBranches", choices=["0", "1"], default=FuSeBMCParams.FuSeBMC_GoalTracer_ENABLED)
	parser.add_argument('--goal-sorting', dest='GoalSorting', help="GoalSorting in CoverBrances: "+
						str(GoalSorting.DEPTH_THEN_TYPE)+': ' + GoalSorting.toString(GoalSorting.DEPTH_THEN_TYPE)+', '+
						str(GoalSorting.TYPE_THEN_DEPTH)+': ' + GoalSorting.toString(GoalSorting.TYPE_THEN_DEPTH)+', '+
						str(GoalSorting.SEQUENTIAL)+': ' + GoalSorting.toString(GoalSorting.SEQUENTIAL),
						type=int,
					choices=[GoalSorting.DEPTH_THEN_TYPE, GoalSorting.TYPE_THEN_DEPTH, GoalSorting.SEQUENTIAL], default=FuSeBMCParams.goalSorting)
	
	parser.add_argument("--global-depth", dest='GlobalDepth', help='Use Global depth of goals instead of local depth', choices=["0", "1"], default=FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH)
	parser.add_argument('--cover-branches-num-testcases-to-run-afl', dest='FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL', help="Number of Testcases to Run AFL in CoverBranches", \
					type=check_positive, default=FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL)
	parser.add_argument("--fuzzer-error-call-1", dest='FuSeBMCFuzzerLib_ERRORCALL_ENABLED', help='Enable Fuzzer 1 in Error-Call', choices=["0", "1"], default=FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_ENABLED)
	parser.add_argument('--fuzzer-error-call-1-time', dest='FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT', help="Time of Fuzzer 1 in Error-Call", type=int, default=FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT)
	parser.add_argument("--fuzzer-error-call-2", dest='FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED', help='Enable Fuzzer 2 in Error-Call', choices=["0", "1"], default=FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED)
	parser.add_argument('--fuzzer-error-call-2-time', dest='FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT_2', help="Time of Fuzzer 2 in Error-Call", type=int, default=FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT_2)
	parser.add_argument('--esbmc-error-call-run-1-time', dest='ERRORCALL_ESBMC_RUN1_TIMEOUT', help="Time of ESBMC Run 1 in Error-Call", type=int, default=FuSeBMCParams.ERRORCALL_ESBMC_RUN1_TIMEOUT)
	parser.add_argument('--seeds-num-fuzzer1-error-call', dest='FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_SEEDS_NUM', help="Number of Seeds to be generated for Fuzzer 1 in Error-Call", type=int, default=FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_SEEDS_NUM)
	parser.add_argument('--run-esbmc-twice-error-call', dest='ERRORCALL_RUNTWICE_ENABLED', help='Run ESBMC Twice in Error-Call', choices=["0", "1"], default=FuSeBMCParams.ERRORCALL_RUNTWICE_ENABLED)
	parser.add_argument('--handle-infinite-while-loop-error-call', dest='ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED', help='Handle Infinite-while loops in Error-Call', choices=["0", "1"], default=FuSeBMCParams.ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED)
	parser.add_argument('--error-call-infinite-while-loop-increment-time', dest='ERRORCALL_INFINITE_WHILE_TIME_INCREMENT', help="Extra Time for Infinite-while loops in Error-Call", type=int, default=FuSeBMCParams.ERRORCALL_INFINITE_WHILE_TIME_INCREMENT)
	
	parser.add_argument('--ml', dest='ML', help="Machine Learning operation: "+
						str(Feature.NONE)+': nothing to do, ' +
						str(Feature.ExtractFeaturesOnly)+': Only extaract features from source code, '+
						str(Feature.PredicateParams)+': extract features and predicate FuSeBMC parameters values ' ,
						type=int,
						choices=[Feature.NONE, Feature.ExtractFeaturesOnly, Feature.PredicateParams], default=FuSeBMCParams.ML)
	parser.add_argument('--ml-model', dest='MLModel', help="Machine Learning model: "+
						str(ModelType.DTC)+': Decision Tree Classifier, ' +
						str(ModelType.SVC)+': C-Support Vector Classification, '+
						str(ModelType.NRR)+': Multi-layer Perceptron regressor ' +
						str(ModelType.MULTI_MODEL)+': Multi.models dtc then svc then nnr ',
						type=int,
						choices=[ModelType.DTC, ModelType.SVC, ModelType.NRR, ModelType.MULTI_MODEL],
						default=FuSeBMCParams.MLModel)
	parser.add_argument('--handle-infinite-while-loop-cover-branches', dest='COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED', help='Handle Infinite-while loops in Cover-Branches', choices=["0", "1"], default=FuSeBMCParams.COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED)
	parser.add_argument('--cover-branches-infinite-while-loop-increment-time', dest='COVERBRANCHES_INFINITE_WHILE_TIME_INCREMENT', help="Extra Time for Infinite-while loops in Cover-Branches", type=int, default=FuSeBMCParams.COVERBRANCHES_INFINITE_WHILE_TIME_INCREMENT)
	
	parser.add_argument('--cover-branches-selective-inputs-enable', dest='COVERBRANCHES_SELECTIVE_INPUTS_ENABLED', help='Extract Selective Inputs in Cover-Branches', choices=["0", "1"], default=FuSeBMCParams.COVERBRANCHES_SELECTIVE_INPUTS_ENABLED)
	parser.add_argument('--cover-branches-selective-inputs-increment-time', dest='COVERBRANCHES_SELECTIVE_INPUTS_TIME_INCREMENT', help="Extra Time for Selective Inputs in Cover-Branches", type=int, default=FuSeBMCParams.COVERBRANCHES_SELECTIVE_INPUTS_TIME_INCREMENT)
	
	parser.add_argument('--error-call-selective-inputs-enable', dest='ERRORCALL_SELECTIVE_INPUTS_ENABLED', help='Extract Selective Inputs in ErrorCall', choices=["0", "1"], default=FuSeBMCParams.ERRORCALL_SELECTIVE_INPUTS_ENABLED)
	parser.add_argument('--error-call-selective-inputs-increment-time', dest='ERRORCALL_SELECTIVE_INPUTS_TIME_INCREMENT', help="Extra Time for Selective Inputs in Error-Call", type=int, default=FuSeBMCParams.ERRORCALL_SELECTIVE_INPUTS_TIME_INCREMENT)
	
	parser.add_argument('--max-k-step', dest='MAX_K_STEP', help="the value of '--max-k-step' parameter in ESBMC.", \
					type=int, default=FuSeBMCParams.MAX_K_STEP)
	parser.add_argument('--unwind', dest='UNWIND', help="the value of '--unwind' parameter in ESBMC.", \
					type=int, default=FuSeBMCParams.UNWIND)
	parser.add_argument('--k-step', dest='k_step', help="the value of '--k-step' parameter in ESBMC.", \
					type=int, default=FuSeBMCParams.k_step)
	parser.add_argument('--context-bound', dest='contextBound', help="the value of '--context-bound' parameter in ESBMC.", \
					type=int, default=FuSeBMCParams.contextBound)
	parser.add_argument('--context-bound-step', dest='contextBoundStep', help="the value of '--context-bound-step' parameter in ESBMC.", \
					type=int, default=FuSeBMCParams.contextBoundStep)
	parser.add_argument('--max-context-bound', dest='maxContextBound', help="the value of '--max-context-bound' parameter in ESBMC.", \
					type=int, default=FuSeBMCParams.maxContextBound)
	parser.add_argument('--max-inductive-step', dest='maxInductiveStep', help="the value of '--max-inductive-step' parameter in ESBMC.", \
					type=int, default=FuSeBMCParams.maxInductiveStep)
	parser.add_argument("--add-symex-value-sets", dest='addSymexValueSets', help='enable/disable --add-symex-value-sets parmameter in ESBMC', action='store_true', default=FuSeBMCParams.addSymexValueSets)
	
	if pCmdLine is None:
		args = parser.parse_args()
	else:
		args = parser.parse_args(pCmdLine)
	return args

def parseStrAsBool(val)->bool:
	if isinstance(val, str):
		if val == "1" :
			return True
		if val == "0":
			return False
	elif isinstance(val, bool):
		return val
	else:
		sys.exit(f"{val} has type = {type(val)} is invalid.")

