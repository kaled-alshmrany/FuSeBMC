#!/usr/bin/env python3
import os
import sys
import csv
from tempfile import NamedTemporaryFile
import shutil
import logging
import random
from fusebmc_util.customformatter import CustomFormatter

logger = CustomFormatter.getLogger(__name__, logging.DEBUG)
logger.setLevel(logging.DEBUG)
lsFiles = [
	("./testcomp22_svcomp22/svcomp22/no-overflow.csv", "svcomp", 20),
	("./testcomp22_svcomp22/svcomp22/termination.csv", "svcomp", 20),
	("./testcomp22_svcomp22/svcomp22/unreach-call.csv", "svcomp", 5),
	("./testcomp22_svcomp22/svcomp22/valid-memcleanup.csv", "svcomp", 100),
	("./testcomp22_svcomp22/svcomp22/valid-memsafety.csv", "svcomp", 10), #3440
	#coverage-branches
	("./testcomp22_svcomp22/testcomp22/coverage-branches.FuSeBMC-Validation.csv", "testcomp", 100),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-Arrays.csv", "testcomp", 5),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-BitVectors.csv", "testcomp", 5),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-Combinations.csv", "testcomp", 5),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-ControlFlow.csv", "testcomp", 5),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-ECA.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-Floats.csv", "testcomp", 5),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-Heap.csv", "testcomp", 4),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-ProductLines.csv", "testcomp", 3),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-Recursive.csv", "testcomp", 5),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-Sequentialized.csv", "testcomp", 5),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.ReachSafety-XCSP.csv", "testcomp", 5),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.SoftwareSystems-BusyBox-MemSafety.csv", "testcomp", 5),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.SoftwareSystems-DeviceDriversLinux64-ReachSafety.csv", "testcomp", 2),
	#("./testcomp22_svcomp22/testcomp22/coverage-branches.SoftwareSystems-SQLite-MemSafety.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-branches.Termination-MainHeap.csv", "testcomp", 5),
	
	#coverage-error-call
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.FuSeBMC-Validation.csv", "testcomp", 100),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-Arrays.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-BitVectors.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-ControlFlow.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-ECA.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-Floats.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-Heap.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-ProductLines.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-Recursive.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-Sequentialized.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.ReachSafety-XCSP.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.SoftwareSystems-BusyBox-MemSafety.csv", "testcomp", 10),
	("./testcomp22_svcomp22/testcomp22/coverage-error-call.SoftwareSystems-DeviceDriversLinux64-ReachSafety.csv", "testcomp", 10),

]
svcompFileds = ['name', 'category', 'cpuWallTime', 'status', 'chosen']
testcompFileds = ['name', 'cpuWallTime', 'score','mycls', 'chosen']
fields = []

def getRandomSet(num:int , pLen:int)->list:
	retSet = []
	myls = list(range(0, pLen))
	while len(retSet) < num and len(myls) != 0 :
		myrnd = random.randint(0,len(myls)-1)
		elem = myls[myrnd]
		retSet.append(elem)
		myls.remove(elem)
	return retSet

for f,typ, perCent in lsFiles:
	#if f != "./testcomp22_svcomp22/svcomp22/valid-memsafety.csv" : continue
	if typ == 'svcomp':
		fields = svcompFileds
	elif typ == 'testcomp':
		fields = testcompFileds
	else:
		exit(f"typ {type} is not supported.")
	
	logger.info(f"-----------------------------------------\nstarting: {f}")
	tempfile = NamedTemporaryFile(mode='w', delete=False, newline='')
	with open(f, 'r', newline='') as csvfile:
		reader = csv.DictReader(csvfile, fieldnames=None, delimiter=',')
		#next(reader)
		lsReader = list(reader)
		ln = len(lsReader)
		print('len =', ln , 'perCent =', perCent , 'mustChoose =' , ln * perCent // 100)
		
		writer = csv.DictWriter(tempfile, fieldnames=fields, delimiter=',')
		writer.writeheader()
		
		i = 0
		chosenCounter = 0
		ls10 = []
		for row in lsReader:
			i += 1
			if row['chosen'] == 'y':
				row['chosen'] = ''
			elif row['chosen'] == 'xy':
				row['chosen'] = 'x'
			elif row['chosen'] == '' or row['chosen'] == 'x':
				pass
			else:
				print(f"{f} unknow value '{row['chosen']}'")
				print(row)
				exit(0)
			ls10.append(row)
			if len(ls10) == 100 or i == ln:
				mustChoose = len(ls10) * perCent // 100
				if mustChoose == 0: mustChoose = 1
				print("We have group of" , len(ls10), "mustChoose", mustChoose, "perCent", perCent)
				rnd10 = getRandomSet(mustChoose, len(ls10))
				for idx, row2 in enumerate(ls10):
					if idx in rnd10:
						chosenCounter += 1
						row2['chosen'] += 'y'
						print(chosenCounter,'-',row2['name'])
					writer.writerow(row2)
				ls10 = []
		
	tempfile.close()
	shutil.move(tempfile.name, f)
	