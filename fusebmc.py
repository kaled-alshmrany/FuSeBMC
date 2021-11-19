#!/usr/bin/env python3
import os
import sys
import os.path
import xml.etree.ElementTree as ET # To parse XML
import shlex
import subprocess
import signal
import time
import resource
import re
import shutil
import glob

#from time import process_time 
#from time import process_time_ns
from datetime import datetime
from random import randrange
import random


from fusebmc_util.util import *
from fusebmc_util.consts import *
from fusebmc_util.tcolors import TColors
from fusebmc_util.goaltype import GoalType
from fusebmc_util.goalinfo import GoalInfo
#from fusebmc_util.goalsorting import GoalSorting
from fusebmc_util.inputtype import InputType
from fusebmc_util.nonblockingstreamreader import NonBlockingStreamReader
from fusebmc_util.assumptions import AssumptionHolder, AssumptionParser, MetadataParser
from fusebmc_util.graph import Vertex, Graph,shortest,dijkstra
if RUN_TESTCOV: from fusebmc_util.testcov import *
#os.system('clear')
FUSEBMC_VERSION = 'v.4.1.11'

# Start time for this script
start_time = time.time()
#start_time=process_time()
property_file_content = ""
category_property = 0
benchmark=''
property_file=''
witness_file_name=''
toWorkSourceFile=''
arch=''
infinteWhileNum = 0

WRAPPER_Output_Dir ='./fusebmc_output/'
TestSuite_Dir = 'test-suite/'

INSTRUMENT_Output_Dir = './fusebmc_instrument_output/'
INSTRUMENT_Output_File = './fusebmc_instrument_output/instrumented.c'
INSTRUMENT_Output_Goals_File = './fusebmc_instrument_output/goals.txt'
#INSTRUMENT_OUTPUT_GOALS_DIR = './fusebmc_instrument_output/goals_output/'



map2checkWitnessFile='' # will be set later in the wrapper output

time_out_s = 890 # 890 seconds 
time_for_zipping_s = 10 # the required time for zipping folder; Can Zero ??
is_ctrl_c = False
remaining_time_s = 0

goals_count = 0

hasInputInTestcase = False
lastInputInTestcaseCount = 0

runNumber = 1

fuSeBMC_run_id =''

#important_outs_by_ESBMC=["Chosen solver doesn\'t support floating-point numbers"]

lineNumberForNonDetCallsLst = None
funcDeclInfoLst = None
funcCallInfoLst = None
mainFuncID = -1
callGraph = None
selectiveInputsLst = None
isSelectiveInputsFromMain = True

stdCFuncsLst = []
#lineNumberForNonDetCallsLst_Map2check = None
lstAllTestcases, lstFuzzerSeeds, lstFuzzerSeeds2 = [], [], [] # [(goal_id1,assumptioLst1),(goal_id2,assumptionLst2)]
lstFuSeBMC_GoalTracerGoals, lstFuSeBMC_FuzzerGoals = [], []
nRepeatedTCs = 0



FuSeBMCFuzzerLib_CoverBranches_Input_Covered_Goals_File = ''
FuSeBMCFuzzerLib_CoverBranches_Output_Covered_Goals_File = ''
FuSeBMCFuzzerLib_CoverBranches_Done = False
FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes = -1

important_outs_by_ESBMC=["Timed out","Out of memory","Chosen solver doesn\'t support floating-point numbers",
						"dereference failure: forgotten memory","dereference failure: invalid pointer",
						"dereference failure: Access to object out of bounds", "dereference failure: NULL pointer",
						"dereference failure: invalidated dynamic object", "dereference failure: invalidated dynamic object freed", 
						"dereference failure: invalid pointer freed","dereference failure: free() of non-dynamic memory","array bounds violated",
						"Operand of free must have zero pointer offset", "VERIFICATION FAILED", "unwinding assertion loop", 
						" Verifier error called", "VERIFICATION SUCCESSFUL"]
#def timeOutSigHandler(signum, frame):
#	print(TColors.FAIL,'Timeout signal recieved',TColors.ENDC)
#	with open (WRAPPER_Output_Dir + '/.timeout.txt','w') as f:
#		f.write('TIME OUT...... Ha')
#	exit(0)

current_process_name = ''
def limit_virtual_memory():
	global current_process_name
	#print('pid in limit_virtual_memory =',os.getpid())
	# The tuple below is of the form (soft limit, hard limit). Limit only
	# the soft part so that the limit can be increased later (setting also
	# the hard limit would prevent that).
	# When the limit cannot be changed, setrlimit() raises ValueError.
	 
	if current_process_name == FuSeBMCProcessName.Tracer_EXE:
		mem_limit = FuSeBMC_GoalTracer_MEM_LIMIT * 1024 * 1024 *1024
	elif current_process_name == FuSeBMCProcessName.SeedGen:
		mem_limit = FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_MEM_LIMIT * 1024 * 1024 *1024
	else:
		mem_limit = 5 * 1024 *1024 * 1024
	try:
		resource.setrlimit(resource.RLIMIT_AS, (mem_limit, resource.RLIM_INFINITY))
	except: pass
	try:
		resource.setrlimit(resource.RLIMIT_CORE, (0 ,resource.RLIM_INFINITY))
		resource.setrlimit(resource.RLIMIT_CORE, (0 ,0))
	except: pass
	try:
		os.system('ulimit -c 0')
	except: pass

#maxRSS = 0
def IsTimeOut(must_throw_ex = False):
	global is_ctrl_c
	global time_out_s
	global start_time
	global remaining_time_s
	#global maxRSS
	#global lasttime
	if is_ctrl_c is True: raise KeyboardInterrupt()
	if IS_TIME_OUT_ENABLED == False: return False

	#curr_gp_times = os.times()
	#user=curr_gp_times[0]
	#system=curr_gp_times[1]
	#children_user=curr_gp_times[2]
	#children_system=curr_gp_times[3]
	#exec_time_s = int(user + system + children_user + children_system)
	
	#if(exec_time_s != lasttime):
	#	lasttime=exec_time_s
	#	logText('exec_time_s=' + str(exec_time_s) + ' time_out_s:' + str(time_out_s) + '\n')

	end_time = time.time()
	wall_exec_time_s=(end_time - start_time)
	wall_remaining_time_s= time_out_s - wall_exec_time_s
	remaining_time_s = wall_remaining_time_s
	isWallTimeout = False
	if(wall_exec_time_s >= time_out_s):
		isWallTimeout = True
		if must_throw_ex:
			raise MyTimeOutException()

	#RUSAGE_CHILDREN
	ruSelf = resource.getrusage(resource.RUSAGE_SELF)
	rChild = resource.getrusage(resource.RUSAGE_CHILDREN)
	cpu_exec_time_s = (ruSelf.ru_utime + ruSelf.ru_stime + rChild.ru_utime + rChild.ru_stime)
	
	#current_RSS = ruSelf.ru_maxrss + rChild.ru_maxrss
	#if(current_RSS > maxRSS):
	#	maxRSS = current_RSS
	#	print(TColors.OKGREEN,'maxRSS:',maxRSS,TColors.ENDC)
	
	
	#print('cpu_exec_time_s',cpu_exec_time_s)

	cpu_remaining_time_s = time_out_s - cpu_exec_time_s
	if cpu_remaining_time_s < remaining_time_s :
		remaining_time_s = cpu_remaining_time_s

	isCpuTimeout = False
	if(cpu_exec_time_s >= time_out_s):
		isCpuTimeout = True
		if must_throw_ex:
			raise MyTimeOutException()

	return isWallTimeout or isCpuTimeout

def WriteMetaDataFromWrapper():
	now = datetime.now()
	Meta_Data_File = TestSuite_Dir + '/metadata.xml'
	with open(Meta_Data_File, 'w') as meta_f:
		meta_f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE test-metadata PUBLIC "+//IDN sosy-lab.org//DTD test-format test-metadata 1.0//EN" "https://sosy-lab.org/test-format/test-metadata-1.0.dtd">')
		meta_f.write('<test-metadata>')
		meta_f.write('<entryfunction>main</entryfunction>')
		meta_f.write('<specification>'+property_file_content.strip()+'</specification>')
		meta_f.write('<sourcecodelang>'+'C'+'</sourcecodelang>')
		_arch ='32bit'
		if arch == 64: _arch='64bit'
		meta_f.write('<architecture>'+_arch+'</architecture>')
		#meta_f.write('<creationtime>2020-07-27T21:33:51.462605</creationtime>')
		meta_f.write('<creationtime>'+now.strftime("%Y-%m-%dT%H:%M:%S.%f")+'</creationtime>')
		meta_f.write('<programhash>'+GetSH1ForFile(benchmark)+'</programhash>')
		meta_f.write('<producer>FuSeBMC ' + FUSEBMC_VERSION + '</producer>')
		meta_f.write('<programfile>'+benchmark+'</programfile>')
		meta_f.write('</test-metadata>')

class NonDeterministicCall(object):
	def __init__(self,value):
		"""
		Default constructor.
		Parameters
		----------
		value : str
			String containing value from input
		"""
		self.inputType = InputType.unkonwn
		assert(len(value) > 0)
		self.value = value

	def __str__(self):
		return "NonDeterministicCall: VALUE: {0}".format(self.value)
	@staticmethod
	def extract_byte_little_endian(value):
		"""
		Converts an byte_extract_little_endian(%d, %d) into an value
				Parameters
		----------
		value : str
			Nondeterministic assumption
		"""
		PATTERN = 'byte_extract_little_endian\((.+), (.+)\)'
		INT_BYTE_SIZE = 4
		match = re.search(PATTERN, value)
		if match == None:
			return value
		number = match.group(1)
		index = match.group(2)

		byte_value = (int(number)).to_bytes(INT_BYTE_SIZE, byteorder='little', signed=False)
		return str(byte_value[int(index)])


	@staticmethod
	def fromAssumptionHolder(pAssumptionHolder, isFromMap2Check = False):
		"""
		Converts an Assumption (that is nondet, this function will not verify this) into a NonDetermisticCall
		Parameters
		----------
		pAssumptionHolder : AssumptionHolder
			Nondeterministic assumption
		"""
		#value = NonDeterministicCall.extract_byte_little_endian(pAssumptionHolder.varVal)
		#return NonDeterministicCall(value)
		
		if isFromMap2Check:
			#assum_l,assum_r= assumption.split(' == ')
			#if assum_l.find('\\')== 0: assum_l = assum_l.replace('\\','',1)
			try:
				_,val = pAssumptionHolder.assumption.split(' == ')
			except Exception as ex:
				if IS_DEBUG:
					print(TColors.FAIL+ ' Error in File (fromAssumptionHolder,isFromMap2Check):'+ TColors.ENDC, benchmark)
				val = '0'
		else:
			#assum_l,assum_r= assumption.split('=')
			#assum_r = assum_r.replace(';','',1)
			#if assum_r[-1] == "f" or assum_r[-1] == "l": 
			#	assum_r = assum_r[:-1]

		#TODO: handle f and l
		#_, right = pAssumptionHolder.assumption.split("=")
		#assum_l = assum_l.strip()
		#assum_r = assum_r.strip()	

			#TODO: copy this
			try:
				_,val = pAssumptionHolder.assumption.split("=")
				val,_ = val.split(';')
				if val[-1] == "f" or val[-1] == "l":
					val = val[:-1]
			except Exception as ex:
				if IS_DEBUG:
					print(TColors.FAIL+ ' Error in File (fromAssumptionHolder):'+ TColors.ENDC, benchmark)
				val = '0'
				#return None
				pass

		value = NonDeterministicCall.extract_byte_little_endian(val.strip())
		nonDeterministicCall = NonDeterministicCall(value)
		lineNumberForNonDetCallsLst_tmp = []
		if lineNumberForNonDetCallsLst is not None:
			for (line,funcName) in lineNumberForNonDetCallsLst:
				if pAssumptionHolder.line == line:
					lineNumberForNonDetCallsLst_tmp.append((line,funcName))
			lineNumberForNonDetCallsLst_tmp_len = len(lineNumberForNonDetCallsLst_tmp)
			if lineNumberForNonDetCallsLst_tmp_len == 1:
				(_,funcName) = lineNumberForNonDetCallsLst_tmp [0]
				nonDeterministicCall.inputType = InputType.GetInputTypeForNonDetFunc(funcName)
			elif lineNumberForNonDetCallsLst_tmp_len > 1:
				(_,funcName) = lineNumberForNonDetCallsLst_tmp [0]
				isAllEqqual = True
				for (_,funcName_loop) in lineNumberForNonDetCallsLst_tmp:
					if funcName != funcName_loop :
						isAllEqqual = False
						break
				if isAllEqqual:
					nonDeterministicCall.inputType = InputType.GetInputTypeForNonDetFunc(funcName)
			#else:
				#TODO: hanle if many nonDetFuncs in the same line; Now as unkown
			
		return nonDeterministicCall

	def debugInfo(self):
		print("Nondet call: {0}".format(self.value))


class SourceCodeChecker(object):
	"""
		This class will read the original source file and checks if lines from assumptions contains nondeterministic calls	
	"""

	__lines__ = None

	def __init__(self, source, plstAssumptionHolder,pIsFromMap2Check = False):
		"""
		Default constructor.

		Parameters
		----------
		source : str
			Path to source code file (absolute/relative)
		plstAssumptionHolder : [AssumptionHolder]
			List containing all lstAssumptionHolder of the witness
		"""
		assert(os.path.isfile(source))
		assert(plstAssumptionHolder is not None)
		self.source = source
		self.lstAssumptionHolder = plstAssumptionHolder
		#self.__lines__ = None
		self.isFromMap2Check = pIsFromMap2Check

	@staticmethod
	def loadSourceFromFile(pFile):
		SourceCodeChecker.__lines__ = open(pFile, "r").readlines()

	def __openfile__(self):
		"""Open file in READ mode"""
		SourceCodeChecker.__lines__ = open(self.source, "r").readlines()

	def __is_not_repeated__(self, i):
		if self.isFromMap2Check : return True
		
		x_AssumptionHolder = self.lstAssumptionHolder[i]
		y_AssumptionHolder = self.lstAssumptionHolder[i+1]

		if x_AssumptionHolder.line != y_AssumptionHolder.line:
			return True

		try:
			_, x_right = x_AssumptionHolder.assumption.split("=")
			_, y_right = y_AssumptionHolder.assumption.split("=")
			return x_right != y_right
		except Exception as ex:
			if IS_DEBUG:
				print(TColors.FAIL+ 'Error in File (__is_not_repeated__):'+TColors.ENDC , benchmark)
		return True

	def __isNonDet__(self, p_AssumptionHolder):
		global lineNumberForNonDetCallsLst
		#global lineNumberForNonDetCallsLst_Map2check
		"""
			Checks if p_AssumptionHolder is nondet by checking if line contains __VERIFIER_nondet
		"""

		#if self.isFromMap2Check : return True
		if p_AssumptionHolder is None: return False
		if "=" in p_AssumptionHolder.assumption:
			check_cast = p_AssumptionHolder.assumption.split("=")
			if len(check_cast) > 1:
				if check_cast[1].startswith(" ( struct "):
					return False
		if lineNumberForNonDetCallsLst is not None:
			for (line,_) in lineNumberForNonDetCallsLst:
				if p_AssumptionHolder.line == line: return True
			return False
		
		#print('We must not hier')
		#exit(0)
		if SourceCodeChecker.__lines__ is None:
			self.__openfile__()
		lineContent = ''
		try:
			lineContent = SourceCodeChecker.__lines__[p_AssumptionHolder.line - 1]
		except:
			pass
		# At first we do not care about variable name or nondet type
		# TODO: Add support to variable name
		# TODO: Add support to nondet type
		
		#print('LiNE', lineContent)
		#index = lineContent.find('__VERIFIER_nondet_')
		#if index >= 0:
		#	lineContent=lineContent.replace(';', ',')
			#lineLst =['  unsigned int i', ' n=__VERIFIER_nondet_uint()', ' sn=0', '\n']
			#lineLst ['  unsigned long pat_len = __VERIFIER_nondet_ulong()', ' a_len = __VERIFIER_nondet_ulong()', '\n']

			#lineLst=lineContent.split(',')
			#print('lineLst', lineLst)
			#for stmt in lineLst:
			#	if stmt.find('__VERIFIER_nondet_') >=0 :
			#		left,right = stmt.split('=');
			#		left = left.strip()
			#		left_lst = left.split(' ')
			#		left=left_lst[:-1]
			#		print('LLLLLEEEFT',left)
			#		return p_AssumptionHolder.varName == left				
					

		result = lineContent.split("__VERIFIER_nondet_")
		return len(result) > 1
		#return False
		# return right != ""

	"""
	return list of NonDeterministicCall objects.
	"""
	def getNonDetAssumptions(self):
		filtered_assumptions = list()
		#print('self.lstAssumptionHolder',self.lstAssumptionHolder)
		#if len(self.lstAssumptionHolder)==0 :
		#	return []
		
		for i in range(len(self.lstAssumptionHolder)-1):
			if self.__is_not_repeated__(i):
				filtered_assumptions.append(self.lstAssumptionHolder[i])
		if len(self.lstAssumptionHolder)>0:
			filtered_assumptions.append(self.lstAssumptionHolder[-1])
		return [NonDeterministicCall.fromAssumptionHolder(x,self.isFromMap2Check) for x in filtered_assumptions if not x is None and self.__isNonDet__(x)]

	def debugInfo(self):
		for x in self.getNonDetAssumptions(): x.debugInfo()


def __getNonDetAssumptions__(witness, source, isFromMap2Check = False):
	
	"""
	return list of NonDeterministicCall objects.
	"""
	assumptionParser = AssumptionParser(witness,isFromMap2Check)
	assumptionParser.parse()
	assumptions = assumptionParser.assumptions
	return SourceCodeChecker(source, assumptions,isFromMap2Check).getNonDetAssumptions()

# error-call
def createTestFile(witness, source,testCaseFileName,isFromMap2Check = False):
	global hasInputInTestcase
	global lastInputInTestcaseCount
	if not os.path.isfile(witness) : return
	assumptions = __getNonDetAssumptions__(witness, source,isFromMap2Check)
	#print('WE HAVE', len(assumptions))
	assumptionsLen = len(assumptions)
	if(assumptionsLen > 0):
		if FuSeBMCFuzzerLib_ERRORCALL_ENABLED:
			AddToFuzzerSeedsLst_ErrorCall(os.path.basename(testCaseFileName), assumptions)
		generate_testcase_from_assumption_ErrorCall(testCaseFileName,assumptions)
		#
		hasInputInTestcase=True
		if assumptionsLen > lastInputInTestcaseCount: lastInputInTestcaseCount = assumptionsLen

