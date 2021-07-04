#!/usr/bin/env python3
import os.path
import xml.etree.ElementTree as ET  # To parse XML
import os
import argparse
import shlex
import subprocess
import signal
import time
import sys
import resource
import re
import zipfile

import hashlib

from threading import Thread
from queue import  Empty

try:
	import queue
except ImportError:
	import Queue as queue
from random import randrange
import random
import string
from datetime import datetime



# Start time for this script
start_time = time.time()
property_file_content = ""
category_property = 0
benchmark=''
property_file=''
witness_file_name=''
toWorkSourceFile=''
arch=''

__graphml_base__ = '{http://graphml.graphdrawing.org/xmlns}'
__graph_tag__ = __graphml_base__ + 'graph'
__edge_tag__ = __graphml_base__ + 'edge'
__data_tag__ = __graphml_base__ + 'data'
WRAPPER_OUTPUT_DIR ='./fusebmc_output/'

__testSuiteDir__ = "test-suite/"
META_DATA_FILE = __testSuiteDir__ + "/metadata.xml"
TESTCASE_FILE_FOR_COVER_ERROR=__testSuiteDir__ + "/testcase_1_ES.xml"
TESTCASE_FILE_FOR_COVER_ERROR_RANDOM = __testSuiteDir__ + "/testcase_1_Fuzzer.xml"
TESTCASE_FILE_FOR_COVER_ERROR_RANDOM2 = __testSuiteDir__ + "/testcase_2_Fuzzer.xml"
TESTCASE_FILE_FOR_COVER_ERROR_RANDOM3 = __testSuiteDir__ + "/testcase_3_Fuzzer.xml"

INSTRUMENT_OUTPUT_DIR = './fusebmc_instrument_output/'
INSTRUMENT_OUTPUT_FILE = './fusebmc_instrument_output/instrumented.c'
INSTRUMENT_OUTPUT_FILE_OBJ = './fusebmc_instrument_output/instrumented.o'
INSTRUMENT_OUTPUT_GOALS_FILE = './fusebmc_instrument_output/goals.txt'
INSTRUMENT_OUTPUT_GOALS_DIR = './fusebmc_instrument_output/goals_output/'

TEST_SUITE_DIR_ZIP = ''
MAX_NUM_OF_LINES_OUT=50
MAX_NUM_OF_LINES_ERRS=50
SHOW_ME_OUTPUT = False
IS_DEBUG = False
MUST_COMPILE_INSTRUMENTED = False
MUST_GENERATE_RANDOM_TESTCASE = True
MUST_ADD_EXTRA_TESTCASE = True
MUST_APPLY_TIME_PER_GOAL = True
MUST_APPLY_LIGHT_INSTRUMENT_FOR_BIG_FILES = True

MEM_LIMIT_BRANCHES_ESBMC = 10 # giga ; Zero or negative means unlimited. 
MEM_LIMIT_BRANCHES_MAP2CHECK = 1000 # miga

MEM_LIMIT_ERROR_CALL_ESBMC = 10
MEM_LIMIT_ERROR_CALL_MAP2CHECK = 1000 # miga

BIG_FILE_LINES_COUNT = 8000

EXTRA_TESTCASE_COUNT = 6

esbmc_path = "./esbmc "

map2check_path = os.path.abspath('./map2check-fuzzer/map2check ')
map2checkTime = 150  #seconds
map2checkTimeErrorCall_Symex = 40  #seconds
map2checkTimeErrorCall_Fuzzer = 150  #seconds
MUST_RUN_MAP_2_CHECK_FOR_ERROR_CALL_SYMEX = False # we can change it.
MUST_RUN_MAP_2_CHECK_FOR_ERROR_CALL_FUZZER = True # we can change it.
MUST_RUN_MAP_2_CHECK_FOR_BRANCHES = True # we can change it.
map2checkTimeForBranches = 70  #seconds

map2checkWitnessFile='' # will be set later in the wrapper output


COV_TEST_EXE = './val_testcov/testcov/bin/testcov'
FUSEBMC_INSTRUMENT_EXE_PATH = './FuSeBMC_inustrment/FuSeBMC_inustrment'

esbmc_dargs = "--no-div-by-zero-check --force-malloc-success --state-hashing "
esbmc_dargs += "--no-align-check --k-step 5 --floatbv  "
esbmc_dargs += "--context-bound 2 "
esbmc_dargs += "--show-cex "

C_COMPILER = 'gcc'
COV_TEST_PARAMS= ['--no-isolation','--memlimit', '6GB','--timelimit-per-run', '3', '--cpu-cores', '0','--verbose','--no-plots','--reduction', 'BY_ORDER', '--reduction-output','test-suite']
RUN_COV_TEST = True
time_out_s = 850 # 850 seconds 
time_for_zipping_s = 10  # the required time for zipping folder;
is_ctrl_c = False
remaining_time_s=0

goals_count = 0
class TColors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


hasInputInTestcase = False
map2CheckInputCount = 0
lastInputInTestcaseCount = 0

mustRunTwice = True # You can change it.
runNumber=1

important_outs_by_ESBMC=["Chosen solver doesn\'t support floating-point numbers"]
#See http://eyalarubas.com/python-subproc-nonblock.html
class NonBlockingStreamReader:

	def __init__(self, stream):
		'''
		stream: the stream to read from.
				Usually a process' stdout or stderr.
		'''

		self._s = stream
		self._q = queue.Queue()
		self.exception = None
		self.isEndOfStream=True
		#self.mutex = Lock()
		self._t = Thread(target=self._populateQueue, args = ())
		self._t.daemon = True
		self._t.start() #start collecting lines from the stream

	def _populateQueue(self):
		''' Collect lines from 'stream' and put them in 'quque'. '''
		self.isEndOfStream=False
		while True:
			line = self._s.readline()
			if line:
				#self.mutex.acquire()
				line_de=line.decode('utf-8').rstrip()
				#print('line_de',line_de)
				self._q.put(line_de)
				#self.mutex.release()
			else:
				#raise UnexpectedEndOfStream
				self.isEndOfStream=True
				break


	def readline(self, timeout = None):
		data=None
		try:
			#self.mutex.acquire()
			#https://docs.python.org/3/library/queue.html
			data= self._q.get(block = timeout is not None,timeout = timeout)
			if data : self._q.task_done()
			#data= self._q.get()
			
		except Empty as empt:
			#self._q.mutex.release()
			self.exception = empt
			data=None
		finally:
			#self.mutex.release()
			pass
		return data
	def hasMore(self):
		if self.isEndOfStream == True and self._q.empty() == True:
			return False
		return True

class UnexpectedEndOfStream(Exception): pass

class MyTimeOutException(Exception):
	pass
	
def IsTimeOut(must_throw_ex = False):
	global is_ctrl_c
	global time_out_s
	global start_time
	global remaining_time_s
	global fdebug
	#global lasttime
	if is_ctrl_c is True:
		raise KeyboardInterrupt()
		

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
	ruAfter = resource.getrusage(resource.RUSAGE_SELF)
	rChild = resource.getrusage(resource.RUSAGE_CHILDREN)
	cpu_exec_time_s = (ruAfter.ru_utime + ruAfter.ru_stime + rChild.ru_utime + rChild.ru_stime)
	
	cpu_remaining_time_s = time_out_s - cpu_exec_time_s
	if cpu_remaining_time_s > remaining_time_s :
		remaining_time_s = cpu_remaining_time_s
	
	isCpuTimeout = False
	if(cpu_exec_time_s >= time_out_s):
		isCpuTimeout = True
		if must_throw_ex:
			raise MyTimeOutException()

	return isWallTimeout or isCpuTimeout
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
	return ''.join(random.choice(string.ascii_letters) for _ in range(25))
def AddFileToArchive(full_file_name, zip_file_name):
	if not os.path.isfile(full_file_name): return
	os.makedirs(os.path.dirname(os.path.abspath(zip_file_name)), exist_ok=True)
	appendOrCreate='w'
	if os.path.isfile(zip_file_name): appendOrCreate='a'
	zipf = zipfile.ZipFile(zip_file_name, appendOrCreate , zipfile.ZIP_DEFLATED)
	zipf.write(os.path.abspath(full_file_name),os.path.basename(os.path.abspath(full_file_name)))
	zipf.close()
	
