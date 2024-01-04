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

from fusebmc_ml.Feature import Feature
from fusebmc_util.util import getArgs
from fusebmc_util.customformatter import CustomFormatter

hideFuSeBMCFeatures = False
featuresFilename : str = None
resultTimeLimit : float = 0.0
runProperty = None

logger = CustomFormatter.getLogger(__name__, logging.DEBUG)
logger.setLevel(logging.DEBUG)

class RunProperty:
	ErrorCall = 'coverage-error-call'
	CoverBranches = 'coverage-branches'
	UnreachCall = 'unreach-call'
	NoOverflow = 'no-overflow'
	Termination = 'termination'
	ValidMemCleanUp = 'valid-memcleanup'
	ValidMemSafety = 'valid-memsafety'

def parse_args(argv):
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"resultsXML",
		metavar="results-xml",
		help="XML-file containing the verification results.",
	)

	parser.add_argument(
		"--hide-fusebmc-features",
		#action="store_true",
		help="Hide the columns that contain FuSeBMC features.",
		choices=['yes','no'],
		default=None,
	)
	#parser.add_argument(
	#	"-o","--outputpath",
	#	metavar="OUT_PATH",
	#	help="Directory in which the generated output files will be placed.",
	#)
	
	parser.add_argument(
		"--csvFeaturesFile",
		metavar="CSV_FEATURES_FILE",
		help="CSV output file, FuSeBMC features will be exported in.",
	)
	return parser.parse_args(argv)

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

def setScoreAndClass(feature:Feature ,runProperty:str, restTimeRatio:float )->None:
	global resultTimeLimit
	
	if runProperty == RunProperty.ErrorCall:
		if feature.origScore == 0 :
			feature.ourScore = 0
			feature.ClassifyClass = 5
		elif feature.origScore == 1 : # score from 50 to 100
			feature.ourScore = 50 + (50 * restTimeRatio)
			
			if restTimeRatio >= 0.8 :
				feature.ClassifyClass = 0
			elif restTimeRatio >= 0.6 :
				feature.ClassifyClass = 1
			elif restTimeRatio >= 0.4 :
				feature.ClassifyClass = 2
			elif restTimeRatio >= 0.2 :
				feature.ClassifyClass = 3
			elif restTimeRatio >= 0.0 :
				feature.ClassifyClass = 4
			
		else:
			raise Exception(f"invalid score {feature.origScore} for ErrorCall")
	
	elif runProperty == RunProperty.CoverBranches: # step=0.17
		feature.ourScore = feature.origScore * 100
		if feature.ourScore == 100:
			feature.ourScore += restTimeRatio
		
		if feature.origScore >= 0.85 : feature.ClassifyClass = 0
		elif feature.origScore >= 0.68 : feature.ClassifyClass = 1
		elif feature.origScore >= 0.51 : feature.ClassifyClass = 2
		elif feature.origScore >= 0.34 : feature.ClassifyClass = 3
		elif feature.origScore >= 0.17 : feature.ClassifyClass = 4
		elif feature.origScore >= 0.0 : feature.ClassifyClass = 5
	
	elif runProperty == RunProperty.UnreachCall or \
		 runProperty == RunProperty.NoOverflow or \
		 runProperty == RunProperty.Termination or \
		 runProperty == RunProperty.ValidMemCleanUp or \
		 runProperty == RunProperty.ValidMemSafety:
		if feature.origScore == 'correct': # score from 75 to 100 ; classes = [0,1,2]
			feature.ourScore = 75 + (restTimeRatio * 25) # timeScore from 0 to 25
			if feature.ourScore >= 92:
				feature.ClassifyClass = 0
			elif feature.ourScore >= 84:
				feature.ClassifyClass = 1
			elif feature.ourScore >= 75:
				feature.ClassifyClass = 2
		
		elif feature.origScore == 'unknown' or \
			feature.origScore == 'missing':# score from 50 to 65; classes = [3]
			feature.ourScore = 50 + (restTimeRatio * 15) # timeScore from 0 to 15
			feature.ClassifyClass = 3
		
		elif feature.origScore == 'error': # score from 25 to 40; classes = [4]
			feature.ourScore = 25 + (restTimeRatio * 15) # timeScore from 0 to 15
			feature.ClassifyClass = 4
		
		elif feature.origScore == 'wrong': # score from 0 to 15; classes = [5]
			feature.ourScore = 0 + (restTimeRatio * 15) # timeScore from 0 to 15
			feature.ClassifyClass = 5
		else:
			raise Exception(f"feature.ourScore {feature.ourScore} is not supported.")
		#['correct', 'error', 'unknown','wrong']
	else:
		raise Exception(f"runProperty {runProperty} is not supported.")