def CompileFile(fil, include_dir = '.'):
	fil=os.path.abspath(fil)
	if not os.path.isfile(fil):
		print('FILE:',fil, 'not exists')
		exit(0)
	out_obj = WRAPPER_Output_Dir +os.sep+GenerateRondomFileName()+'.o'
	cmd=[C_COMPILER,'-c',fil , '-o', out_obj,'-I'+include_dir]
	runWithoutTimeoutEnabled(' '.join(cmd), WRAPPER_Output_Dir, True)
	if not os.path.isfile(out_obj):
		print('Cannot compile: ',fil)
		exit(0)


def run_without_output(cmd_line, pCwd = None):
	if(SHOW_ME_OUTPUT): print(cmd_line)
	the_args = shlex.split(cmd_line)
	if not pCwd is None:
		_ = subprocess.run(the_args, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,cwd=pCwd)
	else:
		_ = subprocess.run(the_args, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
	#p.communicate()

# Function to run esbmc
def run(cmd_line):
	global category_property
	global important_outs_by_ESBMC
	global is_ctrl_c
	mustReturnImportantOutput = not (category_property == Property.cover_branches or \
					category_property == Property.cover_error_call)
	mustSendToDevNull = mustReturnImportantOutput == False and SHOW_ME_OUTPUT == False
	#print('mustReturnImportantOutput',mustReturnImportantOutput)
	#print('mustSendToDevNull',mustSendToDevNull)
	if(SHOW_ME_OUTPUT): print (TColors.BOLD,'\nCommand:\n', cmd_line, TColors.ENDC)
	if mustReturnImportantOutput:
		outs=['' for _ in range(MAX_NUM_OF_LINES_OUT)]
		errs=['' for _ in range(MAX_NUM_OF_LINES_ERRS)]
		important_outs=[]
		important_errs=[]
		index=-1;
		index_err=-1
	the_args = shlex.split(cmd_line)
	p = None
	try:
		if mustSendToDevNull:
			p = subprocess.Popen(the_args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		else:
			if mustReturnImportantOutput:
				p = subprocess.Popen(the_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			else:
				p = subprocess.Popen(the_args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		#print('pid',p.pid)
		if mustSendToDevNull:
			while True:
				IsTimeOut(True)
				chpid, status, rusage = os.wait4(p.pid, os.WNOHANG)
				if chpid == p.pid: break
				time.sleep(1)
			
		else:
			nbsr_out = NonBlockingStreamReader(p.stdout)
			if mustReturnImportantOutput:
				nbsr_err = NonBlockingStreamReader(p.stderr)
			
			while nbsr_out.hasMore():
				IsTimeOut(True)
				output = nbsr_out.readline(1)
				if output:
					try:os.wait4(p.pid, os.WNOHANG)
					except ChildProcessError as cpe_ex: pass
					if(SHOW_ME_OUTPUT): print(output)
					if mustReturnImportantOutput:
						index =(index + 1) % MAX_NUM_OF_LINES_OUT
						isAddedToImportant=False
						for out_by_ESBMC in important_outs_by_ESBMC:
							if out_by_ESBMC in output:
								important_outs.append(output)
								isAddedToImportant=True
								break
						if not isAddedToImportant : outs[index]= output
				else:
					#IsTimeOut(True)
					#time.sleep(0.1)
					pass
			if mustReturnImportantOutput:
				while nbsr_err.hasMore():
					IsTimeOut(True)
					err = nbsr_err.readline(1)
					if err:
						try:os.wait4(p.pid, os.WNOHANG)
						except ChildProcessError as cpe_ex: pass
						if(SHOW_ME_OUTPUT): print(err)
						index_err =(index_err + 1) % MAX_NUM_OF_LINES_ERRS
						isAddedToImportant=False
						for out_by_ESBMC in important_outs_by_ESBMC:
							if out_by_ESBMC in err:
								important_errs.append(err)
								isAddedToImportant=True
								break
						if not isAddedToImportant : errs[index_err]= err
					else:
						#IsTimeOut(True)
						#time.sleep(0.1)
						pass
			#(stdout, stderr) = p.communicate()
			#print (stdout.decode(), stderr.decode())
			#return stdout.decode()
	except MyTimeOutException as e:
		if p is not None:
			try:
				p.kill()
			except Exception: pass
		raise e
	except KeyboardInterrupt:
		is_ctrl_c = True
	except Exception as ex: HandleException(ex,cmd_line)
		#exit(0)
	#getTime(p.pid)
	# Kill ESBMC When Timeout (maybe)
	if p is not None:
		try:
			p.kill()
		except Exception: pass
	out_str=''
	if mustReturnImportantOutput:
		for imp in important_errs:
			out_str += imp
		#Part 1
		for loop in range(index_err,MAX_NUM_OF_LINES_ERRS):
			out_str += errs[loop]
		#part 02
		for loop in range(0,index_err+1):
			out_str += errs[loop]
		for imp in important_outs:
			out_str += imp
		#Part 1
		for loop in range(index,MAX_NUM_OF_LINES_OUT):
			out_str += outs[loop]
		#part 02
		for loop in range(0,index+1):
			out_str += outs[loop]
	return out_str

def runWithTimeoutEnabled(cmd_line,pCwd=None):
	global is_ctrl_c
	if(SHOW_ME_OUTPUT): print (TColors.BOLD, '\nCommand:\n', cmd_line ,TColors.ENDC)
	the_args = shlex.split(cmd_line)
	p = None
	is_time_out_local = False
	try:
		#os.system('ulimit -Sv 1400000')
		#stderr=subprocess.PIPE
		p = subprocess.Popen(the_args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=pCwd,shell=False,preexec_fn=limit_virtual_memory)
		#p = subprocess.Popen(' '.join(the_args),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=pCwd,shell=True,preexec_fn=limit_virtual_memory)
		nbsr_out = NonBlockingStreamReader(p.stdout)
		#nbsr_err = NonBlockingStreamReader(p.stderr)
		while nbsr_out.hasMore():
			IsTimeOut(True)
			output = nbsr_out.readline(1) # second 0.01
			# 0.1 secs to let the shell output the result
			if output:
				try:os.wait4(p.pid, os.WNOHANG)
				except ChildProcessError as cpe_ex: pass
				
				if(SHOW_ME_OUTPUT): print(output)
			else:
				IsTimeOut(True)
				#time.sleep(0.1)
		#while nbsr_err.hasMore():
		#	IsTimeOut(True)
		#	err = nbsr_err.readline(1) 
		#	if err:
		#		try:os.wait4(p.pid, os.WNOHANG)
		#		except ChildProcessError as cpe_ex: pass
		#		if(SHOW_ME_OUTPUT): print(err)
		#	else:
		#		IsTimeOut(True)
				#time.sleep(0.1)
	except MyTimeOutException: is_time_out_local = True
	except KeyboardInterrupt: is_ctrl_c = True
	except Exception as ex: HandleException(ex,cmd_line)
		#print('CTRLLLLLLLLLL')
	# Kill ESBMC When Timeout (maybe)
	if p is not None:
		try:
			#if p.poll() is None: # proc still working
				#os.killpg(os.getpgid(p.pid), signal.SIGTERM)
				#os.killpg(os.getpgid(p.pid), signal.SIGKILL)
			p.terminate()
			#p.kill()
			#print('Killed......')
		except:
			#print('EXXXXXXXX')
			#print(ex)
			pass
	if is_time_out_local :
		if IS_DEBUG: print('is_time_out_local is True')
		raise MyTimeOutException()

def runWithoutTimeoutEnabled(cmd_line,pCwd=None,forceOutput = False):
	global is_ctrl_c
	if(forceOutput or SHOW_ME_OUTPUT): print (TColors.BOLD, '\nCommand:\n', cmd_line ,TColors.ENDC)
	the_args = shlex.split(cmd_line)
	p = None
	nbsr_out = None
	#nbsr_err = None
	try:
		#stderr=subprocess.PIPE
		p = subprocess.Popen(the_args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=pCwd,shell=False,preexec_fn=limit_virtual_memory) #bufsize=1
		nbsr_out = NonBlockingStreamReader(p.stdout)
		#nbsr_err = NonBlockingStreamReader(p.stderr)
		while nbsr_out.hasMore():
			output = nbsr_out.readline(1) # second 0.01
			if output:
				#try:os.wait4(p.pid, os.WNOHANG)
				#except ChildProcessError as cpe_ex: pass
				
				if(forceOutput or SHOW_ME_OUTPUT): print(output)
		#while nbsr_err.hasMore():
		#	err = nbsr_err.readline(1) # 0.01
		#	if err:
		#		#try:os.wait4(p.pid, os.WNOHANG)
		#		#except ChildProcessError as cpe_ex: pass
		#		if(forceOutput or SHOW_ME_OUTPUT): print(err)

	except KeyboardInterrupt: is_ctrl_c = True
	if p is not None:
		try:
			#if p.poll() is None: # proc still working
				#os.killpg(os.getpgid(p.pid), signal.SIGTERM)
				#os.killpg(os.getpgid(p.pid), signal.SIGKILL)
			
			p.terminate()
			#p.send_signal(signal.CTRL_C_EVENT)
			#p.send_signal(signal.SIGINT)
			#p.kill()
			#print('Killed......')
			while nbsr_out is not None and  nbsr_out.hasMore():
				output = nbsr_out.readline(1) # second 0.01
				if output:
					if(forceOutput or SHOW_ME_OUTPUT): print(output)
			#while nbsr_err is not None and nbsr_err.hasMore():
			#	err = nbsr_err.readline(1) # 0.01
			#	if err:
			#		if(forceOutput or SHOW_ME_OUTPUT): print(err)
		except:
			#print('EXXXXXXXX')
			pass

def get_command_line(strat, prop, arch, benchmark, fp_mode):
	global goals_count
	global runNumber
	
	command_line = ESBMC_EXE + esbmc_dargs
	command_line += benchmark + " --quiet "
	if arch == 32:
		command_line += "--32 "
	else:
		command_line += "--64 "
	# Add witness arg , Now Added in Verify method.
	#witness_file_name = os.path.basename(benchmark) + ".graphml "
	#if prop != Property.cover_branches and prop != Property.cover_error_call:
	#	command_line += "--witness-output " + witness_file_name
	#BEGIN
	# Special case for termination, it runs regardless of the strategy
	if prop == Property.termination:
		if MEM_OVERFLOW_REACH_TERM_RUNTWICE_ENABLED and runNumber ==1:
			command_line += "--partial-loops --no-pointer-check --no-bounds-check --no-assertions --termination --max-inductive-step 3 "
		else:
			command_line += "--no-pointer-check --no-bounds-check --no-assertions --termination --max-inductive-step 3 "
		return command_line	
	
	if prop == Property.overflow:
		if MEM_OVERFLOW_REACH_TERM_RUNTWICE_ENABLED and runNumber ==1:
			command_line += "--partial-loops --no-pointer-check --no-bounds-check --overflow-check --no-assertions "
		else:
			command_line += "--no-pointer-check --no-bounds-check --overflow-check --no-assertions "
	elif prop == Property.memsafety:
		strat = "incr"
		if MEM_OVERFLOW_REACH_TERM_RUNTWICE_ENABLED and runNumber ==1:
			command_line += "--partial-loops --memory-leak-check --no-assertions "
		else:
			command_line += "--memory-leak-check --no-assertions "
	elif prop == Property.memcleanup:
		strat = "incr"
		if MEM_OVERFLOW_REACH_TERM_RUNTWICE_ENABLED and runNumber ==1:
			command_line += "--partial-loops --memory-leak-check --no-assertions "
		else:
			command_line += "--memory-leak-check --no-assertions "
	elif prop == Property.unreach_call:
		if MEM_OVERFLOW_REACH_TERM_RUNTWICE_ENABLED and runNumber ==1:
			command_line += "--partial-loops --no-pointer-check --no-bounds-check --interval-analysis "
		else:
			command_line += "--no-pointer-check --no-bounds-check --interval-analysis "
	elif prop == Property.cover_branches:
		if(goals_count>100):
			if (goals_count<250):
				command_line += "--max-k-step 30 --unwind 1 --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
			else:
				command_line += "--max-k-step 10 --unwind 1 --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
		else:#(goals_count<100)
			command_line += "--unlimited-k-steps --unwind 1 --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
		#20.05.2020 + #03.06.2020 kaled: adding the option "--unlimited-k-steps" for coverage_error_call .... --max-k-step 5
	elif prop == Property.cover_error_call:
	#kaled : 03.06.2020 --unwind 10 --partial-loops
		if ERRORCALL_RUNTWICE_ENABLED and runNumber ==1:
			command_line += "--partial-loops --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
		else:
			command_line += "--unlimited-k-steps --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
	else:
		print ("Unknown property")
		exit(1)
	
	# Add strategy
	if strat == "fixed":
		command_line += "--k-induction --max-inductive-step 3 "
	elif strat == "kinduction":
		#TODO: Check this
		#command_line += "--bidirectional "
		command_line += "--k-induction --max-inductive-step 3 "
	elif strat == "falsi":
		command_line += "--falsification "
	elif strat == "incr":
		command_line += "--incremental-bmc "
	else:
		print ("Unknown strategy")
		exit(1)
	#END
	# if we're running in FP mode, use MathSAT
	if fp_mode:
		command_line += "--mathsat "
	return command_line

def generate_testcase_from_assumption_ErrorCall(p_test_case_file_full,p_inst_assumptions):
	inst_len = len(p_inst_assumptions)
	if (inst_len > 0 ) : print('    Generate Testcase ...')
	with open(p_test_case_file_full, 'w') as testcase_file:
		testcase_file.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
		testcase_file.write('<!DOCTYPE testcase PUBLIC "+//IDN sosy-lab.org//DTD test-format testcase 1.0//EN" "https://sosy-lab.org/test-format/testcase-1.0.dtd">\n')
		testcase_file.write('<testcase>\n')
		for nonDeterministicCall in p_inst_assumptions:
			cType =''
			if nonDeterministicCall.inputType != InputType.unkonwn:
				cType = ' type="'+InputType.GetAs_C_DataType(nonDeterministicCall.inputType)+'"'
			testcase_file.write('<input'+cType+'>'+nonDeterministicCall.value +'</input>\n')
		testcase_file.write('</testcase>')
	#
	
def generate_testcase_from_assumption_CoverBranches(p_test_case_file_full,p_inst_assumptions, p_isSelectiveFuzzer = False):
	
	#if(arch == 32)if(arch == 32)
	# sys.byteorder 'little' or 'big'
	inst_len = len(p_inst_assumptions)
	if (inst_len > 0 ) : print('    Generate Testcase ...')
		#if(inst_len > FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes): FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes = inst_len
	
	with open(p_test_case_file_full, 'w') as testcase_file:
		testcase_file.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
		testcase_file.write('<!DOCTYPE testcase PUBLIC "+//IDN sosy-lab.org//DTD test-format testcase 1.0//EN" "https://sosy-lab.org/test-format/testcase-1.0.dtd">\n')
		testcase_file.write('<testcase>\n')
		for nonDeterministicCall in p_inst_assumptions:
			# if you want to print to std
			#print(nonDeterministicCall)
			cType =''
			if nonDeterministicCall.inputType != InputType.unkonwn:
				cType = ' type="'+InputType.GetAs_C_DataType(nonDeterministicCall.inputType)+'"'
			testcase_file.write('<input'+cType+'>'+nonDeterministicCall.value +'</input>\n')
		
		if p_isSelectiveFuzzer == False:
			tracer_testcase_file = WRAPPER_Output_Dir + '/tracer_testcase.txt'
			if(os.path.isfile(tracer_testcase_file)):
				if IS_DEBUG: testcase_file.write('<!-- FuSeBMC_Tracer -->\n')
				with open(tracer_testcase_file, 'r') as tracer_testcase_f:
					for line in tracer_testcase_f:
						testcase_file.write(line)
				RemoveFileIfExists(tracer_testcase_file)
				print('    Testcase is completed by FuSeBMC_Tracer...')
		
		testcase_file.write('</testcase>')



#replace GOAL_1: with fuseGoalCalled(1);
def ReplaceGoalLabelWithFuseGoalCalledMethod(src_file, dest_file):
	goalRegex = re.compile('GOAL_([0-9]+):')
	with open(dest_file,'w') as fout:
		if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED:
			fout.write('unsigned int fuSeBMC_category = 2 ;\n')
			
			#fout.write('extern void fuSeBMC_return(int code);\n')
		fout.write('char * fuSeBMC_run_id = "'+fuSeBMC_run_id+'";\n')
		fout.write('extern void fuseGoalCalled(int goal);\n')
		fout.write('extern char * fuSeBMC_bitset_arr;\n')
		fout.write('extern void fuSeBMC_init();\n')
		#fout.write('extern void fuSeBMC_log_error (char * format, ...);\n')
		with open(src_file,'r') as fin:
			for line in fin:
				if(line == '//fuSeBMC_init\n'):
					line = 'fuSeBMC_init();\n'
				else:
					regex_result = goalRegex.match(line)
					if regex_result is not None:
						gl = regex_result.group(1)
						#print(regex_result.string,regex_result.group(1))
						line = line.replace(regex_result.string,'fuseGoalCalled('+gl+');\n')
						
						#line = line.replace(regex_result.string, 'if(((fuSeBMC_bitset_arr)['+gl+'/8] >> '+gl+'%8) & (char)1 == (char)0)fuseGoalCalled('+gl+');\n')
						#line = line.replace(regex_result.string, 'if(!((fuSeBMC_bitset_arr['+gl+'/8]) & (char)(1<<('+gl+'%8))))fuseGoalCalled('+gl+');\n')
						#This
						#line = line.replace(regex_result.string, 'if(fuSeBMC_bitset_arr['+gl+']==0)fuseGoalCalled('+gl+');\n')
						
						#line = line.replace(regex_result.string,'fuSeBMC_log_error("gl=%u,val=%d\\n",'+gl+',(fuSeBMC_bitset_arr['+gl+'/8]) & (char)(1<<('+gl+'%8)));')
				
				fout.write(line)

def RunAFLForCoverBranches(instrumented_afl_file):
	'''
	@Return lstFuSeBMC_FuzzerGoals : list of goals covered by Fuzzer.
	'''
	global FuSeBMCFuzzerLib_CoverBranches_Input_Covered_Goals_File ,FuSeBMCFuzzerLib_CoverBranches_Output_Covered_Goals_File
	global FuSeBMCFuzzerLib_CoverBranches_Done
	global lstFuzzerSeeds
	global FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes
	global lstFuSeBMC_GoalTracerGoals
	global remaining_time_s
	global goals_count, infinteWhileNum, selectiveInputsLst
	global stdCFuncsLst
	
	FuSeBMCFuzzerLib_CoverBranches_Seed_Dir = os.path.abspath(os.path.join(WRAPPER_Output_Dir, 'seeds'))
	MakeFolderEmptyORCreate(FuSeBMCFuzzerLib_CoverBranches_Seed_Dir)
	l_seed_dir = FuSeBMCFuzzerLib_CoverBranches_Seed_Dir
	
	# Write lstFuzzerSeeds:
	for goal_id, assump_lst in lstFuzzerSeeds:
		seed_filename = os.path.join(FuSeBMCFuzzerLib_CoverBranches_Seed_Dir,'s_'+str(goal_id)+'.bin')
		testcaseSize = WriteTestcaseInSeedFile(assump_lst,seed_filename,arch)
			#if afl_min_length < testcaseSize : afl_min_length = testcaseSize
		if(testcaseSize > 0 and testcaseSize > FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes):
			FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes = testcaseSize
	#ENDFOR
	afl_min_length = FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes
	if afl_min_length <= 0 :
		afl_min_length = FuSeBMCFuzzerLib_COVERBRANCHES_DEFAULT_AFL_MIN_LENGTH
		seed_filename = os.path.join(FuSeBMCFuzzerLib_CoverBranches_Seed_Dir,'rnd_seed_001.bin')
		with open(seed_filename, 'wb') as seed_f:
			for i in range(0,64):
				seed_f.write((int(i)).to_bytes(4, byteorder=sys.byteorder, signed=True))
	else:
		seed_filename = os.path.join(FuSeBMCFuzzerLib_CoverBranches_Seed_Dir,'zeros_001.bin')
		with open(seed_filename, 'wb') as seed_f:
			for _ in range(0,afl_min_length):
				seed_f.write((int(0)).to_bytes(1, byteorder=sys.byteorder, signed=True))
		
		seed_filename = os.path.join(FuSeBMCFuzzerLib_CoverBranches_Seed_Dir,'ones_001.bin')
		with open(seed_filename, 'wb') as seed_f:
			for _ in range(0,afl_min_length):
				seed_f.write((int(1)).to_bytes(1, byteorder=sys.byteorder, signed=True))
				
	#else:
	#	shutil.copy('./seeds_extra/xxxxxx.bin' ,l_seed_dir])
	
	print('\n\nRun FuSeBMCFuzzer ....\n')
	#afl_min_length *= 3
	#afl_min_length = -1
	if IS_DEBUG:
		print('    afl_min_length=', afl_min_length , 'Byte(s)')
		print('    Timeout=', FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT , 'Second(s)')
		print('    Remaining_time_s =',remaining_time_s,'Second(s).')
	try:
		lstGoalsFuzzerInput = [gl for gl in lstFuSeBMC_GoalTracerGoals]
		lstGoalsFuzzerInput.sort()
		#lstGoalsFuzzerInput = []
		with open (FuSeBMCFuzzerLib_CoverBranches_Input_Covered_Goals_File,'w') as f_covered:
			for gl in lstGoalsFuzzerInput: f_covered.write(str(gl)+'\n')
		
		afl_result_file = WRAPPER_Output_Dir + '/afl_result.txt'
		RemoveFileIfExists(afl_result_file)
		FuSeBMCFuzzerLib_CoverBranches_Done = True
		#ReplaceGoalLabelWithFuseGoalCalledMethod(INSTRUMENT_Output_File, instrumented_afl_file)
		afl_fuzzer_bin = os.path.abspath(WRAPPER_Output_Dir+'/afl.exe')
		lstFuSeBMC_FuzzerGoals_tmp = []
		os.environ["AFL_QUIET"] = "1"
		os.environ["AFL_DONT_OPTIMIZE"] = "1"
		compile_afl_lst = [FuSeBMCFuzzerLib_COVERBRANCHES_CC,FuSeBMCFuzzerLib_COVERBRANCHES_CC_PARAMS,
								#'gcc',
								#'-D exit=fuSeBMC_exit', '-D abort=fuSeBMC_abort_prog',
								#'-D ___assert_fail=fuSeBMC___assert_fail',
								'-std=gnu11',
								#'-std=c99',
								'-D abort=fuSeBMC_abort_prog',
								#'-D read=fuSeBMC_read_X',
								#'-D write=fuSeBMC_write_X',
								'-I'+os.path.dirname(benchmark),
								'-m'+str(arch), '-Wno-attributes', #'-D__alias__(x)=',
								'-o',afl_fuzzer_bin,
								'-L./FuSeBMC_FuzzerLib/',instrumented_afl_file,
								'-lFuSeBMC_FuzzerLib_'+str(arch),'-lm','-lpthread']
		for func in stdCFuncsLst:
			compile_afl_lst.append('-D ' + func + '='+func+'_XXXX')
		runWithTimeoutEnabled(' '.join(compile_afl_lst))
		if not os.path.isfile(afl_fuzzer_bin): raise Exception (afl_fuzzer_bin + ' Not found.')
		
		tcgen_bin = os.path.abspath(WRAPPER_Output_Dir+'/tcgen.exe')
		compile_tcgen_lst = [FuSeBMCFuzzerLib_TESTCASE_GEN_CC,FuSeBMCFuzzerLib_TESTCASE_GEN_CC_PARAMS,
								#'gcc',
								#'-D exit=fuSeBMC_exit', '-D abort=fuSeBMC_abort_prog',
								#'-D ___assert_fail=fuSeBMC___assert_fail',
								'-std=gnu11',
								'-D abort=fuSeBMC_abort_prog',
								#'-std=c99',
								'-I'+os.path.dirname(benchmark),
								'-m'+str(arch), '-Wno-attributes', #'-D__alias__(x)=',
								'-o',tcgen_bin,
								'-L./FuSeBMC_TCGen/',instrumented_afl_file,
								'-lFuSeBMC_TCGen_'+str(arch),'-lm','-lpthread']
		for func in stdCFuncsLst:
			compile_tcgen_lst.append('-D ' + func + '='+func+'_XXXX')
		runWithTimeoutEnabled(' '.join(compile_tcgen_lst))
		if not os.path.isfile(tcgen_bin): raise Exception (tcgen_bin + ' Not found.')
		
		os.environ["AFL_SKIP_CPUFREQ"] = "1"
		os.environ["AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES"] = "1"
		os.environ["AFL_SKIP_CRASHES"] = "1"
		os.environ["AFL_FAST_CAL"] = "1"
		#os.environ["AFL_NO_AFFINITY"] = "1"
		#os.environ[fuSeBMC_run_id+'_gcnt'] = str(goals_count)
		
		fusebmcStageParam = ''
		fuzzTimeout = FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT
		if FuSeBMCFuzzerLib_COVERBRANCHES_SELECTIVE_INPUTS_ENABLED and \
			selectiveInputsLst is not None and len(selectiveInputsLst)>0:
				if afl_min_length < 256 : afl_min_length = 256
				fuzzTimeout += FuSeBMCFuzzerLib_COVERBRANCHES_SELECTIVE_INPUTS_TIME_INCREMENT
				fusebmcStageParam = '-F ' + str(FuSeBMCFuzzerLib_COVERBRANCHES_SELECTIVE_INPUTS_ITERATIONS)
		elif(COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED and infinteWhileNum > 0):
			selectiveInputsLst = [str(i) for i in range(1,18)]
			writeSelectiveInputsLstToFile()
			if afl_min_length < 256 : afl_min_length = 256
			fuzzTimeout += FuSeBMCFuzzerLib_COVERBRANCHES_INFINITE_WHILE_TIME_INCREMENT
			fusebmcStageParam = '-F ' + str(FuSeBMCFuzzerLib_COVERBRANCHES_FUSEBMC_STAGE_ITERATION_INFINITE_WHILE)
		
		afl_command = ' '.join(['timeout' ,'--signal=SIGTERM', '--kill-after=10s', str(fuzzTimeout),
			 AFL_HOME_PATH + '/afl-fuzz',
			#'-n',
			'-Z','-A','2',
			'-l',str(afl_min_length),'-D' , fuSeBMC_run_id,
			'-E',str(FuSeBMCFuzzerLib_COVERBRANCHES_SEED_EXPAND_MAX_SIZE),
			'-G', str(goals_count),
			fusebmcStageParam, 
			'-U', str(FuSeBMCFuzzerLib_COVERBRANCHES_FUSEBMC_SF_STAGE_ITERATION),
			'-i', l_seed_dir,'-o' ,'./FuSeBMCFuzzerOutput',
			'-m', FuSeBMCFuzzerLib_COVERBRANCHES_FUZZED_APP_MEM_LIMIT,
			'-t',FuSeBMCFuzzerLib_COVERBRANCHES_FUZZED_APP_TIMEOUT,
			'--', afl_fuzzer_bin])
		#print('afl_command:', afl_command)
		#exit(0)
		runWithTimeoutEnabled(afl_command, WRAPPER_Output_Dir)
	
		if os.path.isfile(afl_result_file):
			with open(afl_result_file,'r') as f:
				for line in f: print(line.rstrip())
		#lstFuzzerSeeds = [] # make empty
		lstFuSeBMC_FuzzerGoals_tmp = GetGoalListFromFile(FuSeBMCFuzzerLib_CoverBranches_Output_Covered_Goals_File)
		lstFuSeBMC_FuzzerGoals_tmp = [gl for gl in lstFuSeBMC_FuzzerGoals_tmp if gl not in lstGoalsFuzzerInput]

		#print('fuSeBMC_run_id:', os.environ[fuSeBMC_run_id])
		#os.unsetenv(fuSeBMC_run_id)
		#sys.exit(0)
		
		print('    lstFuSeBMC_FuzzerGoals_tmp',lstFuSeBMC_FuzzerGoals_tmp, '\n')
		print('    len(lstFuSeBMC_FuzzerGoals_tmp)=',len(lstFuSeBMC_FuzzerGoals_tmp), '\n')
		
		return lstFuSeBMC_FuzzerGoals_tmp
	except MyTimeOutException as mytime_ex: raise mytime_ex
	except KeyboardInterrupt as kb_ex: raise kb_ex;
	except Exception as ex: 
		HandleException(ex)
		return None

def RunAFLForCoverBranches_Run2():
	global lstFuzzerSeeds
	global lstFuSeBMC_GoalTracerGoals, lstFuSeBMC_FuzzerGoals
	global FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes
	global goals_count, infinteWhileNum, selectiveInputsLst
	
	lstFuSeBMC_FuzzerGoals_Run2 = []
	FuSeBMCFuzzerLib_CoverBranches_Seed2_Dir = os.path.abspath(os.path.join(WRAPPER_Output_Dir, 'seeds2'))
	MakeFolderEmptyORCreate(FuSeBMCFuzzerLib_CoverBranches_Seed2_Dir)
	l_seed_dir = FuSeBMCFuzzerLib_CoverBranches_Seed2_Dir
	for goal_id, assump_lst in lstFuzzerSeeds2:
		seed_filename = os.path.join(FuSeBMCFuzzerLib_CoverBranches_Seed2_Dir,'s_'+str(goal_id)+'.bin')
		testcaseSize = WriteTestcaseInSeedFile(assump_lst,seed_filename,arch)
		if(testcaseSize > 0 and testcaseSize > FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes):
			FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes = testcaseSize
	afl_min_length = FuSeBMCFuzzerLib_CoverBranches_Max_Testcase_Size_Btyes
	if afl_min_length <= 0 :
		afl_min_length = FuSeBMCFuzzerLib_COVERBRANCHES_DEFAULT_AFL_MIN_LENGTH
	print('\n\nRun FuSeBMCFuzzer 2 ....\n');sys.stdout.flush()
	if IS_DEBUG:
		IsTimeOut(False)
		print('   remaining_time_s=', remaining_time_s, 'Second(s)')
		print('    afl_min_length=', afl_min_length, ' Byte(s)')
		print('CTRL+C to Stop .......')
	diff = FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_SEEDS_NUM_MIN - len(lstFuzzerSeeds2)
	if diff > 0:
		for i in range(0,diff):
			l = [randrange(-64,64) for _ in range(0,afl_min_length)]
			seed_filename = os.path.join(FuSeBMCFuzzerLib_CoverBranches_Seed2_Dir,'rnd_'+str(i)+'.bin')
			WriteListInSeedFile(l, seed_filename, 1, True)

	try:
		afl_fuzzer_bin = os.path.abspath(WRAPPER_Output_Dir+'/afl.exe')
		lstGoalsFuzzerInput = [gl for gl in lstFuSeBMC_GoalTracerGoals]
		for gl in lstFuSeBMC_FuzzerGoals: 
			if gl not in lstGoalsFuzzerInput: lstGoalsFuzzerInput.append(gl)
		lstGoalsFuzzerInput.sort()
		with open (FuSeBMCFuzzerLib_CoverBranches_Input_Covered_Goals_File,'w') as f_covered:
			for gl in lstGoalsFuzzerInput: f_covered.write(str(gl)+'\n')
		if not os.path.isfile(afl_fuzzer_bin): raise Exception (afl_fuzzer_bin + ' Not found.')
		os.environ['AFL_NO_UI']='1'
		
		fusebmcStageParam = ''
		if FuSeBMCFuzzerLib_COVERBRANCHES_SELECTIVE_INPUTS_ENABLED and \
			selectiveInputsLst is not None and len(selectiveInputsLst)>0:
				if afl_min_length < 256 : afl_min_length = 256
				fusebmcStageParam = '-F ' + str(FuSeBMCFuzzerLib_COVERBRANCHES_SELECTIVE_INPUTS_ITERATIONS)
		elif(COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED and infinteWhileNum > 0):
			if afl_min_length < 256 : afl_min_length = 256
			fusebmcStageParam = '-F ' + str(FuSeBMCFuzzerLib_COVERBRANCHES_FUSEBMC_STAGE_ITERATION_INFINITE_WHILE)

		runWithoutTimeoutEnabled(' '.join([ AFL_HOME_PATH + '/afl-fuzz',
			#'-n',
			'-Z','-A','2',
			'-l',str(afl_min_length),'-D' , fuSeBMC_run_id,
			'-E', str(FuSeBMCFuzzerLib_COVERBRANCHES_SEED_EXPAND_MAX_SIZE),
			'-G', str(goals_count),
			fusebmcStageParam,
			'-U', str(FuSeBMCFuzzerLib_COVERBRANCHES_FUSEBMC_SF_STAGE_ITERATION),
			'-i', l_seed_dir,'-o' ,'./FuSeBMCFuzzerOutput2',
			'-m', FuSeBMCFuzzerLib_COVERBRANCHES_FUZZED_APP_MEM_LIMIT,
			'-t',FuSeBMCFuzzerLib_COVERBRANCHES_FUZZED_APP_TIMEOUT,
			'--', afl_fuzzer_bin]),WRAPPER_Output_Dir)
		if is_ctrl_c: raise KeyboardInterrupt()
	
	except KeyboardInterrupt as kb_ex:
		lstFuSeBMC_FuzzerGoals_Total_Run2 = GetGoalListFromFile(FuSeBMCFuzzerLib_CoverBranches_Output_Covered_Goals_File)
		lstFuSeBMC_FuzzerGoals_Run2 = [ gl for gl in lstFuSeBMC_FuzzerGoals_Total_Run2 if gl not in lstGoalsFuzzerInput]
		print('lstFuSeBMC_FuzzerGoals_Run2',lstFuSeBMC_FuzzerGoals_Run2)
	except Exception as ex: HandleException(ex)
	return lstFuSeBMC_FuzzerGoals_Run2
	
def RunAFLForErrorCall():
	global lstFuzzerSeeds, infinteWhileNum, selectiveInputsLst
	global current_process_name
	global stdCFuncsLst
	
	afl_fuzzer_src = WRAPPER_Output_Dir+'/instrumented_afl.c'
	afl_fuzzer_bin = os.path.abspath(WRAPPER_Output_Dir+'/afl.exe')
	fuSeBMC_Fuzzer_testcase = WRAPPER_Output_Dir + '/test-suite/FuSeBMC_Fuzzer_testcase.xml'
	try:
		seed_dir = WRAPPER_Output_Dir + '/seeds/'
		MakeFolderEmptyORCreate(seed_dir)
		with open(afl_fuzzer_src,'w') as fout:
			fout.write('unsigned int fuSeBMC_category = 1 ;\n')
			fout.write('char * fuSeBMC_run_id = "'+fuSeBMC_run_id+'";\n')
			fout.write('extern char * fuSeBMC_bitset_arr;\n')
			fout.write('extern void fuSeBMC_init();\n')
			fout.write('extern void fuSeBMC_reach_error();\n')
			with open (INSTRUMENT_Output_File,'r') as fin:
				for line in fin:
					if line == 'fuSeBMC_init:;\n':
						line = 'fuSeBMC_init();\n'
					elif line == 'FuSeBMC_ERROR:;\n':
						line = 'fuSeBMC_reach_error();\n'
					fout.write(line)
		
		
		#print('    ','Starting Instrumentation for Fuzzing ...')
		#paramHandleInfiniteWhileLoop = ''
		#paramInfinteWhileLoopLimit = ''
		#if ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED:
		#	paramHandleInfiniteWhileLoop = '--handle-infinite-while-loop'
		#	paramInfinteWhileLoopLimit = str(ERRORCALL_INFINITE_WHILE_LOOP_LIMIT)
			
		#runWithTimeoutEnabled(' '.join([FUSEBMC_INSTRUMENT_EXE_PATH, '--input',srcFile ,'--output', afl_fuzzer_src , 
		#					paramHandleInfiniteWhileLoop, paramInfinteWhileLoopLimit,
		#					'--add-func-call-in-func','fuSeBMC_reach_error=reach_error,fuSeBMC_init=main',
		#					'--compiler-args', '-I'+os.path.dirname(srcFile)]))
		
		if not os.path.isfile(afl_fuzzer_src): raise Exception (afl_fuzzer_src + ' Not found.')
		#os.system("sed -i '1i unsigned int fuSeBMC_category = 1;' " + afl_fuzzer_src) # Append text to begin of file
		#with open(afl_fuzzer_src, 'a') as f:
		#	f.write('unsigned int fuSeBMC_category = 1;\n');
		#	f.write('char * fuSeBMC_run_id = "'+fuSeBMC_run_id+'";\n')
		
		gccArch = '-m' + str(arch)
		wrapperHomeDir = os.path.dirname(__file__)
		seedGenExe = os.path.abspath(WRAPPER_Output_Dir+'/seedGenExe.exe')
		print('    ','Compiling FuSeBMC_SeedGen ...')
		compille_seedGen_lst = [FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_CC, FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_CC_PARAMS,
									'-std=gnu11',
									'-D abort=fuSeBMC_abort_prog',
									#'-D read=fuSeBMC_read',
									#'-D write=fuSeBMC_write',
									'-I'+os.path.dirname(benchmark),gccArch,'-Wno-attributes','-D__alias__(x)=', '-o',seedGenExe,
							'-L'+wrapperHomeDir+'/FuSeBMC_SeedGenLib/', afl_fuzzer_src,
							'-lFuSeBMC_SeedGenLib_'+str(arch),'-lm','-lpthread']
		for func in stdCFuncsLst:
			compille_seedGen_lst.append('-D ' + func + '='+func+'_XXXX')
		runWithTimeoutEnabled(' '.join(compille_seedGen_lst))
		seedGenExeOK = os.path.isfile(seedGenExe)
		seedMaxSize = 0
		if(seedGenExeOK):
			print('    ','Executing FuSeBMC_SeedGen ...')
			current_process_name = FuSeBMCProcessName.SeedGen
			for _ in range(0,FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_SEEDS_NUM):
				runWithTimeoutEnabled(' '.join(['timeout', '-k','2s','5',seedGenExe]), WRAPPER_Output_Dir)
			current_process_name = ''
			
			#maxTestcaseSize = 0
			if FuSeBMCFuzzerLib_ERRORCALL_USE_SEED_FROM_ESBMC1  and lstFuzzerSeeds is not None:
				for (tc_name,assump_lst) in lstFuzzerSeeds:
					seed_filename = os.path.join(seed_dir,tc_name+'.bin')
					_ = WriteTestcaseInSeedFile(assump_lst,seed_filename,arch)
					#if testcaseSize > maxTestcaseSize: maxTestcaseSize = testcaseSize
				lstFuzzerSeeds = []
			
			'''
			seedGen_size_f = WRAPPER_Output_Dir+'/SeedGen_size.txt'
			if(os.path.isfile(seedGen_size_f)):
				with open (seedGen_size_f,'r') as sG_size_f:
					for line in sG_size_f:
						if line is not None:
							if line.startswith('#'): continue
							sz = int(line)
							if sz > seedMaxSize : seedMaxSize = sz
			'''
			hashes_lst = []
			for root, dirs, files in os.walk(seed_dir):
				for file in files:
					full_file_name = os.path.join(root, file)
					file_stats = os.stat(full_file_name)
					if file_stats.st_size < 4:
						tmp_hash = GetSH1ForFile(full_file_name)
						if tmp_hash in hashes_lst:
							RemoveFileIfExists(full_file_name)
							continue
						else : hashes_lst.append(tmp_hash)
					if file_stats.st_size > seedMaxSize : seedMaxSize = file_stats.st_size
			#print('hashes_lst',hashes_lst)
			if seedMaxSize == 0 :
				seedMaxSize = 32
				seed_filename = seed_dir+'/zeros_001.bin'
				with open (seed_filename,'wb') as seed_f:
					for _ in range(0,seedMaxSize):
						seed_f.write((int(0)).to_bytes(1, byteorder=sys.byteorder, signed=False))
		else:
			print('    ','FuSeBMC_SeedGen failed ...')
		#if seedMaxSize > 8000 : seedMaxSize = 8000
		'''
		seed_filename = seed_dir+'/zeros_001.bin'
		with open (seed_filename,'wb') as seed_f:
			for _ in range(0,seedMaxSize):
				seed_f.write((int(0)).to_bytes(1, byteorder=sys.byteorder, signed=False))
		
		seed_filename = seed_dir+'/ones_001.bin'
		with open (seed_filename,'wb') as seed_f:
			for _ in range(0,seedMaxSize):
				seed_f.write((int(255)).to_bytes(1, byteorder=sys.byteorder, signed=False))
		
		seed_filename = seed_dir+'/rnd_001.bin'
		with open (seed_filename,'wb') as seed_f:
			for i in range(0,seedMaxSize):
				seed_f.write((int(randrange(0,5))).to_bytes(1, byteorder=sys.byteorder, signed=False))
		'''
		print('    ','Compiling App for Fuzzing ...')
		os.environ["AFL_QUIET"] = "1"
		os.environ["AFL_DONT_OPTIMIZE"] = "1"
		print('\n\nRun FuSeBMCFuzzer ....\n')
		compile_afl_lst = [FuSeBMCFuzzerLib_ERRORCALL_CC, FuSeBMCFuzzerLib_ERRORCALL_CC_PARAMS,
									'-D abort=fuSeBMC_abort_prog',
									#'-D read=fuSeBMC_read',
									#'-D write=fuSeBMC_write',
									'-I'+os.path.dirname(benchmark),
									'-m'+str(arch), afl_fuzzer_src, '-o',afl_fuzzer_bin,
									'-L./FuSeBMC_FuzzerLib/','-lFuSeBMC_FuzzerLib_'+str(arch),'-lm','-lpthread']
		for func in stdCFuncsLst:
			compile_afl_lst.append('-D ' + func + '='+func+'_XXXX')
		runWithTimeoutEnabled(' '.join(compile_afl_lst))
		if not os.path.isfile(afl_fuzzer_bin): raise Exception (afl_fuzzer_bin + ' Not found.')
		
		tcgen_bin = os.path.abspath(WRAPPER_Output_Dir+'/tcgen.exe')
		compile_tcgen_lst = [FuSeBMCFuzzerLib_TESTCASE_GEN_CC, FuSeBMCFuzzerLib_TESTCASE_GEN_CC_PARAMS,
									'-D abort=fuSeBMC_abort_prog', '-I'+os.path.dirname(benchmark),
									'-m'+str(arch), afl_fuzzer_src, '-o',tcgen_bin,
									'-L./FuSeBMC_TCGen/','-lFuSeBMC_TCGen_'+str(arch),'-lm','-lpthread']
		for func in stdCFuncsLst:
			compile_afl_lst.append('-D ' + func + '='+func+'_XXXX')
		runWithTimeoutEnabled(' '.join(compile_tcgen_lst))
		if not os.path.isfile(tcgen_bin): raise Exception (tcgen_bin + ' Not found.')
		
		os.environ["AFL_SKIP_CPUFREQ"] = "1"
		os.environ["AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES"] = "1"
		os.environ["AFL_SKIP_CRASHES"] = "1"
		os.environ["AFL_FAST_CAL"] = "1"
		print('    ','Start FuSeBMCFuzzer ...')
		if IS_DEBUG: print('    ','Timeout =',FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT,'Second(s).')
		
		fusebmcStageParam = ''
		fuzzTimeout = FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT
		if FuSeBMCFuzzerLib_ERRORCALL_SELECTIVE_INPUTS_ENABLED and \
			selectiveInputsLst is not None and len(selectiveInputsLst)>0:
				if seedMaxSize < 256 : seedMaxSize = 256
				fuzzTimeout += FuSeBMCFuzzerLib_ERRORCALL_SELECTIVE_INPUTS_TIME_INCREMENT
				fusebmcStageParam = '-F ' + str(FuSeBMCFuzzerLib_ERRORCALL_SELECTIVE_INPUTS_ITERATIONS)
		elif(ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED and infinteWhileNum > 0):
			fuzzTimeout += FuSeBMCFuzzerLib_ERRORCALL_INFINITE_WHILE_TIME_INCREMENT
			selectiveInputsLst = [str(i) for i in range(1,18)]
			writeSelectiveInputsLstToFile()
			fusebmcStageParam = '-F ' + str(FuSeBMCFuzzerLib_ERRORCALL_FUSEBMC_STAGE_ITERATION_INFINITE_WHILE)
		
		runWithTimeoutEnabled(' '.join(['timeout', '-k','2s', str(fuzzTimeout),
									AFL_HOME_PATH + '/afl-fuzz',
									#'-n',
									'-Z','-A','1','-l',str(seedMaxSize), '-D' , fuSeBMC_run_id,
									'-E',str(FuSeBMCFuzzerLib_ERRORCALL_SEED_EXPAND_MAX_SIZE),
									fusebmcStageParam,
									'-U',str(FuSeBMCFuzzerLib_ERRORCALL_FUSEBMC_SF_STAGE_ITERATION),
									'-i', seed_dir,'-o' ,'./FuSeBMCFuzzerOutput',
									'-m', FuSeBMCFuzzerLib_ERRORCALL_FUZZED_APP_MEM_LIMIT,
									'-t',FuSeBMCFuzzerLib_ERRORCALL_FUZZED_APP_TIMEOUT,
									'--', afl_fuzzer_bin]),WRAPPER_Output_Dir)
		if os.path.isfile(fuSeBMC_Fuzzer_testcase):
			print('    ','Testcase is generated.','\n')
			#
	except MyTimeOutException as e: raise e
	except KeyboardInterrupt as kbe: raise kbe
	except Exception as ex : HandleException(ex)

def RunAFLForErrorCall_Run2():
	global lstFuzzerSeeds,infinteWhileNum, selectiveInputsLst
	
	afl_fuzzer_bin = os.path.abspath(WRAPPER_Output_Dir+'/afl.exe')
	if not os.path.isfile(afl_fuzzer_bin):
		print('File not found:',afl_fuzzer_bin)
		return
	fuSeBMC_Fuzzer_testcase = WRAPPER_Output_Dir + '/test-suite/FuSeBMC_Fuzzer_testcase.xml'
	if os.path.isfile(fuSeBMC_Fuzzer_testcase):
		if FuSeBMCFuzzerLib_ERRORCALL_FORCE_RUN2:
			print('  \'FuSeBMC_Fuzzer_testcase.xml\' will be copied to \'FuSeBMC_Fuzzer_testcase_1.xml\' ')
			tc_dest = WRAPPER_Output_Dir + '/test-suite/FuSeBMC_Fuzzer_testcase_1.xml'
			shutil.move(fuSeBMC_Fuzzer_testcase, tc_dest)
		else:
			return

	seed_dir = WRAPPER_Output_Dir + '/seeds2/'
	MakeFolderEmptyORCreate(seed_dir)
	maxTestcaseSize = 0
	if lstFuzzerSeeds is not None:
		for (tc_name,assump_lst) in lstFuzzerSeeds:
			seed_filename = os.path.join(seed_dir,tc_name+'.bin')
			testcaseSize = WriteTestcaseInSeedFile(assump_lst,seed_filename,arch)
			if testcaseSize > maxTestcaseSize: maxTestcaseSize = testcaseSize
	if maxTestcaseSize == 0 :
		maxTestcaseSize = 32
	for i in range(0,2):
		l = [randrange(-64,64) for _ in range(0,maxTestcaseSize)]
		seed_filename = os.path.join(seed_dir,'rnd_'+str(i)+'.bin')
		WriteListInSeedFile(l, seed_filename, 1, True)
	afl_min_length = maxTestcaseSize
	print('\n\nRun FuSeBMCFuzzer 2 ....\n')
	if IS_DEBUG:
		IsTimeOut(False)
		print('   remaining_time_s=', remaining_time_s, 'Second(s)')
		print('    afl_min_length=', afl_min_length, ' Byte(s)')
		print('CTRL+C to Stop .......')
	try:
		os.environ["AFL_SKIP_CPUFREQ"] = "1"
		os.environ["AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES"] = "1"
		os.environ["AFL_SKIP_CRASHES"] = "1"
		os.environ["AFL_FAST_CAL"] = "1"
		fusebmcStageParam = ''
		if FuSeBMCFuzzerLib_ERRORCALL_SELECTIVE_INPUTS_ENABLED and \
			selectiveInputsLst is not None and len(selectiveInputsLst)>0:
				if afl_min_length < 256 : afl_min_length = 256
				fusebmcStageParam = '-F ' + str(FuSeBMCFuzzerLib_ERRORCALL_SELECTIVE_INPUTS_ITERATIONS)
		elif(ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED and infinteWhileNum > 0):
			if afl_min_length < 256 : afl_min_length = 256
			fusebmcStageParam = '-F ' + str(FuSeBMCFuzzerLib_ERRORCALL_FUSEBMC_STAGE_ITERATION_INFINITE_WHILE)
		runWithoutTimeoutEnabled(' '.join([
									AFL_HOME_PATH + '/afl-fuzz',
									#'-n',
									'-Z','-A','1','-l',str(afl_min_length), '-D' , fuSeBMC_run_id,
									'-E',str(FuSeBMCFuzzerLib_ERRORCALL_SEED_EXPAND_MAX_SIZE),
									fusebmcStageParam,
									'-U',str(FuSeBMCFuzzerLib_ERRORCALL_FUSEBMC_SF_STAGE_ITERATION),
									'-i', seed_dir,'-o' ,'./FuSeBMCFuzzerOutput2/',
									'-m', FuSeBMCFuzzerLib_ERRORCALL_FUZZED_APP_MEM_LIMIT,
									'-t',FuSeBMCFuzzerLib_ERRORCALL_FUZZED_APP_TIMEOUT,
									'--', afl_fuzzer_bin]),WRAPPER_Output_Dir)
		if os.path.isfile(fuSeBMC_Fuzzer_testcase):
			print('   ','Testcase is generated.','\n')
	except KeyboardInterrupt as kbe: pass
	except Exception as ex : HandleException(ex)

def parseRootXML_InfinteWhileNum(p_rootXML):
	if p_rootXML is None : return None
	infinteWhileNum = 0
	try:
		elemInfinteWhileNum= p_rootXML.find('infinteWhileNum')
		if elemInfinteWhileNum is not None and elemInfinteWhileNum.text is not None:
			infinteWhileNum = int(elemInfinteWhileNum.text)
	except Exception as ex: HandleException(ex)
	return infinteWhileNum

def parseRootXML_NonDetCalls(p_rootXML):
	if p_rootXML is None : return None
	l_lineNumberForNonDetCallsLst = []
	try:
		elemLineNumberForNonDetCalls= p_rootXML.find('nonDetCalls')
		if elemLineNumberForNonDetCalls is not None and elemLineNumberForNonDetCalls.text != 'ERROR':
			for nonDetCall in elemLineNumberForNonDetCalls.iter('nonDetCall'):
				elemNonDetCall_line = nonDetCall.find('line')
				elemNonDetCall_funcName = nonDetCall.find('funcName')
				if elemNonDetCall_line is not None and elemNonDetCall_funcName is not None:
					l_lineNumberForNonDetCallsLst.append((int(elemNonDetCall_line.text),elemNonDetCall_funcName.text))
		else:
			l_lineNumberForNonDetCallsLst = None
	except Exception as ex:
		l_lineNumberForNonDetCallsLst = None
		HandleException(ex)
	return l_lineNumberForNonDetCallsLst

def parseRootXML_FuncDeclInfo(p_rootXML):
	if p_rootXML is None : return None
	l_FuncDeclInfoLst = []
	try:
		elemFuncDeclInfos= p_rootXML.find('funcDeclInfos')
		if elemFuncDeclInfos is not None and elemFuncDeclInfos.text != 'ERROR':
			for funcDeclInfo in elemFuncDeclInfos.iter('funcDeclInfo'):
				elemFuncDeclInfo_ID = funcDeclInfo.find('id')
				elemFuncDeclInfo_Name = funcDeclInfo.find('name')
				if elemFuncDeclInfo_ID is not None and elemFuncDeclInfo_Name is not None:
					l_FuncDeclInfoLst.append((int(elemFuncDeclInfo_ID.text),elemFuncDeclInfo_Name.text))
		else:
			l_FuncDeclInfoLst = None
	except Exception as ex:
		l_FuncDeclInfoLst = None
		HandleException(ex)
	return l_FuncDeclInfoLst

def parseRootXML_FuncCallInfo(p_rootXML):
	if p_rootXML is None : return None
	l_FuncCallInfoLst = []
	try:
		elemFuncCallInfos= p_rootXML.find('funcCallInfos')
		if elemFuncCallInfos is not None and elemFuncCallInfos.text != 'ERROR':
			for funcCallInfo in elemFuncCallInfos.iter('funcCallInfo'):
				elemFuncCallInfo_Caller = funcCallInfo.find('caller')
				elemFuncCallInfo_Callee = funcCallInfo.find('callee')
				elemFuncCallInfo_Depth = funcCallInfo.find('depth')
				if elemFuncCallInfo_Caller is not None and elemFuncCallInfo_Callee is not None and elemFuncCallInfo_Depth is not None:
					l_FuncCallInfoLst.append((int(elemFuncCallInfo_Caller.text),int(elemFuncCallInfo_Callee.text),int(elemFuncCallInfo_Depth.text)))
		else:
			l_FuncCallInfoLst = None
	except Exception as ex:
		l_FuncCallInfoLst = None
		HandleException(ex)
	return l_FuncCallInfoLst
##
def parseRootXML_SelectiveInputs(p_rootXML):
	if p_rootXML is None : return None
	l_SelectiveInputsLst = []
	isSelectiveInputsFromMain = True
	try:
		elemIsSelectiveInputsFromMain = p_rootXML.find('isSelectiveInputsFromMain')
		if elemIsSelectiveInputsFromMain is not None and elemIsSelectiveInputsFromMain.text is not None \
			and elemIsSelectiveInputsFromMain.text != 'ERROR':
				if elemIsSelectiveInputsFromMain.text != '1':
					isSelectiveInputsFromMain = False
		
		elemSelectiveInputs= p_rootXML.find('selectiveInputs')
		if elemSelectiveInputs is not None and elemSelectiveInputs.text != 'ERROR':
				for e_input in elemSelectiveInputs.iter('input'):
					if e_input is not None and e_input.text is not None:
						l_SelectiveInputsLst.append(e_input.text)
		else:
			l_SelectiveInputsLst = None
	except Exception as ex:
		l_SelectiveInputsLst = None
		HandleException(ex)
	return (l_SelectiveInputsLst,isSelectiveInputsFromMain)


def parseRootXML_StdCFuncs(p_rootXML):
	l_StdCFuncLst = []
	if p_rootXML is None : return l_StdCFuncLst
	try:
		elemStdCFuncs= p_rootXML.find('stdCFuncs')
		if elemStdCFuncs is not None and elemStdCFuncs.text != 'ERROR':
			for stdCFunc in elemStdCFuncs.iter('stdCFunc'):
				if stdCFunc is not None and stdCFunc.text is not None:
					l_StdCFuncLst.append(stdCFunc.text)
	except Exception as ex:
		#l_StdCFuncLst = None
		HandleException(ex)
	return l_StdCFuncLst

def getGlobalDepthOfGoalInfo(p_goalInfo):
	global mainFuncID, callGraph
	if mainFuncID <= 0:
		HandleException(Exception('mainFuncID is not valid = '+ str(mainFuncID)))
		return p_goalInfo.depth
	if callGraph is None:
		HandleException(Exception('callGraph is None..'))
		return p_goalInfo.depth
	try:
		target = callGraph.get_vertex(p_goalInfo.funcID)
		path = [target.get_id()]
		shortest(target, path)
		#print ('The shortest path : %s' %(path[::-1]))
		distance_tmp = target.get_distance()
		if distance_tmp == sys.maxsize: return p_goalInfo.depth
		return distance_tmp + p_goalInfo.depth
	except Exception as ex:
		HandleException(ex)
	return p_goalInfo.depth
	#mainFuncID
	
def getLstGoalsToWorkOn(p_rootXML):
	if p_rootXML is None : return None
	ifGoalsLst, compoundGoalsLst, loopGoalsLst, elseGoalsLst, \
										endOfFuncGoalsLst, afterLoopGoalsLst, emptyElseGoalsLst, \
										forGoalsLst, cXXForRangeGoalsLst, doWhileGoalsLst, whileGoalsLst = \
										[],[],[],[],[],[],[],[],[],[],[]
	l_lstGoalsToWorkOn = None
	goalDepthDict = dict()
	goalFuncDict = dict()
	try:
		#elemGoalsCount = rootXML.find('goalsCount')
		#if elemGoalsCount is not None and elemGoalsCount.text: goalsCC = int(elemGoalsCount.text)
		elemIf = p_rootXML.find('if')
		if elemIf is not None and elemIf.text: ifGoalsLst = [int(x) for x in elemIf.text.split(',') if x]
		elemLoop = p_rootXML.find('loop')
		if elemLoop is not None and elemLoop.text: loopGoalsLst = [int(x) for x in elemLoop.text.split(',') if x]
		elemAfterLoop = p_rootXML.find('afterLoop')
		if elemAfterLoop is not None and elemAfterLoop.text: afterLoopGoalsLst = [int(x) for x in elemAfterLoop.text.split(',') if x]
		elemElse= p_rootXML.find('else')
		if elemElse is not None and elemElse.text: elseGoalsLst = [int(x) for x in elemElse.text.split(',') if x]
		elemEmptyElse= p_rootXML.find('emptyElse')
		if elemEmptyElse is not None and elemEmptyElse.text: emptyElseGoalsLst = [int(x) for x in elemEmptyElse.text.split(',') if x]
		elemCompound= p_rootXML.find('compound')
		if elemCompound is not None and elemCompound.text: compoundGoalsLst = [int(x) for x in elemCompound.text.split(',') if x]
		elemEndOfFunc= p_rootXML.find('endOfFunc')
		if elemEndOfFunc is not None and elemEndOfFunc.text: endOfFuncGoalsLst = [int(x) for x in elemEndOfFunc.text.split(',') if x]
		elemFor= p_rootXML.find('For')
		if elemFor is not None and elemFor.text: forGoalsLst = [int(x) for x in elemFor.text.split(',') if x]
		elemCXXForRange= p_rootXML.find('CXXForRange')
		if elemCXXForRange is not None and elemCXXForRange.text: cXXForRangeGoalsLst = [int(x) for x in elemCXXForRange.text.split(',') if x]
		elemDoWhile= p_rootXML.find('DoWhile')
		if elemDoWhile is not None and elemDoWhile.text: doWhileGoalsLst = [int(x) for x in elemDoWhile.text.split(',') if x]
		elemWhile= p_rootXML.find('While')
		if elemWhile is not None and elemWhile.text: whileGoalsLst = [int(a) for a in elemWhile.text.split(',') if a]
		
		elemGoalInfos= p_rootXML.find('goalInfos')
		if elemGoalInfos is not None and elemGoalInfos.text != 'ERROR':
			for goalInfo in elemGoalInfos.iter('goalInfo'):
				elemGoalInfo_goal = goalInfo.find('goal')
				elemGoalInfo_depth = goalInfo.find('depth')
				goalAsInt = 0
				if elemGoalInfo_goal is not None:
					goalAsInt = int(elemGoalInfo_goal.text)
				if elemGoalInfo_depth is not None:
					goalDepthDict[goalAsInt] = int(elemGoalInfo_depth.text)
				elemGoalInfo_funcID = goalInfo.find('funcID')
				if elemGoalInfo_funcID is not None:
					goalFuncDict[goalAsInt] = int(elemGoalInfo_funcID.text)
		l_lstGoalsToWorkOn = []
		### Sort the Goals					
		for g in ifGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.IF, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1))) # default = -1
		for g in elseGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.ELSE, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		for g in forGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.FOR, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		for g in cXXForRangeGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.CXX_FOR_RANGE, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		for g in doWhileGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.DO_WHILE, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		for g in whileGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.WHILE, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		for g in compoundGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.COMPOUND, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		for g in loopGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.LOOP, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		for g in endOfFuncGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.END_OF_FUNCTION, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		for g in afterLoopGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.AFTER_LOOP, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		for g in emptyElseGoalsLst: l_lstGoalsToWorkOn.append(GoalInfo(g, GoalType.EMPTY_ELSE, goalDepthDict.get(g, -1),-1,goalFuncDict.get(g,-1)))
		lst_len = len(l_lstGoalsToWorkOn)
		if FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH and \
			(goalSorting == GoalSorting.DEPTH_THEN_TYPE or goalSorting ==GoalSorting.TYPE_THEN_DEPTH):
			for i in range(0, lst_len):
				l_lstGoalsToWorkOn[i].globalDepth = getGlobalDepthOfGoalInfo(l_lstGoalsToWorkOn[i])
				
		# BubbleSort
		if goalSorting == GoalSorting.DEPTH_THEN_TYPE:
			for i in range(0, lst_len):
				for j in range(0, lst_len-i-1):
					depthOfCurrent = l_lstGoalsToWorkOn[j].globalDepth if FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH else l_lstGoalsToWorkOn[j].depth
					depthOfNext = l_lstGoalsToWorkOn[j+1].globalDepth if FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH else l_lstGoalsToWorkOn[j+1].depth
					if ((depthOfCurrent < depthOfNext) or \
						((depthOfCurrent == depthOfNext) and (l_lstGoalsToWorkOn[j].goalType > l_lstGoalsToWorkOn[j + 1].goalType))):
							temp = l_lstGoalsToWorkOn[j]
							l_lstGoalsToWorkOn[j]= l_lstGoalsToWorkOn[j + 1]
							l_lstGoalsToWorkOn[j + 1]= temp
			# Applay IF at First & EmptyElse at End
			if goalSorting_IF_first or goalSorting_EMPTYELSE_last:
				tmp_if_lst, tmp_emptyElse_lst, tmp_afterLoop_lst,tmp_endOfFun_lst, rest_lst = [], [], [] , [], []
				for ginfo in l_lstGoalsToWorkOn:
					if goalSorting_IF_first and ginfo.goalType == GoalType.IF: tmp_if_lst.append(ginfo)
					elif goalSorting_AFTERLOOP_last and ginfo.goalType == GoalType.AFTER_LOOP: tmp_afterLoop_lst.append(ginfo)
					elif goalSorting_EMPTYELSE_last and ginfo.goalType == GoalType.EMPTY_ELSE: tmp_emptyElse_lst.append(ginfo)
					elif goalSorting_END_OF_FUN_last and ginfo.goalType == GoalType.END_OF_FUNCTION: tmp_endOfFun_lst.append(ginfo)
					else : rest_lst.append(ginfo)
				l_lstGoalsToWorkOn = tmp_if_lst + rest_lst + tmp_afterLoop_lst + tmp_emptyElse_lst + tmp_endOfFun_lst
				#del tmp_if_lst, tmp_emptyElse_lst, tmp_afterLoop_lst, rest_lst
		else: #GoalSorting.TYPE_THEN_DEPTH:
			for i in range(0, lst_len):
				for j in range(0, lst_len-i-1):
					depthOfCurrent = l_lstGoalsToWorkOn[j].globalDepth if FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH else l_lstGoalsToWorkOn[j].depth
					depthOfNext = l_lstGoalsToWorkOn[j+1].globalDepth if FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH else l_lstGoalsToWorkOn[j+1].depth
					if (l_lstGoalsToWorkOn[j].goalType > l_lstGoalsToWorkOn[j + 1].goalType or \
						(l_lstGoalsToWorkOn[j].goalType == l_lstGoalsToWorkOn[j + 1].goalType and depthOfCurrent < depthOfNext)):
							temp = l_lstGoalsToWorkOn[j]
							l_lstGoalsToWorkOn[j]= l_lstGoalsToWorkOn[j + 1]
							l_lstGoalsToWorkOn[j + 1]= temp

		#if IS_DEBUG : assert (len(l_lstGoalsToWorkOn) == goals_count)
		if SHOW_ME_OUTPUT:
			print('ifGoalsLst',ifGoalsLst)
			print('compoundGoalsLst',compoundGoalsLst)
			print('loopGoalsLst',loopGoalsLst)
			print('elseGoalsLst',elseGoalsLst)
			print('endOfFuncGoalsLst',endOfFuncGoalsLst)
			print('afterLoopGoalsLst',afterLoopGoalsLst)
			print('emptyElseGoalsLst',emptyElseGoalsLst)
			print('forGoalsLst',forGoalsLst)
			print('cXXForRangeGoalsLst',cXXForRangeGoalsLst)
			print('doWhileGoalsLst',doWhileGoalsLst)
			print('whileGoalsLst',whileGoalsLst)
			print('goalDepthDict','(goal : depth)',goalDepthDict)
			print('goalFuncDict','(goal : funcID)',goalFuncDict)
	except Exception as ex:
		l_lstGoalsToWorkOn = None
		if IS_DEBUG: HandleException(ex)
	return l_lstGoalsToWorkOn

def isAssumptionListsEqual(l1,l2):
	len1 = len(l1)
	if(len1 != len(l2)): return False
	for i in range(0,len1):
		if l1[i].value != l2[i].value : return False
	return True

def isIntListsEqual(l1,l2):
	len1 = len(l1)
	if(len1 != len(l2)): return False
	for i in range(0,len1):
		if l1[i] != l2[i] : return False
	return True

def HandleRepeatedTestcase(inst_assumptions):
	global lstAllTestcases, nRepeatedTCs
	isFound = False
	for l in lstAllTestcases:
		if isAssumptionListsEqual(l, inst_assumptions):
			isFound = True
			break
	if isFound:
		print('    Testcase is repeated ...')
		nRepeatedTCs += 1
		for _ in range(0,5):
			try:
				inst_assumptions[randrange(0,len(inst_assumptions))].value = \
					str(randrange(-127,+127))
			except Exception as ex: HandleException(ex)
	else:
		lstAllTestcases.append(inst_assumptions)

def AddToFuzzerSeedsLst_ErrorCall(seed_name,inst_assumptions):
	global lstFuzzerSeeds
	for _,lstAssumption_loop in lstFuzzerSeeds:
			if isAssumptionListsEqual(lstAssumption_loop,inst_assumptions): return
	lstFuzzerSeeds.append((seed_name,inst_assumptions))
	print('    Add to Seeds list ..., We have',len(lstFuzzerSeeds),'list(s)..')

def AddToFuzzerSeedsLst(goal_id, inst_assumptions):
	global lstFuzzerSeeds
	if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED \
			and FuSeBMCFuzzerLib_CoverBranches_Done == False:
		for _,lstAssumption_loop in lstFuzzerSeeds:
			if isAssumptionListsEqual(lstAssumption_loop,inst_assumptions): return
		lstFuzzerSeeds.append((goal_id,inst_assumptions))
		print('    Add to Seeds list ..., We have',len(lstFuzzerSeeds),'list(s)..')
	elif FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED \
			and FuSeBMCFuzzerLib_CoverBranches_Done \
			and FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED:
		global lstFuzzerSeeds2
		for _,lstAssumption_loop in lstFuzzerSeeds:
			if isAssumptionListsEqual(lstAssumption_loop,inst_assumptions): return
		for _,lstAssumption_loop in lstFuzzerSeeds2:
			if isAssumptionListsEqual(lstAssumption_loop,inst_assumptions): return
		if len(lstFuzzerSeeds2) < FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_SEEDS_NUM_MAX:
			lstFuzzerSeeds2.append((goal_id,inst_assumptions))
			print('    Add to second Seeds list ..., We have',len(lstFuzzerSeeds2),'list(s)..')
		else:
			for i in range(0,len(lstFuzzerSeeds2)):
				if(len(inst_assumptions) > len(lstFuzzerSeeds2[i][1])):
					print('....replace seed',lstFuzzerSeeds2[i][0],'(len='+ str(len(lstFuzzerSeeds2[i][1]))+')',
							'with',goal_id, '(len='+str(len(inst_assumptions))+')')
					lstFuzzerSeeds2[i]=(goal_id, inst_assumptions)
					break
			
	
def runGoalTracer(instrumentedTracerExec,inst_assumptions,goals_covered_file,goal_id):
	global goals_count, fuSeBMC_run_id
	global current_process_name
	#print('len(inst_assumptions) =', len(inst_assumptions))
	lstGoalsInFile = []
	retVal = -1
	RemoveFileIfExists(goals_covered_file)
	RemoveFileIfExists(WRAPPER_Output_Dir + '/tracer_testcase.txt')
	proc_inst = None
	try:
		input_lst = [nonDeterministicCall.value for nonDeterministicCall in inst_assumptions]
		input_str = '\n'.join([inp for inp in input_lst])
		#input_str += "\n"
		os.environ[fuSeBMC_run_id+'_gcnt'] = str(goals_count)
		current_process_name = FuSeBMCProcessName.Tracer_EXE
		process = subprocess.Popen(['timeout' ,'--preserve-status','15s',instrumentedTracerExec],
								stdin=subprocess.PIPE if input_str else None,
								stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=False, cwd=WRAPPER_Output_Dir,preexec_fn=limit_virtual_memory)
		current_process_name = ''
		if input_str and not isinstance(input_str, bytes):
			input_str = input_str.encode()
			#print('\n\n\n\ninput_str=',input_str)
		_, _ = process.communicate(input=input_str
												#, timeout=timelimit if timelimit else None
			)
		retVal = process.poll()
		
		#proc_inst = subprocess.Popen(['timeout' ,'5s',instrumentedTracerExec],stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, cwd=WRAPPER_Output_Dir,preexec_fn=limit_virtual_memory)
		#for nonDeterministicCall in inst_assumptions:
		#	input_str = nonDeterministicCall.value + '\n'
		#if input_str and not isinstance(input_str, bytes):
		#	input_str = input_str.encode()
		#proc_inst.stdin.write(input_str)
		#proc_inst.stdin.flush()
		#proc_inst.wait()
		#print('proc_inst.returncode=',proc_inst.returncode)
		lstGoalsInFile = GetGoalListFromFile(goals_covered_file)
		#lstGoalsToWorkOn = [ginf for ginf in lstGoalsToWorkOn if not ginf.goal in lstGoalsInFile]
		#if IS_DEBUG and len(lstGoalsInFile) > 0:
		#	goals_covered_file_for_goal = WRAPPER_Output_Dir + '/goals_covered_'+str(goal_id)+'.txt'
		#	shutil.move(goals_covered_file, goals_covered_file_for_goal)
	except Exception as ex:
		if proc_inst is not None: proc_inst.kill()
		HandleException(ex)
	return lstGoalsInFile , retVal
	
def writeSelectiveInputsLstToFile():
	global selectiveInputsLst, isSelectiveInputsFromMain
	if selectiveInputsLst is not None and len(selectiveInputsLst) > 0:
		with open (WRAPPER_Output_Dir+'/selective_inputs.txt', 'w') as f:
			if isSelectiveInputsFromMain:
				f.write('99\n')
			else:
				f.write('88\n')
			for s_input in selectiveInputsLst:
				f.write(s_input+'\n')

def getSingleValueFromFuSeBMCFuzzer(p_prop):
	'''
	Return tuple (singleValueFromFuSeBMCFuzzer,maxLengthOfTestcaseFromFuSeBMCFuzzer)
	'''
	global TestSuite_Dir
	singleValueFromFuSeBMCFuzzer = 0
	maxLengthOfTestcaseFromFuSeBMCFuzzer = 0
	try:
		if(p_prop == Property.cover_branches):
			if FuSeBMCFuzzerLib_COVERBRANCHES_EXTRACT_SINGLEVAL_MAXLEN_FROM_TC:
				lsXML_files = glob.glob(TestSuite_Dir + '/FUZ_*.xml')
			else:
				return (singleValueFromFuSeBMCFuzzer,maxLengthOfTestcaseFromFuSeBMCFuzzer)
		elif(p_prop == Property.cover_error_call):
			if FuSeBMCFuzzerLib_ERRORCALL_EXTRACT_SINGLEVAL_MAXLEN_FROM_TC:
				lsXML_files = []
				lsXML_files.extend(glob.glob(TestSuite_Dir + '/FUZ_*.xml'))
				lsXML_files.extend(glob.glob(TestSuite_Dir + '/FuSeBMC_Fuzzer_*.xml'))
			else:
				return (singleValueFromFuSeBMCFuzzer,maxLengthOfTestcaseFromFuSeBMCFuzzer)
		else:
			lsXML_files = glob.glob(TestSuite_Dir + '/FUZ_*.xml')
		if lsXML_files is None or len(lsXML_files) == 0 :
			return (singleValueFromFuSeBMCFuzzer,maxLengthOfTestcaseFromFuSeBMCFuzzer)
		for xml_f in lsXML_files:
			singleValueFromFuSeBMCFuzzerTmp = 0
			try:
					rootXML = ET.parse(xml_f).getroot()
					lsInputs = [inp.text for inp in rootXML.iter('input')]
					tc_len = len(lsInputs)
					if (tc_len > maxLengthOfTestcaseFromFuSeBMCFuzzer):
						maxLengthOfTestcaseFromFuSeBMCFuzzer = tc_len;
					if(tc_len == 1):
						try:
							singleValueFromFuSeBMCFuzzerTmp = int(lsInputs[0])
						except: pass
						if singleValueFromFuSeBMCFuzzerTmp != singleValueFromFuSeBMCFuzzer:
							singleValueFromFuSeBMCFuzzer = singleValueFromFuSeBMCFuzzerTmp
			except Exception as ex:
				HandleException(ex)
	except Exception as ex2:
		HandleException(ex2)
	return (singleValueFromFuSeBMCFuzzer,maxLengthOfTestcaseFromFuSeBMCFuzzer)

def verify(strat, prop, fp_mode):
	global is_ctrl_c
	global remaining_time_s
	global hasInputInTestcase
	global lastInputInTestcaseCount 
	global goals_count
	global lineNumberForNonDetCallsLst
	global witness_file_name
	global infinteWhileNum
	global selectiveInputsLst, isSelectiveInputsFromMain
	global stdCFuncsLst
	
	#sglobal MUST_APPLY_TIME_PER_GOAL
	lastInputInTestcaseCount = 5 # default
	goal_id=0
	goal_witness_file_full=''
	inst_assumptions=[]
	if(prop == Property.cover_branches):
		numOfESBMCRun = 0
		try:
			global lstFuSeBMC_GoalTracerGoals, lstFuSeBMC_FuzzerGoals, callGraph,mainFuncID
			paramAddElse = '--add-else'
			paramAddLabelAfterLoop = '--add-label-after-loop'
			paramAddGoalAtEndOfFunc='--add-goal-at-end-of-func'
			paramExportGoalInfo = ''
			paramGlobalDepth = ''
			if FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH: paramGlobalDepth = '--export-call-graph'
			
			if MUST_APPLY_LIGHT_INSTRUMENT_FOR_BIG_FILES:
				linesCountInSource = getLinesCountInFile(benchmark)
				if linesCountInSource >= BIG_FILE_LINES_COUNT:
					paramAddElse = ''
					paramAddLabelAfterLoop=''
					paramAddGoalAtEndOfFunc = ''
			addFuSeBMCFuncParam = ''
			paramHandleInfiniteWhileLoop = ''
			paramSelectiveInputs = ''
			if COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED:
				paramHandleInfiniteWhileLoop = '--handle-infinite-while-loop'
			if FuSeBMCFuzzerLib_COVERBRANCHES_SELECTIVE_INPUTS_ENABLED:
				paramSelectiveInputs = '--export-selective-inputs'
			#paramHandleReturnInMain = ''
			#if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED : paramHandleReturnInMain = '--handle-return-in-main'
			if MAP2CHECK_COVERBRANCHES_ENABLED: addFuSeBMCFuncParam = '--add-FuSeBMC-func'
			if goalSorting == GoalSorting.DEPTH_THEN_TYPE or goalSorting == GoalSorting.TYPE_THEN_DEPTH:
				paramExportGoalInfo = '--export-goal-info'
			infoFile = WRAPPER_Output_Dir + '/info.xml'
			runWithTimeoutEnabled(' '.join([FUSEBMC_INSTRUMENT_EXE_PATH, '--input',benchmark ,'--output', INSTRUMENT_Output_File , 
								'--goal-output-file',INSTRUMENT_Output_Goals_File, paramAddElse,'--add-labels', '--export-line-number-for-NonDetCalls',
								paramExportGoalInfo,'--add-comment-in-func','fuSeBMC_init=main',
								paramAddLabelAfterLoop, paramAddGoalAtEndOfFunc, addFuSeBMCFuncParam, paramGlobalDepth,
								'--info-file', infoFile,
								paramHandleInfiniteWhileLoop, paramSelectiveInputs,'--export-stdc-func',
								'--compiler-args','-I'+os.path.dirname(benchmark)]))
			
			#Without else + without label-after-loop but with goal at end of function
			#run_without_output(' '.join([FUSEBMC_INSTRUMENT_EXE_PATH, '--input',benchmark ,'--output', INSTRUMENT_Output_File , 
			#					  '--goal-output-file',INSTRUMENT_Output_Goals_File,'--add-labels','--add-goal-at-end-of-func',
			#					  '--compiler-args', '-I'+os.path.dirname(benchmark)]))
			if os.path.isfile(INSTRUMENT_Output_Goals_File):
				with open(INSTRUMENT_Output_Goals_File, 'r') as f_goals_cnt:
					goals_count = int(f_goals_cnt.read())
			
			lstGoalsToWorkOn = None
			lineNumberForNonDetCallsLst = None
			
			if os.path.isfile(infoFile):
				rootXML = ET.parse(infoFile).getroot()
				lineNumberForNonDetCallsLst = parseRootXML_NonDetCalls(rootXML)
				if FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH:
					funcDeclInfoLst = parseRootXML_FuncDeclInfo(rootXML)
					if funcDeclInfoLst is not None:
						callGraph = Graph()
						for (funcID,funcName) in funcDeclInfoLst:
							callGraph.add_vertex(funcID)
							if funcName =='main':
								mainFuncID = funcID
						if mainFuncID <= 0:
							callGraph = None
							HandleException(Exception('mainFuncID is not valid:'+ str(mainFuncID)))
						funcCallInfoLst = parseRootXML_FuncCallInfo(rootXML)
						if funcCallInfoLst is None: callGraph = None
						if funcCallInfoLst is not None and callGraph is not None:
							for(callerID,calleeID,depth) in funcCallInfoLst:
								callGraph.add_edge(callerID, calleeID, depth)
							if IS_DEBUG: callGraph.print_graph()
							dijkstra(callGraph,callGraph.get_vertex(mainFuncID))
				if FuSeBMCFuzzerLib_COVERBRANCHES_SELECTIVE_INPUTS_ENABLED:
					selectiveInputsLst, isSelectiveInputsFromMain = parseRootXML_SelectiveInputs(rootXML)
					writeSelectiveInputsLstToFile()
					if IS_DEBUG:
						print('selectiveInputsLst',selectiveInputsLst)
						print('isSelectiveInputsFromMain', isSelectiveInputsFromMain)
					#exit(0)
				stdCFuncsLst = parseRootXML_StdCFuncs(rootXML)
				if IS_DEBUG:
					print('stdCFuncsLst',stdCFuncsLst)
				if (goalSorting == GoalSorting.DEPTH_THEN_TYPE or goalSorting == GoalSorting.TYPE_THEN_DEPTH):
					lstGoalsToWorkOn = getLstGoalsToWorkOn(rootXML)
				infinteWhileNum = parseRootXML_InfinteWhileNum(rootXML)
				if(infinteWhileNum != 0): print('Infinte While Loops =',infinteWhileNum)
				
				del rootXML

			if goalSorting == GoalSorting.SEQUENTIAL or lstGoalsToWorkOn is None:
				lstGoalsToWorkOn = [GoalInfo(g, GoalType.NONE , -1) for g in range(1,goals_count+1)]
			lstGoalsToWorkOnLen = len(lstGoalsToWorkOn)
			if IS_DEBUG:
				print('lstGoalsToWorkOn:',lstGoalsToWorkOnLen, 'Goal(s)')
				for ginfo in lstGoalsToWorkOn: print(ginfo.toString())
			IsTimeOut(True)
			#check if FuSeBMC_inustrument worked
			if not os.path.isfile(INSTRUMENT_Output_File):
				print("Cannot instrument the file.")
				if IS_DEBUG:
					print(TColors.FAIL,'Cannot instrument the file.',TColors.ENDC)
					exit(0)
				#return Result.unknown
			if not os.path.isfile(INSTRUMENT_Output_Goals_File):
				print("Cannot instrument the file, goalFile cannot be found.")
				if IS_DEBUG:
					print(TColors.FAIL,'Cannot instrument the file, goalFile cannot be found.',TColors.ENDC)
					exit(0)
				#return Result.unknown
			#with open(INSTRUMENT_Output_File, 'a') as f:
			#	f.write('\nvoid my_assert(const char * a, const char * b, unsigned int c, const char * d){exit(0);}\n')

			if MUST_COMPILE_INSTRUMENTED:
				CompileFile(INSTRUMENT_Output_File,os.path.dirname(benchmark))
			if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED:
				instrumentedAFL_src = WRAPPER_Output_Dir + '/instrumented_afl.c'
				ReplaceGoalLabelWithFuseGoalCalledMethod(INSTRUMENT_Output_File, instrumentedAFL_src)
			goalTracerExecOK = False
			if FuSeBMC_GoalTracer_ENABLED:
				instrumentedTracer = WRAPPER_Output_Dir + '/instrumented_tracer.c'
				instrumentedTracerExec = os.path.abspath(WRAPPER_Output_Dir + '/tracer.exe')
				goals_covered_file = WRAPPER_Output_Dir + '/goals_covered.txt'
				wrapperHomeDir = os.path.dirname(__file__)
				gccArch = '-m' + str(arch)
				if not FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED:
					ReplaceGoalLabelWithFuseGoalCalledMethod(INSTRUMENT_Output_File, instrumentedTracer)
				else:
					instrumentedTracer = instrumentedAFL_src # the same file from fuzzer.
				#-std=gnu11 -m32 -Wno-attributes -D__alias__(x)=
				compile_tracer_lst = [FuSeBMC_GoalTracer_CC,FuSeBMC_GoalTracer_CC_PARAMS,
											'-D abort=fuSeBMC_abort_prog',
											'-I'+os.path.dirname(benchmark),
											'-std=gnu11',gccArch,'-Wno-attributes','-D__alias__(x)=', '-o',instrumentedTracerExec,
											'-L'+wrapperHomeDir+'/FuSeBMC_GoalTracerLib/', instrumentedTracer,
											'-lFuSeBMC_GoalTracerLib_'+str(arch),'-lm','-lpthread']
				for func in stdCFuncsLst:
					compile_tracer_lst.append('-D ' + func + '='+func+'_XXXX')
				runWithTimeoutEnabled(' '.join(compile_tracer_lst))
				goalTracerExecOK = os.path.isfile(instrumentedTracerExec)

			goals_covered_lst = []
			goals_covered_by_map2check=[]
			goals_to_be_run_map2check = []
			nTestcasesCoverItsGoal = nTestcasesNotCoverItsGoal= 0
			#if MUST_APPLY_TIME_PER_GOAL and goals_count>0 :
			#	time_per_goal_for_esbmc=int(time_out_s) / goals_count
			#	time_per_goal_for_esbmc =int(time_per_goal_for_esbmc) # ms to second
			#	if time_per_goal_for_esbmc == 0 : time_per_goal_for_esbmc = 1

			#counter=0
			isFromMap2Check=False

			if MAP2CHECK_COVERBRANCHES_ENABLED:
				if(lstGoalsToWorkOnLen > 2): goals_to_be_run_map2check.append(lstGoalsToWorkOn[1].goal)
				if(lstGoalsToWorkOnLen > 5): goals_to_be_run_map2check.append(lstGoalsToWorkOn[4].goal)
				goalInTheMiddle = int(lstGoalsToWorkOnLen / 2) if lstGoalsToWorkOnLen > 0 else 0
				if goalInTheMiddle not in goals_to_be_run_map2check:
					goals_to_be_run_map2check.append(lstGoalsToWorkOn[goalInTheMiddle].goal)
				goals_to_be_run_map2check.append(lstGoalsToWorkOn[-1].goal)
	
			print('\nRunning FuSeBMC for Cover-Branches:\n')
			#if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED:
			#	instrumentedESBMC = WRAPPER_Output_Dir + '/instrumented_esbmc.c'
			#	with open(instrumentedESBMC,'w') as fout:
			#		fout.write('extern void fuSeBMC_return(int code){}\n')
			#		with open(INSTRUMENT_Output_File,'r') as fin:
			#			for line in fin: fout.write(line)
			#	if lineNumberForNonDetCallsLst is not None:
			#		lineNumberForNonDetCallsLst = [(line_nr + 1,funcName) for (line_nr,funcName) in lineNumberForNonDetCallsLst] # icrease by 2 Line.
			#else: instrumentedESBMC = INSTRUMENT_Output_File
			instrumentedESBMC = INSTRUMENT_Output_File

			SourceCodeChecker.loadSourceFromFile(instrumentedESBMC)
			linesInSource = len(SourceCodeChecker.__lines__)
			if IS_DEBUG: print(TColors.OKGREEN,'Lines In source:',linesInSource,TColors.ENDC)
			if SHOW_ME_OUTPUT: print('lineNumberForNonDetCallsLst','(line,funcName)',lineNumberForNonDetCallsLst)
			lstFuSeBMC_FuzzerGoals = []
			## Starting Goals LOOP !!!
			#for goalInfo in lstGoalsToWorkOn:
			counter = 0
			if MUST_APPLY_TIME_PER_GOAL : time_for_goal_max = int(time_out_s / 5)
			while len(lstGoalsToWorkOn) > 0:
				counter += 1
				goalInfo = lstGoalsToWorkOn.pop(0)
				goal_id = goalInfo.goal
				goal='GOAL_'+str(goal_id)
				isFromMap2Check = False
				IsTimeOut(True)
				if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED and not FuSeBMCFuzzerLib_CoverBranches_Done \
					and (len(lstFuzzerSeeds) >= FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL \
					or remaining_time_s < time_out_s / 3):
					lstFuSeBMC_FuzzerGoals = RunAFLForCoverBranches(instrumentedAFL_src)
					'''
					#### BEGIN CHECK ####
					tc_counter = 1000
					for root, dirs, files in os.walk(TestSuite_Dir):
						for file in files:
							if file.startswith('FUZ_') and file.endswith('.xml'):
								tc_counter += 1
								print('*************************s')
								print(file)
								full_file_name = os.path.join(root, file)
								rootXML_t = ET.parse(full_file_name).getroot()
								lsInputs = [inp.text for inp in rootXML_t.iter('input')]
								inst_assumptions_gl = [NonDeterministicCall(inp) for inp in lsInputs]
								gls_lst = []
								gls_file = full_file_name + '.txt'
								with open (gls_file,'r') as gls_file_f:
									for gl in gls_file_f:
										if len(gl)>0 :
											if gl.startswith('#'): continue
											gl_int = int(gl)
											#if gl_int not in gls_lst :
											gls_lst.append(gl_int)
								os.environ['xxx']='./test-suite/'+file+'.inp'
								gls_lst_tracer,retValTmp = runGoalTracer(instrumentedTracerExec,inst_assumptions_gl,goals_covered_file,tc_counter)
								isGoalsEQ = isIntListsEqual(gls_lst,gls_lst_tracer)
								generatedInlst = []
								with open(full_file_name+'.inp','r') as f:
									for inpTmp in f: generatedInlst.append(inpTmp.rstrip())
								isInputsEQ = isIntListsEqual(lsInputs,generatedInlst)
								if not isGoalsEQ or not isInputsEQ:
									print('gls_lst       ',gls_lst)
									print('gls_lst_tracer',gls_lst_tracer)
									
									print('lsInputs      ',lsInputs)
									print('generatedInlst',generatedInlst)
								
					del tc_counter,file,full_file_name,rootXML_t,lsInputs,inst_assumptions_gl
					del gls_lst,gls_file,gls_lst_tracer,retValTmp
					exit(0)
					'''
					#### END  CHECK ####
				
				param_timeout_esbmc = ''
				time_for_goal = -1
				param_memlimit_esbmc = ''
				if MUST_APPLY_TIME_PER_GOAL:
					factor=2 # 1/2 of the remaining time
					if counter < goals_count / 2 : factor=3 # 1/3 of the remaining time
					#remaining_time_s = int(remaining_time_ms / 1000) # ms to second
					if counter < goals_count and remaining_time_s > 10:
						time_for_goal = int(remaining_time_s/factor)
						if counter < goals_count / 2 and time_for_goal > time_for_goal_max :
							time_for_goal = time_for_goal_max
						if time_for_goal < 20 : time_for_goal = -1
					if time_for_goal > 0 : param_timeout_esbmc = ' --timeout ' + str(time_for_goal) + 's '
				if MEM_LIMIT_BRANCHES_ESBMC > 0:
					param_memlimit_esbmc = ' --memlimit ' + str(MEM_LIMIT_BRANCHES_ESBMC) + 'g '
					
				inst_assumptions=[]
				if(SHOW_ME_OUTPUT): print(TColors.OKGREEN+'+++++++++++++++++++++++++++++++'+TColors.ENDC)
				print('------------------------------------')
				print('STARTING : ', goalInfo.toString(),'     ('+str(counter)+'/'+str(lstGoalsToWorkOnLen)+')')
				sys.stdout.flush()
				# You can use or True to run all
				if MAP2CHECK_COVERBRANCHES_ENABLED and (goal_id in goals_to_be_run_map2check):
					isFromMap2Check = True
					test_case_file_full=os.path.join(TestSuite_Dir,'testcase_'+str(goal_id)+'_map.xml')
					goal_witness_file_full = map2checkWitnessFile
					RemoveFileIfExists(map2checkWitnessFile)
					map2CheckSrc = os.path.abspath(WRAPPER_Output_Dir+'/fusebmc_instrument_output/sed_' + goal + '.c')
					sed_cmd_line = ' '.join(['sed',"'s/"+goal+':'+"/FuSeBMC_custom_func()/g'", INSTRUMENT_Output_File])
					try:
						map2CheckSrc_f = open(map2CheckSrc, 'a')
						#if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED :
						#	sedOutFile.write('void fuSeBMC_return(int code){}\n')
						#	sedOutFile.flush()
						_ = subprocess.run(shlex.split(sed_cmd_line), stdout=map2CheckSrc_f,stderr=subprocess.DEVNULL)
						map2CheckSrc_f.flush()
						map2CheckSrc_f.close()
						#MAP2CHECK_COVERBRANCHES_TIMEOUT : can be caculated !!
						#map2CheckNonDetGenerator = 'symex' if linesInSource >= 11000 else 'fuzzer'
						map2CheckNonDetGenerator = 'fuzzer'
						runWithTimeoutEnabled(' '.join(['timeout',str(MAP2CHECK_COVERBRANCHES_TIMEOUT)+'s', MAP2CHECK_EXE,'--timeout',str(MAP2CHECK_COVERBRANCHES_TIMEOUT),'--fuzzer-mb', str(MEM_LIMIT_BRANCHES_MAP2CHECK),'--nondet-generator',map2CheckNonDetGenerator , '--target-function','--target-function-name', 'FuSeBMC_custom_func', '--generate-witness',map2CheckSrc]), WRAPPER_Output_Dir)
						if os.path.isfile(map2checkWitnessFile):
							inst_assumptions=__getNonDetAssumptions__(map2checkWitnessFile,instrumentedESBMC,True)
							inst_assumptions_len = len(inst_assumptions)
							shutil.copy(map2checkWitnessFile,WRAPPER_Output_Dir + '/map2check_'+str(goal_id)+'.graphml')
							if inst_assumptions_len > 0 :
								generate_testcase_from_assumption_CoverBranches(test_case_file_full,inst_assumptions)
								if inst_assumptions_len > lastInputInTestcaseCount: lastInputInTestcaseCount = inst_assumptions_len
								hasInputInTestcase = True
								goals_covered_lst.append(goal_id)
								goals_covered_by_map2check.append(goal_id)	
						# comment or uncomment kaled ...
						#continue: means don't execute ESBMC on goal_id
						#if len(inst_assumptions)>0: # for example
						#	continue
						#if goals_count > 20: # for example
						#	continue
						#continue # always # you can not use it again
					except MyTimeOutException as mytime_ex: raise mytime_ex
					except KeyboardInterrupt as kb_ex: raise kb_ex;
					except Exception as ex: print(TColors.FAIL); print(ex); print(TColors.ENDC)
					
					# End of MAP2CHECK_COVERBRANCHES_ENABLED
				if FuSeBMC_GoalTracer_ENABLED and goalTracerExecOK and goal_id in lstFuSeBMC_GoalTracerGoals:
					print('    is already covered by FuSeBMC_Tracer...')
					continue
				if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED and FuSeBMCFuzzerLib_CoverBranches_Done \
				and lstFuSeBMC_FuzzerGoals is not None and goal_id in lstFuSeBMC_FuzzerGoals:
					print('    is already covered by FuSeBMC_Fuzzer...')
					continue
				
				print('    time_for_goal:', time_for_goal, 's', '/', remaining_time_s, 's')
				####### START ESBMC ######
				try:
					isFromMap2Check = False
					goal_witness_file=goal+'.graphml'
					goal_witness_file_full=os.path.join(INSTRUMENT_Output_Dir ,goal_witness_file)
					test_case_file_full=os.path.join(TestSuite_Dir,'testcase_'+str(goal_id)+'_ES.xml')
					inst_esbmc_command_line = get_command_line(strat, prop, arch, instrumentedESBMC, fp_mode)
					
					#idx = 10 if len(lstGoalsToWorkOn) > 10 else len(lstGoalsToWorkOn)
					#ll=[lstGoalsToWorkOn[i].goal for i in range(0,idx)]
					#ll.append(goalInfo.goal)
					#ll_str = ['GOAL_' + str(g) for g in ll]
					
					
					inst_new_esbmc_command_line = inst_esbmc_command_line + ' --witness-output ' + goal_witness_file_full + ' --error-label ' + goal \
													+ ' -I'+os.path.dirname(benchmark) + param_timeout_esbmc + param_memlimit_esbmc
													# + ' --timeout ' + str(time_per_goal_for_esbmc)+ 's '
					output = run(inst_new_esbmc_command_line)
					numOfESBMCRun += 1
					IsTimeOut(True)
					res = parse_result(output, category_property)
					if(res == Result.force_fp_mode):
						print('Chosen solver doesn\'t support floating-point numbers.')
						fp_mode = True
						inst_esbmc_command_line = get_command_line(strat, prop, arch, instrumentedESBMC, fp_mode)
						inst_new_esbmc_command_line = inst_esbmc_command_line + ' --witness-output ' + goal_witness_file_full + ' --error-label ' + goal \
													+ ' -I'+os.path.dirname(benchmark) + param_timeout_esbmc + param_memlimit_esbmc
													# + ' --timeout ' + str(time_per_goal_for_esbmc)+ 's '
						output = run(inst_new_esbmc_command_line)
	
					if not os.path.isfile(goal_witness_file_full):
						print('Cannot run ESBMC for '+ goal)
					else:
						inst_assumptions=__getNonDetAssumptions__(goal_witness_file_full,instrumentedESBMC)
						if len(inst_assumptions)>0 :
							AddToFuzzerSeedsLst(goal_id, inst_assumptions)
							if COVERBRANCHES_HANDLE_REPEATED_TESTCASES_ENABLED:
								HandleRepeatedTestcase(inst_assumptions)
							if len(inst_assumptions) > lastInputInTestcaseCount: lastInputInTestcaseCount = len(inst_assumptions)
							hasInputInTestcase=True
							goals_covered_lst.append(goal_id)
							
							if FuSeBMC_GoalTracer_ENABLED and goalTracerExecOK:
								lstGoalsTracerTmp,tracerRetVal = runGoalTracer(instrumentedTracerExec,inst_assumptions,goals_covered_file,goal_id)
								if lstGoalsTracerTmp is not None:
									for g_loop in lstGoalsTracerTmp:
										if g_loop not in lstFuSeBMC_GoalTracerGoals: lstFuSeBMC_GoalTracerGoals.append(g_loop)
								print('   ', goal,'covers:',lstGoalsTracerTmp,' =',len(lstGoalsTracerTmp))
								if IS_DEBUG:
									if goal_id in lstGoalsTracerTmp:
										nTestcasesCoverItsGoal += 1
										print('   ','Testcase COVERS its goal.','tracerRetVal =',tracerRetVal)
									else:
										nTestcasesNotCoverItsGoal += 1
										print('   ','Testcase DOESN\'T COVER its goal.','tracerRetVal =',tracerRetVal)
								del lstGoalsTracerTmp
							
							generate_testcase_from_assumption_CoverBranches(test_case_file_full,inst_assumptions)
							#else:
		
				except MyTimeOutException as eTime: raise eTime
				except KeyboardInterrupt as ex_kb: raise ex_kb 
				except Exception as ex: HandleException(ex)
				####### END ESBMC ######
		except MyTimeOutException as e: pass
		except KeyboardInterrupt: pass
		except Exception as ex: HandleException(ex)
		#IsTimeOut(False)
		#print('remaining_time_s=',remaining_time_s)
		#if not IsMetaDataGenerated:
		#	generate_metadata_from_witness(goal_witness_file_full)
		
		if os.path.isfile(goal_witness_file_full) and not os.path.isfile(test_case_file_full):
			inst_assumptions=__getNonDetAssumptions__(goal_witness_file_full,instrumentedESBMC, isFromMap2Check)
			#inst_all_assumptions.append(inst_assumptions)
			if len(inst_assumptions)>0 :
				if len(inst_assumptions) > lastInputInTestcaseCount: lastInputInTestcaseCount = len(inst_assumptions)
				hasInputInTestcase=True
				if isFromMap2Check : goals_covered_by_map2check.append(goal_id)
				else:goals_covered_lst.append(goal_id)
				
				generate_testcase_from_assumption_CoverBranches(test_case_file_full,inst_assumptions)

		if not is_ctrl_c and FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED and not FuSeBMCFuzzerLib_CoverBranches_Done:
			lstFuSeBMC_FuzzerGoals = RunAFLForCoverBranches(instrumentedAFL_src)
		
		if MUST_GENERATE_RANDOM_TESTCASE or MUST_ADD_EXTRA_TESTCASE:
			extra_test_case_id = goals_count + 1
		#hasInputInTestcase=False # for test
		if MUST_GENERATE_RANDOM_TESTCASE: #and not hasInputInTestcase:
			singleValueFromFuSeBMCFuzzer, maxLengthOfTestcaseFromFuSeBMCFuzzer = getSingleValueFromFuSeBMCFuzzer(prop)
			singleValueFromFuSeBMCFuzzer *= 4
			
			random_testcase_file=os.path.join(TestSuite_Dir,'Testcase_'+str(extra_test_case_id)+'_Fu.xml')
			extra_test_case_id += 1
			randomMaxRange = 5 # hh
			rndLst=[]
			if lastInputInTestcaseCount > 0:
				randomMaxRange = lastInputInTestcaseCount + 1
			if randomMaxRange == 3:
				randomMaxRange -= 1
				rndLst=[NonDeterministicCall('0')] + \
						[NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]
			elif randomMaxRange == 2:
				rndLst = [NonDeterministicCall(str(singleValueFromFuSeBMCFuzzer))]
			else:
				randomMaxRange -= 2
				rndLst = [NonDeterministicCall('0')] + \
							[NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]+[NonDeterministicCall('0')]
			#randomMaxRange = 36
			#rndLst = [NonDeterministicCall('0')]
			#		[NonDeterministicCall('0')] + \
			#		[NonDeterministicCall('0')] # note : Two Zeros
			generate_testcase_from_assumption_CoverBranches(random_testcase_file, rndLst, True)# was 5
		
		if MUST_ADD_EXTRA_TESTCASE:
			lst2=[NonDeterministicCall('0'),NonDeterministicCall('128')] * int(lastInputInTestcaseCount/2)
			if lastInputInTestcaseCount % 2 == 1: lst2.append(NonDeterministicCall('0'))
			lst4=[]
			for i in range(0,lastInputInTestcaseCount):
				if i % 3 == 0 : lst4.append(NonDeterministicCall('0'))
				if i % 3 == 1 : lst4.append(NonDeterministicCall('128'))
				if i % 3 == 2 : lst4.append(NonDeterministicCall('-256'))
			
			#randomMaxRange = 36
			if singleValueFromFuSeBMCFuzzer == 0: singleValueFromFuSeBMCFuzzer = 128 # No Sigle Value; default 128
			elif singleValueFromFuSeBMCFuzzer < 0: singleValueFromFuSeBMCFuzzer *= -1
			
			if IS_DEBUG: print(TColors.OKGREEN,'singleValueFromFuSeBMCFuzzer=',singleValueFromFuSeBMCFuzzer, TColors.ENDC)
			lst5 = [NonDeterministicCall(str(randrange(-singleValueFromFuSeBMCFuzzer,singleValueFromFuSeBMCFuzzer))) for i in range(1,lastInputInTestcaseCount)] + \
					[NonDeterministicCall('0'), NonDeterministicCall('0')]
			lst6 = [NonDeterministicCall('0')]
				
			extra_lsts=[[NonDeterministicCall(str(randrange(-128,128))) for _ in range(0,lastInputInTestcaseCount-1)],
						lst2,
						[NonDeterministicCall('128')]+[NonDeterministicCall('0') for _ in range(0,lastInputInTestcaseCount-1)],
						lst4, lst5 , lst6]
			for l in extra_lsts:
				extra_testcase_file=os.path.join(TestSuite_Dir,'Testcase_'+str(extra_test_case_id)+'_Fu.xml')
				extra_test_case_id += 1
				generate_testcase_from_assumption_CoverBranches(extra_testcase_file,l, True)

		lstFuSeBMC_FuzzerGoals_Run2 = []
		if not is_ctrl_c and FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED:
			lstFuSeBMC_FuzzerGoals_Run2 = RunAFLForCoverBranches_Run2()
		if RUN_TESTCOV: RunTestCov(benchmark,property_file,arch,WRAPPER_Output_Dir)
		if COVERBRANCHES_SHOW_UNIQUE_TESTCASES:
			os.system('python3 fusebmc_non_repeated_testcases.py --testsuite ' + TestSuite_Dir)
		if IS_DEBUG:
			print('fuSeBMC_run_id:',fuSeBMC_run_id)
			print('goals_count',goals_count)
			print('goals_covered_lst',goals_covered_lst,'=', len(goals_covered_lst))
			print('numOfESBMCRun =', numOfESBMCRun)
			if MAP2CHECK_COVERBRANCHES_ENABLED:
				print('goals_covered_by_map2check',goals_covered_by_map2check)
				print('goals_to_be_run_map2check', goals_to_be_run_map2check)
			if FuSeBMC_GoalTracer_ENABLED:
				print('lstFuSeBMC_GoalTracerGoals',lstFuSeBMC_GoalTracerGoals,'=',len(lstFuSeBMC_GoalTracerGoals))
				print('nTestcasesCoverItsGoal =',nTestcasesCoverItsGoal)
				print('nTestcasesNotCoverItsGoal =',nTestcasesNotCoverItsGoal)
			if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED and lstFuSeBMC_FuzzerGoals is not None:
				print('lstFuSeBMC_FuzzerGoals',lstFuSeBMC_FuzzerGoals,'=',len(lstFuSeBMC_FuzzerGoals))
			if FuSeBMC_GoalTracer_ENABLED and FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED:
				lstTracer_union_Fuzzer = [g for g in lstFuSeBMC_GoalTracerGoals]
				for g in lstFuSeBMC_FuzzerGoals:
					if g not in lstTracer_union_Fuzzer: lstTracer_union_Fuzzer.append(g)
				print('lstTracer_union_Fuzzer',lstTracer_union_Fuzzer,'=',len(lstTracer_union_Fuzzer))
				
				Tracer_itersect_Fuzzer = [g for g in lstFuSeBMC_GoalTracerGoals if g in lstFuSeBMC_FuzzerGoals]
				print('Tracer_itersect_Fuzzer',Tracer_itersect_Fuzzer)
				
				lstTracer_but_not_Fuzzer = [g for g in lstFuSeBMC_GoalTracerGoals if g not in lstFuSeBMC_FuzzerGoals]
				print('lstTracer_but_not_Fuzzer',lstTracer_but_not_Fuzzer,'=',len(lstTracer_but_not_Fuzzer))
				
				lstFuzzer_but_not_Tracer = [g for g in lstFuSeBMC_FuzzerGoals if g not in lstFuSeBMC_GoalTracerGoals]
				print('lstFuzzer_but_not_Tracer',lstFuzzer_but_not_Tracer,'=',len(lstFuzzer_but_not_Tracer))
			if FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED:
				print('lstFuSeBMC_FuzzerGoals_Run2',lstFuSeBMC_FuzzerGoals_Run2,'=',len(lstFuSeBMC_FuzzerGoals_Run2))
			if COVERBRANCHES_HANDLE_REPEATED_TESTCASES_ENABLED:
				print('nRepeatedTCs =',nRepeatedTCs)
		
		#global start_time
		#print('Execution t_i_m_e:',time.time() - start_time,' Second.')

		# todo: what is the result
		#if(len(inst_all_assumptions)>0):
		#	return parse_result("VERIFICATION FAILED",prop)
		#else:
		#	return parse_result("VERIFICATION SUCCESSFUL",prop)
		if is_ctrl_c:
			#return parse_result("something else will get unknown",prop)
			return 'DONE'
		if IsTimeOut(False):
			#return parse_result("Timed out",prop)
			print('The Time is out..')
		#print('remaining_time_s=',remaining_time_s)
		#return parse_result("VERIFICATION SUCCESSFUL",prop)
		return 'DONE'
		
	if(prop == Property.cover_error_call):
		goal = 0
		isFromMap2Check = False
		try:
			print('STARTING INSTRUMENTATION  ... \n')
			global toWorkSourceFile
			global runNumber
			is_test_file_created=False
			witness_file_name = ''
			testCaseFileName = None
			myLabel = 'FuSeBMC_ERROR'
			infoFile = WRAPPER_Output_Dir + '/info.xml'
			paramHandleInfiniteWhileLoop = ''
			paramInfinteWhileLoopLimit = ''
			paramSelectiveInputs = ''
			if ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED:
				paramHandleInfiniteWhileLoop = '--handle-infinite-while-loop'
			if FuSeBMCFuzzerLib_ERRORCALL_SELECTIVE_INPUTS_ENABLED:
				paramSelectiveInputs = '--export-selective-inputs'
			
			runWithTimeoutEnabled(' '.join([FUSEBMC_INSTRUMENT_EXE_PATH, '--input',benchmark ,'--output', INSTRUMENT_Output_File , 
									paramHandleInfiniteWhileLoop, paramInfinteWhileLoopLimit, paramSelectiveInputs,
									'--add-label-in-func',myLabel + '=reach_error,fuSeBMC_init=main','--info-file', infoFile,
									'--export-line-number-for-NonDetCalls','--export-stdc-func',
									'--compiler-args', '-I'+os.path.dirname(benchmark)]))
			IsTimeOut(True)
			lineNumberForNonDetCallsLst = None
			if os.path.isfile(infoFile):
				try:
					rootXML = ET.parse(infoFile).getroot()
					lineNumberForNonDetCallsLst = parseRootXML_NonDetCalls(rootXML)
					infinteWhileNum = parseRootXML_InfinteWhileNum(rootXML)
					if(infinteWhileNum != 0): print('Infinte While Loops =',infinteWhileNum)
					if FuSeBMCFuzzerLib_ERRORCALL_SELECTIVE_INPUTS_ENABLED:
						selectiveInputsLst, isSelectiveInputsFromMain = parseRootXML_SelectiveInputs(rootXML)
						if selectiveInputsLst is not None and len(selectiveInputsLst) > 0:
							writeSelectiveInputsLstToFile()
						if IS_DEBUG:
							print('selectiveInputsLst', selectiveInputsLst)
							print('isSelectiveInputsFromMain', isSelectiveInputsFromMain)
					stdCFuncsLst = parseRootXML_StdCFuncs(rootXML)
					if IS_DEBUG:
						print('stdCFuncsLst',stdCFuncsLst)
					del rootXML
				except Exception as ex : HandleException(ex)
			isInstrumentOK=True
			#check if FuSeBMC_inustrument worked
			if not os.path.isfile(INSTRUMENT_Output_File):
				HandleException(Exception('Cannot instrument the file'), '', True)
				isInstrumentOK = False
				myLabel = 'ERROR'
				toWorkSourceFile=benchmark
			else:
				toWorkSourceFile=INSTRUMENT_Output_File
				#return "Error"
			if MUST_COMPILE_INSTRUMENTED :
				CompileFile(toWorkSourceFile,os.path.dirname(os.path.abspath(toWorkSourceFile)))
			#SourceCodeChecker.loadSourceFromFile(toWorkSourceFile)
			#linesInSource = len(SourceCodeChecker.__lines__)

			if MAP2CHECK_ERRORCALL_FUZZER_ENABLED:
				goal += 1
				print('STARTING GOAL '+str(goal)+' ... \n');sys.stdout.flush()
				try:
					isFromMap2Check = True
					is_test_file_created = False
					#RemoveFileIfExists(map2checkWitnessFile)
					#map2CheckNonDetGenerator = 'symex' if linesInSource >= 11000 else 'fuzzer'
					map2CheckNonDetGenerator = 'fuzzer'
					witness_file_name = map2checkWitnessFile
					testCaseFileName = TestSuite_Dir + "/testcase_map_fuzzer.xml"
					runWithTimeoutEnabled(' '.join(['timeout',str(MAP2CHECK_ERRORCALL_FUZZER_TIMEOUT)+'s', MAP2CHECK_EXE,'--timeout',str(MAP2CHECK_ERRORCALL_FUZZER_TIMEOUT),'--fuzzer-mb', str(MEM_LIMIT_ERROR_CALL_MAP2CHECK), '--nondet-generator', map2CheckNonDetGenerator, '--target-function', '--target-function-name','reach_error','--generate-witness',os.path.abspath(toWorkSourceFile)]), WRAPPER_Output_Dir)
					if os.path.isfile(map2checkWitnessFile):
						createTestFile(map2checkWitnessFile,toWorkSourceFile, testCaseFileName ,True)
						if MAP2CHECK_ERRORCALL_SYMEX_ENABLED:
							shutil.copy(map2checkWitnessFile, WRAPPER_Output_Dir + '/map2check_fuzzer.graphml')
						is_test_file_created=True
				except MyTimeOutException as e: raise e
				except KeyboardInterrupt as kbe: raise kbe
				except Exception as ex :HandleException(ex)
				
			if MAP2CHECK_ERRORCALL_SYMEX_ENABLED:
				goal += 1
				print('STARTING GOAL '+str(goal)+' ... \n')
				try:
					isFromMap2Check = True
					is_test_file_created = False
					RemoveFileIfExists(map2checkWitnessFile)
					#map2CheckNonDetGenerator = 'symex' if linesInSource >= 11000 else 'fuzzer'
					map2CheckNonDetGenerator = 'symex'
					testCaseFileName = TestSuite_Dir + '/testcase_map_symex.xml'
					witness_file_name = map2checkWitnessFile
					runWithTimeoutEnabled(' '.join(['timeout',str(MAP2CHECK_ERRORCALL_SYMEX_TIMEOUT)+'s', MAP2CHECK_EXE,'--timeout',str(MAP2CHECK_ERRORCALL_SYMEX_TIMEOUT),'--fuzzer-mb', str(MEM_LIMIT_ERROR_CALL_MAP2CHECK),'--nondet-generator', map2CheckNonDetGenerator, '--target-function', '--target-function-name','reach_error','--generate-witness',os.path.abspath(toWorkSourceFile)]), WRAPPER_Output_Dir)
					if os.path.isfile(map2checkWitnessFile):
						createTestFile(map2checkWitnessFile,toWorkSourceFile, testCaseFileName ,True)
						#shutil.copy(map2checkWitnessFile, WRAPPER_Output_Dir + '/map2check_symex.graphml'))
						is_test_file_created=True
				except MyTimeOutException as e: raise e
				except KeyboardInterrupt as kbe: raise kbe
				except Exception as ex :HandleException(ex)

			
			if ERRORCALL_RUNTWICE_ENABLED:
				try:
					IsTimeOut(True)
					runNumber = 1
					goal += 1
					print('STARTING GOAL '+str(goal)+' ... \n');sys.stdout.flush()
					is_test_file_created = False
					isFromMap2Check = False
					testCaseFileName = TestSuite_Dir + '/testcase_'+str(goal)+'_ES.xml'
					esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)	
					witness_file_name = os.path.join(INSTRUMENT_Output_Dir,os.path.basename(benchmark) + '__2.graphml')
					esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(benchmark)+ ' '
					if isInstrumentOK : esbmc_command_line += ' --error-label ' + myLabel + ' '
					#timeout_for_run1 = remaining_time_s - 5
					#if FuSeBMCFuzzerLib_ERRORCALL_ENABLED:
					#	timeout_for_run1 -= FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT
					#if timeout_for_run1 < 0 : timeout_for_run1 = 10
					#timeout_for_run1 = 60 # second
					esbmc_command_line += ' --timeout ' + str(ERRORCALL_ESBMC_RUN1_TIMEOUT)+'s '
					esbmc_command_line += ' --memlimit ' + str(MEM_LIMIT_ERROR_CALL_ESBMC) + 'g '
					output = run(esbmc_command_line)
					IsTimeOut(True)
					if os.path.isfile(witness_file_name):
						createTestFile(witness_file_name,toWorkSourceFile, testCaseFileName , False)
						is_test_file_created=True
				except MyTimeOutException as e: raise e
				except KeyboardInterrupt as kbe: raise kbe
				except Exception as ex : HandleException(ex)
			
			if FuSeBMCFuzzerLib_ERRORCALL_ENABLED:
				try:
					print('\nRunning FuSeBMC for Cover-Error:\n')
					RunAFLForErrorCall()
				except MyTimeOutException as e: raise e
				except KeyboardInterrupt as kbe: raise kbe
				except Exception as ex :HandleException(ex)
			
			try:
				runNumber = 2
				goal += 1
				print('STARTING GOAL '+str(goal)+' ... \n');sys.stdout.flush()
				is_test_file_created = False
				isFromMap2Check = False
				testCaseFileName = TestSuite_Dir + '/testcase_'+str(goal)+'_ES.xml'
				witness_file_name = os.path.join(INSTRUMENT_Output_Dir,os.path.basename(benchmark) + '__1.graphml')
				esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)
				esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(benchmark)+ ' '
				if isInstrumentOK : esbmc_command_line += ' --error-label ' + myLabel + ' '
				esbmc_command_line += ' --timeout ' + str(int(time_out_s - 1))+'s '
				esbmc_command_line += ' --memlimit ' + str(MEM_LIMIT_ERROR_CALL_ESBMC) + 'g '
				output = run(esbmc_command_line)
				IsTimeOut(True)
				res = parse_result(output, category_property)
				if(res == Result.force_fp_mode):
					fp_mode = True
					esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)
					esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(benchmark)+ ' '
					if isInstrumentOK : esbmc_command_line += ' --error-label ' + myLabel + ' '
					esbmc_command_line += ' --timeout ' + str(int(time_out_s - 1))+'s '
					esbmc_command_line += ' --memlimit ' + str(MEM_LIMIT_ERROR_CALL_ESBMC) + 'g '
					output = run(esbmc_command_line)
					IsTimeOut(True)
					
				if os.path.isfile(witness_file_name):
					createTestFile(witness_file_name,toWorkSourceFile, testCaseFileName , False)
					is_test_file_created=True
			except MyTimeOutException as e: raise e
			except KeyboardInterrupt as kbe: raise kbe
			except Exception as ex : HandleException(ex)

			
			#res = parse_result(output, category_property)
			
		except MyTimeOutException as e:
			#print('Timeout !!!')
			pass
		except KeyboardInterrupt:
			#print('CTRL + C')
			pass

		if not is_test_file_created: createTestFile(witness_file_name,toWorkSourceFile, testCaseFileName, isFromMap2Check)
		
		if MUST_GENERATE_RANDOM_TESTCASE:
			singleValueFromFuSeBMCFuzzer, maxLengthOfTestcaseFromFuSeBMCFuzzer = getSingleValueFromFuSeBMCFuzzer(prop)
			singleValueFromFuSeBMCFuzzer *= 4
			
			randomLsts = []
			lst1 = None
			randomMaxRange = 5
			if maxLengthOfTestcaseFromFuSeBMCFuzzer > 0:
				randomMaxRange = maxLengthOfTestcaseFromFuSeBMCFuzzer + 1
				if randomMaxRange == 3:
					randomMaxRange -= 1
					lst1=[NonDeterministicCall('0')]+[NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]
				elif randomMaxRange == 2:
					lst1 = [NonDeterministicCall(str(singleValueFromFuSeBMCFuzzer))]
				else:
					randomMaxRange -= 2
					lst1=[NonDeterministicCall('0')]+ \
						 [NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]+ \
						[NonDeterministicCall('0')]
			if lst1 is not None : randomLsts.append(lst1)
			
			randomMaxRange = 36
			lst2 = [NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]+ \
						[NonDeterministicCall('0')]+[NonDeterministicCall('0')]
			randomLsts.append(lst2)
			
			randomMaxRange = lastInputInTestcaseCount
			lst3 = [NonDeterministicCall('0')]+ \
					[NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]
			randomLsts.append(lst3)

			if singleValueFromFuSeBMCFuzzer == 0: singleValueFromFuSeBMCFuzzer = 128 # No Sigle Value; default 128
			elif singleValueFromFuSeBMCFuzzer < 0: singleValueFromFuSeBMCFuzzer *= -1
			if IS_DEBUG: 
				print(TColors.OKGREEN,'singleValueFromFuSeBMCFuzzer=',singleValueFromFuSeBMCFuzzer,TColors.ENDC)
				print(TColors.OKGREEN,'lastInputInTestcaseCount=',lastInputInTestcaseCount,TColors.ENDC)
				print(TColors.OKGREEN,'maxLengthOfTestcaseFromFuSeBMCFuzzer=',maxLengthOfTestcaseFromFuSeBMCFuzzer,TColors.ENDC)
			# Do We Need +1 ??
			lst4 = [NonDeterministicCall(str(randrange(-singleValueFromFuSeBMCFuzzer,singleValueFromFuSeBMCFuzzer))) \
							for i in range(1,lastInputInTestcaseCount)] + \
						[NonDeterministicCall('0'), NonDeterministicCall('0')]
			randomLsts.append(lst4)
			
			tmpCounter = 0
			for lst_rnd in randomLsts:
				tmpCounter += 1
				tmpTestCaseFile = TestSuite_Dir+ '/testcase_'+str(tmpCounter)+'_Fuzzer.xml'
				generate_testcase_from_assumption_ErrorCall(tmpTestCaseFile,lst_rnd)
				#

		if not is_ctrl_c and FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED:
			RunAFLForErrorCall_Run2()
		if RUN_TESTCOV: RunTestCov(benchmark,property_file,arch,WRAPPER_Output_Dir)
		
		#if IS_DEBUG:
			#print(os.times())
		if is_ctrl_c:
			print('CTRL + C ....')
			return 'Done'
			#return parse_result("something else will get unknown",prop)
		#Important with False
		#if IsTimeOut(False):
		#	return parse_result("Timed out",prop)
		#return res
		#return parse_result("VERIFICATION SUCCESSFUL",prop)
		if IsTimeOut(False):
			print('The Time is out...')
		return 'DONE'
		
	if prop in [Property.memsafety, Property.overflow, Property.unreach_call, Property.termination, Property.memcleanup]:
		toWorkSourceFile=benchmark # toWorkSourceFile=INSTRUMENT_Output_File
		isFromMap2Check = False		
		try:
			if MAP2CHECK_MEM_OVERFLOW_REACH_TERM_ENABLED:
				print('STARTING GOAL 1 ... \n')
				try:
					isFromMap2Check = True
					is_test_file_created = False
					map2CheckNonDetGenerator = 'fuzzer'
					witness_file_name = map2checkWitnessFile
					testCaseFileName = TestSuite_Dir + '/testcase_map_fuzzer.xml'
					runWithTimeoutEnabled(' '.join(['timeout',str(MAP2CHECK_MEM_OVERFLOW_REACH_TERM_FUZZER_TIMEOUT)+'s', MAP2CHECK_EXE,'--timeout',str(MAP2CHECK_MEM_OVERFLOW_REACH_TERM_FUZZER_TIMEOUT),'--fuzzer-mb', str(MEM_LIMIT_MEM_OVERFLOW_REACH_TERM_MAP2CHECK), '--nondet-generator', map2CheckNonDetGenerator, '--target-function', '--target-function-name','reach_error','--generate-witness',os.path.abspath(toWorkSourceFile)]), WRAPPER_Output_Dir)
					if os.path.isfile(map2checkWitnessFile):
						createTestFile(map2checkWitnessFile,toWorkSourceFile, testCaseFileName ,True)
						is_test_file_created = True
				except MyTimeOutException as e: raise e
				except KeyboardInterrupt as kbe: raise kbe
				except Exception as ex :HandleException(ex)
					
			if MEM_OVERFLOW_REACH_TERM_RUNTWICE_ENABLED:
				try:
					print('STARTING GOAL 2 ... \n')
					runNumber = 1
					isFromMap2Check = False
					#is_test_file_created = False
					witness_file_name = os.path.join(INSTRUMENT_Output_Dir, os.path.basename(benchmark) + '_1.graphml')
					testCaseFileName = TestSuite_Dir + "/testcase_1.xml"
					esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)
					esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(benchmark)+ ' '
					esbmc_command_line += ' --timeout ' + str(int(time_out_s - 1))+'s '
					esbmc_command_line += ' --memlimit ' + str(MEM_LIMIT_ESBMC) + 'g '
					output = run(esbmc_command_line)
					IsTimeOut(True)
					res = parse_result(output, category_property)
					if(res == Result.force_fp_mode):
						fp_mode = True
						esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)
						esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(benchmark)+ ' '
						#if isInstrumentOK : esbmc_command_line += ' --error-label ' + myLabel + ' '
						esbmc_command_line += ' --timeout ' + str(int(time_out_s - 1))+'s '
						esbmc_command_line += ' --memlimit ' + str(MEM_LIMIT_ERROR_CALL_ESBMC) + 'g '
						output = run(esbmc_command_line)
						IsTimeOut(True)	
					if os.path.isfile(witness_file_name):
						createTestFile(witness_file_name, benchmark, testCaseFileName , False)
						is_test_file_created=True
				except MyTimeOutException as e: raise e
				except KeyboardInterrupt as kbe: raise kbe
				except Exception as ex : HandleException(ex)


			try:
				print('STARTING GOAL 3 ... \n')
				runNumber = 2
				isFromMap2Check = False
				is_test_file_created = False
				witness_file_name = os.path.join(INSTRUMENT_Output_Dir, os.path.basename(benchmark) + '_2.graphml')
				testCaseFileName = TestSuite_Dir + "/testcase_2.xml"
				esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)
				esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(benchmark)+ ' '
				esbmc_command_line += ' --timeout ' + str(int(time_out_s - 1))+'s '
				esbmc_command_line += ' --memlimit ' + str(MEM_LIMIT_ESBMC) + 'g '
				output = run(esbmc_command_line)
				IsTimeOut(True)
				res = parse_result(output, category_property)
				if(res == Result.force_fp_mode):
					fp_mode = True
					esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)
					esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(benchmark)+ ' '
					#if isInstrumentOK : esbmc_command_line += ' --error-label ' + myLabel + ' '
					esbmc_command_line += ' --timeout ' + str(int(time_out_s - 1))+'s '
					esbmc_command_line += ' --memlimit ' + str(MEM_LIMIT_ERROR_CALL_ESBMC) + 'g '
					output = run(esbmc_command_line)
					IsTimeOut(True)					
				if os.path.isfile(witness_file_name):
					createTestFile(witness_file_name,toWorkSourceFile, testCaseFileName , False)
					is_test_file_created = True
			except MyTimeOutException as e: raise e
			except KeyboardInterrupt as kbe: raise kbe
			except Exception as ex :HandleException(ex)

			return res
		except MyTimeOutException as e:
			#print('Timeout !!!')
			pass
		except KeyboardInterrupt:
			#print('CTRL + C')
			pass
		except Exception: pass
		if not is_test_file_created: createTestFile(witness_file_name, benchmark, testCaseFileName, isFromMap2Check)
		if is_ctrl_c:
			return parse_result(output,prop)
		if IsTimeOut(False):
			print('The Time is out...')
		res = parse_result(output, category_property)
		return res