def ZipDir(path, zip_file_name):
	os.makedirs(os.path.dirname(os.path.abspath(zip_file_name)), exist_ok=True)
	#RemoveFileIfExists(zip_file_name)
	zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
	for root, dirs, files in os.walk(os.path.abspath(path)):
		for file in files:
			zipf.write(os.path.join(root,file),file)
	zipf.close()

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

class AssumptionHolder(object):
	"""Class to hold line number and assumption from ESBMC Witness."""

	def __init__(self, line, assumption):
		"""
		Default constructor.

		Parameters
		----------
		line : unsigned
			Line Number from the source file
		assumption : str
			Assumption string from ESBMC.
		"""
		assert(line >= 0)
		assert(len(assumption) > 0)
		self.line = line
		self.assumption = assumption
		#self.varName = varName
		#self.varVal = varVal

	def __str__(self):
		return "AssumptionInfo: LINE: {0}, ASSUMPTION: {1}".format(self.line, self.assumption)
	
	def debugInfo(self):
		"""Print info about the object"""
		print("AssumptionInfo: LINE: {0}, ASSUMPTION: {1}".format(
			self.line, self.assumption))


class AssumptionParser(object):
	"""Class to parse a witness file generated from ESBMC and create a Set of AssumptionHolder."""

	def __init__(self, witness,pIsFromMap2Check = False):
		"""
		Default constructor.

		Parameters
		----------

		witness : str
			Path to witness file (absolute/relative)
		"""
		assert(os.path.isfile(witness))
		self.__xml__ = None
		self.assumptions = list()
		self.__witness__ = witness
		self.isFromMap2Check = pIsFromMap2Check

	def __openwitness__(self):
		"""Parse XML file using ET"""
		self.__xml__ = ET.parse(self.__witness__).getroot()

	def parse(self):
		""" Iterates over all elements of GraphML and extracts all Assumptions """
		if self.__xml__ is None:
			try:
				self.__openwitness__()
			except:
				if IS_DEBUG :
					print(TColors.FAIL,'Cannot parse file:', self.__witness__,TColors.ENDC)
		if self.__xml__ is None:
			return
		
		graph = self.__xml__.find(__graph_tag__)
		for node in graph:
			try:
				if(node.tag == __edge_tag__):
					startLine = 0
					assumption = ""
					for data in node:
						if data.attrib['key'] == 'startline':
							startLine = int(data.text)
						elif data.attrib['key'] == 'assumption':
							assumption = data.text
					if assumption != "":
						self.assumptions.append(AssumptionHolder(startLine, assumption))

			except:
				if IS_DEBUG :
					print(TColors.FAIL,'Cannot parse node:',TColors.ENDC)

	def debugInfo(self):
		"""Print current info about the object"""
		print("XML: {0}".format(self.__witness__))
		print("ET: {0}".format(self.__xml__))
		for assumption in self.assumptions:
			assumption.debugInfo()

def WriteMetaDataFromWrapper():
	now = datetime.now()
	with open(META_DATA_FILE, 'w') as meta_f:
		meta_f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE test-metadata PUBLIC "+//IDN sosy-lab.org//DTD test-format test-metadata 1.0//EN" "https://sosy-lab.org/test-format/test-metadata-1.0.dtd">')
		meta_f.write('<test-metadata>')
		meta_f.write('<entryfunction>main</entryfunction>')
		meta_f.write('<specification>'+property_file_content.strip()+'</specification>')
		meta_f.write('<sourcecodelang>'+'C'+'</sourcecodelang>')
		_arch ='32bit'
		if arch == 64:
			_arch='64bit'
		meta_f.write('<architecture>'+_arch+'</architecture>')
		#meta_f.write('<creationtime>2020-07-27T21:33:51.462605</creationtime>')
		meta_f.write('<creationtime>'+now.strftime("%Y-%m-%dT%H:%M:%S.%f")+'</creationtime>')
		meta_f.write('<programhash>'+GetSH1ForFile(benchmark)+'</programhash>')
		meta_f.write('<producer>FuSeBMC</producer>')
		meta_f.write('<programfile>'+benchmark+'</programfile>')
		meta_f.write('</test-metadata>')

class MetadataParser(object):
	"""Class to parse a witness file generated from ESBMC and extract all metadata from it."""

	def __init__(self, witness):
		"""
		Default constructor.

		Parameters
		----------

		witness : str
			Path to witness file (absolute/relative)
		"""
		assert(os.path.isfile(witness))
		self.__xml__ = None
		self.metadata = {}
		self.__witness__ = witness

	def __openwitness__(self):
		"""Parse XML file using ET"""
		self.__xml__ = ET.parse(self.__witness__).getroot()

	def parse(self):
		""" Iterates over all elements of GraphML and extracts all Metadata """
		if self.__xml__ is None:
			self.__openwitness__()
		graph = self.__xml__.find(__graph_tag__)
		for node in graph:			
			if(node.tag == __data_tag__):
				self.metadata[node.attrib['key']] = node.text


class NonDeterministicCall(object):
	def __init__(self, value):
		"""
		Default constructor.

		Parameters
		----------
		value : str
			String containing value from input		
		"""
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
		
		if isFromMap2Check:
			try:
				_,val = pAssumptionHolder.assumption.split(' == ')
			except Exception as ex:
				if IS_DEBUG:
					print(TColors.FAIL+ ' Error in File (fromAssumptionHolder,isFromMap2Check):'+ TColors.ENDC, benchmark)
				val = '0'
		else:
			try:
				_,val = pAssumptionHolder.assumption.split("=")
				val,_ = val.split(';')
				if val[-1] == "f" or val[-1] == "l":
					val = val[:-1]
			except Exception as ex:
				if IS_DEBUG:
					print(TColors.FAIL+ ' Error in File (fromAssumptionHolder):'+ TColors.ENDC, benchmark)
				val = '0'
				pass
			
		value = NonDeterministicCall.extract_byte_little_endian(val.strip())
		return NonDeterministicCall(value)

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
		"""
			Checks if p_AssumptionHolder is nondet by checking if line contains __VERIFIER_nondet
			
		"""

		if self.isFromMap2Check : return True
		if p_AssumptionHolder is None: return False
		
		if "=" in p_AssumptionHolder.assumption:
			check_cast = p_AssumptionHolder.assumption.split("=")
			if len(check_cast) > 1:
				if check_cast[1].startswith(" ( struct "):
					return False
		
		if SourceCodeChecker.__lines__ is None:
			self.__openfile__()
		lineContent = ''
		try:
			lineContent = SourceCodeChecker.__lines__[p_AssumptionHolder.line - 1]
		except:
			pass					
			
		result = lineContent.split("__VERIFIER_nondet_")
		return len(result) > 1
		
	"""
	return list of NonDeterministicCall objects.
	"""
	def getNonDetAssumptions(self):
		
		filtered_assumptions = list()

		for i in range(len(self.lstAssumptionHolder)-1):
			if self.__is_not_repeated__(i):
				filtered_assumptions.append(self.lstAssumptionHolder[i])
		if len(self.lstAssumptionHolder)>0:
			filtered_assumptions.append(self.lstAssumptionHolder[-1])
		return [NonDeterministicCall.fromAssumptionHolder(x,self.isFromMap2Check) for x in filtered_assumptions if not x is None and self.__isNonDet__(x)]

	def debugInfo(self):
		for x in self.getNonDetAssumptions():
			x.debugInfo()