def main(argv=None):
	global hideFuSeBMCFeatures, featuresFilename
	global resultTimeLimit
	
	runProperty = None
	lstParams, lstParamCols = None, None
	dStrategy = {'incr':0,'kinduction':1,'falsi':2, 'fixed':3}
	dSolver ={'boolector': 0, 'z3':1}
	dEncoding ={'floatbv':0, 'fixedbv':1}
	
	lstFeature = []
	
	if argv is None:
		argv = sys.argv[1:]
	args = parse_args(argv)
	result_file = args.resultsXML
	lsResult_file = glob.glob(result_file)
	if len(lsResult_file) != 1:
		print(lsResult_file)
		sys.exit(f"resultsXML must be 1 file, not {len(lsResult_file)} files.")
	result_file = lsResult_file[0]
	#out_dir = args.outputpath
	hideFuSeBMCFeatures = args.hide_fusebmc_features
	featuresFilename = args.csvFeaturesFile
	print('hideFuSeBMCFeatures:', hideFuSeBMCFeatures)
	if hideFuSeBMCFeatures is None and featuresFilename is None:
		print(f"No action to do; please see:{sys.argv[0]} -h")
		parse_args(sys.argv[0:1] + ['-h'])
		sys.exit(-1)


	if not os.path.exists(result_file) or not os.path.isfile(result_file):
		sys.exit(f"File {result_file} does not exist.")
	
	tree = ET.parse(result_file)
	result_xml = tree.getroot()
	if hideFuSeBMCFeatures == 'yes':
		elemCols = result_xml.find('columns')
		for col in elemCols.findall('column'):
			title = col.get('title')
			if title is not None and title.startswith('FuseBMC_'):
				elemCols.remove(col)
				del col
	elif hideFuSeBMCFeatures == 'no':
		fCols = Feature.getColumnsHeader()
		elemCols = result_xml.find('columns')
		for fCol in fCols:
			xCol = 'FuseBMC_' + fCol
			findCol = elemCols.find('column[@title="'+xCol+'"]')
			if findCol is None:
				newCol = ET.Element("column", title=xCol)
				elemCols.append(newCol)
	
	if featuresFilename is not None:
		resultOptions = shlex.split(result_xml.get('options'))
		resultArgs = getArgs(resultOptions)
		
		timelimit = result_xml.get('timelimit')
		resultTimeLimit = float(''.join([x for x in timelimit if x.isdigit() or x in ['.']]))
		print('resultTimeLimit:', resultTimeLimit)
	
	feature : Feature = None
	for run in result_xml.findall("run"):
		if hideFuSeBMCFeatures =='yes' or hideFuSeBMCFeatures =='no' or featuresFilename is not None:
			feature = Feature()
			for col in run.findall('column'):
				try:
					title = col.get('title')
					if title is not None and title.startswith('FuseBMC_'):
						if hideFuSeBMCFeatures == 'yes':
							col.set('hidden', 'true')
						elif hideFuSeBMCFeatures == 'no':
							col.set('hidden', 'false')
						
						if featuresFilename is not None:
							feature.parseFromBenchExecXMLColumn(col)
							#feature.printOut()
				except Exception as ex:
					print(ex)
		if featuresFilename is not None:
			feature.name = run.get('name',None)
			prop = run.get('properties',None)
			if prop is None: raise Exception('run has no properties attribute')
			if runProperty is None:
				runProperty = prop
			elif runProperty != prop:
				raise Exception('We have more than property: '+ runProperty + ' and ' + prop)
			
			#cpuTime_s = run.find('column[@title="cputime"]').get("value")
			#wallTime_s = run.find('column[@title="walltime"]').get("value")
			
			try:
				cpuTime_s = run.find('column[@title="cputime"]').get("value")
			except Exception as ex:
				logger.warning(f"cannot extract cpuTime_s from {feature.name}")
				cpuTime_s = '0'
			
			
			try:
				wallTime_s = run.find('column[@title="walltime"]').get("value")
			except Exception as ex:
				logger.warning(f"cannot extract wallTime_s from {feature.name}")
				wallTime_s = '0'
				
			
			
			cpuTime = float(''.join([x for x in cpuTime_s if x.isdigit() or x in ['.', '-']]))
			wallTime = float(''.join([x for x in wallTime_s if x.isdigit() or x in ['.', '-']]))
			feature.wallCpuTime = cpuTime if cpuTime > wallTime else wallTime
			
			restTime = resultTimeLimit - feature.wallCpuTime
			if restTime <= 5: restTime = 0
			restTimeRatio = (restTime / resultTimeLimit) # ex: restTimeRatio = 30% of time
			
			if runProperty == RunProperty.ErrorCall or runProperty == RunProperty.CoverBranches:
				try:
					feature.origScore = float(run.find('column[@title="score"]').get("value"))
				except AttributeError:
					feature.origScore = 0
			elif runProperty == RunProperty.UnreachCall or \
				 runProperty == RunProperty.NoOverflow or \
				 runProperty == RunProperty.Termination or \
				 runProperty == RunProperty.ValidMemCleanUp or \
				 runProperty == RunProperty.ValidMemSafety:
				try:
					feature.origScore = run.find('column[@title="category"]').get("value")
				except AttributeError as ae:
					feature.origScore = 'unknown'
			else:
				raise Exception(f"runProperty {runProperty} is not supported.")
			
			setScoreAndClass(feature, runProperty, restTimeRatio)
			lstFeature.append(feature)
		#END if featuresFilename is not None:
	#END FOR
	if featuresFilename is not None:
		print('runProperty', runProperty)
		if runProperty == RunProperty.ErrorCall:
			#'strategy','','','','contextBound','unwind', 'fuzz1Enabled','fuzz1Time'
			lstParams = [
					dStrategy[resultArgs.strategy],
					dSolver[resultArgs.solver],
					dEncoding[resultArgs.encoding],
					resultArgs.k_step,
					#resultArgs.MAX_K_STEP,
					resultArgs.contextBound,
					#resultArgs.maxInductiveStep,
					1 if resultArgs.FuSeBMCFuzzerLib_ERRORCALL_ENABLED else 0,
					resultArgs.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT,
					#resultArgs.FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_SEEDS_NUM,
					
					#1 if resultArgs.FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED else 0,
					#resultArgs.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT_2,
					#resultArgs.ERRORCALL_ESBMC_RUN1_TIMEOUT,
					
					#1 if resultArgs.ERRORCALL_RUNTWICE_ENABLED else 0,
					#1 if resultArgs.ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED else 0,
					#resultArgs.ERRORCALL_INFINITE_WHILE_TIME_INCREMENT,
					#1 if resultArgs.ERRORCALL_SELECTIVE_INPUTS_ENABLED else 0,
					#resultArgs.ERRORCALL_SELECTIVE_INPUTS_TIME_INCREMENT,
					
					
					]
			lstParamCols = [
					'strategy',
					'solver',
					'encoding',
					'k_step',
					#'MAX_K_STEP',
					'contextBound',
					#'maxInductiveStep',
					'FuSeBMCFuzzerLib_ERRORCALL_ENABLED',
					'FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT',
					#'FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_SEEDS_NUM',
					
					#'FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED',
					#'FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT_2',
					#'ERRORCALL_ESBMC_RUN1_TIMEOUT',
					#'ERRORCALL_RUNTWICE_ENABLED',
					#'ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED',
					#'ERRORCALL_INFINITE_WHILE_TIME_INCREMENT',
					#'ERRORCALL_SELECTIVE_INPUTS_ENABLED',
					#'ERRORCALL_SELECTIVE_INPUTS_TIME_INCREMENT',
					
					'origScore',
					'wallCpuTime',
					'resultTimeLimit',
					'ourScore',
					'ClassifyClass',
						]
		elif runProperty == RunProperty.CoverBranches:
			
			lstParams = [
					dStrategy[resultArgs.strategy],
					dSolver[resultArgs.solver],
					dEncoding[resultArgs.encoding],
					resultArgs.k_step,
					#resultArgs.MAX_K_STEP,
					resultArgs.contextBound,
					#resultArgs.maxInductiveStep,
					resultArgs.UNWIND,
					1 if resultArgs.FuzzerCoverBranches1 else 0,
					resultArgs.FuzzerCoverBranches1Time,
					#resultArgs.FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL,
					#
					#1 if resultArgs.FuzzerCoverBranches1 else 0,
					#resultArgs.FuzzerCoverBranches1Time,
					#1 if resultArgs.FuzzerCoverBranches2 else 0,
					#resultArgs.FuzzerCoverBranches2Time,
					#1 if resultArgs.GoalTracer else 0,
					#resultArgs.GoalSorting,
					#1 if resultArgs.GlobalDepth else 0,
					#resultArgs.FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL,
					#1 if resultArgs.COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED else 0,
					#resultArgs.COVERBRANCHES_INFINITE_WHILE_TIME_INCREMENT,
					#1 if resultArgs.COVERBRANCHES_SELECTIVE_INPUTS_ENABLED else 0,
					#resultArgs.COVERBRANCHES_SELECTIVE_INPUTS_TIME_INCREMENT
					]
			#strategy,solver,encoding,kstep,contextBound,unwind,fuzz1Enabled,fuzz1Time]
			lstParamCols = [
					'strategy',
					'solver',
					'encoding',
					'k_step',
					#'MAX_K_STEP',
					'contextBound',
					#'maxInductiveStep',
					'unwind',
					'FuzzerCoverBranches1',
					'FuzzerCoverBranches1Time',
					
					#'FuzzerCoverBranches2',
					#'FuzzerCoverBranches2Time',
					#'GoalTracer',
					#'GoalSorting',
					#'GlobalDepth',
					#'FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL',
					#'COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED',
					#'COVERBRANCHES_INFINITE_WHILE_TIME_INCREMENT',
					#'COVERBRANCHES_SELECTIVE_INPUTS_ENABLED',
					#'COVERBRANCHES_SELECTIVE_INPUTS_TIME_INCREMENT',
					'origScore',
					'wallCpuTime',
					'resultTimeLimit',
					'ourScore',
					'ClassifyClass',
					]
		elif runProperty == RunProperty.Termination :
			lstParams = [
					#dStrategy[resultArgs.strategy],
					dSolver[resultArgs.solver],
					dEncoding[resultArgs.encoding],
					
					resultArgs.k_step,
					#resultArgs.MAX_K_STEP,
					#resultArgs.contextBound,
					#resultArgs.contextBoundStep,
					#resultArgs.maxContextBound,
					resultArgs.UNWIND,
					#resultArgs.maxInductiveStep,
					1 if resultArgs.addSymexValueSets else 0,
					]
			lstParamCols = [
					#'strategy',
					'solver',
					'encoding',
					'k_step',
					#'MAX_K_STEP',
					#'contextBound',
					#'contextBoundStep',
					#'maxContextBound',
					'unwind',
					#'maxInductiveStep',
					'addSymexValueSets',
					'origScore',
					'wallCpuTime',
					'resultTimeLimit',
					'ourScore',
					'ClassifyClass',
					]
		elif runProperty == RunProperty.UnreachCall:
			lstParams = [
					dStrategy[resultArgs.strategy],
					dSolver[resultArgs.solver],
					dEncoding[resultArgs.encoding],
					
					resultArgs.k_step,
					#resultArgs.MAX_K_STEP,
					resultArgs.contextBound,
					#resultArgs.contextBoundStep,
					#resultArgs.maxContextBound,
					resultArgs.UNWIND,
					#resultArgs.maxInductiveStep,
					1 if resultArgs.addSymexValueSets else 0,
					]
			lstParamCols = [
					'strategy',
					'solver',
					'encoding',
					'k_step',
					#'MAX_K_STEP',
					'contextBound',
					#'contextBoundStep',
					#'maxContextBound',
					'unwind',
					#'maxInductiveStep',
					'addSymexValueSets',
					'origScore',
					'wallCpuTime',
					'resultTimeLimit',
					'ourScore',
					'ClassifyClass',
					]
		elif  runProperty == RunProperty.NoOverflow or \
			 runProperty == RunProperty.ValidMemCleanUp or \
			 runProperty == RunProperty.ValidMemSafety:
			lstParams = [
					dStrategy[resultArgs.strategy],
					dSolver[resultArgs.solver],
					dEncoding[resultArgs.encoding],
					
					resultArgs.k_step,
					#resultArgs.MAX_K_STEP,
					#resultArgs.contextBound,
					#resultArgs.contextBoundStep,
					#resultArgs.maxContextBound,
					resultArgs.UNWIND,
					#resultArgs.maxInductiveStep,
					1 if resultArgs.addSymexValueSets else 0,
					]
			lstParamCols = [
					'strategy',
					'solver',
					'encoding',
					'k_step',
					#'MAX_K_STEP',
					#'contextBound',
					#'contextBoundStep',
					#'maxContextBound',
					'unwind',
					#'maxInductiveStep',
					'addSymexValueSets',
					'origScore',
					'wallCpuTime',
					'resultTimeLimit',
					'ourScore',
					'ClassifyClass',
					]
		else:
			sys.exit(f"unsupported runProperty {runProperty}")
	
		print('lstParams', lstParams)
		lstCols = ['name']+Feature.getColumnsHeader()
		lstCols.extend(lstParamCols)
		lstRows = [lstCols]
		lstFeature.sort(key=lambda f: (-1 * f.ourScore,f.wallCpuTime))
		for f in lstFeature:
			row = [f.name]+f.toList()
			row.extend(lstParams)
			row.extend([f.origScore,f.wallCpuTime, resultTimeLimit, f.ourScore,f.ClassifyClass])
			lstRows.append(row)
		
		with open(featuresFilename, 'w', newline='') as file:
			writer = csv.writer(file)
			writer.writerows(lstRows)
		print('len(lstRows) =', len(lstRows))
		#print('lstFeature', lstFeature)
	#END if featuresFilename is not None:
	if hideFuSeBMCFeatures =='yes' or hideFuSeBMCFeatures =='no':
		with io.TextIOWrapper(open(result_file, "wb"), encoding="utf-8") as xml_file:
			xml_file.write(
				xml_to_string(result_xml).replace("	\n", "").replace("  \n", "")
			)
		print(f"file: '{result_file}' is modified.")

	
if __name__ == "__main__":
	sys.exit(main())