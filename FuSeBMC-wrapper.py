#!/usr/bin/env python3
import os.path
import xml.etree.ElementTree as ET  # To parse XML
import os
import argparse
import shlex
import subprocess
import time
import sys
import resource
import re
#20.05.2020
import zipfile
#from time import process_time 
#from time import process_time_ns
import hashlib



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

__graphml_base__ = '{http://graphml.graphdrawing.org/xmlns}'
__graph_tag__ = __graphml_base__ + 'graph'
__edge_tag__ = __graphml_base__ + 'edge'
__data_tag__ = __graphml_base__ + 'data'
__testSuiteDir__ = "test-suite/"
META_DATA_FILE = __testSuiteDir__ + "/metadata.xml"

# 16.05.2020 + kaled 03.06.2020
INSTRUMENT_OUTPUT_DIR = './my_instrument_outpt/'
INSTRUMENT_OUTPUT_FILE = './my_instrument_outpt/instrumented.c'
INSTRUMENT_OUTPUT_FILE_OBJ = './my_instrument_outpt/instrumented.o'
INSTRUMENT_OUTPUT_GOALS_FILE = './my_instrument_outpt/goals.txt'
INSTRUMENT_OUTPUT_GOALS_DIR = './my_instrument_outpt/goals_output/'

#20.05.2020
TEST_SUITE_DIR_ZIP = 'test-suite.zip'
MAX_NUM_OF_LINES_OUT=50
MAX_NUM_OF_LINES_ERRS=50
SHOW_ME_OUTPUT = False
MUST_COMPILE_INSTRUMENTED = False


# strings
esbmc_path = "./esbmc "
#COV_TEST_EXE = '/home/kaled/Downloads/test-suite-validator/bin/testcov'
#MY_INSTRUMENT_EXE_PATH = './my_instrument'


#esbmc_path='/home/kaled/sdb1/esbmc+python-v6.0.0-linux-static-64/bin/esbmc '
#COV_TEST_EXE = '/home/kaled/sdb1/test-suite-validator/bin/testcov'
COV_TEST_EXE = './bin/testcov'
MY_INSTRUMENT_EXE_PATH = './my_instrument'
#MY_INSTRUMENT_EXE_PATH = './my_instrument_06_06'
# 16.05.2020

# ESBMC default commands: this is the same for every submission
esbmc_dargs = "--no-div-by-zero-check --force-malloc-success --state-hashing "
#16.05.2020 remove --unlimited-k-steps
#03.06.2020 kaled reduce the number of "--k-step 120"
esbmc_dargs += "--no-align-check --k-step 5 --floatbv  "
#02.06.2020 adding options for Coverage-error-call
# kaled : 03.06.2020 you must put it in method 'get_command_line line 844'; here is general
#esbmc_dargs += "--no-align-check --k-step 120 --floatbv --unlimited-k-steps "
esbmc_dargs += "--context-bound 2 "
#16.05.2020
#--unwind 1000 --max-k-step 1000 
esbmc_dargs += "--show-cex "

#29.05.2020
C_COMPILER = 'gcc'
#COV_TEST_PARAMS = ['--no-runexec','--use-gcov','-64']
#kaled 03.06.2020
#COV_TEST_PARAMS= ['--no-runexec','--use-gcov','--cpu-cores','0', '--verbose', '--no-plots','--reduction','BY_ORDER','--reduction-output','test-suite']
COV_TEST_PARAMS= ['--no-runexec', '--no-isolation', '--memlimit', '6GB', '--timelimit-per-run', '3', '--cpu-cores', '0', '--verbose', '--no-plots','--reduction', 'BY_ORDER','--reduction-output','test-suite']
RUN_COV_TEST = True
#kaled 03.06.2020
time_out_ms = 900 * 1000 # 100 seconds
time_for_zipping_ms = 500 # the required time for zipping folder; Can Zero ??
is_ctrl_c = False
class MyTimeOutException(Exception):
    pass