class TestCompMetadataGenerator(object):
	def __init__(self, metadata):
		"""
		Default constructor.

		Parameters
		----------
		metadata : { key: value}
			A dictionary containing metada info
		"""
		self.metadata = metadata

	def writeMetadataFile(self):
		""" Write metadata.xml file """
		root = ET.Element("test-metadata")
		ET.SubElement(root, 'entryfunction').text = 'main'
		ET.SubElement(root, 'specification').text = property_file_content.strip()
		properties = {'sourcecodelang', 'sourcecodelang', 'producer',
					  'programfile', 'programhash', 'architecture', 'creationtime'}
		for property in properties:
			if (category_property == Property.cover_branches or category_property == Property.cover_error_call):
				if property == 'programfile':
					ET.SubElement(root, property).text= benchmark
				elif property == 'programhash':
					ET.SubElement(root, property).text= GetSH1ForFile(benchmark)
				else:
					ET.SubElement(root, property).text = self.metadata[property]
					
			else:
				ET.SubElement(root, property).text = self.metadata[property]
		
		ET.ElementTree(root).write(META_DATA_FILE)
		with open(META_DATA_FILE, 'r') as original: data = original.read()
		with open(META_DATA_FILE, 'w') as modified: modified.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE test-metadata PUBLIC "+//IDN sosy-lab.org//DTD test-format test-metadata 1.0//EN" "https://sosy-lab.org/test-format/test-metadata-1.0.dtd">' + data)

class TestCompGenerator(object):
	def __init__(self, nondetList):
		"""
		Default constructor.

		Parameters
		----------
		value : [NonDeterministicCall]
			All NonDeterministicCalls from the program
		"""
		self.__root__ = ET.Element("testcase")
		for inputData in nondetList:
			if not inputData is None:
				ET.SubElement(self.__root__, "input").text = inputData.value

	def writeTestCase(self, output):
		"""
		Write testcase into XML file.

		Parameters
		----------
		output : str
			filename (with extension)
		"""
		ET.ElementTree(self.__root__).write(output)
		with open(output, 'r') as original: data = original.read()
		with open(output, 'w') as modified: modified.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE testcase PUBLIC "+//IDN sosy-lab.org//DTD test-format testcase 1.0//EN" "https://sosy-lab.org/test-format/testcase-1.0.dtd">' + data)

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
	global map2CheckInputCount
	global singleValueFromMap2Check
	global lastInputInTestcaseCount
	#global mustRunTwice
	#global runNumber
	
	if not os.path.isfile(witness) : return
	assumptions = __getNonDetAssumptions__(witness, source,isFromMap2Check)
	assumptionsLen = len(assumptions)
	if(assumptionsLen > 0):
		TestCompGenerator(assumptions).writeTestCase(testCaseFileName)
		AddFileToArchive(testCaseFileName,TEST_SUITE_DIR_ZIP)
		hasInputInTestcase=True
		if isFromMap2Check :
			if assumptionsLen > map2CheckInputCount:  
				map2CheckInputCount = assumptionsLen
			if assumptionsLen == 1:
				try:
					singleValueFromMap2CheckTmp = int(assumptions[0].value) * 4
					if singleValueFromMap2CheckTmp != 0: singleValueFromMap2Check = singleValueFromMap2CheckTmp
				except:
					pass
		
		if assumptionsLen > lastInputInTestcaseCount:
			lastInputInTestcaseCount = assumptionsLen
		

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
	#20.05.2020
	fail_cover_error_call = 13
	fail_cover_branches = 14
	

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


class Property:
	reach = 1
	memory = 2
	overflow = 3
	termination = 4
	memcleanup = 5
	cover_branches = 6
	cover_error_call = 7 # 20.05.2020
#29.05.2020
def CompileFile(fil, include_dir = '.'):
	fil=os.path.abspath(fil)
	if not os.path.isfile(fil):
		print('FILE:',fil, 'not exists')
		exit(0)
	cmd=[C_COMPILER,'-c',fil , '-o', INSTRUMENT_OUTPUT_FILE_OBJ,'-I'+include_dir]
	p=subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	while True:
		line = p.stdout.readline()
		if not line: break
		line_de=line.decode('utf-8')
		print(line_de)
	while True:
		line = p.stderr.readline()
		if not line: break
		line_de=line.decode('utf-8')
		print(line_de)
	if not os.path.isfile(INSTRUMENT_OUTPUT_FILE_OBJ):
		print('Cannot compile: ',fil)
		exit(0)
	
def RunCovTest():
	print("\nValidating Test-Cases ...\n")
	global toWorkSourceFile
	cov_test_exe_abs=os.path.abspath(COV_TEST_EXE)
	cov_test_cmd =[cov_test_exe_abs]
	cov_test_cmd.extend(COV_TEST_PARAMS)
	test_suite_dir_zip_abs=os.path.abspath(TEST_SUITE_DIR_ZIP)
	property_file_abs = os.path.abspath(property_file)
	benchmark_abs = os.path.abspath(benchmark)
	sourceForTestCov = WRAPPER_OUTPUT_DIR + '/' + os.path.basename(benchmark_abs)
	sourceForTestCov = os.path.abspath(sourceForTestCov)
	testCovOutputDir = os.path.abspath(INSTRUMENT_OUTPUT_DIR + '/output_cov')
	cov_test_cmd.extend(['--output', testCovOutputDir])
	print('sourceForTestCov',sourceForTestCov)
	run_without_output(' '.join(['cp',benchmark_abs ,sourceForTestCov]))
	cov_test_cmd.extend(['-'+str(arch),'--test-suite' ,test_suite_dir_zip_abs , '--goal' ,property_file_abs , sourceForTestCov])
	print(' '.join(cov_test_cmd))
	p=subprocess.Popen(cov_test_cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE , cwd = INSTRUMENT_OUTPUT_DIR)
	while True:
		line = p.stderr.readline()
		if not line: break
		line_de=line.rstrip().decode('utf-8')
		print(line_de)	
		
	while True:
		line = p.stdout.readline()
		if not line: break
		line_de=line.rstrip().decode('utf-8')
		print(line_de)


