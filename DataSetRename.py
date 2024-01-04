#!/usr/bin/env python3
import sys
import os
import io
import argparse
from xml.etree import ElementTree as ET
import shlex
import glob
import re
import shutil
import csv
import logging
from fusebmc_util.util import Property

from fusebmc_util.customformatter import CustomFormatter

from tempfile import NamedTemporaryFile


logger = CustomFormatter.getLogger(__name__, logging.DEBUG)
logger.setLevel(logging.DEBUG)

class P:
	cb = "coverage-branches"
	ec="coverage-error-call"
	uc ="unreach-call"
	vms = "valid-memsafety"
	vmc = "valid-memcleanup"
	ter ="termination"
	noo = "no-overflow"
cb = P.cb
ec = P.ec

def printList(lstNum:list, isForPython=True):
	print('----------------------------')
	print('len =', len(lstNum))
	if isForPython:
		print('Arr=[',end='')
	else:
		print('Arr=(',end='')
		
	for n in lstNum:
		if isForPython:
			print(f'"{n}", ', end='')
		else:
			print(f'"{n}" ', end='')
	if isForPython:
		print(']',end='')
	else:
		print(')',end='')
	print('')
	print('----------------------------')

def getIDOfFile(prop:str, fullFileName:str)->str:
	if prop == ec:
		pattern = '^(coverage\-error\-call_)([0-9]*)$'
	elif prop == cb:
		pattern = '^(coverage\-branches_)([0-9]*)$'
	else:
		exit(f"prop: {prop} is not supported")
		
	base=os.path.basename(fullFileName)
	fdName, ext = os.path.splitext(base)
	res = re.search(pattern, fdName)
	if res is not None:
		#print('groups:',res.groups())
		part1 = res.group(1)
		part2_str = res.group(2)
		return part2_str
	return ''

def getFilesID(prop:str, myDir:str, isForPython=True):
	if not os.path.isdir(myDir):
		exit(f"dir {myDir} does not exit.")
	
	if prop == ec:
		pattern = '^(coverage\-error\-call_)([0-9]*)$'
		myDir = f"{myDir}/coverage-error-call_*"
		
	elif prop == cb:
		pattern = '^(coverage\-branches_)([0-9]*)$'
		myDir = f"{myDir}/coverage-branches_*"
	else:
		exit(f"prop: {prop} is not supported")
	
	#
	#myDir = '/home/hosam/Desktop/shared/to_repeat/results-verified/coverage-branches_*/'
	#myDir = '/home/hosam/Desktop/shared/to_repeat/results-verified/coverage-error-call_*/'
	#myDir = '/home/hosam/sdb2/19_08_2023/fm10/results-verified/coverage-error-call_*/'
	lstNum =[]
	fileList = glob.glob(myDir, recursive=False)
	for f in fileList:
		base=os.path.basename(f)
		print('base', base)
		fdName, ext = os.path.splitext(base)
		print('fdName', fdName)
		subdirname = os.path.basename(os.path.dirname(f))
		print('subdirname', subdirname)
		res = re.search(pattern, fdName)
		if res is not None:
			#print('groups:',res.groups())
			part1 = res.group(1)
			part2_str = res.group(2)
			part2 = int(part2_str)
			print('part2:', part2)
			print('part2_str:', part2_str)
			lstNum.append(part2_str)
		else:
			logger.critical(f"not match {f}")
	lstNum.sort()
	#print('lstNum:', lstNum)
	#printList(lstNum, isForPython)
	return lstNum
	
	return lstNum
def getCBDone():
	return getFilesID(cb, '/home/hosam/sdc1/done/results-verified')
def getCBIgnore():
	return ["00008","00009","00010","00011","00012","00013","00014","00029","00030","00031","00032",
		"00033","00034","00035","00050","00051","00052","00053","00054","00055","00056","00071","00072",
		"00073","00074","00075","00076","00077","00085","00086","00087","00088","00089","00090","00091",
		"00092","00093","00094","00095","00096","00097","00098","00099","00100","00101","00102","00103",
		"00104","00105","00106","00107","00108","00109","00110","00111","00112","00113","00114","00115",
		"00116","00117","00118","00119","00120","00121","00122","00123","00124","00125","00126","00134",
		"00135","00136","00137","00138","00139","00140","00155","00156","00157","00158","00159","00160",
		"00161","00176","00177","00178","00179","00180","00181","00182","00197","00198","00199","00200",
		"00201","00202","00203","00218","00219","00220","00221","00222","00223","00224","00239","00240",
		"00241","00242","00243","00244","00245","00253","00254","00255","00256","00257","00258","00259",
		"00260","00261","00262","00263","00264","00265","00266","00267","00268","00269","00270","00271",
		"00272","00273","00274","00275","00276","00277","00278","00279","00280","00281","00282","00283",
		"00284","00285","00286","00287","00288","00289","00290","00291","00292","00293","00294","00302",
		"00303","00304","00305","00306","00307","00308","00323","00324","00325","00326","00327","00328",
		"00329","00344","00345","00346","00347","00348","00349","00350","00365","00366","00367","00368",
		"00369","00370","00371","00386","00387","00388","00389","00390","00391","00392","00407","00408",
		"00409","00410","00411","00412","00413","00421","00422","00423","00424","00425","00426","00427",
		"00428","00429","00430","00431","00432","00433","00434","00435","00436","00437","00438","00439",
		"00440","00441","00442","00443","00444","00445","00446","00447","00448","00449","00450","00451",
		"00452","00453","00454","00455","00456","00457","00458","00459","00460","00461","00462","00470",
		"00471","00472","00473","00474","00475","00476","00491","00492","00493","00494","00495","00496",
		"00497","00512","00513","00514","00515","00516","00517","00518","00533","00534","00535","00536",
		"00537","00538","00539","00554","00555","00556","00557","00558","00559","00560","00575","00576",
		"00577","00578","00579","00580","00581","00596","00597","00598","00599","00600","00601","00602",
		"00617","00618","00619","00620","00621","00622","00623","00625","00626","00627","00628","00629",
		"00630","00631","00632","00633","00634","00635","00636","00637","00638","00639","00640","00641",
		"00642","00643","00644","00645","00646","00647","00648","00649","00650","00651","00652","00709",
		"00710","00711","00712","00713","00714","00715","00716","00717","00718","00719","00720","00721",
		"00722","00723","00724","00725","00726","00727","00728","00729","00730","00731","00732","00733",
		"00734","00735","00736","00793","00794","00795","00796","00797","00798","00799","00800","00801",
		"00802","00803","00804","00805","00806","00807","00808","00809","00810","00811","00812","00813",
		"00814","00815","00816","00817","00818","00819","00820",]
