#!/usr/bin/env python3
#./fusebmc_getinput_from_testcase.py --testcase 

import argparse
import os
import sys
import os.path
import xml.etree.ElementTree as ET # To parse XML

MAX_ELEMENTS_TO_PRINT = 20

def processCommandLineArguements():
	parser = argparse.ArgumentParser(description="Getting Inputs From Testcase for FuSEBMC..")
	parser.add_argument('--testcase', required=True, help="TXML testcase .")
	return parser.parse_args()

	#sys.exit(0)
def isListsEquals(l1,l2):
	len1 = len(l1)
	if(len1 != len(l2)): return False
	for i in range(0,len1):
		if l1[i] != l2[i] : return False
	return True

#def isListInUnique(lst, lstUnique):
#	for fname, l in lstUnique:
#		if isListsEquals(l,lst) : return True
#	return False
def isFileNameInList(p_fname,lst):
	for fname,_ in lst:
		if fname == p_fname : return True
	return False

def main():
	cmdArgs = processCommandLineArguements()
	testcase = cmdArgs.testcase
	if not os.path.isfile(testcase):
		print('testcase is not exists !!!', testcase)
		sys.exit(0)
	
	#print(full_file_name)
	lsInputs = []
	rootXML = ET.parse(testcase).getroot()
	for inp in rootXML.iter('input'):
		if inp is not None and inp.text is not None and len(inp.text) > 0:
			lsInputs.append(inp.text)
			print(inp.text+'\n',end='')
		else:
			lsInputs.append('')
			print('\n',end='')

if __name__ == "__main__":
	main()
