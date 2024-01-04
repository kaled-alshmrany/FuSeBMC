#!/usr/bin/env python3
import os
import sys
import argparse
import io
import subprocess
import shlex
import resource
import re
from xml.etree import ElementTree as ET
import csv
import logging
from fusebmc_util.customformatter import CustomFormatter

logger = CustomFormatter.getLogger(__name__, logging.DEBUG)
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--type", dest = 'theType',required = True,
				help="Either x or y ; x: traing, y: testing;",type=str,
				choices=['x', 'y'])
parser.add_argument('-p',"--property",
		dest ='property',
		#action="store_true",
		help="the property",
		choices= ['all','coverage-error-call', 'coverage-branches', 'no-overflow',
				'termination','unreach-call', 'valid-memcleanup', 'valid-memsafety'],
		type=str,
		required=False,
		default='all'
	)
args = parser.parse_args()


def runProc(cmd:list,pCwd:str = None):
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=pCwd)
	(stdout, stderr) = p.communicate()
	print(stdout.decode())
	print(stderr.decode())

def run_fast_scandir(dir:str, ext:list): # dir: str, ext: list
	subfolders, files = [], []
	for f in os.scandir(dir):
		if f.is_dir():
			subfolders.append(f.path)
		if f.is_file():
			if os.path.splitext(f.name)[1].lower() in ext:
				files.append(f.path)
	for dir in list(subfolders):
		sf, f = run_fast_scandir(dir, ext)
		subfolders.extend(sf)
		files.extend(f)
	return subfolders, files
myDir=os.path.abspath('./testcomp22_svcomp22/')

_, files = run_fast_scandir(myDir,['.csv'])

totalCount , totalChosen = 0 , 0
lsProp = ['coverage-error-call', 'coverage-branches', 'no-overflow', 'termination','unreach-call',
		'valid-memcleanup', 'valid-memsafety']

outDir = f"{myDir}/{args.theType}/"
if not os.path.isdir(outDir):
	os.mkdir(outDir)
	logger.info(f"{outDir} is created.")

dic = {}
for prop in lsProp:
	dic[prop] = [
				f"{outDir}/my_{prop}.set",
				None, #open(f"{myDir}/my_{prop}.set", 'w', newline='')				
				]
for f in files:
	fname = os.path.basename(f)
	tmpFilename = fname
	if tmpFilename.startswith('coverage-error-call'):
		properties = 'coverage-error-call'
	elif tmpFilename.startswith('coverage-branches'):
		properties = 'coverage-branches'
	elif tmpFilename.startswith('no-overflow'):
		properties = 'no-overflow'
	elif tmpFilename.startswith('termination'):
		properties = 'termination'
	elif tmpFilename.startswith('unreach-call'):
		properties = 'unreach-call'
	elif tmpFilename.startswith('valid-memcleanup'):
		properties = 'valid-memcleanup'
	elif tmpFilename.startswith('valid-memsafety'):
		properties = 'valid-memsafety'
	else:
		raise Exception(f"{tmpFilename} cannot be recognized.")
	if args.property == 'all' or args.property == properties:
		print(f"Processing {fname} [{properties}]")
	elif args.property != properties:
		print(f"Skipping {fname} [{properties}]")
		continue
	
	f_name , fOut = dic[properties]
	if fOut is None:
		fOut = open(f_name, 'w', newline='')
		dic[properties][1] = fOut
	isNew = True
	with open(f, 'r', newline='') as fCsv:
		reader = csv.DictReader(fCsv, fieldnames=None, delimiter=',')
		#header = next(reader)
		if isNew :
			fOut.write('\n# '+tmpFilename + '\n')
			isNew = False
		count, nChosen = 0 , 0
		for data in reader:
			#print(data)
			count += 1
			if len(data)!= 5 :
				print(data, 'length =', len(data), 'must be 5.')
				continue
			chosen = data['chosen']
			chosen = chosen.strip()
			if chosen != '' and chosen != 'x' and chosen != 'y' and chosen != 'xy':
				logger.critical(f"{data} has invalid chosen field.")
			if args.theType in chosen:
				nChosen += 1
				fOut.write(data['name']+'\n')
		
		totalCount += count
		totalChosen += nChosen
		
		print('\tchosen  =', nChosen)
		print('\tcount   =', count)
		percent = 0 if count == 0 else round(nChosen/count * 100)
		print(f"\tpercent = {percent}%")
		fOut.write(f"\n# count = {count}, chosen = {nChosen}, percent = {percent}%")
		fOut.write('\n#---------------------------------------')
#close all files
print('\n##################################\n','outputFiles:')
for prop in dic:
	fname , f = dic[prop]
	if f is not None: f.close()
	if args.property == 'all' or args.property == prop:
		print(fname)
	

