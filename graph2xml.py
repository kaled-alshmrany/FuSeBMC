#!/usr/bin/env python3
import os.path  # To check if file exists
import xml.etree.ElementTree as ET  # To parse XML
import os
import argparse
#import shlex
#import subprocess
import time
import sys
#import resource
import re

# Start time for this script
start_time = time.time()
benchmark=""
meta_file=""
testcase_file=""
witness_file_name =""


__graphml_base__ = '{http://graphml.graphdrawing.org/xmlns}'
__graph_tag__ = __graphml_base__ + 'graph'
__edge_tag__ = __graphml_base__ + 'edge'
__data_tag__ = __graphml_base__ + 'data'
__testSuiteDir__ = "test-suite/"


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

	def debugInfo(self):
		"""Print info about the object"""
		print("AssumptionInfo: LINE: {0}, ASSUMPTION: {1}".format(self.line, self.assumption))


class AssumptionParser(object):
	"""Class to parse a witness file generated from ESBMC and create a Set of AssumptionHolder."""

	def __init__(self, witnessfile):
		"""
		Default constructor.

		Parameters
		----------

		witness : str
			Path to witness file (absolute/relative)
		"""
		#assert(os.path.isfile(witnessfile))
		if(not os.path.isfile(witnessfile)):
			print('\n'+witnessfile+' File not exists.....!\n')
			exit(0)
		self.__xml__ = None
		self.assumptions = list()
		self.__witness__ = witnessfile

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
		graph = self.__xml__.find(
			__graph_tag__)
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
	def fromAssumptionHolder(assumption):
		"""
		Converts an Assumption (that is nondet, this function will not verify this) into a NonDetermisticCall

		Parameters
		----------
		assumption : AssumptionHolder
			Nondeterministic assumption
		"""
		try:
			_, right = assumption.assumption.split("=")
			left, _ = right.split(";")
			assert(len(right) > 0)
			if left[-1] == "f" or left[-1] == "l":
				left = left[:-1]
			value = NonDeterministicCall.extract_byte_little_endian(left.strip())
			return NonDeterministicCall(value)
		except:
			return None

	def debugInfo(self):
		print("Nondet call: {0}".format(self.value))


class SourceCodeChecker(object):
	"""
		This class will read the original source file and checks if lines from assumptions contains nondeterministic calls
	"""

	def __init__(self, source, assumptions):
		"""
		Default constructor.

		Parameters
		----------
		source : str
			Path to source code file (absolute/relative)
		assumptions : [AssumptionHolder]
			List containing all assumptions of the witness
		"""
		assert(os.path.isfile(source))
		assert(assumptions is not None)
		self.source = source
		self.assumptions = assumptions
		self.__lines__ = None

	def __openfile__(self):
		"""Open file in READ mode"""
		self.__lines__ = open(self.source, "r").readlines()

	def __is_not_repeated__(self, i):
		x = self.assumptions[i]
		y = self.assumptions[i+1]

		if x.line != y.line:
			return True

		_, x_right = x.assumption.split("=")
		_, y_right = y.assumption.split("=")
  
		return x_right != y_right

	def __isNonDet__(self, assumption):
		"""
			Checks if assumption is nondet by checking if line contains __VERIFIER_nondet
		"""

		if "=" in assumption.assumption:
			check_cast = assumption.assumption.split("=")
			if len(check_cast) > 1:
				if check_cast[1].startswith(" ( struct "):
					return False
		
		if self.__lines__ is None:
			self.__openfile__()
		lineContent = self.__lines__[assumption.line - 1]
		# At first we do not care about variable name or nondet type
		# TODO: Add support to variable name
		# TODO: Add support to nondet type

		result = lineContent.split("__VERIFIER_nondet_")
		return len(result) > 1
		# return right != ""

	def getNonDetAssumptions(self):
		filtered_assumptions = list()
		for i in range(len(self.assumptions)-1):
			if self.__is_not_repeated__(i):
				filtered_assumptions.append(self.assumptions[i])
		if(len(self.assumptions)>0):
			filtered_assumptions.append(self.assumptions[-1])
		return [NonDeterministicCall.fromAssumptionHolder(x) for x in filtered_assumptions if self.__isNonDet__(x)]

	def getNonDetAssumptions_New(self):
		#filtered_assumptions = list()
		#for i in range(len(self.assumptions)-1):
		#	if self.__is_not_repeated__(i):
		#		filtered_assumptions.append(self.assumptions[i])
		#if(len(self.assumptions)>0):
		#	filtered_assumptions.append(self.assumptions[-1])
		#print('SSSSSSSSSSSSSSSS',self.assumptions)
		newList=[]		
		for i in range(len(self.assumptions)-1):
			if self.__is_not_repeated__(i):
				#holder is NonDeterministicCall: it has only value
				holder=NonDeterministicCall.fromAssumptionHolder(self.assumptions[i])
				if holder != None:
					newList.append(holder)		
		return newList

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
			ET.SubElement(root, property).text = self.metadata[property]
		
		#output = __testSuiteDir__ + witnessfile
		output = __testSuiteDir__ + meta_file
		
		ET.ElementTree(root).write(output)
		with open(output, 'r') as original: data = original.read()
		with open(output, 'w') as modified: modified.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE test-metadata PUBLIC "+//IDN sosy-lab.org//DTD test-format test-metadata 1.0//EN" "https://sosy-lab.org/test-format/test-metadata-1.0.dtd">' + data)

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
	assumptionParser = AssumptionParser(witness)
	assumptionParser.parse()
	#assumptionParser.debugInfo()
	assumptions = assumptionParser.assumptions
	return SourceCodeChecker(source, assumptions).getNonDetAssumptions_New()


def createTestFile(witness, source):
	assumptions = __getNonDetAssumptions__(witness, source)
	#TestCompGenerator(assumptions).writeTestCase(__testSuiteDir__ + "/" + testcase_file)
	TestCompGenerator(assumptions).writeTestCase(testcase_file)
	metadataParser = MetadataParser(witness)
	metadataParser.parse()
	#kaled
	#TestCompMetadataGenerator(metadataParser.metadata).writeMetadataFile()




parser = argparse.ArgumentParser()

parser.add_argument("-w", "--witnessfile", help="Path to the property file")
parser.add_argument("-t", "--testcasefile", help="Path to the output testcase file")
parser.add_argument("benchmark", nargs='?', help="Path to the benchmark")


args = parser.parse_args()

benchmark = args.benchmark
witnessfile=args.witnessfile
my_testcasefile=args.testcasefile

testcase_file=my_testcasefile
witness_file_name=witnessfile
#print('We have: witness_file_name', witness_file_name)
#witness_file_name = os.path.basename(benchmark) + ".graphml"

#if not os.path.exists(__testSuiteDir__):
#	os.mkdir(__testSuiteDir__)
meta_file=os.path.basename(witnessfile)+".meta"
#testcase_file=os.path.basename(witnessfile)+".xml"


createTestFile(witness_file_name,benchmark)