def run_without_output(cmd_line, pCwd = None):
	if(SHOW_ME_OUTPUT): print(cmd_line)
	the_args = shlex.split(cmd_line)
	try:
		if not pCwd is None:
			p = subprocess.run(the_args, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,cwd=pCwd)
		else:
			p = subprocess.run(the_args, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
	except Exception as ex:
		print(ex)

# Function to run esbmc
def run(cmd_line):
	global important_outs_by_ESBMC
	
	if(SHOW_ME_OUTPUT): print (TColors.BOLD,'Command: ', cmd_line, TColors.ENDC)
	outs=['' for i in range(MAX_NUM_OF_LINES_OUT)]
	errs=['' for i in range(MAX_NUM_OF_LINES_ERRS)]
	important_outs=[]
	important_errs=[]
	index=-1;
	index_err=-1
	the_args = shlex.split(cmd_line)
	p = None
	try:
		p = subprocess.Popen(the_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE) #bufsize=1
		#print('pid',p.pid)
		nbsr_out = NonBlockingStreamReader(p.stdout)
		nbsr_err = NonBlockingStreamReader(p.stderr)
		
		while nbsr_out.hasMore():
			IsTimeOut(True)
			try:
				output = nbsr_out.readline(0.01) # second
				# 0.1 secs to let the shell output the result
				if output:
					index =(index + 1) % MAX_NUM_OF_LINES_OUT
					if(SHOW_ME_OUTPUT): print(output)
					isAddedToImportant=False
					for out_by_ESBMC in important_outs_by_ESBMC:
						if out_by_ESBMC in output:
							important_outs.append(output)
							isAddedToImportant=True
							break
					if not isAddedToImportant : outs[index]= output
				else:
					IsTimeOut(True)
					#time.sleep(0.1)
			except UnexpectedEndOfStream as ueos:
				pass
		
		while nbsr_err.hasMore():
			IsTimeOut(True)
			try:
				err = nbsr_err.readline(0.01)
				# 0.1 secs to let the shell output the result
				if err:
					index_err =(index_err + 1) % MAX_NUM_OF_LINES_ERRS
					if(SHOW_ME_OUTPUT): print(err)
					isAddedToImportant=False
					for out_by_ESBMC in important_outs_by_ESBMC:
						if out_by_ESBMC in err:
							important_errs.append(err)
							isAddedToImportant=True
							break
					if not isAddedToImportant : errs[index_err]= err
				else:
					IsTimeOut(True)
					#time.sleep(0.1)
			except UnexpectedEndOfStream as ueos:
				pass
			
	except MyTimeOutException as e:
		if p is not None:
			try:
				p.kill()
			except Exception:
				pass
		raise e
		pass
	except KeyboardInterrupt:
		global is_ctrl_c
		is_ctrl_c = True
		pass

	if p is not None:
		try:
			p.kill()
		except Exception:
			pass
	out_str=''
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

#####
def runWithTimeoutEnabled(cmd_line,pCwd=None):
	if(SHOW_ME_OUTPUT): print (TColors.BOLD, 'Command: ', cmd_line ,TColors.ENDC)
	the_args = shlex.split(cmd_line)
	p = None
	try:
		p = subprocess.Popen(the_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=pCwd) #bufsize=1
		nbsr_out = NonBlockingStreamReader(p.stdout)
		nbsr_err = NonBlockingStreamReader(p.stderr)
		
		while nbsr_out.hasMore():
			IsTimeOut(True)
			try:
				output = nbsr_out.readline(0.01) # second
				# 0.1 secs to let the shell output the result
				if output:
					if(SHOW_ME_OUTPUT): print(output)
				else:
					IsTimeOut(True)
			except UnexpectedEndOfStream as ueos:
				pass
		
		while nbsr_err.hasMore():
			IsTimeOut(True)
			try:
				err = nbsr_err.readline(0.01)
				# 0.1 secs to let the shell output the result
				if err:
					if(SHOW_ME_OUTPUT): print(err)
				else:
					IsTimeOut(True)
			except UnexpectedEndOfStream as ueos:
				pass
	
	except KeyboardInterrupt:
		global is_ctrl_c
		is_ctrl_c = True
		pass
	if p is not None:
		try:
			p.kill()
		except Exception:
			pass

def parse_result(the_output, prop):
	
	# Parse output
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

		if prop == Property.memory:
			if memory_leak in the_output:
				return Result.fail_memtrack

			if invalid_pointer_free in the_output:
				return Result.fail_free

			if invalid_object_free in the_output:
				return Result.fail_free

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
		if prop == Property.cover_error_call:
			return Result.fail_cover_error_call
		if prop == Property.cover_branches:
			return Result.fail_cover_branches

		if prop == Property.overflow:
			return Result.fail_overflow

		
		
		if prop == Property.reach:
			return Result.fail_reach
		

	if "VERIFICATION SUCCESSFUL" in the_output:
		return Result.success
	
	return Result.unknown


def get_result_string(the_result):
	if the_result == Result.fail_memcleanup:
		return "FALSE_MEMCLEANUP"

	if the_result == Result.fail_memtrack:
		return "FALSE_MEMTRACK"

	if the_result == Result.fail_free:
		return "FALSE_FREE"

	if the_result == Result.fail_deref:
		return "FALSE_DEREF"

	if the_result == Result.fail_overflow:
		return "FALSE_OVERFLOW"

	if the_result == Result.fail_reach:
		return "DONE"

	if the_result == Result.success:
		return "DONE"

	if the_result == Result.err_timeout:
		return "Timed out"

	if the_result == Result.err_unwinding_assertion:
		return "Unknown"
	
	if the_result == Result.fail_cover_error_call:
		return "FAIL_COVER_ERROR_CALL"
	
	if the_result == Result.fail_cover_branches:
		return "FAIL_COVER_BRANCHES"

	if the_result == Result.err_memout:
		return "Unknown"

	if the_result == Result.unknown:
		return "TIMEOUT"

	exit(0)



def get_command_line(strat, prop, arch, benchmark, fp_mode):
	global goals_count
	global mustRunTwice
	global runNumber
	
	command_line = esbmc_path + esbmc_dargs
	command_line += benchmark + " --quiet "
	if arch == 32:
		command_line += "--32 "
	else:
		command_line += "--64 "
	# Add witness arg
	witness_file_name = os.path.basename(benchmark) + ".graphml "
	if prop != Property.cover_branches and prop != Property.cover_error_call:
		command_line += "--witness-output " + witness_file_name
	# Special case for termination, it runs regardless of the strategy
	if prop == Property.termination:
		command_line += "--no-pointer-check --no-bounds-check --no-assertions "
		command_line += "--termination "
		return command_line
	
	# Add strategy
	if strat == "kinduction":
		command_line += "--bidirectional "
	elif strat == "falsi":
		command_line += "--falsification "
	elif strat == "incr":
		command_line += "--incremental-bmc "
	else:
		print ("Unknown strategy")
		exit(1)
		
	if prop == Property.overflow:
		command_line += "--no-pointer-check --no-bounds-check --overflow-check --no-assertions "
	elif prop == Property.memory:
		command_line += "--memory-leak-check --no-assertions "
	elif prop == Property.memcleanup:
		command_line += "--memory-leak-check --no-assertions "
	elif prop == Property.reach:
		command_line += "--no-pointer-check --no-bounds-check --interval-analysis --no-slice "
	elif prop == Property.cover_branches:
		
		if(goals_count>100):
			if (goals_count<250):
				command_line += "--max-k-step 10 --unwind 1 --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
			else:
				command_line += "--max-k-step 10 --unwind 1 --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
		elif (goals_count<100):
			command_line += "--unlimited-k-steps --unwind 1 --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
	elif prop == Property.cover_error_call:
		if mustRunTwice and runNumber ==1:
			command_line += "--partial-loops --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
		else:
			command_line += "--unlimited-k-steps --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
	else:
		print ("Unknown property")
		exit(1)
	# if we're running in FP mode, use MathSAT
	if fp_mode:
		command_line += "--mathsat "
	
	return command_line

def generate_metadata_from_witness(p_witness_file):
	
	global META_DATA_FILE
	global TEST_SUITE_DIR_ZIP
	
	if not os.path.isfile(p_witness_file): return
	metadataParser = MetadataParser(p_witness_file)
	metadataParser.parse()
	if len(metadataParser.metadata) > 0 :
		TestCompMetadataGenerator(metadataParser.metadata).writeMetadataFile()
		AddFileToArchive(META_DATA_FILE , TEST_SUITE_DIR_ZIP)

def generate_testcase_from_assumption(p_test_case_file_full,p_inst_assumptions):
	with open(p_test_case_file_full, 'w') as testcase_file:
		testcase_file.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
		testcase_file.write('<!DOCTYPE testcase PUBLIC "+//IDN sosy-lab.org//DTD test-format testcase 1.0//EN" "https://sosy-lab.org/test-format/testcase-1.0.dtd">')
		testcase_file.write('<testcase>')
		for nonDeterministicCall in p_inst_assumptions:
			testcase_file.write('<input>'+nonDeterministicCall.value +'</input>')
		testcase_file.write('</testcase>')
	AddFileToArchive(p_test_case_file_full , TEST_SUITE_DIR_ZIP)
	
def getLinesCountInFile(pFilePath):
	line_count = 0
	file = open(pFilePath, 'r')
	for line in file:
		if line != '\n' : line_count += 1
	file.close()
	return 	line_count

def verify(strat, prop, fp_mode):
	global is_ctrl_c
	global remaining_time_s
	global hasInputInTestcase
	global lastInputInTestcaseCount 
	global goals_count
	global mustRunTwice
	global runNumber
	global  __testSuiteDir__
	global singleValueFromMap2Check
	
	#sglobal MUST_APPLY_TIME_PER_GOAL
	lastInputInTestcaseCount = 5 # default
	singleValueFromMap2Check = 0
	goal_id=0
	
	goal_witness_file_full=''
	inst_assumptions=[]
	if(prop == Property.cover_branches):
		try:
			paramAddElse = '--add-else'
			paramAddLabelAfterLoop = '--add-label-after-loop'
			paramAddGoalAtEndOfFunc='--add-goal-at-end-of-func'
			if MUST_APPLY_LIGHT_INSTRUMENT_FOR_BIG_FILES:
				linesCountInSource = getLinesCountInFile(benchmark)
				if linesCountInSource >= BIG_FILE_LINES_COUNT:
					paramAddElse = ''
					paramAddLabelAfterLoop=''
					paramAddGoalAtEndOfFunc = ''
				
			addFuSeBMCFuncParam = ''
			if MUST_RUN_MAP_2_CHECK_FOR_BRANCHES: addFuSeBMCFuncParam= '--add-FuSeBMC-func'
			runWithTimeoutEnabled(' '.join([FUSEBMC_INSTRUMENT_EXE_PATH, '--input',benchmark ,'--output', INSTRUMENT_OUTPUT_FILE , 
								  '--goal-output-file',INSTRUMENT_OUTPUT_GOALS_FILE, paramAddElse,'--add-labels', paramAddLabelAfterLoop,
								  paramAddGoalAtEndOfFunc ,addFuSeBMCFuncParam, 
								  '--compiler-args','-I'+os.path.dirname(os.path.abspath(benchmark))]))
			
			IsTimeOut(True)
			#check if FuSeBMC_inustrment worked
			if not os.path.isfile(INSTRUMENT_OUTPUT_FILE):
				print("Cannot instrument the file.")
				if IS_DEBUG:
					print(TColors.FAIL,'Cannot instrument the file.',TColors.ENDC)
					exit(0)
				#return Result.unknown
			if not os.path.isfile(INSTRUMENT_OUTPUT_GOALS_FILE):
				print("Cannot instrument the file, goalFile cannot be found.")
				if IS_DEBUG:
					print(TColors.FAIL,'Cannot instrument the file, goalFile cannot be found.',TColors.ENDC)
					exit(0)
				#return Result.unknown
			if MUST_COMPILE_INSTRUMENTED:
				CompileFile(INSTRUMENT_OUTPUT_FILE,os.path.dirname(os.path.abspath(benchmark)))
			if os.path.isfile(INSTRUMENT_OUTPUT_GOALS_FILE):
				goals_count_file = open(INSTRUMENT_OUTPUT_GOALS_FILE, "r")
				goals_count = int(goals_count_file.read())
				goals_count_file.close()
			goals_count_original=goals_count
			goals_covered=0
			goals_covered_lst=[]
			goals_to_be_covered_with_extra_lst=[]
			goals_covered_by_map2check=[]
			goals_to_be_run_map2check = []
			goalInTheMiddle = 0			
			if goals_count > 0: goalInTheMiddle = int(goals_count / 2)
			inst_all_assumptions=[]
			inst_esbmc_command_line = get_command_line(strat, prop, arch, INSTRUMENT_OUTPUT_FILE, fp_mode)
			counter=0
			singleValueFromMap2Check = 0
			isLastGoalSuccessful=False
			hasLastGoalResult = False
			isFromMap2Check=False
			SourceCodeChecker.loadSourceFromFile(INSTRUMENT_OUTPUT_FILE)
			linesInSource = len(SourceCodeChecker.__lines__)
			if IS_DEBUG:
				print(TColors.OKGREEN,'Lines In source:',linesInSource,TColors.ENDC)
			if MUST_RUN_MAP_2_CHECK_FOR_BRANCHES:
				goals_to_be_run_map2check=[1,4, goalInTheMiddle, goals_count]
			print('\nRunning FuSeBMC for Cover-Branches:\n')
			for i in range(1,goals_count+1):
				isLastGoalSuccessful = False
				hasLastGoalResult = False
				isFromMap2Check = False
				goal_id = i
				param_timeout_esbmc = ''
				param_memlimit_esbmc = ''
				IsTimeOut(True)
				if MUST_APPLY_TIME_PER_GOAL:
					factor=2 # 1/2 of the remaining time
					if i < goals_count / 2 : factor=3 # 1/3 of the remaining time
					#remaining_time_s = int(remaining_time_ms / 1000) # ms to second
					if i < goals_count and remaining_time_s > 10:
						param_timeout_esbmc = ' --timeout ' + str(int(remaining_time_s/factor)) + 's '
				if MEM_LIMIT_BRANCHES_ESBMC > 0:
					param_memlimit_esbmc = ' --memlimit ' + str(MEM_LIMIT_BRANCHES_ESBMC) + 'g '
					
				inst_assumptions=[]
				goal='GOAL_'+str(i)
				
				if(SHOW_ME_OUTPUT): print(TColors.OKGREEN+'+++++++++++++++++++++++++++++++'+TColors.ENDC)
				print('STARTING GOAL: '+goal)
				
				# You can use or True to run all
				if MUST_RUN_MAP_2_CHECK_FOR_BRANCHES and (goal_id in goals_to_be_run_map2check):
					isFromMap2Check = True
					test_case_file_full=os.path.join(__testSuiteDir__,'testcase_'+str(i)+'_map.xml')
					goal_witness_file_full = map2checkWitnessFile
					RemoveFileIfExists(map2checkWitnessFile)
					sedOutputPath = WRAPPER_OUTPUT_DIR+'/fusebmc_instrument_output/sed_' + goal + '.c'
					sed_cmd_line = ' '.join(['sed',"'s/"+goal+':'+"/FuSeBMC_custom_func()/g'", INSTRUMENT_OUTPUT_FILE])
					the_args = shlex.split(sed_cmd_line)
					try:
						sedOutFile = open(sedOutputPath, 'w')
						pSed = subprocess.run(the_args, stdout=sedOutFile,stderr=subprocess.DEVNULL)
						map2CheckNonDetGenerator = 'fuzzer'
						runWithTimeoutEnabled(' '.join(['timeout',str(map2checkTimeForBranches)+'s', map2check_path,'--timeout',str(map2checkTimeForBranches),'--fuzzer-mb', str(MEM_LIMIT_BRANCHES_MAP2CHECK),'--nondet-generator',map2CheckNonDetGenerator , '--target-function','--target-function-name', 'FuSeBMC_custom_func', '--generate-witness',os.path.abspath(sedOutputPath)]), WRAPPER_OUTPUT_DIR)
						if os.path.isfile(map2checkWitnessFile):
							inst_assumptions=__getNonDetAssumptions__(map2checkWitnessFile,INSTRUMENT_OUTPUT_FILE,True)
							inst_assumptions_len = len(inst_assumptions)
							run_without_output(' '.join(['cp',map2checkWitnessFile,WRAPPER_OUTPUT_DIR + '/map2check_'+str(goal_id)+'.graphml']))
							if inst_assumptions_len > 0 :
								if inst_assumptions_len == 1:
									try:
										singleValueFromMap2CheckTmp = int(inst_assumptions[0].value) * 4
										if singleValueFromMap2CheckTmp != 0: singleValueFromMap2Check = singleValueFromMap2CheckTmp
									except:
										pass
								generate_testcase_from_assumption(test_case_file_full,inst_assumptions)
								if inst_assumptions_len > lastInputInTestcaseCount: lastInputInTestcaseCount = inst_assumptions_len
								hasInputInTestcase = True
								hasLastGoalResult = True
								goals_covered_lst.append(i)
								goals_covered_by_map2check.append(i)
								
						isLastGoalSuccessful = True
					except MyTimeOutException as mytime_ex: raise mytime_ex						
					except KeyboardInterrupt as kb_ex: raise kb_ex;
					except Exception as ex: print(TColors.FAIL);  print(ex); print(TColors.ENDC)
					
					# End of MUST_RUN_MAP_2_CHECK_FOR_BRANCHES
				if (goals_count > 1000 and goal_id % 2 == 0): continue # for example
				isFromMap2Check = False
				goal_witness_file=goal+'.graphml'
				goal_witness_file_full=os.path.join(INSTRUMENT_OUTPUT_DIR ,goal_witness_file)
				test_case_file_full=os.path.join(__testSuiteDir__,'testcase_'+str(i)+'_ES.xml')
				inst_new_esbmc_command_line = inst_esbmc_command_line + ' --witness-output ' + goal_witness_file_full + ' --error-label ' + goal \
												+ ' -I'+os.path.dirname(os.path.abspath(benchmark)) + param_timeout_esbmc + param_memlimit_esbmc
												# + ' --timeout ' + str(time_per_goal_for_esbmc)+ 's '
				output = run(inst_new_esbmc_command_line)
				IsTimeOut(True)
				if not os.path.isfile(goal_witness_file_full):
					print('Cannot run ESBMC for '+ goal)
				else:
					#if not IsMetaDataGenerated:
					#	generate_metadata_from_witness(goal_witness_file_full)
					
					# it is only for __VERIFIER_nondet_int but not __VERIFIER_nondet_uint
					inst_assumptions=__getNonDetAssumptions__(goal_witness_file_full,INSTRUMENT_OUTPUT_FILE)
					
					#inst_all_assumptions.append(inst_assumptions)
					if len(inst_assumptions)>0 :
						if len(inst_assumptions) > lastInputInTestcaseCount: lastInputInTestcaseCount = len(inst_assumptions)
						hasInputInTestcase=True
						hasLastGoalResult = True
						goals_covered += 1						
						goals_covered_lst.append(i)
						#22.06.2020
						generate_testcase_from_assumption(test_case_file_full,inst_assumptions)
					else:
						#goals_to_be_covered_with_extra_lst.append(i)
						pass
					isLastGoalSuccessful=True
				

				if not hasLastGoalResult and i not in goals_to_be_covered_with_extra_lst:
					goals_to_be_covered_with_extra_lst.append(i)
			#here we write many testcases;
		except MyTimeOutException as e:
			#print('Timeout !!!')
			pass
		except KeyboardInterrupt:
			#print('CTRL + C')
			pass
		
		if os.path.isfile(goal_witness_file_full) and not os.path.isfile(test_case_file_full):
			inst_assumptions=__getNonDetAssumptions__(goal_witness_file_full,INSTRUMENT_OUTPUT_FILE, isFromMap2Check)
			 
			if len(inst_assumptions)>0 :
				if len(inst_assumptions) > lastInputInTestcaseCount: lastInputInTestcaseCount = len(inst_assumptions)
				hasInputInTestcase=True
				
				if isFromMap2Check : 
					goals_covered_by_map2check.append(goal_id)
				else:
					goals_covered += 1
					goals_covered_lst.append(goal_id)
				
				generate_testcase_from_assumption(test_case_file_full,inst_assumptions) 
			else:
				if goal_id not in goals_to_be_covered_with_extra_lst: goals_to_be_covered_with_extra_lst.append(goal_id)
			isLastGoalSuccessful=True
		
		if MUST_GENERATE_RANDOM_TESTCASE or MUST_ADD_EXTRA_TESTCASE:
			lastSuccessfulGoal=goal_id
			if isLastGoalSuccessful : lastSuccessfulGoal = goal_id + 1
			for i in range(lastSuccessfulGoal,goals_count+1):
				if i not in goals_to_be_covered_with_extra_lst:
					goals_to_be_covered_with_extra_lst.append(i)
		 
		if MUST_GENERATE_RANDOM_TESTCASE: #and not hasInputInTestcase:
			if len(goals_to_be_covered_with_extra_lst) > 0:
				random_goal_id=goals_to_be_covered_with_extra_lst.pop(0)
			else:
				goals_count +=1
				random_goal_id = goals_count
			random_testcase_file=os.path.join(__testSuiteDir__,'testcase_'+str(random_goal_id)+'_Fu.xml')
			randomMaxRange = 5 # hh
			rndLst=[]
			if lastInputInTestcaseCount > 0:
				randomMaxRange =  lastInputInTestcaseCount + 1
			if randomMaxRange == 3:
				randomMaxRange -= 1
				rndLst=[NonDeterministicCall('0')] + \
						[NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]
			elif randomMaxRange == 2:
				rndLst = [NonDeterministicCall(str(singleValueFromMap2Check))]
			else:		
				randomMaxRange -= 2
				rndLst = [NonDeterministicCall('0')] + \
							[NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]+[NonDeterministicCall('0')]

			generate_testcase_from_assumption(random_testcase_file, rndLst)# was 5
			
			
			goals_covered += 1
			goals_covered_lst.append(random_goal_id)
		
		if MUST_ADD_EXTRA_TESTCASE:
			diff = EXTRA_TESTCASE_COUNT - len(goals_to_be_covered_with_extra_lst)
			if diff > 0:
				for i in range(0,diff):
					extra_testcase_file=os.path.join(__testSuiteDir__,'testcase_'+str(goals_count+i+1)+'_Fu.xml')
					goals_to_be_covered_with_extra_lst.append(goals_count+i+1)
				goals_count += diff
			
			if len(goals_to_be_covered_with_extra_lst) > 0:
				lst2=[NonDeterministicCall('0'),NonDeterministicCall('128')] * int(lastInputInTestcaseCount/2)
				if lastInputInTestcaseCount % 2 == 1:
					lst2.append(NonDeterministicCall('0'))
				lst4=[]
				for i in range(0,lastInputInTestcaseCount):
					if i % 3 == 0 : lst4.append(NonDeterministicCall('0'))
					if i % 3 == 1 : lst4.append(NonDeterministicCall('128'))
					if i % 3 == 2 : lst4.append(NonDeterministicCall('-256'))
				
				if singleValueFromMap2Check == 0: singleValueFromMap2Check = 128 # No Sigle Value; default 128
				elif singleValueFromMap2Check < 0: singleValueFromMap2Check *= -1
				
				if IS_DEBUG: print(TColors.OKGREEN,'singleValueFromMap2Check=',singleValueFromMap2Check,TColors.ENDC)
				lst5 = [NonDeterministicCall(str(randrange(-singleValueFromMap2Check,singleValueFromMap2Check))) for i in range(1,lastInputInTestcaseCount)] + \
						[NonDeterministicCall('0'), NonDeterministicCall('0')]
				lst6 = [NonDeterministicCall('0')]
					
				extra_lsts=[[NonDeterministicCall(str(randrange(-128,128))) for _ in range(0,lastInputInTestcaseCount-1)],
							lst2,
							[NonDeterministicCall('128')]+[NonDeterministicCall('0') for _ in range(0,lastInputInTestcaseCount-1)],
							lst4, lst5 , lst6]
			for i in range(0,len(goals_to_be_covered_with_extra_lst)):
				goal_loop = goals_to_be_covered_with_extra_lst[i]
				if i < len(extra_lsts):
					extra_testcase_file=os.path.join(__testSuiteDir__,'testcase_'+str(goal_loop)+'_Fu.xml')
					generate_testcase_from_assumption(extra_testcase_file,extra_lsts[i])
					goals_covered +=1
					goals_covered_lst.append(goal_loop)
					
				
		if RUN_COV_TEST:
			RunCovTest() 
		if IS_DEBUG:
			if MUST_ADD_EXTRA_TESTCASE:
				print('goals_count',goals_count)
			print('goals_count_original',goals_count_original)
			print('goals_covered',goals_covered)
			print('goals_covered_lst',goals_covered_lst)
			if MUST_ADD_EXTRA_TESTCASE :
				print('goals_to_be_covered_with_extra_lst',goals_to_be_covered_with_extra_lst)
			if MUST_RUN_MAP_2_CHECK_FOR_BRANCHES:
				print('goals_covered_by_map2check',goals_covered_by_map2check)
				print('goals_to_be_run_map2check', goals_to_be_run_map2check)
		
		if is_ctrl_c:
			return parse_result("something else will get unknown",prop)
		#Important with False
		if IsTimeOut(False):
			print('The Time is out..')
		return 'DONE'
		
	if(prop == Property.cover_error_call):
		print('\nRunning FuSeBMC for Cover-Error:\n')
		isFromMap2Check = False
		try:
			print('STARTING INSTRUMENTATION ... \n')
			global toWorkSourceFile
			global map2CheckInputCount
			is_test_file_created=False
			witness_file_name = ''
			testCaseFileName = None
			myLabel = 'FuSeBMC_ERROR'
			runWithTimeoutEnabled(' '.join([FUSEBMC_INSTRUMENT_EXE_PATH, '--input',benchmark ,'--output', INSTRUMENT_OUTPUT_FILE , 
									  '--add-label-in-func',myLabel + '=reach_error',
									  '--compiler-args', '-I'+os.path.dirname(os.path.abspath(benchmark))]))
			IsTimeOut(True)	 
			isInstrumentOK=True
			#check if FuSeBMC_inustrment worked
			if not os.path.isfile(INSTRUMENT_OUTPUT_FILE):
				print("Cannot instrument the file.")
				if IS_DEBUG:
					print(TColors.FAIL,'Cannot instrument the file.',TColors.ENDC)
					exit(0)
				isInstrumentOK = False
				myLabel = 'ERROR'
				toWorkSourceFile=benchmark
			else:
				toWorkSourceFile=INSTRUMENT_OUTPUT_FILE
				#return "Error"
			if MUST_COMPILE_INSTRUMENTED :
				CompileFile(toWorkSourceFile,os.path.dirname(os.path.abspath(toWorkSourceFile)))
			SourceCodeChecker.loadSourceFromFile(toWorkSourceFile)
			linesInSource = len(SourceCodeChecker.__lines__)			
			
						
			if MUST_RUN_MAP_2_CHECK_FOR_ERROR_CALL_FUZZER:
				print('STARTING GOAL 1 ... \n')
				try:
					isFromMap2Check = True
					is_test_file_created = False
					map2CheckNonDetGenerator = 'fuzzer'
					witness_file_name = map2checkWitnessFile
					testCaseFileName =  __testSuiteDir__  + "/testcase_map_fuzzer.xml"
					runWithTimeoutEnabled(' '.join(['timeout',str(map2checkTimeErrorCall_Fuzzer)+'s', map2check_path,'--timeout',str(map2checkTimeErrorCall_Fuzzer),'--fuzzer-mb', str(MEM_LIMIT_ERROR_CALL_MAP2CHECK), '--nondet-generator', map2CheckNonDetGenerator, '--target-function', '--target-function-name','reach_error','--generate-witness',os.path.abspath(toWorkSourceFile)]), WRAPPER_OUTPUT_DIR)
					if os.path.isfile(map2checkWitnessFile):
						createTestFile(map2checkWitnessFile,toWorkSourceFile, testCaseFileName ,True)
						if MUST_RUN_MAP_2_CHECK_FOR_ERROR_CALL_SYMEX:
							run_without_output(' '.join(['cp', map2checkWitnessFile, WRAPPER_OUTPUT_DIR + '/map2check_fuzzer.graphml']))
						is_test_file_created=True
				except MyTimeOutException as e: raise e
				except KeyboardInterrupt as kbe: raise kbe
				except Exception as ex :
					if IS_DEBUG : print(TColors.FAIL,' Exception', ex , TColors.ENDC)
					pass
				
			if MUST_RUN_MAP_2_CHECK_FOR_ERROR_CALL_SYMEX:
				print('STARTING GOAL 1.1 ... \n')
				try:
					isFromMap2Check = True
					is_test_file_created = False
					RemoveFileIfExists(map2checkWitnessFile)
					map2CheckNonDetGenerator = 'symex'
					testCaseFileName =  __testSuiteDir__  + "/testcase_map_symex.xml"
					witness_file_name = map2checkWitnessFile
					runWithTimeoutEnabled(' '.join(['timeout',str(map2checkTimeErrorCall_Symex)+'s', map2check_path,'--timeout',str(map2checkTimeErrorCall_Symex),'--fuzzer-mb', str(MEM_LIMIT_ERROR_CALL_MAP2CHECK),'--nondet-generator', map2CheckNonDetGenerator, '--target-function', '--target-function-name','reach_error','--generate-witness',os.path.abspath(toWorkSourceFile)]), WRAPPER_OUTPUT_DIR)
					if os.path.isfile(map2checkWitnessFile):
						createTestFile(map2checkWitnessFile,toWorkSourceFile, testCaseFileName ,True)
						is_test_file_created=True
				except MyTimeOutException as e: raise e
				except KeyboardInterrupt as kbe: raise kbe
				except Exception as ex :
					if IS_DEBUG : print(TColors.FAIL,' Exception', ex , TColors.ENDC)
					pass
			
			try:
				print('STARTING GOAL 2 ... \n')
				runNumber = 1
				is_test_file_created = False
				isFromMap2Check = False
				testCaseFileName = TESTCASE_FILE_FOR_COVER_ERROR
				witness_file_name = os.path.join(INSTRUMENT_OUTPUT_DIR,os.path.basename(benchmark) +  '__1.graphml')
				esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)			
				esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(os.path.abspath(benchmark))+ ' '
				if isInstrumentOK : esbmc_command_line += ' --error-label ' + myLabel + ' '
				esbmc_command_line += ' --timeout ' + str(int(time_out_s - 1))+'s '
				esbmc_command_line += ' --memlimit ' + str(MEM_LIMIT_ERROR_CALL_ESBMC) + 'g '
				output = run(esbmc_command_line)
				IsTimeOut(True)
				res = parse_result(output, category_property)
				if(res == Result.force_fp_mode):
					fp_mode = True
					esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)			
					esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(os.path.abspath(benchmark))+ ' '
					if isInstrumentOK : esbmc_command_line += ' --error-label  ' + myLabel + ' '
					esbmc_command_line += ' --timeout ' + str(int(time_out_s - 1))+'s '
					esbmc_command_line += ' --memlimit ' + str(MEM_LIMIT_ERROR_CALL_ESBMC) + 'g '
					output = run(esbmc_command_line)
					IsTimeOut(True)
					
				if os.path.isfile(witness_file_name):
					createTestFile(witness_file_name,toWorkSourceFile, testCaseFileName , False)
					is_test_file_created=True
			except MyTimeOutException as e: raise e
			except KeyboardInterrupt as kbe: raise kbe
			except Exception as ex : pass
			
			if mustRunTwice:
				try:
					print('STARTING GOAL 3 ... \n')
					is_test_file_created = False
					isFromMap2Check = False
					runNumber = 2
					testCaseFileName = __testSuiteDir__ + "/testcase_2_ES.xml"
					esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)	
					witness_file_name = os.path.join(INSTRUMENT_OUTPUT_DIR,os.path.basename(benchmark) +  '__2.graphml')
					esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(os.path.abspath(benchmark))+ ' '
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
				except Exception as ex : pass
				
			
		except MyTimeOutException as e:
			#print('Timeout !!!')
			pass
		except KeyboardInterrupt:
			#print('CTRL + C')
			pass
		if not is_test_file_created: createTestFile(witness_file_name,toWorkSourceFile, testCaseFileName, isFromMap2Check)
		
		if MUST_GENERATE_RANDOM_TESTCASE:
			randomMaxRange = 5
			if map2CheckInputCount > 0:
				randomMaxRange =  map2CheckInputCount + 1
				if randomMaxRange == 3:
					randomMaxRange -= 1
					TestCompGenerator([NonDeterministicCall('0')]+\
									[NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)])\
									.writeTestCase(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM)
					AddFileToArchive(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM,TEST_SUITE_DIR_ZIP)
				elif randomMaxRange == 2:
					TestCompGenerator([NonDeterministicCall(str(singleValueFromMap2Check))])\
									.writeTestCase(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM)
					AddFileToArchive(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM,TEST_SUITE_DIR_ZIP)
				else:		
					randomMaxRange -= 2
					TestCompGenerator([NonDeterministicCall('0')]+\
									[NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]+\
									[NonDeterministicCall('0')]).writeTestCase(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM)
					AddFileToArchive(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM,TEST_SUITE_DIR_ZIP)
			
			randomMaxRange = 36
			TestCompGenerator([NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)]+ \
							[NonDeterministicCall('0')]+[NonDeterministicCall('0')])\
							.writeTestCase(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM2)
			AddFileToArchive(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM2,TEST_SUITE_DIR_ZIP)
			
			randomMaxRange = lastInputInTestcaseCount
			TestCompGenerator([NonDeterministicCall('0')]+\
							[NonDeterministicCall(str(randrange(-128,128))) for i in range(1,randomMaxRange)])\
							.writeTestCase(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM3)
			AddFileToArchive(TESTCASE_FILE_FOR_COVER_ERROR_RANDOM3,TEST_SUITE_DIR_ZIP)
			
			
			#The New List
			if singleValueFromMap2Check == 0: singleValueFromMap2Check = 128 # No Sigle Value; default 128
			elif singleValueFromMap2Check < 0: singleValueFromMap2Check *= -1
			if IS_DEBUG: 
				print(TColors.OKGREEN,'singleValueFromMap2Check=',singleValueFromMap2Check,TColors.ENDC)
				print(TColors.OKGREEN,'lastInputInTestcaseCount=',lastInputInTestcaseCount,TColors.ENDC)
				print(TColors.OKGREEN,'map2CheckInputCount=',map2CheckInputCount,TColors.ENDC)

			lst4 = [NonDeterministicCall(str(randrange(-singleValueFromMap2Check,singleValueFromMap2Check))) \
							for i in range(1,lastInputInTestcaseCount)] + \
						[NonDeterministicCall('0'), NonDeterministicCall('0')]
			tmpTestCaseFile = __testSuiteDir__+ '/testcase_4_Fuzzer.xml'
			TestCompGenerator(lst4).writeTestCase(tmpTestCaseFile)
			AddFileToArchive(tmpTestCaseFile,TEST_SUITE_DIR_ZIP)
			
			

		if RUN_COV_TEST:
			RunCovTest() 
		
		if is_ctrl_c:
			return parse_result("something else will get unknown",prop)
		if IsTimeOut(False):
			print('The Time is out...')
		return 'DONE'
		
	# Get command line
	esbmc_command_line = get_command_line(strat, prop, arch, benchmark, fp_mode)
	output = run(esbmc_command_line)
	res = parse_result(output, category_property)
	if(res == Result.force_fp_mode):
		tmp_result=verify(strat, prop, True)
		return tmp_result
 
	# Parse output
	return res