print('----------------------')
print('totalChosen  =', totalChosen)
print('totalCount   =', totalCount)
percent = 0 if totalCount == 0 else round(totalChosen/totalCount * 100)
print(f"percent      = {percent}%")
print('----------------------')
print('Done ...!!')
sys.exit(0)

for f in files:
	lstData = []
	fname = os.path.basename(f)
	if not (fname.startswith('FuSeBMC.2021-12-16_03-43-34.results.Test-Comp22_') and \
		fname.endswith('.xml.fixed.xml')):
		continue
	print(fname)
	csvFilename = fname.replace('.xml.fixed.xml', '.csv')
	tree = ET.parse(f)
	root = tree.getroot()
	for run in root.findall('run'):
		name = run.get('name')
		name = name.replace('../sv-benchmarks/c/','')
		properties = run.get('properties')
		#print(properties)
		if properties == 'coverage-error-call' or properties == 'coverage-branches':
			score = '0'
			try:
				score = run.find('column[@title="score"]').get("value")
			except Exception as ex:
				print(ex, f"name={name}", f"file:{fname}")
			score_f=float(''.join([x for x in score if x.isdigit() or x in ['.']]))
			if score_f > 1:
				raise Exception(f"score_f = {score_f} is invalid !!.")
			cputime_s = run.find('column[@title="cputime"]').get("value")
			cputime = float(''.join([x for x in cputime_s if x.isdigit() or x in ['.']]))
			
			walltime_s = run.find('column[@title="walltime"]').get("value")
			walltime = float(''.join([x for x in walltime_s if x.isdigit() or x in ['.']]))
			cpuWallTime = cputime if cputime > walltime else walltime
			mycls = 5
		if properties == 'coverage-error-call':
			if score_f == 0:
				mycls = 5
			else:
				if cpuWallTime>= 720: mycls = 4
				elif cpuWallTime>= 540: mycls = 3
				elif cpuWallTime>= 360: mycls = 2
				elif cpuWallTime>= 180: mycls = 1
				elif cpuWallTime>= 0: mycls = 0
				else:
					raise Exception(f"cpuWallTime = {cpuWallTime} is invalid.")
				
			print(name ,cpuWallTime, score_f, mycls)
			lstData.append([name ,cpuWallTime, score_f,mycls, ''])

		elif properties == 'coverage-branches':
			if score_f >= 0.85 : mycls = 0
			elif score_f >= 0.68 : mycls = 1
			elif score_f >= 0.51 : mycls = 2
			elif score_f >= 0.34 : mycls = 3
			elif score_f >= 0.17 : mycls = 4
			elif score_f >= 0.0 : mycls = 5
			else: 
				raise Exception (f"{score_f} is invalid score_f.")
			
			lstData.append([name ,cpuWallTime, score_f,mycls, ''])
		else:
			raise Exception (f"{properties} is invalid ptoperty.")
	
	if len(lstData) > 0:
		lstData.sort(key=lambda x: (x[3], x[1]))
		with open(myDir+'/'+csvFilename, 'w', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(['name' ,'cpuWallTime', 'score','mycls', 'chosen'])
			writer.writerows(lstData)
	#x = re.findall("^testcov-validate-test-suites-FuSeBMC.2021-12-16_09-49-13.results.Test-Comp22_(.*)$", fname)
	#print(x)
	#os.rename(f, myDir+ x[0])
	pass
print('Done!!!')
sys.exit(0)
parser = argparse.ArgumentParser()
cmd_line = " -s incr --result-dir ./results-verified/run2/${rundefinition_name}/${taskdef_name}/ --timeout 100 --verbose --ml 1"
the_args = shlex.split(cmd_line)
print('the_args', the_args)
print (sys.argv)
parser.add_argument("-s", "--strategy", help="ESBMC's strategy", choices=["kinduction", "falsi", "incr", "fixed"], default="fixed")
parser.add_argument("--verbose", dest = 'SHOW_ME_OUTPUT', help="Show messages verbose (default: False)", action='store_true')
parser.add_argument("--result-dir", dest = 'ResultDir', help="Set the results output directory")
parser.add_argument('--ml', dest = 'ML', help="Machine Learning operation: ", type=int)
parser.add_argument('--timeout', dest = 'time_out_s', help="Timeout in seconds", type=int)
args = parser.parse_args(the_args)
print(args.strategy)
print(args.SHOW_ME_OUTPUT)
print(args.ResultDir)
print(args.ML)
print(args.time_out_s)
sys.exit(0)

print('Done')
#fuSeBMCYAMLParser.parse(yamlFile)
#fuSeBMCYAMLParser.print_str()
