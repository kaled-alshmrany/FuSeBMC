#!/usr/bin/env python3
import io, os,sys
import argparse
import csv
from fusebmc_util.util import Property
from fusebmc_ml.Predictor import Predictor

testcomp_template = './FuSeBMC-testcomp-template.xml'
svcomp_template = './FuSeBMC-svcomp-template.xml'

testcomp_tool = './FuSeBMC-testcomp.xml'
svcomp_tool = './FuSeBMC-svcomp.xml'

params = ''

lsProp = ["coverage-error-call","coverage-branches","no-overflow", 
		"termination", "valid-memcleanup","valid-memsafety", "unreach-call"]

dic = {
	"coverage-error-call":(testcomp_template,testcomp_tool,'<!-- coverage-error-call-TEMPLATE -->',300),
	"coverage-branches":(testcomp_template,testcomp_tool,'<!-- coverage-branches-TEMPLATE -->',300),
	"no-overflow":(svcomp_template,svcomp_tool,'<!-- no-overflow-TEMPLATE -->',300),
	"termination":(svcomp_template,svcomp_tool,'<!-- termination-TEMPLATE -->',300),
	"valid-memcleanup":(svcomp_template,svcomp_tool,'<!-- valid-memcleanup-TEMPLATE -->',300),
	"valid-memsafety":(svcomp_template,svcomp_tool,'<!-- valid-memsafety-TEMPLATE -->',300),
	"unreach-call":(svcomp_template,svcomp_tool,'<!-- unreach-call-TEMPLATE -->',300),
	}
def parse_args(argv):
	def check_positive(value: int)-> int:
		ivalue = int(value)
		if ivalue <= 0:
			raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
		return ivalue
	
	parser = argparse.ArgumentParser()
	
	parser.add_argument('-p', "--property",
		dest ='property',
		#action="store_true",
		help="the property",
		choices= lsProp,
		type=str,
		required=True,
	)
	parser.add_argument('-n', "--run-num",
		dest ='runNum',
		#action="store_true",
		help="the number of the run",
		type=check_positive,
		required=True,
	)
	return parser.parse_args(argv)

def getCSVHeaders(prp:str)->list:
	if prop == "coverage-error-call":
		return Predictor.getHeaderList(Property.cover_error_call)
	elif prop == "coverage-branches":
		return Predictor.getHeaderList(Property.cover_branches)
	elif prop == "termination" :
		return Predictor.getHeaderList(Property.termination)
	elif prop == "no-overflow" :
		return Predictor.getHeaderList(Property.overflow)
	elif prop == "valid-memcleanup" :
		return Predictor.getHeaderList(Property.memcleanup)
	elif prop == "valid-memsafety":
		return Predictor.getHeaderList(Property.memsafety)
	elif prop == "unreach-call":
		return Predictor.getHeaderList(Property.unreach_call)
	else:
		sys.exit(f"unknown prop {prp}")

args = parse_args(sys.argv[1:])
prop = args.property
runNum = int(args.runNum)
lsStrategy = ['incr', 'kinduction', 'falsi', 'fixed']
lsSolver = ['boolector', 'z3']
lsEncoding = ['floatbv', 'fixedbv']

csvFile =f"./ml_runs_params/{prop}.csv"
if not os.path.isfile(csvFile):
	sys.exit(f"file does not exits:{csvFile}")
template_file,tool_file,template_str, timeout = dic[prop]

if not os.path.isfile(template_file):
	sys.exit(f"file does not exits:{template_file}")

isFound = False
lsParams = None
headers = getCSVHeaders(prop)
with open(csvFile, 'r') as csvfileptr:
	paramReader = csv.DictReader(csvfileptr, headers)
	next(paramReader, None)  # skip the headers
	for l in paramReader:
		num = int(l['Num'])
		if runNum == num:
			lsParams = l
			print(lsParams)
			isFound = True
if not isFound:
	sys.exit(f"runNum={runNum} is not found in : {csvFile}")

if prop == "coverage-error-call":
	#<option name="--seeds-num-fuzzer1-error-call">{lsParams[8]}</option>
	#<option name="--max-k-step">{lsParams[3]}</option>
	#<option name="--max-inductive-step">{lsParams[5]}</option>
	#	<option name="--fuzzer-error-call-2"/>
	#<option name="--fuzzer-error-call-2-time">300</option>
	#<option name="--unwind">{lsParams['unwind']}</option>
	
	params = f'''	<option name="--strategy">{lsStrategy[int(lsParams['strategy'])]}</option>
	<option name="--timeout">{timeout}</option>
	<option name="--ml">1</option>'''

	if lsParams['fuzz1Enabled'] == '1':
		params += '''
	<option name="--fuzzer-error-call-1"/>'''
	
	params += f'''
	<option name="--solver">{lsSolver[int(lsParams['solver'])]}</option>
	<option name="--encoding">{lsEncoding[int(lsParams['encoding'])]}</option>
	<option name="--fuzzer-error-call-1-time">{lsParams['fuzz1Time']}</option>
	<option name="--run-esbmc-twice-error-call"/>
	<option name="--esbmc-error-call-run-1-time">50</option>
	<option name="--handle-infinite-while-loop-error-call"/>
	<option name="--error-call-infinite-while-loop-increment-time">1</option>
	<option name="--error-call-selective-inputs-enable"/>
	<option name="--error-call-selective-inputs-increment-time">1</option>
	<option name="--k-step">{lsParams['kstep']}</option>
	<option name="--context-bound">{lsParams['contextBound']}</option>
	'''