# End of verify mthode

args = getArgs()
arch = args.arch
version = args.version
property_file = args.propertyfile
benchmark = args.benchmark
strategy = args.strategy
concurrency = args.concurrency

if version:
	#print (os.popen(ESBMC_EXE + "--version").read()[6:]),
	print (FUSEBMC_VERSION)
	exit(0)
if property_file is None:
	print ("Please, specify a property file")
	exit(1)
if benchmark is None:
	print ("Please, specify a benchmark to verify")
	exit(1)
elif not os.path.isfile(benchmark):
	print(benchmark,'is not valid file')
	exit(1)
else: benchmark = os.path.abspath(benchmark)

if args.timeout is not None :
	time_out_s = args.timeout
time_out_s -= time_for_zipping_s
if(SHOW_ME_OUTPUT) : print('time_out_s',time_out_s)


category_property, property_file_content = GetPropertyFromFile(property_file)
if(category_property is None): exit(1)

if args.output is not None:
	WRAPPER_Output_Dir = os.path.abspath(args.output)
	fuSeBMC_run_id = str(GenerateRondomFileName())
	if not os.path.isdir(WRAPPER_Output_Dir):
		os.makedirs(WRAPPER_Output_Dir,exist_ok=True)
else:
	while True:
		fuSeBMC_run_id = str(GenerateRondomFileName())
		tmpOutputFolder = WRAPPER_Output_Dir + os.path.basename(benchmark)+'_'+ fuSeBMC_run_id
		if not os.path.isdir(tmpOutputFolder):
			WRAPPER_Output_Dir = os.path.abspath(tmpOutputFolder)
			os.makedirs(WRAPPER_Output_Dir,exist_ok=True)
			break