# End of verify

# Options
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--arch", help="Either 32 or 64 bits",type=int, choices=[32, 64], default=32)
parser.add_argument("-v", "--version",help="Prints ESBMC's version", action='store_true')
parser.add_argument("-p", "--propertyfile", help="Path to the property file")
parser.add_argument("benchmark", nargs='?', help="Path to the benchmark")
parser.add_argument("-s", "--strategy", help="ESBMC's strategy",choices=["kinduction", "falsi", "incr"], default="incr")
parser.add_argument("-z", "--zip_path", help="the tesuite Zip file to generate", default=TEST_SUITE_DIR_ZIP)
parser.add_argument("-t", "--timeout", help="time out seconds",type=float, default=time_out_s)
args = parser.parse_args()

arch = args.arch
version = args.version
property_file = args.propertyfile
benchmark = args.benchmark
strategy = args.strategy

if version:
	print ('v.3.6.6')
	exit(0)
if property_file is None:
	print ("Please, specify a property file")
	exit(1)
if benchmark is None:
	print ("Please, specify a benchmark to verify")
	exit(1)

if not args.timeout is None :
	time_out_s = args.timeout
time_out_s -= time_for_zipping_s
if(SHOW_ME_OUTPUT) : print('time_out_s',time_out_s)

if not args.zip_path is None :
	TEST_SUITE_DIR_ZIP = args.zip_path

