#!/usr/bin/env python3
import sys
import os
import io
import argparse
from xml.etree import ElementTree as ET
import shlex
import glob
import logging
import re
import shutil

from fusebmc_util.customformatter import CustomFormatter
try:
	import xlsxwriter
except ModuleNotFoundError:
	sys.exit("No module named 'xlsxwriter'\ninstall it:\npip3 install XlsxWriter")

#./XMLResultToXLS.py -r '/home/hosam/Desktop/shared/www/results-verified/coverage-branches_*/FuSeBMC-testcomp.*my_coverage-branches.xml.fixed.xml' -t total -o a.xlsx
#./XMLResultToXLS.py -r '/home/hosam/Desktop/shared/www/results-verified/coverage-branches_*/FuSeBMC-testcomp.*my_coverage-branches.xml.fixed.xml' -t data -o a.xlsx
#./XMLResultToXLS.py -r '/home/hosam/Desktop/shared/www/results-verified/coverage-error-call_*/FuSeBMC-testcomp.*Coverage-Error-Call.my_coverage-error-call.xml.fixed.xml' -t total -o a.xlsx
#./XMLResultToXLS.py -r '/home/hosam/sdb1/FuSeBMC/results-verified/unreach-call_*/FuSeBMC-svcomp.*.unreach-call.my_unreach-call.xml' -t data -o a.xlsx



class RunProperty:
	ErrorCall = 'coverage-error-call'
	CoverBranches = 'coverage-branches'
	UnreachCall = 'unreach-call'
	NoOverflow = 'no-overflow'
	Termination = 'termination'
	ValidMemCleanUp = 'valid-memcleanup'
	ValidMemSafety = 'valid-memsafety'

class ResultItem:

	def __init__(self):
		self.name = ''
		self.status = ''
		self.cpuTime = 0.0
		self.wallTime = 0.0
		self.memory = 0.0
		self.score = 0.0
		

def parse_args(argv):
	parser = argparse.ArgumentParser()
	parser.add_argument("-r",
		"--resultsXML",
		metavar="results-xml",
		nargs='+',
		help="XML-file containing the verification results.",
	)

	parser.add_argument(
		"-t","--type",
		#action="store_true",
		help="",
		choices=['total','data'],
		required=True
	)
	parser.add_argument(
		"-o","--output",
		metavar="OUT_FILE",
		required=True,
		help="The XLS outout file",
	)
	
	return parser.parse_args(argv)

def split_string_at_suffix(s, numbers_into_suffix=False):
	if not s: return s, ""
	pos = len(s)
	while pos and numbers_into_suffix == s[pos - 1].isdigit():
		pos -= 1
	return s[:pos], s[pos:]