def getOnlyTestCov():
	return ["00113","00114","00115","00116","00117","00118","00119","00120","00121","00122","00123","00124",
		"00125","00126","00127","00128","00129","00130","00131","00132","00133","00134","00135","00136",
		"00137","00138","00139","00140","00141","00142","00143","00144","00145","00146","00147","00148",
		"00149","00150","00151","00152","00153","00154","00155","00156","00157","00158","00159","00160",
		"00625","00725","00726","00727","00728","00729","00730","00731","00732","00733","00734","00735",
		"00736","00737","00738","00739","00740","00741","00742","00743","00744","00745","00746","00747",
		"00748","00749","00750","00751","00752","00753","00754","00755","00756","00757","00758","00759",
		"00760","00761","00762","00763","00764","00765","00766","00767","00768","00769","00770","00771",
		"00772","00773","00774","00775","00776","00777","00778","00779","00780","00781","00782","00783",
		"00784","00785","00786","00787","00788","00789","00790","00791","00792","00793","00794","00795",
		"00796","00797","00798","00799","00800","00801","00802","00803","00804","00805","00806","00807",
		"00808","00809","00810","00811","00812","00813","00814","00815","00816","00817","00818","00819",
		"00820","00821","00822","00823","00824","00825","00826","00827","00828","00829","00830","00831",
		"00832","00833","00834","00835","00836","00837","00838","00839","00840","00841","00842","00843",
		"00844","00845","00846","00847","00848",]
def ReadCSVResult(csvFile:str,prop:str)->list:
	if prop == cb:
		headers = ['name', 'forCount', 'forMaxDepth' , 'forDepthAvg', 'whileCount', 'whileMaxDepth',
					'whileDepthAvg', 'whileInfiniteCount', 'whileInfiniteWithNonDetCallCount', 'doCount', 
					'doMaxDepth', 'doDepthAvg', 'doInfiniteCount', 'ifCount', 'ifMaxDepth', 'ifDepthAvg', 
					'nestedIfCount', 'elseCount', 'elseDepthAvg', 'nonDetCallCount', 'nonDetCallDepthAvg',
					'hasConcurrency', 'hasNonDetCallInLoop', 'strategy', 'k_step', 'MAX_K_STEP', 
					'contextBound', 'maxInductiveStep', 'unwind', 'FuzzerCoverBranches1', 
					'FuzzerCoverBranches1Time', 'FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL',
					'origScore', 'wallCpuTime', 'resultTimeLimit', 'ourScore', 'ClassifyClass']
	elif prop == ec:
		headers = ['name', 'forCount', 'forMaxDepth', 'forDepthAvg', 'whileCount', 'whileMaxDepth',
				'whileDepthAvg', 'whileInfiniteCount', 'whileInfiniteWithNonDetCallCount', 'doCount',
				'doMaxDepth', 'doDepthAvg', 'doInfiniteCount', 'ifCount', 'ifMaxDepth', 'ifDepthAvg',
				'nestedIfCount', 'elseCount', 'elseDepthAvg', 'nonDetCallCount', 'nonDetCallDepthAvg',
				'hasConcurrency', 'hasNonDetCallInLoop', 'strategy', 'k_step', 'MAX_K_STEP', 'contextBound',
				'maxInductiveStep', 'FuSeBMCFuzzerLib_ERRORCALL_ENABLED', 'FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT', 
				'FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_SEEDS_NUM', 'origScore', 'wallCpuTime', 'resultTimeLimit',
				 'ourScore', 'ClassifyClass'
				 ]
	else:
		#sys.exit(f"not supported prop: {prop}")
		headers = None

	
	with open(csvFile, 'r') as csvfileptr:
		reader = csv.DictReader(csvfileptr, None)
		#next(reader)
		lsReader = list(reader)
		return lsReader