elif prop == "coverage-branches":
	#,,fuzz1Enabled,fuzz1Time]]
	#<option name="--cover-branches-num-testcases-to-run-afl">{lsParams[9]}</option>
	#<option name="--max-k-step">{lsParams[3]}</option>
	#<option name="--max-inductive-step">{lsParams[5]}</option>
	params = f'''	<option name="--strategy">{lsStrategy[int(lsParams['strategy'])]}</option>
	<option name="--solver">{lsSolver[int(lsParams['solver'])]}</option>
	<option name="--encoding">{lsEncoding[int(lsParams['encoding'])]}</option>
	<option name="--timeout">{timeout}</option>
	<option name="--ml">1</option>'''
	if lsParams['fuzz1Enabled'] == '1':
		params += '''
	<option name="--fuzzer-cover-branches-1"/>'''
	params += f'''
	<option name="--fuzzer-cover-branches-1-time">{lsParams['fuzz1Time']}</option>
	<option name="--goal-tracer"/>
	<option name="--goal-sorting">3</option>
	<option name="--global-depth"/>
	<option name="--handle-infinite-while-loop-cover-branches"/>
	<option name="--cover-branches-infinite-while-loop-increment-time">1</option>
	<option name="--cover-branches-selective-inputs-enable"/>
	<option name="--cover-branches-selective-inputs-increment-time">1</option>
	<option name="--unwind">{lsParams['unwind']}</option>
	<option name="--k-step">{lsParams['kstep']}</option>
	<option name="--context-bound">{lsParams['contextBound']}</option>
	'''
#Property.termination: ['Num','strategy','contextBound','contextBoundStep', 'maxContextBoundStep','unnwind', 'kstep','maxKStep','maxInductiveStep'],
elif prop == "termination" :
	#	<option name="--context-bound">{lsParams['contextBound']}</option>
	params = f'''	<option name="--timeout">{timeout}</option>
	<option name="--ml">1</option>
	<option name="--solver">{lsSolver[int(lsParams['solver'])]}</option>
	<option name="--encoding">{lsEncoding[int(lsParams['encoding'])]}</option>
	<option name="--k-step">{lsParams['kStep']}</option>
	<option name="--unwind">{lsParams['unwind']}</option>
	'''
	if lsParams['addSymexValueSets'] == '1':
		params += '''
	<option name="--add-symex-value-sets"/>
	'''
elif prop == "unreach-call":
	params = f'''	<option name="--strategy">{lsStrategy[int(lsParams['strategy'])]}</option>
	<option name="--timeout">{timeout}</option>
	<option name="--ml">1</option>
	<option name="--solver">{lsSolver[int(lsParams['solver'])]}</option>
	<option name="--encoding">{lsEncoding[int(lsParams['encoding'])]}</option>
	<option name="--k-step">{lsParams['kStep']}</option>
	<option name="--context-bound">{lsParams['contextBound']}</option>
	<option name="--unwind">{lsParams['unwind']}</option>
	'''
	if lsParams['addSymexValueSets'] == '1':
		params += '''
	<option name="--add-symex-value-sets"/>
	'''
elif prop == "no-overflow" or prop == "valid-memcleanup" or prop == "valid-memsafety":
	#	<option name="--context-bound">{lsParams['contextBound']}</option>
	params = f'''	<option name="--strategy">{lsStrategy[int(lsParams['strategy'])]}</option>
	<option name="--timeout">{timeout}</option>
	<option name="--ml">1</option>
	<option name="--solver">{lsSolver[int(lsParams['solver'])]}</option>
	<option name="--encoding">{lsEncoding[int(lsParams['encoding'])]}</option>
	<option name="--k-step">{lsParams['kStep']}</option>
	<option name="--unwind">{lsParams['unwind']}</option>
	'''
	if lsParams['addSymexValueSets'] == '1':
		params += '''
	<option name="--add-symex-value-sets"/>
	'''
else:
	sys.exit(f"unknown prop {prop}")
print(params)
isReplaced = False
with open(template_file, 'r') as fTmpl:
	with open(tool_file, 'w', newline='') as fTool:
		for line in fTmpl:
			if isReplaced == False and line.startswith(template_str):
				line = line.replace(template_str,params)
				isReplaced = True
			fTool.write(line)
if not isReplaced:
	sys.exit('Error: Template is not replaced...')

