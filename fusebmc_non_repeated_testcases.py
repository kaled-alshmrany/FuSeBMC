#!/usr/bin/env python3
import argparse
import os
import sys
import os.path
import xml.etree.ElementTree as ET # To parse XML

MAX_ELEMENTS_TO_PRINT = 20

def processCommandLineArguements():
	parser = argparse.ArgumentParser(description="Getting non-repeated Testcases for FuSEBMC..")
	parser.add_argument('--testsuite', required=True, help="Test-suite directory to scan.")
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

def main():
	cmdArgs = processCommandLineArguements()
	testsuite_dir = cmdArgs.testsuite
	if not os.path.exists(testsuite_dir):
		print('testsuite is not exists !!!', testsuite_dir)
		sys.exit(0)
	lst = []
	for root, dirs, files in os.walk(testsuite_dir):
		for file in files:
			if file == 'metadata.xml': continue
			#print(file)
			full_file_name = os.path.join(root, file)
			#print(full_file_name)
			try:
				rootXML = ET.parse(full_file_name).getroot()
				lsInputs = [inp.text for inp in rootXML.iter('input')]
				lst.append((file,lsInputs))
			except Exception as ex:
				print('EXCEPTION:', ex)
				print('FILE:', full_file_name)
	#print(lst)
	lst_group = [] # [[('case1',[1,2,3]),('case2',[4,5,6])],
					#[]]
	#lst_repeated = []
	#lst_unique = []
	for fname, l in lst:
		isInOneGroup = False
		for group in lst_group:
			for fname_g, l_g in group:
				if isListsEquals(l, l_g):
					group.append((fname,l))
					isInOneGroup = True
					break
			if isInOneGroup : break
		if not isInOneGroup:
			lst_group.append([(fname,l)])
	#print(lst_group)
	lst_group_len = len(lst_group)
	for i in range(0, lst_group_len):
		for j in range(0, lst_group_len-i-1):
			if len(lst_group[j]) < len(lst_group[j+1]):
				tmp = lst_group[j]
				lst_group[j] = lst_group[j+1]
				lst_group[j+1] = tmp
	print('----------------------------------')
	counter = 0
	print('We found',lst_group_len,'group(s).')
	for group in lst_group:
		counter += 1
		print('Group',counter,'contains',len(group),'testcase(s):')
		for fname_g, l_g in group:
			elemToPrint = MAX_ELEMENTS_TO_PRINT if len(l_g) > MAX_ELEMENTS_TO_PRINT else len(l_g)
			print('    ',fname_g,'=[',end='')
			for i in range(0,elemToPrint): print(l_g[i],',',end='')
			if elemToPrint == len(l_g) : print(']')
			else: print(',...]')
	print('----------------------------------')

if __name__ == "__main__":
	main()