def getSumScore(csvFile:str, prop:str)->float:
	lsReader = ReadCSVResult(csvFile, prop)
	sumScore = 0
	for r in lsReader:
		#print(r)
		if prop == P.cb or prop == P.ec:
			sumScore += float(r['origScore'])
		else:
			sumScore += float(r['ourScore'])
	return sumScore

def isRowsEqual(r1:dict, r2:dict)->bool:
	if len(r1.keys()) != len(r2.keys()):
		return False
	for k in r1:
		if k== 'Num': continue
		if r1[k] != r2[k]:
			return False
	for k in r2:
		if k== 'Num': continue
		if r2[k] != r2[k]:
			return False
	return True
def main(argv=None):
	myDir = '/home/hosam/sdb1/FuSeBMC/mytmp/results-verified/dataset/*.csv'
	myDir = '/home/hosam/Desktop/shared/www/results-verified/dataset/*.csv'
	#myDir = '/home/hosam/Desktop/shared/www/results-verified/*'
	#file1 = open('./missed_branches.txt', 'r')
	#file1 = open('./missed_errorcall.txt', 'r')
	#Lines = file1.readlines()
	#for line in Lines:
	#	print(f"\"{line.strip()}\" ",end='')
	op = 12
	
	
	if op == 1:
		pattern = '^(coverage\-branches_)([0-9]*)$'
		pattern = '^(coverage\-error\-call_)([0-9]*)$'
		myDir = '/home/hosam/sdb1/FuSeBMC/dataset/coverage-branches/test/coverage-branches_*.csv'
		myDir = '/home/hosam/sdb1/FuSeBMC/dataset/coverage-error-call/train/coverage-error-call_*.csv'
		fileList = glob.glob(myDir, recursive=False)
		for f in fileList:
			mPath , nameWithExt = os.path.split(os.path.abspath(f))
			base=os.path.basename(f)
			fdName, ext = os.path.splitext(base)
			#if os.path.isdir(filePath): shutil.rmtree(filePath)
			#else: os.remove(filePath)
			print('filePath:', f)
			print('fdName:', fdName)
			res = re.search(pattern, fdName)
			if res is not None:
				print('groups:',res.groups())
				part1 = res.group(1)
				part2 = res.group(2).zfill(5)
				print('part2', part2)
				print('fdName:', fdName)
				#print('ext:', ext)
				os.rename(f,mPath+'/'+part1+part2+ext)
		exit(0)
	
	'''
	Dataset with SumScore = Zero
	'''
	if op == 2:
		#pattern = '^(coverage\-branches_)([0-9]*)$'
		#pattern = '^(coverage\-error\-call_)([0-9]*)$'
		myDir = '/home/hosam/sdb1/FuSeBMC/dataset/coverage-branches/train/coverage-branches_*.csv'
		#myDir = '/home/hosam/sdb1/FuSeBMC/dataset/coverage-error-call/train/coverage-error-call_*.csv'
		fileList = glob.glob(myDir, recursive=False)
		for f in fileList:
			#print('filePath:', f)
			sumScore = 0
			with open(f) as csv_file:
				#csv_reader = csv.reader(csv_file, delimiter=',')
				csv_reader = csv.DictReader(csv_file)
				for row in csv_reader:
					#print(row)
					sumScore += float(row['origScore'])
			print('sumScore:', sumScore)
			if sumScore == 0 :
				logger.warning(f"Zero: {f}")
			#break
		exit(0)
	
	'''
	missed runs (numbers)
	'''
	if op == 3:
		lstNum = []
		pattern = '^(coverage\-branches_)([0-9]*)$'
		#pattern = '^(coverage\-error\-call_)([0-9]*)$'
		#myDir = '/home/hosam/sdb1/FuSeBMC/dataset/coverage-branches/train/coverage-branches_*.csv'
		myDir = '/home/hosam/sdb1/FuSeBMC/dataset/coverage-error-call/train/coverage-error-call_*.csv'
		fileList = glob.glob(myDir, recursive=False)
		for f in fileList:
			base=os.path.basename(f)
			fdName, ext = os.path.splitext(base)
			res = re.search(pattern, fdName)
			if res is not None:
				#print('groups:',res.groups())
				part1 = res.group(1)
				part2 = int(res.group(2))
				#print('part2:', part2)
				lstNum.append(part2)
			else:
				logger.critical(f"not match {f}")
		lstNum.sort()
		print('lstNum:', lstNum)
		myLen = len(lstNum)
		print('len(lstNum):', myLen)
		if myLen > 1:
			myMin = lstNum[0]
			myMax = lstNum[myLen - 1]
			print('myMin', myMin)
			print('myMax', myMax)
			for i in range(myMin, myMax + 1):
				if i not in lstNum:
					logger.debug(f"{i} not in list")
		exit(0)
	'''
	Build coverage-branches new params.
	'''
	if op == 4:
		def IsItemInList(item,ls:list)->bool:
			lsHeader = ['startegy','kstep','maxKStep','contextBound','maxInductiveStep','unwind','fuzz1Enabled','fuzz1Time','seedsNum']
			for row in ls:
				isEq = True
				for hdr in lsHeader:
					isEq = (row[hdr] == item[hdr]) and isEq
				if isEq:
					return True
			return False
		
		f = "/home/hosam/sdb1/FuSeBMC/ml_runs_params/coverage-branches_ORIG.csv"
		paramsLst = []
		with open(f) as csv_file:
				#csv_reader = csv.reader(csv_file, delimiter=',')
				csv_reader = csv.DictReader(csv_file)
				for row in csv_reader:
					num = int(row['Num'])
					if num <= 624:
						print(num)
						paramsLst.append(row)
		f = "/home/hosam/sdb1/FuSeBMC/ml_runs_params/coverage-branches_NEW.csv"
		lsAfterFilter = []
		with open(f) as csv_file:
				#csv_reader = csv.reader(csv_file, delimiter=',')
				csv_reader = csv.DictReader(csv_file)
				for row in csv_reader:
					if not IsItemInList(row,paramsLst):
						lsAfterFilter.append(row)
					
		
		outFileName = "/home/hosam/sdb1/FuSeBMC/ml_runs_params/coverage-branches_after_filter.csv"
		header = ['Num','startegy','kstep','maxKStep','contextBound','maxInductiveStep','unwind','fuzz1Enabled','fuzz1Time','seedsNum']
		with open(outFileName, 'w') as f:
			writer = csv.writer(f)
			writer.writerow(header)
			counter = 1
			for row in paramsLst + lsAfterFilter:
				row['Num'] = counter
				writer.writerow(row.values())
				counter += 1
		exit(0)
	'''
	Test
	'''
	
	if op == 5:
		dic = {}
		dic['a'] = ['Hallo','World']
		tpl = dic['a']
		tpl [1] = 'New World'
		print(dic['a'])
		exit(0)
	
	'''
	Extract to_repeat nums
	'''
	if op == 6:
		#Arr= ["00002", "00003", "00004", "00005", "00006", "00007", "00008", "00009", "00010", "00011", "00012", "00013", "00014", "00015", "00016", "00017", "00018", "00019", "00020", "00021", "00022", "00023", "00024", "00025", "00026", "00027", "00028", "00029", "00030", "00031", "00032", "00033", "00034", "00035", "00036", "00037", "00038", "00039", "00040", "00041", "00042", "00043", "00044", "00045", "00046", "00047", "00048", "00049", "00050", "00051", "00052", "00053", "00054", "00055", "00056", "00057", "00058", "00059", "00060", "00061", "00062", "00063", "00064", "00065", "00066", "00067", "00068", "00069", "00070", "00071", "00072", "00073", "00074", "00075", "00076", "00077", "00078", "00079", "00080", "00081", "00082", "00083", "00084", "00085", "00086", "00087", "00088", "00089", "00090", "00091", "00092", "00093", "00094", "00095", "00096", "00097", "00098", "00099", "00100", "00101", "00102", "00103", "00104", "00105", "00106", "00107", "00108", "00109", "00110", "00111", "00112", "00113", "00114", "00115", "00116", "00117", "00118", "00119", "00120", "00121", "00122", "00123", "00124", "00125", "00126", "00127", "00128", "00129", "00130", "00131", "00132", "00133", "00134", "00135", "00136", "00137", "00138", "00139", "00140", "00141", "00142", "00143", "00144", "00145", "00146", "00147", "00148", "00149", "00150", "00151", "00152", "00153", "00154", "00155", "00156", "00157", "00158", "00159", "00160", "00725", "00726", "00727", "00728", "00729", "00730", "00731", "00732", "00733", "00734", "00735", "00736", "00737", "00738", "00739", "00740", "00741", "00742", "00743", "00744", "00745", "00746", "00747", "00748", "00749", "00750", "00751", "00752", "00753", "00754", "00755", "00756", "00757", "00758", "00759", "00760", "00761", "00762", "00763", "00764", "00765", "00766", "00767", "00768", "00769", "00770", "00771", "00772", "00773", "00774", "00775", "00776", "00777", "00778", "00779", "00780", "00781", "00782", "00783", "00784", "00785", "00786", "00787", "00788", "00789", "00790", "00791", "00792", "00793", "00794", "00795", "00796", "00797", "00798", "00799", "00800", "00801", "00802", "00803", "00804", "00805", "00806", "00807", "00808", "00809", "00810", "00811", "00812", "00813", "00814", "00815", "00816", "00817", "00818", "00819", "00820", "00821", "00822", "00823", "00824", "00825", "00826", "00827", "00828", "00829", "00830", "00831", "00832", "00833", "00834", "00835", "00836", "00837", "00838", "00839", "00840", "00841", "00842", "00843", "00844", "00845", "00846", "00847", "00848", ]
		#Arr2 = ["00003", "00004", "00005", "00006", "00007", "00008", "00009", "00010", "00011", "00012", "00013", "00014", "00015", "00016", "00017", "00018", "00019", "00020", "00021", "00022", "00023", "00024", "00025", "00026", "00027", "00028", "00029", "00030", "00031", "00032", "00033", "00034", "00035", "00036", "00037", "00038", "00039", "00040", "00041", "00042", "00043", "00044", "00045", "00046", "00047", "00048", "00049", "00050", "00051", "00052", "00053", "00054", "00055", "00056", "00057", "00058", "00059", "00060", "00061", "00062", "00063", "00064", "00065", "00066", "00067", "00068", "00069", "00070", "00071", "00072", "00073", "00074", "00075", "00076", "00077", "00078", "00079", "00080", "00081", "00082", "00083", "00084", "00085", "00086", "00087", "00088", "00089", "00090", "00091", "00092", "00093", "00094", "00095", "00096", "00097", "00098", "00099", "00100", "00101", "00102", "00103", "00104", "00105", "00106", "00107", "00108", "00109", "00110", "00111", "00112", "00113", "00114", "00115", "00116", "00117", "00118", "00119", "00120", "00121", "00122", "00123", "00124", "00125", "00126", "00127", "00128", "00129", "00130", "00131", "00132", "00133", "00134", "00135", "00136", "00137", "00138", "00139", "00140", "00141", "00142", "00143", "00144", "00145", "00146", "00147", "00148", "00149", "00150", "00151", "00152", "00153", "00154", "00155", "00156", "00157", "00158", "00159", "00160", "00625", ]
		
		#Arr=["00001", "00002", "00003", "00004", "00005", "00006", "00007", "00008", "00009", "00010", "00011", "00012", "00013", "00014", "00015", "00016", "00017", "00018", "00019", "00020", "00041", "00042", "00043", "00044", "00045", "00046", "00047", "00048", "00049", "00050", "00051", "00052", "00053", "00054", "00055", "00056", "00057", "00058", "00059", "00060", "00061", "00062", "00063", "00064", "00065", "00066", "00067", "00068", "00069", "00070", "00071", "00072", "00073", "00074", "00075", "00076", "00077", "00078", "00079", "00080", "00081", "00082", "00083", "00084", "00085", "00086", "00087", "00088", "00089", "00090", "00091", "00092", "00093", "00094", "00095", "00096", "00097", "00098", "00099", "00100", "00101", "00102", "00103", "00104", "00105", "00106", "00107", "00108", "00109", "00110", "00111", "00112", "00113", "00114", "00115", "00116", "00117", "00118", "00119", "00120", "00141", "00142", "00143", "00144", "00145", "00146", "00147", "00148", "00149", "00150", "00151", "00152", "00153", "00154", "00155", "00156", "00157", "00158", "00159", "00160", "00181", "00182", "00183", "00184", "00185", "00186", "00187", "00188", "00189", "00190", "00191", "00192", "00193", "00194", "00195", "00196", "00197", "00198", "00199", "00200", "00221", "00222", "00223", "00224", "00225", "00226", "00227", "00228", "00229", "00230", "00231", "00232", "00233", "00234", "00235", "00236", "00237", "00238", "00239", "00240", "00261", "00262", "00263", "00264", "00265", "00266", "00267", "00268", "00269", "00270", "00271", "00272", "00273", "00274", "00275", "00276", "00277", "00278", "00279", "00280", "00281", "00282", "00283", "00284", "00285", "00286", "00287", "00288", "00289", "00290", "00291", "00292", "00293", "00294", "00295", "00296", "00297", "00298", "00299", "00300", "00301", "00302", "00303", "00304", "00305", "00306", "00307", "00308", "00309", "00310", ]
		#Arr2 = ["00001", "00002", "00003", "00004", "00005", "00006", "00007", "00008", "00009", "00010", "00011", "00012", "00013", "00014", "00015", "00016", "00017", "00018", "00019", "00020", "00041", "00042", "00043", "00044", "00045", "00046", "00047", "00048", "00049", "00050", "00051", "00052", "00053", "00054", "00055", "00056", "00057", "00058", "00059", "00060", "00061", "00062", "00063", "00064", "00065", "00066", "00067", "00068", "00069", "00070", "00071", "00072", "00073", "00074", "00075", "00076", "00077", "00078", "00079", "00080", "00081", "00082", "00083", "00084", "00085", "00086", "00087", "00088", "00089", "00090", "00091", "00092", "00093", "00094", "00095", "00096", "00097", "00098", "00099", "00100", "00101", "00102", "00103", "00104", "00105", "00106", "00107", "00108", "00109", "00110", "00111", "00112", "00113", "00114", "00115", "00116", "00117", "00118", "00119", "00120", "00141", "00142", "00143", "00144", "00145", "00146", "00147", "00148", "00149", "00150", "00151", "00152", "00153", "00154", "00155", "00156", "00157", "00158", "00159", "00160", "00181", "00182", "00183", "00184", "00185", "00186", "00187", "00188", "00189", "00190", "00191", "00192", "00193", "00194", "00195", "00196", "00197", "00198", "00199", "00200", "00221", "00222", "00223", "00224", "00225", "00226", "00227", "00228", "00229", "00230", "00231", "00232", "00233", "00234", "00235", "00236", "00237", "00238", "00239", "00240", "00261", "00262", "00263", "00264", "00265", "00266", "00267", "00268", "00269", "00270", "00271", "00272", "00273", "00274", "00275", "00276", "00277", "00278", "00279", "00280", "00281", "00282", "00283", "00284", "00285", "00286", "00287", "00288", "00289", "00290", "00291", "00292", "00293", "00294", "00295", "00296", "00297", "00298", "00299", "00300", "00301", "00302", "00303", "00304", "00305", "00306", "00307", "00308", "00309", "00310", ]
		#print('Arr - Arr2 = ', set(Arr) - set(Arr2))
		#print('Arr2 - Arr = ', set(Arr2) - set(Arr))
		#exit(0)


		lstNum=[]
		print('We 6')
		pattern = '^(coverage\-error\-call_)([0-9]*)$'
		#pattern = '^(coverage\-branches_)([0-9]*)$'
		myDir = '/home/hosam/Desktop/shared/to_repeat/results-verified/coverage-branches_*/'
		myDir = '/home/hosam/Desktop/shared/to_repeat/results-verified/coverage-error-call_*/'
		myDir = '/home/hosam/sdb2/19_08_2023/fm10/results-verified/coverage-error-call_*/'
		
		cbRepeat = getFilesID(ec,'/home/hosam/sdb1/FuSeBMC/results-verified/')
		cbDone = getFilesID(ec,'/home/hosam/Desktop/shared/www/results-verified')
		print('len(cbRepeat)=', len(cbRepeat))
		print('len(cbDone)=', len(cbDone))
		print('set(cbRepeat) - set(cbDone):',set(cbRepeat) - set(cbDone), 'len =', len(set(cbRepeat) - set(cbDone)))
		print('set(cbDone) - set(cbRepeat):',set(cbDone) - set(cbRepeat), 'len =',len(set(cbDone) - set(cbRepeat)))
		print('set(cbDone) & set(cbRepeat)', set(cbDone) & set(cbRepeat))
		#cb10 = getFilesID("coverage-branches",'/home/hosam/Desktop/shared/19_08_2023/fm10/results-verified/')
		#print('set(cb10) - set(cbRepeat):',set(cb10) - set(cbRepeat))
		#exit(0)
		tot = cbRepeat + cbDone
		notDone = []
		for i in range(1,167):
			nu = str(i).zfill(5)
			if nu not in tot :
				notDone.append(nu)
		middle_i = int(len(notDone)/2)
		#notDone1=notDone[:middle_i]
		#notDone2=notDone[middle_i:]
		
		printList(notDone, False)
		#printList(notDone2, False)
		exit(0)
		
	'''
	delete run dirs from results-verified
	'''
	if op == 7:
		print(os.path.dirname(__file__))
		exit(0)
		toDel = f"/home/hosam/sdb2/to_repeat/results-verified/coverage-error-call_*/Coverage-Error-Call/*.yml/*_*"
		toDel ="/home/hosam/sdb2/to_repeat/results-verified/coverage-branches_*/Coverage-Branches/*.yml/*_*"
		fileList = glob.glob(toDel, recursive=False)
		for filePath in fileList:
			#print('filePath', filePath)
			if os.path.isdir(filePath):
				lsd = os.listdir(filePath)
				shutil.rmtree(filePath)
				if len(lsd) == 0:
					#print("Empty directory")
					pass
				else:
					print("Not empty directory", filePath)
					print(lsd)
		exit(0)
	
	'''
	delete entries from ./ml_runs_params/coverage-branches.csv
	'''
	if op == 8:
		lsnonDone = ['00162','00163','00164','00165','00166','00167','00168','00169','00170','00171','00172','00173','00174','00175','00176','00177','00178',
					'00179','00180','00181','00182','00183','00184','00185','00186','00187','00188','00189','00190',
					'00191','00192','00193','00194','00195','00196','00197','00198','00199','00200','00201','00202',
					'00203','00204','00205','00206','00207','00208','00209','00210','00211','00212','00213','00214',
					'00215','00216','00217','00218','00219','00220','00221','00222','00223','00224','00225','00226','00227',
					'00228','00229','00230','00231','00232','00233','00234','00235','00236','00237','00238',
					'00239','00240','00241','00242','00243','00244','00245','00246','00247','00248',
					'00249','00250','00251','00252','00253','00254','00255','00256','00257','00258',
					'00259','00260','00261','00262','00263','00264','00265','00266',
					'00267','00268','00269','00270','00271','00272','00273','00274','00275','00276',
					'00277','00278','00279','00280','00281','00282','00283','00284','00285','00286','00287',
					'00288','00289','00290','00291','00292','00293','00294','00295','00296','00297','00298','00299','00300',
					'00301','00302','00303','00304','00305','00306','00307','00308','00309',
					'00310','00311','00312','00313','00314','00315','00316','00317','00318','00319',
					'00320','00321','00322','00323','00324','00325','00326','00327','00328','00329',
					'00330','00331','00332','00333','00334','00335','00336','00337','00338','00339',
					'00340','00341','00342','00343','00344','00345','00346','00347','00348','00349','00350','00351','00352','00353','00354','00355','00356','00357','00358','00359','00360','00361',
					'00362','00363','00364','00365','00366','00367','00368','00369','00370','00371','00372',
					'00373','00374','00375','00376','00377','00378','00379','00380','00381','00382','00383','00384',
					'00385','00386','00387','00388','00389','00390','00391','00392','00393','00394','00395','00396','00397',
					'00398','00399','00400','00401','00402','00403','00404','00405','00406','00407','00408','00409','00410','00411',
					'00412','00413','00414','00415','00416','00417','00418','00419','00420','00421','00422','00423','00424','00425',
					'00426','00427','00428','00429','00430','00431','00432','00433','00434','00435','00436','00437',
					'00438','00439','00440','00441','00442','00443','00444','00445','00446','00447','00448','00449','00450',
					'00451','00452','00453','00454','00455','00456','00457','00458','00459','00460','00461','00462','00463','00464','00465',
					'00466','00467','00468','00469','00470','00471','00472','00473','00474','00475','00476','00477','00478','00479','00480',
					'00481','00482','00483','00484','00485','00486','00487','00488','00489','00490','00491','00492','00493','00494',
					'00495','00496','00497','00498','00499','00500','00626','00627','00628','00629','00630','00631','00632','00633',
					'00634','00635','00636','00637','00638','00639','00640','00641','00642','00643','00644','00645','00646','00647',
					'00648','00649','00650','00651','00652','00653','00654','00655','00656','00657','00658','00659','00660','00661','00662','00663',
					'00664',
					'00665','00666','00667','00668','00669','00670','00671','00672','00673','00674','00675',
					'00676','00677','00678','00679','00680','00681','00682','00683','00684','00685',
					'00686','00687','00688','00689','00690','00691','00692','00693',
					'00694','00695','00696','00697','00698','00699','00700','00701','00702','00703','00704','00705','00706',
					'00707','00708','00709','00710','00711','00712','00713','00714','00715','00716','00717','00718','00719','00720',
					'00721','00722','00723','00724',
]
	
		cbParams_file = './ml_runs_params/coverage-branches.csv'
		tempfile = NamedTemporaryFile(mode='w', delete=False)
		fileds = ['Num','startegy','kstep','maxKStep','contextBound','maxInductiveStep','unwind','fuzz1Enabled','fuzz1Time','seedsNum']
		lsDel =[]
		with open(cbParams_file, 'r') as csvfile:
			writer = csv.DictWriter(tempfile, fileds)
			reader = csv.DictReader(csvfile, fieldnames=fileds  , delimiter = ',')
			next(reader, None)
			lsReader = list(reader)
			for r in lsReader:
				#print(r)
				#r['del'] = 'x'
				num = int(r['Num'])
				if int(r['unwind']) == 10 or int(r['maxKStep']) == 50:
					print(num)
					lsDel.append(str(num).zfill(5))
				#writer.writerow(r)
		tempfile.close()
		print('lens', len(lsDel))
		#shutil.move(tempfile.name, cbParams_file)
		lsremain = list(set(lsnonDone) - set(lsDel))
		print(len(lsremain))
		printList(list(lsDel),False)
		exit(0)
	
	'''
	'''
	if op == 9:
		myDir = '/home/hosam/sdc1/done/results-verified'
		#myDir = '/home/hosam/sdc1/26_08_2023/fm10/results-verified'
		#myDir = '/home/hosam/sdc1/26_08_2023/fm11/results-verified'
		myPrp = ec
		for i in range(1,379):
			iStr = str(i).zfill(5)
			rDir = f"{myDir}/{myPrp}_{iStr}"
			if os.path.isdir(rDir):
				pass
			else:
				logger.critical(f"No: {rDir}")
		exit(0)
		ids = getFilesID(myPrp, myDir)
		for i in ids:
			#iStr = str(i).zfill(5)
			iStr = i
			i_n = int(i)
			cbDir = f"{myDir}/{myPrp}_{iStr}"
			if not os.path.isdir(cbDir):
				print('No', cbDir)
				continue
			csvFile=f"{cbDir}/{myPrp}_{iStr}.csv"
			#csvFile_min=f"{cbDir}/{myPrp}_{i_n}.csv"
			#if os.path.isfile(csvFile_min):
			#	os.rename(csvFile_min, csvFile)
			#continue
			
			if not os.path.isfile(csvFile):
				print('No', csvFile)
				continue
			
			lsReader = ReadCSVResult(csvFile, ec)
			sumScore = 0
			for r in lsReader:
				#print(r)
				sumScore += float(r['origScore'])
			if sumScore == 0:
				logger.critical(f"ZERO: {csvFile}")
			else:
				logger.info(f"{csvFile} = {sumScore}")
				#shutil.move(cbDir, '/home/hosam/sdc1/done/results-verified/')
		exit(0)

	'''
	'''
	if op == 10:
		myPrp = cb
		myDir = f"/home/hosam/sdb1/FuSeBMC/dataset/{myPrp}/train/{myPrp}_*.csv"
		myDir=f"/home/hosam/sdc1/done/results-verified"
		ls = getFilesID(myPrp, myDir, isForPython=False)
		exit(0)
		
		fileList = glob.glob(myDir, recursive=False)
		for f in fileList:
			sumScore = getSumScore(f, myPrp)
			if sumScore > 0:
				id = getIDOfFile(myPrp, f)
				print(id)
				dDir = f"/home/hosam/sdc1/done/results-verified/{myPrp}_{id}"
				if not os.path.isdir(dDir):
					logger.critical(f"No: {dDir}")
		
		exit(0)
	
	'''
	'''
	if op == 11:
		lsDone = getCBDone()
		lsOnlyTestCov = getOnlyTestCov()
		lsIgnore=getCBIgnore()
		nonDoneTestCov = []
		myDir = '/home/hosam/sdc1/17_09_2023/fm10/results-verified'
		myDir = '/home/hosam/sdc1/17_09_2023/fm11/results-verified'
		lsInDs= getFilesID(cb,myDir)
		for n in lsInDs :
			if n not in lsDone:
				print('n=', n)
				f =f"{myDir}/coverage-branches_{n}/coverage-branches_{n}.csv"
				myScore=getSumScore(f, cb)
				print('myScore', myScore)
				if myScore > 0:
					shutil.move(f"{myDir}/coverage-branches_{n}", '/home/hosam/sdc1/done/results-verified/')
		
		#print(lsInDs)
		exit(0)
		
		
		lsInDs= getFilesID(cb,'/home/hosam/sdb1/FuSeBMC/dataset/coverage-branches/train')
		for n in lsInDs :
			if n not in lsDone and n not in lsOnlyTestCov:
				print(n)
		exit(0)
		for lcov in lsOnlyTestCov:
			if not lcov in lsDone:
				print(lcov)
				nonDoneTestCov.append(lcov)
		
		print(len(lsOnlyTestCov))
		print(len(nonDoneTestCov))
		#printList(ls)
		for i in range(1,849):
			istr=str(i).zfill(5)
			if istr not in lsDone and istr not in lsOnlyTestCov and istr not in lsIgnore:
				print(f"\"{istr}\" ", end='')
		exit(0)
		fileList.sort()
		for f in fileList:
			subDir=f+'/*'
			subDirls = glob.glob(subDir, recursive=False)
			if len(subDirls) == 3:
				#csvF = 
				pass
				#shutil.rmtree(f)
			else:
				#logger.critical(f"OK: {subDir}")
				csvList = glob.glob(f"{f}/coverage-branches_*[0-9].csv", recursive=False)
				for scf in csvList:
					score = getSumScore(scf, cb)
					print(scf, score)
					#shutil.move(f,'/home/hosam/sdc1/done/results-verified')
		exit(0)
		
	if op == 12:
		
		myp = P.vms
		myp = P.vmc
		myp = P.noo
		myp = P.ter
		myp = P.uc
		myp = P.ec
		myp = P.cb
		myp = P.uc
		myDir = f"/home/hosam/sdc1/done/results-verified/{myp}/{myp}_*/{myp}_*[0-9].csv"
		print(myDir)
		ls = []
		fileList = glob.glob(myDir, recursive=False)
		for f in sorted(fileList):
			print(f)
			score = getSumScore(f, myp)
			if score == 0 :
				logger.critical(f"score = {score}")
			else:
				logger.info(f"score = {score}")
				#shutil.copy(f, f"/home/hosam/sdb1/FuSeBMC/dataset/{myp}/train/")
			lsReader = ReadCSVResult(f, myp)
			sumScore = 0
			sumWallCpuTime = 0
			for r in lsReader:
				orig = r['origScore']
				wallCpuTime = float(r['wallCpuTime'])
				sumWallCpuTime += wallCpuTime
				if orig not in ls : ls.append(orig)
				#print(r)
			print('sumWallCpuTime', sumWallCpuTime)
		print('ls', ls)
		exit(0)
	
	if op == 13:
		lsReader_old = ReadCSVResult('/home/hosam/sdb1/FuSeBMC/ml_runs_params/unreach-call_old.csv', P.uc)
		lsReader = ReadCSVResult('/home/hosam/sdb1/FuSeBMC/ml_runs_params/unreach-call.csv', P.uc)
		lsOldDone = []
		for rold in lsReader_old:
			numOld = int(rold['Num'])
			if numOld <= 576 and numOld >= 558 :
				for rnew in lsReader:
					if isRowsEqual(rnew, rold):
						numNew = rnew['Num'].zfill(5)
						numOld = rold['Num'].zfill(5)
						print('EQ', numNew, numOld)
						dirOld = f"/home/hosam/sdc1/done/results-verified/unreach-call/unreach-call_{numOld}"
						dirNew = f"/home/hosam/sdc1/done/results-verified/unreach-call/unreach-call_{numNew}"
						cmd = f"mv {dirOld} /home/hosam/sdc1/done/results-verified/unreach-call_new/unreach-call_{numNew}"
						#print(cmd)
						#os.system(cmd)
						break
				lsOldDone.append(rold)
			#print(rold['Num'])
		print(lsOldDone)
		
		exit(0)
	
	toDel = f"/home/hosam/Desktop/shared/to_repeat/results-verified/coverage-error-call_*/Coverage-Error-Call/*/*/test-suite"
	fileList = glob.glob(toDel, recursive=False)
	for filePath in fileList:
		#if os.path.isdir(filePath): shutil.rmtree(filePath)
		#else: os.remove(filePath)
		print('filePath', filePath)
	 #shutil.move(f"/home/hosam/Desktop/shared/www/results-verified/coverage-branches_{line.strip()}/",
	#		f"/home/hosam/Desktop/shared/to_repeat/results-verified/")
	
	exit(0)
	
	
	

	globRes = glob.glob(myDir)
	
	#pattern = '^(coverage\-error\-call_)([0-9]*)$'
	pattern = '^(coverage\-branches_)([0-9]*)$'
	handleFiles = True
	handleDirs = not True
	for fglob in globRes:
		mPath , nameWithExt = os.path.split(os.path.abspath(fglob))
		if handleFiles and os.path.isfile(fglob):
			base=os.path.basename(fglob)
			fdName, ext = os.path.splitext(base)
		if handleDirs and os.path.isdir(fglob):
			print('nameWithExt', nameWithExt)
			fdName = nameWithExt
			ext = ''
		res = re.search(pattern, fdName)
		if res is not None:
			print('groups:',res.groups())
			part1 = res.group(1)
			part2 = res.group(2).zfill(5)
			print('part2', part2)
			print('fdName:', fdName)
			#print('ext:', ext)
			os.rename(fglob,mPath+'/'+part1+part2+ext)

	
if __name__ == "__main__":
	sys.exit(main())

