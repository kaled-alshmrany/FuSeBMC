#!/usr/bin/env python3
import sys
import os
import io
import argparse
from xml.etree import ElementTree as ET
import shlex
import csv
import glob
import logging
import yaml

from fusebmc_util.customformatter import CustomFormatter
from fusebmc_util.util import Property, get_result_string, parse_result

logger = CustomFormatter.getLogger(__name__, logging.DEBUG)
logger.setLevel(logging.DEBUG)
def xml_to_string(elem, qualified_name=None, public_id=None, system_id=None):
	"""
	Return a pretty-printed XML string for the Element.
	Also allows setting a document type.
	"""
	from xml.dom import minidom

	rough_string = ET.tostring(elem, "utf-8")
	reparsed = minidom.parseString(rough_string)
	if qualified_name:
		doctype = minidom.DOMImplementation().createDocumentType(
			qualified_name, public_id, system_id
		)
		reparsed.insertBefore(doctype, reparsed.documentElement)
	return reparsed.toprettyxml(indent="  ")

def getExpected_verdictYml(f:str) ->bool|None:
	with open(f, 'r') as ymlFile:
		res = yaml.safe_load(ymlFile)
		lsPrp = res['properties']
		for prp in lsPrp:
			if 'property_file' not in prp:
				print('prp', prp)
				exit(0)
			#if 'expected_verdict' not in prp:
			#	print('prp', prp)
			#	exit(0)
			property_file = prp['property_file']
			head, tail = os.path.split(property_file)
			#print('tail', tail)
			if tail == 'valid-memsafety.prp':
				expected_verdict = prp['expected_verdict']
				return expected_verdict
				#print('ttt', type(expected_verdict))
				#if expected_verdict != True and expected_verdict != False:
				#	print('property_file', property_file)
				#	print('expected_verdict', expected_verdict)
				#	logger.critical(f"{expected_verdict}")
				#	exit(0)
			#print()
	return None

def getResultFromLogFile(logFile:str):
	with open(logFile, 'r') as fd:
		txt = fd.read()
		#print(txt)
		res = parse_result(txt, Property.memsafety)
		resString = get_result_string(res)
		return resString
	
def main():
	#ff="/home/hosam/sdc1/done/results-verified/valid-memsafety/valid-memsafety_00003/FuSeBMC-svcomp.00003.2023-09-24_12-43-52.logfiles/valid-memsafety.CWE590_Free_Memory_Not_on_Heap---s04---CWE590_Free_Memory_Not_on_Heap__free_long_declare_18_bad.yml.log"
	#res = getResultFromLogFile(ff)
	#print(res)
	#exit(0)
	myDir = f"/home/hosam/sdc1/done/results-verified/valid-memsafety/valid-memsafety_*[0-9]/FuSeBMC-svcomp.*[0-9].*.results.valid-memsafety.my_valid-memsafety.xml"
	print(myDir)
	ls = []
	fileList = glob.glob(myDir, recursive=False)
	lsVerdict =[]
	lsLogRes =[]
	for f in sorted(fileList):
		dir_path = os.path.dirname(os.path.realpath(f))
		logDir = glob.glob(f"{dir_path}/FuSeBMC-svcomp.*[0-9].*.logfiles/",recursive=False)[0]
		logger.info(f)
		#print('logDir', logDir)
		tree = ET.parse(f)
		result_xml = tree.getroot()
		for run in result_xml.findall("run"):
			name = run.get('name',None)
			#print(name)
			ymlFile =os.path.abspath(name)
			#print('ymlFile', ymlFile)
			verdict = getExpected_verdictYml(ymlFile)
			#if verdict not in lsVerdict:
			#	lsVerdict.append(verdict)
			#	logger.critical(f" new : {verdict}")
			#continue
			if verdict is None or not isinstance(verdict, bool):
				logger.critical(f" not valid value: {verdict}")
				exit(0)
			head, tail = os.path.split(name)
			#print('tail', tail)
			logFile=glob.glob(f"{logDir}/valid-memsafety.{tail}.log",recursive=False)[0]
			if os.path.isfile(logFile):
				#logger.debug(logFile)
				pass
			else:
				logger.critical(logFile)
				exit(0)
			logRes = getResultFromLogFile(logFile)
			#if logRes not in lsLogRes:
			#	lsLogRes.append(logRes)
			#	logger.critical(f" new : {logRes}")
			#continue
			#print('res', logRes)
			statusElem = run.find('column[@title="status"]')
			status = statusElem.get("value")
			
			categElem = run.find('column[@title="category"]')
			categ = categElem.get("value")
			if verdict == True:
				if logRes == 'TRUE':
					categElem.set('value', 'correct')
				elif logRes == 'FALSE_DEREF' or logRes == 'FALSE_FREE' or logRes == 'FALSE_MEMTRACK':
					statusElem.set('value', logRes)
					categElem.set('value', 'wrong')
				elif logRes == 'Timed out' or logRes == 'Unknown':
					categElem.set('value', 'unknown')
				else:
					logger.critical(f"must not hier logRes = {logRes}")
			elif verdict == False:
				if logRes == 'TRUE':
					categElem.set('value', 'wrong')
				elif logRes == 'FALSE_DEREF' or logRes == 'FALSE_FREE' or logRes == 'FALSE_MEMTRACK':
					statusElem.set('value', logRes)
					categElem.set('value', 'correct')
				elif logRes == 'Timed out' or logRes == 'Unknown':
					categElem.set('value', 'unknown')
				else:
					logger.critical(f"must not hier logRes = {logRes}")
		with io.TextIOWrapper(open(f, "wb"), encoding="utf-8") as xml_file:
			xml_file.write(
				xml_to_string(result_xml).replace("	\n", "").replace("  \n", "")
			)
		print(f"file: '{f}' is modified.")
		
	print('lsVerdict',lsVerdict)
	print('lsLogRes',lsLogRes)
	
	#lsVerdict [True, False]
	#lsLogRes ['FALSE_DEREF', 'TRUE', 'FALSE_FREE', 'Unknown', 'Timed out', 'FALSE_MEMTRACK']
	#status : TIMEOUT -> category=error
	#	false(valid-deref), false(valid-free), true


if __name__ == '__main__':
	main()