if IS_DEBUG : print('fuSeBMC_run_id=',fuSeBMC_run_id)
TestSuite_Dir = WRAPPER_Output_Dir + "/test-suite/"
INSTRUMENT_Output_Dir = WRAPPER_Output_Dir + '/fusebmc_instrument_output/'


if category_property == Property.cover_branches or category_property == Property.cover_error_call:
	important_outs_by_ESBMC = []
	#signal.signal(signal.SIGALRM, timeOutSigHandler)
	#signal.signal(signal.SIGTERM, timeOutSigHandler)
	#signal.signal(signal.SIGINT, timeOutSigHandler)
	# ESBMC default commands: this is only for Cover-error and cover-branches
	esbmc_dargs = "--no-div-by-zero-check --force-malloc-success --state-hashing "
	#16.05.2020 remove --unlimited-k-steps
	#03.06.2020 kaled reduce the number of "--k-step 120"
	esbmc_dargs += "--no-align-check --k-step 5 --floatbv "
	#02.06.2020 adding options for Coverage-error-call
	# kaled : 03.06.2020 you must put it in method 'get_command_line line 844'; here is general
	#esbmc_dargs += "--no-align-check --k-step 120 --floatbv --unlimited-k-steps "
	esbmc_dargs += "--context-bound 2 "
	#--unwind 1000 --max-k-step 1000 
	esbmc_dargs += "--show-cex "
	#esbmc_dargs += " --overflow-check " 
	
	INSTRUMENT_Output_File = WRAPPER_Output_Dir+'/fusebmc_instrument_output/instrumented.c'
	INSTRUMENT_Output_Goals_File = INSTRUMENT_Output_Dir+'/goals.txt'
	#INSTRUMENT_OUTPUT_GOALS_DIR = WRAPPER_Output_Dir+'/fusebmc_instrument_output/goals_output/'

	
	MakeFolderEmptyORCreate(INSTRUMENT_Output_Dir)
	RemoveFileIfExists(INSTRUMENT_Output_File)
	if category_property == Property.cover_branches:
		RemoveFileIfExists(INSTRUMENT_Output_Goals_File)
		if MAP2CHECK_COVERBRANCHES_ENABLED:
			map2checkWitnessFile= WRAPPER_Output_Dir + '/witness.graphml'
		if FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED:
			FuSeBMCFuzzerLib_CoverBranches_Input_Covered_Goals_File = os.path.abspath(WRAPPER_Output_Dir+'/FuSeBMC_Fuzzer_input_goals.txt')
			FuSeBMCFuzzerLib_CoverBranches_Output_Covered_Goals_File = os.path.abspath(WRAPPER_Output_Dir+'/FuSeBMC_Fuzzer_output_goals.txt')

		#MakeFolderEmptyORCreate(INSTRUMENT_OUTPUT_GOALS_DIR)
	MakeFolderEmptyORCreate(TestSuite_Dir)
	
	if category_property == Property.cover_error_call:
		if MAP2CHECK_ERRORCALL_FUZZER_ENABLED or MAP2CHECK_ERRORCALL_SYMEX_ENABLED:
			map2checkWitnessFile= WRAPPER_Output_Dir + '/witness.graphml'
			#RemoveFileIfExists(map2checkWitnessFile)
	WriteMetaDataFromWrapper()
	
	if not os.path.isfile(FUSEBMC_INSTRUMENT_EXE_PATH) and category_property == Property.cover_branches:
		print("FuSeBMC_inustrument cannot be found..")
		#exit(1)
	result = verify(strategy, category_property, False)
	#print(get_result_string(result))
	print(result)
	exit(0)
	

elif category_property in [Property.memsafety ,Property.overflow, Property.unreach_call,Property.termination, Property.memcleanup]:
	
	# ESBMC default commands: this is the same for : memory, overflow , reach, termination
	esbmc_dargs = "--no-div-by-zero-check --force-malloc-success --state-hashing "
	esbmc_dargs += "--no-align-check --k-step 2 --floatbv --unlimited-k-steps "
	esbmc_dargs += "--no-por --context-bound-step 5 --max-context-bound 15 "
	if concurrency:
		esbmc_dargs += "--incremental-cb --context-bound-step 5 "
		esbmc_dargs += "--unwind 8 "
		esbmc_dargs += "--no-slice " # TODO: Witness validation is only working without slicing
		# NOTE: max-context-bound and no-por are already in the default params
	
	MakeFolderEmptyORCreate(INSTRUMENT_Output_Dir)
	MakeFolderEmptyORCreate(TestSuite_Dir)
	WriteMetaDataFromWrapper()
	#
	result = verify(strategy, category_property, False)
	print (get_result_string(result))
	exit(0)
else:
	print(category_property , ' is Unkown...!!')
	exit(0)

