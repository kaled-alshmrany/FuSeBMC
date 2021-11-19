#!/usr/bin/env python3
#./fusebmc_compare_testcases.py --s1 /home/hosam/sdb1/compare/local --s2 /home/hosam/sdb1/compare/server

import argparse
import os
import sys
import os.path
import xml.etree.ElementTree as ET # To parse XML

MAX_ELEMENTS_TO_PRINT = 20

def processCommandLineArguements():
	parser = argparse.ArgumentParser(description="Getting non-repeated Testcases for FuSEBMC..")
	parser.add_argument('--s1', required=True, help="Test-suite1 directory to scan.")
	parser.add_argument('--s2', required=True, help="Test-suite2 directory to scan.")
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
	s1 = cmdArgs.s1
	s2 = cmdArgs.s2
	if not os.path.exists(s1):
		print('testsuite is not exists !!!', s1)
		sys.exit(0)
	if not os.path.exists(s2):
		print('testsuite is not exists !!!', s2)
		sys.exit(0)
	lst1 = []
	for root, dirs, files in os.walk(s1):
		for file in files:
			if file == 'metadata.xml': continue
			#print(file)
			full_file_name = os.path.join(root, file)
			#print(full_file_name)
			rootXML = ET.parse(full_file_name).getroot()
			lsInputs = [inp.text for inp in rootXML.iter('input')]
			lst1.append((file,lsInputs))
	
	lst2 = []
	for root, dirs, files in os.walk(s2):
		for file in files:
			if file == 'metadata.xml': continue
			#print(file)
			full_file_name = os.path.join(root, file)
			#print(full_file_name)
			rootXML = ET.parse(full_file_name).getroot()
			lsInputs = [inp.text for inp in rootXML.iter('input')]
			lst2.append((file,lsInputs))
	#print('lst1',lst1)
	#print('lst2',lst2)
	lst1_not_lst2 = []
	lst2_not_lst1 = []
	lst1_and_lst2 = []
	for fname_loop,lst_loop in lst1:
		if isFileNameInList(fname_loop,lst2):
			if not isFileNameInList(fname_loop,lst1_and_lst2): lst1_and_lst2.append((fname_loop,lst_loop))
		else:
			lst1_not_lst2.append((fname_loop,lst_loop))
	
	for fname_loop,lst_loop in lst2:
		if isFileNameInList(fname_loop,lst1):
			if not isFileNameInList(fname_loop,lst1_and_lst2): lst1_and_lst2.append((fname_loop,lst_loop))
		else:
			lst2_not_lst1.append((fname_loop,lst_loop))
	print('lst1_not_lst2')
	for f,l in lst1_not_lst2: print(f,l)
	print('----------------------------------------------------------------------------')
	print('lst2_not_lst1')
	for f,l in lst2_not_lst1: print(f,l)
	print('----------------------------------------------------------------------------')
	#print('lst1_and_lst2')
	#for f,l in lst1_and_lst2: print(f,l)
	print('----------------------------------------------------------------------------')
	print('lst1_and_lst2')
	for fname_loop,lst_loop in lst1_and_lst2:
		lFrom_lst1 = None
		for fname_loop1,lst_loop1 in lst1:
			if fname_loop1 == fname_loop :
				lFrom_lst1 = lst_loop1
				break
		lFrom_lst2 = None
		for fname_loop2,lst_loop2 in lst2:
			if fname_loop2 == fname_loop :
				lFrom_lst2 = lst_loop2
				break
		if lFrom_lst1 is None or lFrom_lst2 is None:
			print('NOOOONE')
			exit(0)
		if isListsEquals(lFrom_lst1,lFrom_lst2):
			print('EQuAL')
		else:
			print('+++++++++')
			print('NOT',fname_loop)
			print('lFrom_lst1',lFrom_lst1)
			print('lFrom_lst2',lFrom_lst2)
				
	exit(0)
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