# Parse property files
f = open(property_file, 'r')
property_file_content = f.read()

if "CHECK( init(main()), LTL(G valid-free) )" in property_file_content:
	category_property = Property.memory
elif "CHECK( init(main()), LTL(G ! overflow) )" in property_file_content:
	category_property = Property.overflow
elif "CHECK( init(main()), LTL(G ! call(__VERIFIER_error())) )" in property_file_content:
	category_property = Property.reach
elif "CHECK( init(main()), LTL(F end) )" in property_file_content:
	category_property = Property.termination
elif "COVER( init(main()), FQL(COVER EDGES(@CALL(reach_error))) )"  in property_file_content:
	category_property = Property.cover_error_call
elif "COVER( init(main()), FQL(COVER EDGES(@DECISIONEDGE)) )" in property_file_content:
	category_property = Property.cover_branches
else:
	print ("Unsupported Property") 
	exit(1)

if not os.path.isdir(WRAPPER_OUTPUT_DIR):
	os.mkdir(WRAPPER_OUTPUT_DIR)
while True:
	tmpOutputFolder = WRAPPER_OUTPUT_DIR +  os.path.basename(benchmark)+'_'+str(GenerateRondomFileName())
	if not os.path.isdir(tmpOutputFolder):
		WRAPPER_OUTPUT_DIR = tmpOutputFolder
		os.mkdir(WRAPPER_OUTPUT_DIR)
		break
		