def main(argv=None):
	if argv is None:
		argv = sys.argv[1:]
	args = parse_args(argv)
	lResult_files = args.resultsXML
	lsResultsXML = []
	lsPath = []
	for f in lResult_files:
		globRes = glob.glob(f)
		for fglob in globRes:
			if fglob not in lsResultsXML:
				lsResultsXML.append(fglob)
	#print('lsResultsXML:', lsResultsXML)
	#duplicate /home/hosam/Desktop/shared/www/results-verified/coverage-branches_00001
	#duplicate /home/hosam/Desktop/shared/www/results-verified/coverage-branches_00161
	
	logger = CustomFormatter.getLogger(__name__, logging.DEBUG)
	logger.setLevel(logging.DEBUG)

	logger.debug("debug message")
	logger.info("info message")
	logger.warning("warning message")
	logger.error("error message")
	logger.critical("critical message")
	
	mainProp = None
	mainMemUnit = None
	dicResult = {}
	if len(lsResultsXML) == 0:
		sys.exit(f"resultsXML has no files.")
	else:
		print(f"We have {len(lsResultsXML)} files:")
	for f in lsResultsXML:
		mPath , nameWithExt = os.path.split(os.path.abspath(f))
		
		#if mPath not in lsPath: lsPath.append(mPath)
		#else: print('duplicate', mPath)
		print('---------------------------------------')
		logger.info(f"processing file: {f}")
		tree = ET.parse(f)
		result_xml = tree.getroot()
		lsOut = []
		for run in result_xml.findall("run"):
			itm = ResultItem()
			itm.name = run.get('name',None)
			prop = run.get('properties',None)
			if prop is None: raise Exception('run has no properties attribute')
			if mainProp is None:
				mainProp = prop
				logger.debug(f"detected prop is {prop}")
			elif mainProp != prop:
				sys.exit(f"not the same properties: ({mainProp}, {prop})")
			
			try:
				itm.status = run.find('column[@title="status"]').get("value")
			except Exception as ex:
				logger.warning(f"cannot extract status from {itm.name}")

			
			try:
				cpuTime_s = run.find('column[@title="cputime"]').get("value")
			except Exception as ex:
				logger.warning(f"cannot extract cpuTime_s from {itm.name}")
				cpuTime_s = '0'
			
			
			try:
				wallTime_s = run.find('column[@title="walltime"]').get("value")
			except Exception as ex:
				logger.warning(f"cannot extract wallTime_s from {itm.name}")
				wallTime_s = '0'
			try:
				memory_s = run.find('column[@title="memory"]').get("value")
				memory, memUnit = split_string_at_suffix(memory_s)
				if mainMemUnit is None:
					mainMemUnit = memUnit
					logger.debug(f"detected memUnit is {memUnit}")
				elif mainMemUnit != memUnit:
					sys.exit(f"different memory units {mainMemUnit} and {memUnit}")
				itm.memory = float(''.join([x for x in memory if x.isdigit() or x in ['.', '-']]))
			except Exception as ex:
				logger.warning(f"cannot extract memory_s from {itm.name}")
			
			itm.cpuTime = float(''.join([x for x in cpuTime_s if x.isdigit() or x in ['.', '-']]))
			itm.wallTime = float(''.join([x for x in wallTime_s if x.isdigit() or x in ['.', '-']]))
			
			if prop == RunProperty.ErrorCall or prop == RunProperty.CoverBranches:
				try:
					itm.score = float(run.find('column[@title="score"]').get("value"))
				except AttributeError:
					logger.warning(f"cannot extract origScore from {itm.name}")
					itm.score = 0
			elif prop == RunProperty.UnreachCall or \
				 prop == RunProperty.NoOverflow or \
				 prop == RunProperty.Termination or \
				 prop == RunProperty.ValidMemCleanUp or \
				 prop == RunProperty.ValidMemSafety:
				try:
					itm.score = run.find('column[@title="category"]').get("value")
				except AttributeError as ae:
					itm.score = 'unknown'
					logger.warning(f"cannot extract category from {itm.name}")
			else:
				raise Exception(f"runProperty {prop} is not supported.")
			#print(name,cpuTime,wallTime,origScore)
			lsOut.append(itm)
		dicResult[f] = lsOut
		#END FOR
	logger.debug(f"Excel file: {args.output}")
	workbook = xlsxwriter.Workbook(args.output)
	bold = workbook.add_format({'bold': 1})
	if args.type == 'total':
		worksheet = workbook.add_worksheet()
		headers = ['Full_Filename', 'FileName', 
				#Status,
				'CpuTime', 'WallTime', 'Memory', 'Score']
		#worksheet.set_column(0, 0, 39.74)
		col = 0
		row = 0
		for hdr in headers:
			worksheet.write(row ,col , hdr, bold)
			col += 1

		
		row = 1
		for f in dicResult:
			lstResultItem = dicResult[f]
			cpuTimeTotal = 0
			wallTimeTotal = 0
			memoryTotal = 0
			origScoreTotal = 0
			for resItem in lstResultItem:
				cpuTimeTotal += resItem.cpuTime
				wallTimeTotal += resItem.wallTime
				memoryTotal += resItem.memory
				if prop == RunProperty.ErrorCall or prop == RunProperty.CoverBranches:
					origScoreTotal += resItem.score
			#print(f,cpuTimeTotal,wallTimeTotal,origScoreTotal)
			mPath , nameWithExt = os.path.split(os.path.abspath(f))
			'''file1 = open('./missed_branches.txt', 'r')
			Lines = file1.readlines()
			for line in Lines:
				toDel = f"/home/hosam/Desktop/shared/www/results-verified/coverage-branches_{line.strip()}/TestCov.*.logfiles"
				fileList = glob.glob(toDel)
				for filePath in fileList:
					if os.path.isdir(filePath):
						shutil.rmtree(filePath)
					else:
						os.remove(filePath)
					print('filePath', filePath)
				'''
			with open('./missed.txt', 'a') as fmissed:
				if origScoreTotal == 0:
					#pattern = '^(coverage\-branches_)([0-9]*)$'
					pattern = '^(coverage\-error\-call_)([0-9]*)$'
					subdirname = os.path.basename(os.path.dirname(f))
					res = re.search(pattern, subdirname)
					if res is not None:
						print('groups:',res.groups())
						part1 = res.group(1)
						part2 = res.group(2).zfill(5)
						fmissed.write(part2+'\n')
						#fileList = glob.glob(f"{mPath}/coverage-branches_*_res.table.html")
						#fileList = glob.glob(f"{mPath}/FuSeBMC-testcomp.*.Coverage-Branches.my_coverage-branches.xml.fixed.xml")
						toDel = f"{mPath}/FuSeBMC-testcomp.*.Coverage-Error-Call.my_coverage-error-call.xml.fixed.xml"
						print('toDel', toDel)
						fileList = glob.glob(toDel)
						for filePath in fileList:
							if os.path.isdir(filePath):
								shutil.rmtree(filePath)
							else:
								os.remove(filePath)
							print('filePath', filePath)
				
			worksheet.write_string(row, 0, f)
			
			worksheet.write_string(row, 1, nameWithExt)
			worksheet.write_number(row, 2, round(cpuTimeTotal,2))
			worksheet.write_number(row, 3, round(wallTimeTotal,2))
			worksheet.write_number(row, 4, round(memoryTotal,2))
			worksheet.write_number(row, 5, round(origScoreTotal,2))
			row += 1
	elif args.type == 'data':
		headers = ['name','Status', 'CpuTime', 'WallTime', 'Memory', 'Score']
		counter = 1
		for f in dicResult:
			mPath , nameWithExt = os.path.split(os.path.abspath(f))
			worksheet = workbook.add_worksheet(f"{counter}_{nameWithExt[:25]}")
			counter += 1
			worksheet.merge_range("A1:M1", f)
			
			col = 0
			row = 1
			for hdr in headers:
				worksheet.write(row ,col , hdr, bold)
				col += 1
			
			row = 2
			lstResultItem = dicResult[f]
			for resItem in lstResultItem:
				worksheet.write_string(row, 0, resItem.name)
				worksheet.write_string(row, 1, resItem.status)
				worksheet.write_number(row, 2, round(resItem.cpuTime,2))
				worksheet.write_number(row, 3, round(resItem.wallTime,2))
				worksheet.write_number(row, 4, round(resItem.memory,2))
				if prop == RunProperty.ErrorCall or prop == RunProperty.CoverBranches:
					worksheet.write_number(row, 5, round(resItem.score,2))
				else:
					worksheet.write_string(row, 5, resItem.score)
				row += 1
			
	workbook.close()
	
if __name__ == "__main__":
	sys.exit(main())