def IsTimeOut(must_throw_ex = False):
    global is_ctrl_c
    global time_out_ms
    global start_time
    if is_ctrl_c is True:
        raise KeyboardInterrupt()
    
    # time.time() : seconds since 1970
    end_time=time.time()
    exec_time_ms=(end_time - start_time) * 1000
    #print('start_time',start_time)
    #print('end_time',end_time) 
    #print('exec_time_ms',exec_time_ms)
    if(exec_time_ms>= time_out_ms):
        if must_throw_ex:
            raise MyTimeOutException()
        else:
            return True
    return False
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
#20.05.2020
def ZipDir(path, zip_file_name):
    #return
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

    #16.05.2020
    def __str__(self):
        return "AssumptionInfo: LINE: {0}, ASSUMPTION: {1}".format(self.line, self.assumption)
    
    def debugInfo(self):
        """Print info about the object"""
        print("AssumptionInfo: LINE: {0}, ASSUMPTION: {1}".format(
            self.line, self.assumption))


class AssumptionParser(object):
    """Class to parse a witness file generated from ESBMC and create a Set of AssumptionHolder."""

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
        self.assumptions = list()
        self.__witness__ = witness

    def __openwitness__(self):
        """Parse XML file using ET"""
        self.__xml__ = ET.parse(self.__witness__).getroot()

    def parse(self):
        """ Iterates over all elements of GraphML and extracts all Assumptions """
        if self.__xml__ is None:
            self.__openwitness__()
        graph = self.__xml__.find(__graph_tag__)
        for node in graph:
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

    def debugInfo(self):
        """Print current info about the object"""
        print("XML: {0}".format(self.__witness__))
        print("ET: {0}".format(self.__xml__))
        for assumption in self.assumptions:
            assumption.debugInfo()


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
        Converts an byte_extract_little_endian((unsigned int)%d, %d) into an value

                Parameters
        ----------
        value : str
            Nondeterministic assumption
        """
        PATTERN = 'byte_extract_little_endian\(\(unsigned int\)(.+), (.+)\)'
        INT_BYTE_SIZE = 4
        match = re.search(PATTERN, value)
        if match == None:
            return value
        number = match.group(1)
        index = match.group(2)

        byte_value = (int(number)).to_bytes(INT_BYTE_SIZE, byteorder='little', signed=True)
        return str(byte_value[int(index)])

    
    @staticmethod
    def fromAssumptionHolder(pAssumptionHolder):
        """
        Converts an Assumption (that is nondet, this function will not verify this) into a NonDetermisticCall

        Parameters
        ----------
        pAssumptionHolder : AssumptionHolder
            Nondeterministic assumption
        """
        _, right = pAssumptionHolder.assumption.split("=")
        left, _ = right.split(";")
        assert(len(right) > 0)
        if left[-1] == "f" or left[-1] == "l":
            left = left[:-1]
        value = NonDeterministicCall.extract_byte_little_endian(left.strip())
        return NonDeterministicCall(value)

    def debugInfo(self):
        print("Nondet call: {0}".format(self.value))


class SourceCodeChecker(object):
    """
        This class will read the original source file and checks if lines from assumptions contains nondeterministic calls    
    """

    def __init__(self, source, plstAssumptionHolder):
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
        self.__lines__ = None

    def __openfile__(self):
        """Open file in READ mode"""
        self.__lines__ = open(self.source, "r").readlines()

    def __is_not_repeated__(self, i):
        x_AssumptionHolder = self.lstAssumptionHolder[i]
        y_AssumptionHolder = self.lstAssumptionHolder[i+1]

        if x_AssumptionHolder.line != y_AssumptionHolder.line:
            return True

        _, x_right = x_AssumptionHolder.assumption.split("=")
        _, y_right = y_AssumptionHolder.assumption.split("=")
  
        return x_right != y_right

    def __isNonDet__(self, p_AssumptionHolder):
        """
            Checks if p_AssumptionHolder is nondet by checking if line contains __VERIFIER_nondet
            
        """

        if "=" in p_AssumptionHolder.assumption:
            check_cast = p_AssumptionHolder.assumption.split("=")
            if len(check_cast) > 1:
                if check_cast[1].startswith(" ( struct "):
                    return False
        
        if self.__lines__ is None:
            self.__openfile__()
        lineContent = self.__lines__[p_AssumptionHolder.line - 1]
        # At first we do not care about variable name or nondet type
        # TODO: Add support to variable name
        # TODO: Add support to nondet type

        result = lineContent.split("__VERIFIER_nondet_")
        return len(result) > 1
        # return right != ""

    """
    return list of NonDeterministicCall objects.
    """
    def getNonDetAssumptions(self):
        
        filtered_assumptions = list()
        
        #16.05.2020
        #print('self.lstAssumptionHolder',self.lstAssumptionHolder)
        #if len(self.lstAssumptionHolder)==0 :
        #    return []
        # 16.05. end
        
        for i in range(len(self.lstAssumptionHolder)-1):
            if self.__is_not_repeated__(i):
                filtered_assumptions.append(self.lstAssumptionHolder[i])
        if len(self.lstAssumptionHolder)>0:
            filtered_assumptions.append(self.lstAssumptionHolder[-1])
        return [NonDeterministicCall.fromAssumptionHolder(x) for x in filtered_assumptions if self.__isNonDet__(x)]

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
        # TODO: add support to enter function
        ET.SubElement(root, 'entryfunction').text = 'main'
        ET.SubElement(root, 'specification').text = property_file_content.strip()
        properties = {'sourcecodelang', 'sourcecodelang', 'producer',
                      'programfile', 'programhash', 'architecture', 'creationtime'}
        for property in properties:
            # 16.05.2020 && 29.05.2020
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

def __getNonDetAssumptions__(witness, source):
    
    """
    return list of NonDeterministicCall objects.
    """
    assumptionParser = AssumptionParser(witness)
    assumptionParser.parse()
    assumptions = assumptionParser.assumptions
    return SourceCodeChecker(source, assumptions).getNonDetAssumptions()


def createTestFile(witness, source):
    if not os.path.isfile(witness) : return
    assumptions = __getNonDetAssumptions__(witness, source)
    TestCompGenerator(assumptions).writeTestCase(__testSuiteDir__ + "/testcase.xml")
    metadataParser = MetadataParser(witness)
    metadataParser.parse()
    TestCompMetadataGenerator(metadataParser.metadata).writeMetadataFile()


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
    
#29.05.2020
def RunCovTest():
    global toWorkSourceFile
    cov_test_exe_abs=os.path.abspath(COV_TEST_EXE)
    cov_test_cmd =[cov_test_exe_abs]
    cov_test_cmd.extend(COV_TEST_PARAMS)
    test_suite_dir_zip_abs=os.path.abspath(TEST_SUITE_DIR_ZIP)
    property_file_abs = os.path.abspath(property_file)
    #05_06_2020
    #if category_property == Property.cover_error_call:
    #    benchmark_abs = os.path.abspath(toWorkSourceFile)
    #else:
    benchmark_abs = os.path.abspath(benchmark)
    cov_test_cmd.extend(['-'+str(arch),'--test-suite' ,test_suite_dir_zip_abs , '--goal' ,property_file_abs , benchmark_abs])
    print(' '.join(cov_test_cmd))
    p=subprocess.Popen(cov_test_cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE, cwd = INSTRUMENT_OUTPUT_DIR)
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

#20.05.2020
def run_without_output(cmd_line):
    if(SHOW_ME_OUTPUT): print(cmd_line)
    the_args = shlex.split(cmd_line)
    p = subprocess.run(the_args, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    #p.communicate()

# Function to run esbmc
def run(cmd_line):
    if(SHOW_ME_OUTPUT): print ("Command: " + cmd_line)

    #20.05.2020
    important_outs_by_ESBMC=["Timed out","Out of memory","Chosen solver doesn\'t support floating-point numbers",
                            "dereference failure: forgotten memory","dereference failure: invalid pointer",
                            "dereference failure: Access to object out of bounds", "dereference failure: NULL pointer",
                            "dereference failure: invalidated dynamic object", "dereference failure: invalidated dynamic object freed", 
                            "dereference failure: invalid pointer freed","dereference failure: free() of non-dynamic memory","array bounds violated",
                            "Operand of free must have zero pointer offset", "VERIFICATION FAILED", "unwinding assertion loop", 
                            " Verifier error called", "VERIFICATION SUCCESSFUL"]
    outs=['' for i in range(MAX_NUM_OF_LINES_OUT)]
    errs=['' for i in range(MAX_NUM_OF_LINES_ERRS)]
    important_outs=[]
    important_errs=[]
    index=-1;
    index_err=-1
    the_args = shlex.split(cmd_line)
      
    #29.05.2020
    try:
        p = subprocess.Popen(the_args, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        while True:
            IsTimeOut(True)
            index =(index + 1) % MAX_NUM_OF_LINES_OUT
            line = p.stdout.readline()
            if not line: break
            line_de=line.decode('utf-8')
            if(SHOW_ME_OUTPUT): print(line_de.rstrip())
            isAddedToImportant=False
            for out_by_ESBMC in important_outs_by_ESBMC:
                if out_by_ESBMC in line_de:
                    important_outs.append(line_de)
                    isAddedToImportant=True
                    break
            if not isAddedToImportant : outs[index]= line_de
    
        
        while True:
            IsTimeOut(True)
            index_err =(index_err + 1) % MAX_NUM_OF_LINES_ERRS
            line = p.stderr.readline()
            if not line: break
            line_de=line.decode('utf-8')
            if(SHOW_ME_OUTPUT): print(line_de.rstrip())
            isAddedToImportant=False
            for out_by_ESBMC in important_outs_by_ESBMC:
                if out_by_ESBMC in line_de:
                    important_errs.append(line_de)
                    isAddedToImportant=True
                    break
            if not isAddedToImportant : errs[index]= line_de
    
        #(stdout, stderr) = p.communicate()
        
          
        #print (stdout.decode(), stderr.decode())
        #return stdout.decode()
    except MyTimeOutException as e:
        pass
    except KeyboardInterrupt:
        global is_ctrl_c
        is_ctrl_c = True
        #exit(0)
        pass
    #29.05.2020
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
        #20.05.2020
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
    
    #20.05.2020
    # TODO: What is the output
    if the_result == Result.fail_cover_error_call:
        return "FAIL_COVER_ERROR_CALL"
    
    if the_result == Result.fail_cover_branches:
        return "FAIL_COVER_BRANCHES"

    if the_result == Result.err_memout:
        return "Unknown"

    if the_result == Result.unknown:
        return "Unknown"

    exit(0)



def get_command_line(strat, prop, arch, benchmark, fp_mode):
    command_line = esbmc_path + esbmc_dargs
    command_line += benchmark + " "
    if arch == 32:
        command_line += "--32 "
    else:
        command_line += "--64 "

    # Add witness arg
    witness_file_name = os.path.basename(benchmark) + ".graphml "
    # 16.05.2020
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
    #16.05.2020
    elif prop == Property.cover_branches:
        command_line += "--unwind 1000 --no-pointer-check --no-bounds-check --interval-analysis --no-slice "
     #20.05.2020 + #03.06.2020 kaled: adding the option "--unlimited-k-steps" for coverage_error_call
    elif prop == Property.cover_error_call:
        #kaled : 03.06.2020
        command_line += "--unlimited-k-steps --no-pointer-check --no-bounds-check --interval-analysis --no-slice --no-align-check  "
    else:
        print ("Unknown property")
        exit(1)

    # if we're running in FP mode, use MathSAT
    if fp_mode:
        command_line += "--mathsat "

    return command_line

#22.06.2020
def generate_metadata_from_witness(p_witness_file):
    if not os.path.isfile(p_witness_file): return
    metadataParser = MetadataParser(p_witness_file)
    metadataParser.parse()
    TestCompMetadataGenerator(metadataParser.metadata).writeMetadataFile()
#22.06.2020
def generate_testcase_from_assumption(p_test_case_file_full,p_inst_assumptions):
    with open(p_test_case_file_full, 'w') as testcase_file:
        testcase_file.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
        testcase_file.write('<!DOCTYPE testcase PUBLIC "+//IDN sosy-lab.org//DTD test-format testcase 1.0//EN" "https://sosy-lab.org/test-format/testcase-1.0.dtd">')
        testcase_file.write('<testcase>')
        for nonDeterministicCall in p_inst_assumptions:
            # if you want to print to std
            #print(nonDeterministicCall)
            testcase_file.write('<input>'+nonDeterministicCall.value +'</input>')
        testcase_file.write('</testcase>')
    
    
def verify(strat, prop, fp_mode):
    #29.05.2020
    global is_ctrl_c
    goal_witness_file_full=''
    inst_assumptions=[]
    # 16.05.2020
    if(prop == Property.cover_branches):
        try:
            run_without_output(' '.join([MY_INSTRUMENT_EXE_PATH, '--input',benchmark ,'--output', INSTRUMENT_OUTPUT_FILE , 
                                  '--goal-output-file',INSTRUMENT_OUTPUT_GOALS_FILE,'--add-else','--add-labels','--add-label-after-loop',
                                  '--compiler-args', '-I'+os.path.dirname(os.path.abspath(benchmark))]))
            IsTimeOut(True)
            #check if my_instrument worked
            if not os.path.isfile(INSTRUMENT_OUTPUT_FILE):
                print("Cannot instrument the file.")
                return Result.unknown
            if not os.path.isfile(INSTRUMENT_OUTPUT_GOALS_FILE):
                print("Cannot instrument the file, goalFile cannot be found.")
                return Result.unknown
            if MUST_COMPILE_INSTRUMENTED:
                CompileFile(INSTRUMENT_OUTPUT_FILE,os.path.dirname(os.path.abspath(benchmark)))
            goals_count_file = open(INSTRUMENT_OUTPUT_GOALS_FILE, "r")
            goals_count = int(goals_count_file.read())
            goals_covered=0
            goals_covered_lst=[]
            #29.05.2020
            time_per_goal_for_esbmc=int(time_out_ms - 1000) / goals_count
            time_per_goal_for_esbmc =int(time_per_goal_for_esbmc / 1000) # to ms
            if time_per_goal_for_esbmc == 0 : time_per_goal_for_esbmc = 1
            #list of list of NonDeterministicCall: each NonDeterministicCall has a value
            inst_all_assumptions=[]
            #--witness-output
            # NOTE: We work with : INSTRUMENT_OUTPUT_FILE
            inst_esbmc_command_line = get_command_line(strat, prop, arch, INSTRUMENT_OUTPUT_FILE, fp_mode)
            counter=0
            for i in range(1,goals_count+1):
                #IsTimeOut(True)
                #22.06.2020
                inst_assumptions=[]
                goal='GOAL_'+str(i)
                goal_witness_file=goal+'.graphml'
                goal_witness_file_full=os.path.join(INSTRUMENT_OUTPUT_DIR ,goal_witness_file)
                test_case_file_full=os.path.join(__testSuiteDir__,'testcase_'+str(i)+'.xml')
                inst_new_esbmc_command_line = inst_esbmc_command_line + ' --witness-output ' + goal_witness_file_full + ' --error-label ' + goal \
                                                + ' -I'+os.path.dirname(os.path.abspath(benchmark)) + ' ' \
                                                # + ' --timeout ' + str(time_per_goal_for_esbmc)+ 's ' \
                print('STARTING GOAL: '+goal)
                #print('COMMAAND:'+inst_new_esbmc_command_line)
                output = run(inst_new_esbmc_command_line)
                IsTimeOut(True)
                if not os.path.isfile(goal_witness_file_full):
                    print('Cannot run ESBMC for '+ goal)
                else:
                    if i==1:
                        #22.06.2020
                        generate_metadata_from_witness(goal_witness_file_full)
                    
                    # it is only for __VERIFIER_nondet_int but not __VERIFIER_nondet_uint
                    inst_assumptions=__getNonDetAssumptions__(goal_witness_file_full,INSTRUMENT_OUTPUT_FILE)
                    #inst_all_assumptions.append(inst_assumptions)
                    if len(inst_assumptions)>0 :
                        goals_covered += 1                        
                        goals_covered_lst.append(goal)
                        #22.06.2020
                        generate_testcase_from_assumption(test_case_file_full,inst_assumptions)
                   
            
            
            #here we write many testcases;we can write one
            #for one_list in inst_all_assumptions:
            #    counter+=1
        except MyTimeOutException as e:
            print('Timeout !!!')
            pass
        except KeyboardInterrupt:
            print('CTRL + C')
            pass
        #22.06.2020
        if not os.path.isfile(META_DATA_FILE):
            generate_metadata_from_witness(goal_witness_file_full)
        
        #22.06.2020
        if os.path.isfile(goal_witness_file_full) and not os.path.isfile(test_case_file_full):
            inst_assumptions=__getNonDetAssumptions__(goal_witness_file_full,INSTRUMENT_OUTPUT_FILE)
            #inst_all_assumptions.append(inst_assumptions)
            if len(inst_assumptions)>0 :
                goals_covered += 1                        
                goals_covered_lst.append(goal)
                #22.06.2020
                generate_testcase_from_assumption(test_case_file_full,inst_assumptions)          
        
        #20.05.2020
        ZipDir(__testSuiteDir__ ,TEST_SUITE_DIR_ZIP)
        print('goals_count',goals_count)
        print('goals_covered',goals_covered)
        print('goals_covered_lst',goals_covered_lst)
        if RUN_COV_TEST:
            RunCovTest()            

        # todo: what is the result
        #if(len(inst_all_assumptions)>0):
        #    return parse_result("VERIFICATION FAILED",prop)
        #else:
        #    return parse_result("VERIFICATION SUCCESSFUL",prop)
        
        #29.05.2020
        if is_ctrl_c:
            return parse_result("something else will get unknown",prop)
        #Important with False
        if IsTimeOut(False):
            return parse_result("Timed out",prop)
        return parse_result("VERIFICATION SUCCESSFUL",prop)
        
    #20.05.2020
    if(prop == Property.cover_error_call):
        try:
            global toWorkSourceFile
            is_test_file_created=False
            run_without_output(' '.join([MY_INSTRUMENT_EXE_PATH, '--input',benchmark ,'--output', INSTRUMENT_OUTPUT_FILE , 
                                  '--add-label-in-func','ERROR=reach_error',
                                  '--compiler-args', '-I'+os.path.dirname(os.path.abspath(benchmark))]))
            IsTimeOut(True)     
            isInstrumentOK=True
            #check if my_instrument worked
            if not os.path.isfile(INSTRUMENT_OUTPUT_FILE):
                print("Cannot instrument the file.")
                isInstrumentOK=False
                toWorkSourceFile=benchmark
            else:
                toWorkSourceFile=INSTRUMENT_OUTPUT_FILE
                #return "Error"
            if MUST_COMPILE_INSTRUMENTED :
                CompileFile(toWorkSourceFile,os.path.dirname(os.path.abspath(toWorkSourceFile)))
            esbmc_command_line = get_command_line(strat, prop, arch, toWorkSourceFile, fp_mode)
            witness_file_name = os.path.join(INSTRUMENT_OUTPUT_DIR,os.path.basename(benchmark) + ".graphml")
            esbmc_command_line += ' --witness-output ' + witness_file_name +' '+'-I'+os.path.dirname(os.path.abspath(benchmark))+ ' '
            if isInstrumentOK:
                esbmc_command_line+= ' --error-label ERROR '
                pass
                
            #29.05.2020
            # what is the suitable time for us and ESBMC ??
            esbmc_command_line += '--timeout ' + str(int((time_out_ms -1000) / 1000))+'s'
            output = run(esbmc_command_line)
            IsTimeOut(True)
            #print('outputYYY',output)
            res = parse_result(output, category_property)
            #20.05.2020
            if(res == Result.force_fp_mode):
                tmp_result=verify(strat, prop, True)
                return tmp_result
            #witness && meta
            if not os.path.isfile(witness_file_name):
                print("No witness")
                return res
            IsTimeOut(True)
            createTestFile(witness_file_name,toWorkSourceFile)
            is_test_file_created=True
        
        except MyTimeOutException as e:
            print('Timeout !!!')
            pass
        except KeyboardInterrupt:
            print('CTRL + C')
            pass
        #22.06.2020
        if not is_test_file_created: createTestFile(witness_file_name,toWorkSourceFile)
        ZipDir(__testSuiteDir__ ,TEST_SUITE_DIR_ZIP)
        if RUN_COV_TEST:
            RunCovTest() 
        
        #29.05.2020
        if is_ctrl_c:
            return parse_result("something else will get unknown",prop)
        #Important with False
        if IsTimeOut(False):
            return parse_result("Timed out",prop)
        #return res
        return parse_result("VERIFICATION SUCCESSFUL",prop)
        
    #16.05.2020 END
    # Get command line
    esbmc_command_line = get_command_line(strat, prop, arch, benchmark, fp_mode)
    output = run(esbmc_command_line)
    res = parse_result(output, category_property)
    
    if(res == Result.force_fp_mode):
        tmp_result=verify(strat, prop, True)
        return tmp_result
 
    # Parse output
    return res


# Options
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--arch", help="Either 32 or 64 bits",type=int, choices=[32, 64], default=32)
parser.add_argument("-v", "--version",help="Prints ESBMC's version", action='store_true')
parser.add_argument("-p", "--propertyfile", help="Path to the property file")
parser.add_argument("benchmark", nargs='?', help="Path to the benchmark")
parser.add_argument("-s", "--strategy", help="ESBMC's strategy",choices=["kinduction", "falsi", "incr"], default="incr")
parser.add_argument("-z", "--zip_path", help="the tesuite Zip file to generate", default=TEST_SUITE_DIR_ZIP)

#29.05.2020
parser.add_argument("-t", "--timeout", help="time out millisecond",type=float, default=time_out_ms)
args = parser.parse_args()

arch = args.arch
version = args.version
property_file = args.propertyfile
benchmark = args.benchmark
strategy = args.strategy

if version:
    print (os.popen(esbmc_path + "--version").read()[6:]),
    exit(0)
if property_file is None:
    print ("Please, specify a property file")
    exit(1)
if benchmark is None:
    print ("Please, specify a benchmark to verify")
    exit(1)
#29.05.2020
if not args.timeout is None :
    time_out_ms = args.timeout
time_out_ms -= time_for_zipping_ms
print('time_out_ms',time_out_ms)

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
#20.05.2020 TODO : remove reach
elif "COVER( init(main()), FQL(COVER EDGES(@CALL(__VERIFIER_error))) )"  in property_file_content:
    category_property = Property.cover_error_call
#elif "COVER( init(main()), FQL(COVER EDGES(@CALL(__VERIFIER_error))) )" in property_file_content:
#    category_property = Property.reach
elif "COVER( init(main()), FQL(COVER EDGES(@DECISIONEDGE)) )" in property_file_content:
    category_property = Property.cover_branches
else:
    print ("Unsupported Property") 
    exit(1)

#TEST_SUITE_DIR_ZIP_PA='./results-verified/test-comp20_prop-coverage-branches.'+os.path.basename(benchmark)
#if not os.path.isdir(TEST_SUITE_DIR_ZIP_PA):
#    os.makedirs(TEST_SUITE_DIR_ZIP_PA)
#TEST_SUITE_DIR_ZIP=TEST_SUITE_DIR_ZIP_PA+'/test-suite.zip'
 
#print('VARRRRRR',os.environ)
# 16.05.2020
#20.05.2020
if  category_property == Property.cover_branches or category_property == Property.cover_error_call:
    MakeFolderEmptyORCreate(INSTRUMENT_OUTPUT_DIR)
    RemoveFileIfExists(INSTRUMENT_OUTPUT_FILE)
    RemoveFileIfExists(INSTRUMENT_OUTPUT_GOALS_FILE)
    MakeFolderEmptyORCreate(INSTRUMENT_OUTPUT_GOALS_DIR)
    MakeFolderEmptyORCreate(__testSuiteDir__)
    
    #20.05.2020
    RemoveFileIfExists(TEST_SUITE_DIR_ZIP)
    
    if not os.path.isfile(MY_INSTRUMENT_EXE_PATH) and category_property == Property.cover_branches:
        print("my_instrument cannot be found..")
        exit(1)
    #must print result
    result = verify(strategy, category_property, False)
    print(get_result_string(result))
    exit(0)
    
    #assumptionParser=AssumptionParser('/home/kaled/counter_example/GOAL_2.graphml');
    #assumptionParser.parse()
    #print(assumptionParser.assumptions)
    #for ass in assumptionParser.assumptions:
    #    ass.debugInfo()
    #sourceCodeChecker=SourceCodeChecker('/home/kaled/sdb1/my_wrapper/my_instrument_outpt/instrumrnted.c',assumptionParser.assumptions)
    #exit(1)


result = verify(strategy, category_property, False)
print (get_result_string(result))
witness_file_name = os.path.basename(benchmark) + ".graphml"

if not os.path.exists(__testSuiteDir__):
    os.mkdir(__testSuiteDir__)
createTestFile(witness_file_name, benchmark)
ZipDir(__testSuiteDir__ ,TEST_SUITE_DIR_ZIP) 