__testSuiteDir__ = WRAPPER_OUTPUT_DIR+"/test-suite/"
META_DATA_FILE = __testSuiteDir__ + "/metadata.xml"
TESTCASE_FILE_FOR_COVER_ERROR = __testSuiteDir__ + "/testcase_1_ES.xml"
TESTCASE_FILE_FOR_COVER_ERROR_RANDOM = __testSuiteDir__ + "/testcase_1_Fuzzer.xml"
TESTCASE_FILE_FOR_COVER_ERROR_RANDOM2 = __testSuiteDir__ + "/testcase_2_Fuzzer.xml"
TESTCASE_FILE_FOR_COVER_ERROR_RANDOM3 = __testSuiteDir__ + "/testcase_3_Fuzzer.xml"
TESTCASE_FILE_FOR_MAP_CHECK = __testSuiteDir__  + "/testcase_map.xml"
INSTRUMENT_OUTPUT_DIR = WRAPPER_OUTPUT_DIR+'/fusebmc_instrument_output/'
INSTRUMENT_OUTPUT_FILE = WRAPPER_OUTPUT_DIR+'/fusebmc_instrument_output/instrumented.c'
INSTRUMENT_OUTPUT_FILE_OBJ = WRAPPER_OUTPUT_DIR+'/fusebmc_instrument_output/instrumented.o'
INSTRUMENT_OUTPUT_GOALS_FILE = WRAPPER_OUTPUT_DIR+'/fusebmc_instrument_output/goals.txt'
INSTRUMENT_OUTPUT_GOALS_DIR = WRAPPER_OUTPUT_DIR+'/fusebmc_instrument_output/goals_output/'
if TEST_SUITE_DIR_ZIP == '':
	TEST_SUITE_DIR_ZIP = WRAPPER_OUTPUT_DIR + '/test-suite.zip'

if  category_property == Property.cover_branches or category_property == Property.cover_error_call:
	MakeFolderEmptyORCreate(INSTRUMENT_OUTPUT_DIR)
	RemoveFileIfExists(INSTRUMENT_OUTPUT_FILE)
	if category_property == Property.cover_branches:
		RemoveFileIfExists(INSTRUMENT_OUTPUT_GOALS_FILE)
		if MUST_RUN_MAP_2_CHECK_FOR_BRANCHES:
			map2checkWitnessFile= WRAPPER_OUTPUT_DIR + '/witness.graphml'

	MakeFolderEmptyORCreate(__testSuiteDir__)
	
	if category_property == Property.cover_error_call:
		if MUST_RUN_MAP_2_CHECK_FOR_ERROR_CALL_FUZZER or MUST_RUN_MAP_2_CHECK_FOR_ERROR_CALL_SYMEX:
			map2checkWitnessFile= WRAPPER_OUTPUT_DIR + '/witness.graphml'
	
	RemoveFileIfExists(TEST_SUITE_DIR_ZIP)
	WriteMetaDataFromWrapper()
	AddFileToArchive(META_DATA_FILE,TEST_SUITE_DIR_ZIP)
	
	if not os.path.isfile(FUSEBMC_INSTRUMENT_EXE_PATH) and category_property == Property.cover_branches:
		print("FuSeBMC_inustrment cannot be found..")
		#exit(1)
	benchmarkbase=os.path.basename(benchmark)

	result = verify(strategy, category_property, False)
	print(result)
	exit(0)
	

result = verify(strategy, category_property, False)
print (get_result_string(result))
witness_file_name = os.path.basename(benchmark) + ".graphml"

if not os.path.exists(__testSuiteDir__):
	os.mkdir(__testSuiteDir__)
createTestFile(witness_file_name, benchmark)
ZipDir(__testSuiteDir__ ,TEST_SUITE_DIR_ZIP)
