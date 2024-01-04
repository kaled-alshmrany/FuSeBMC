#!/usr/bin/env python3
import io, os,sys
import pickle

if __name__ == '__main__':
	sys.path.append('./../')
	import argparse

from fusebmc_util.util import Property
from fusebmc_util.goalsorting import GoalSorting
from fusebmc_util.consts import FuSeBMCParams

from fusebmc_ml.Feature import Feature,ModelType

from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPRegressor

class Predictor(object):
	def __init__(self, feature:Feature, prop:int):
		self.feature = feature
		self.prop = prop
		self.lsStrategy = ['incr', 'kinduction', 'falsi', 'fixed']
		self.lsSolver = ['boolector', 'z3']
		self.lsEncoding = ['floatbv', 'fixedbv']
	
	def getParamsCombinations(self,prop:int = None) ->list:
		lsAll = []
		if prop is None : prop = self.prop
		if self.prop == Property.cover_error_call :
			lsStrategy = [0, 1]
			lsSolver = [0, 1] #boolector, z3
			lsEncoding = [0, 1] #floatbv, fixedbv
			
			lsKStep = [1,2,3]
			lsContextBound = [2,4]
			#lsUnwind =[10,40,-1] #-1 defaulr
			
			lsFuzz1Enabled = [0,1]
			
			lsFuzz1Time = []
			lsFuzz1Time_enabled = [25,83,188] # 10%,33.3%, 75%
			lsFuzz1Time_disabled = [0]
			
			#lsSeedsNum_enabled = [1,3]
			
			for strategy in lsStrategy:
				for solver in lsSolver:
					for encoding in lsEncoding:
						for kstep in lsKStep:
							for contextBound in lsContextBound:
								for fuzz1Enabled in lsFuzz1Enabled:
									if fuzz1Enabled == 0 :
										lsFuzz1Time = lsFuzz1Time_disabled
									else:
										lsFuzz1Time = lsFuzz1Time_enabled
									for fuzz1Time in lsFuzz1Time:
										lsAll.append([strategy,solver,encoding,kstep,contextBound,fuzz1Enabled,fuzz1Time])
		elif self.prop == Property.cover_branches:
			lsStrategy = [0, 1] #'incr', 'kinduction'
			lsSolver = [0, 1] #boolector, z3
			lsEncoding = [0, 1] #floatbv, fixedbv
			
			lsKStep = [1,2,3]
			
			lsContextBound = [2,4]
			
			lsUnwind =[10,-1]#-1 defaul
			
			lsFuzz1Enabled = [0,1]
			
			lsFuzz1Time = []
			lsFuzz1Time_enabled = [25,83,188] # 10%,33.3%, 75%
			lsFuzz1Time_disabled = [0]
			
			#lsSeedsNum = [1,3]
			
			for strategy in lsStrategy:
				for solver in lsSolver:
					for encoding in lsEncoding:
						for kstep in lsKStep:
								for contextBound in lsContextBound:
										for unwind in lsUnwind:
											for fuzz1Enabled in lsFuzz1Enabled:
												if fuzz1Enabled == 0 :
													lsFuzz1Time = lsFuzz1Time_disabled
												else:
													lsFuzz1Time = lsFuzz1Time_enabled
												for fuzz1Time in lsFuzz1Time:
													lsAll.append([strategy,solver,encoding,kstep,contextBound,unwind,fuzz1Enabled,fuzz1Time])
		elif self.prop == Property.termination:
			lsSolver = [0, 1] #boolector, z3
			lsEncoding = [0, 1] #floatbv, fixedbv
			lsKStep = [1,2,3]
			#lsContextBound = [2,3,4,5]
			lsUnwind =[10,40,-1] #-1 defaulr
			lsAddSymexValueSets = [0,1]
			
			for solver in lsSolver:
				for encoding in lsEncoding:
					for kStep in lsKStep:
							for unwind in lsUnwind:
								for addSymexValueSets in lsAddSymexValueSets:
									lsAll.append([solver,encoding,kStep,unwind, addSymexValueSets])

		elif self.prop == Property.unreach_call:
			lsStrategy = [0, 1] #incr, k-induction
			lsSolver = [0, 1] #boolector, z3
			lsEncoding = [0, 1] #floatbv, fixedbv
			lsKStep = [1,2,3]
			#lsContextBound = [2,3,4,5]
			lsContextBound = [2,4]
			#lsContextBoundStep = [2,6]
			#lsMaxContextBound = [6,10,-1] #-1 unlimited #  --unlimited-context-bound
			#  --inductive-step                 check the inductive step
			
			lsUnwind =[10,40,-1]#-1 defaul
			lsAddSymexValueSets = [0,1]
			
			for strategy in lsStrategy:
				for solver in lsSolver:
					for encoding in lsEncoding:
						for kStep in lsKStep:
							for contextBound in lsContextBound:
								for unwind in lsUnwind:
									for addSymexValueSets in lsAddSymexValueSets:
										lsAll.append([strategy,solver,encoding,
													kStep, contextBound, unwind, addSymexValueSets
													])
					
		elif self.prop == Property.overflow or \
			self.prop == Property.memcleanup or \
			self.prop == Property.memsafety :
			
			lsStrategy = [0, 1] #incr, k-induction
			lsSolver = [0, 1] #boolector, z3
			lsEncoding = [0, 1] #floatbv, fixedbv
			lsKStep = [1,2,3]
			
			#lsContextBoundStep = [2,6]
			#lsMaxContextBound = [6,10,-1] #-1 unlimited #  --unlimited-context-bound
			#  --inductive-step                 check the inductive step
			
			lsUnwind =[10,40,-1]#-1 defaul
			lsAddSymexValueSets = [0,1]
			
			for strategy in lsStrategy:
				for solver in lsSolver:
					for encoding in lsEncoding:
						for kStep in lsKStep:
								for unwind in lsUnwind:
									for addSymexValueSets in lsAddSymexValueSets:
										lsAll.append([strategy,solver,encoding, kStep, unwind, addSymexValueSets])
					
		return lsAll


	@staticmethod
	def getHeaderList(prop:int)->list:
		lsHeader_unreach_call = ['Num','strategy','solver','encoding', 'kStep', 'contextBound', 'unwind', 'addSymexValueSets']
		lsHeader_termination = ['Num','solver','encoding', 'kStep', 'unwind', 'addSymexValueSets']
		lsHeader_memsafety = lsHeader_overflow = lsHeader_memcleanup = ['Num','strategy','solver','encoding', 
																	'kStep', 'unwind', 'addSymexValueSets']
		lsHeader_cover_error_call = ['Num', 'strategy','solver','encoding','kstep','contextBound',
									'fuzz1Enabled','fuzz1Time']
		lsHeader_cover_branches = ['Num', 'strategy','solver','encoding','kstep','contextBound','unwind','fuzz1Enabled','fuzz1Time']
		headerDict = {
			Property.unreach_call: lsHeader_unreach_call,
			Property.memsafety: lsHeader_memsafety,
			Property.overflow: lsHeader_overflow,
			Property.termination: lsHeader_termination,
			Property.memcleanup: lsHeader_memcleanup,
			Property.cover_branches: lsHeader_cover_branches,
			Property.cover_error_call: lsHeader_cover_error_call,
		}
		if prop not in headerDict:
			raise Exception(f"property {prop} is not in Dictionary.")
		return headerDict[prop]

	@staticmethod
	def getFilenameForProp(prop:int)->str:
		filesDict = {
			Property.unreach_call:'unreach-call',
			Property.memsafety: 'valid-memsafety',
			Property.overflow: 'no-overflow',
			Property.termination: 'termination',
			Property.memcleanup: 'valid-memcleanup',
			Property.cover_branches: 'coverage-branches',
			Property.cover_error_call: 'coverage-error-call',
		}
		if prop not in filesDict:
			raise Exception(f"property {prop} is not in Dictionary.")
		return filesDict[prop]
	def writeParamsToCSVFile(self, prop:int, paramsLst:list) -> None:
		import csv
		outDir = './../ml_runs_params/'
		if prop is None : prop = self.prop
		
		fname = Predictor.getFilenameForProp(prop)
		header = Predictor.getHeaderList(prop)
		outFileName = outDir+fname+'.csv'
		print('outFileName',outFileName, 'len =', len(paramsLst))
		with open(outFileName, 'w') as f:
			writer = csv.writer(f)
			writer.writerow(header)
			runNum = 1
			for row in paramsLst:
				writer.writerow([str(runNum).zfill(4),]+row)
				runNum += 1


	def printParamsAsXML(self, isClassification:bool,bestScoreClass:float):
		if FuSeBMCParams.SVCOMP24_PRE_RUN:
			return
		xmlstr=f"<mlparams><prop>{self.prop}</prop><strategy>{self.lsStrategy.index(FuSeBMCParams.strategy)}</strategy>"\
			f"<isClassification>{int(isClassification)}</isClassification>"\
			f"<bestScoreClass>{round(bestScoreClass,3)}</bestScoreClass>"\
			f"<k_step>{FuSeBMCParams.k_step}</k_step>"\
			f"<MAX_K_STEP>{FuSeBMCParams.MAX_K_STEP}</MAX_K_STEP>"\
			f"<contextBound>{FuSeBMCParams.contextBound}</contextBound>"
	
		if self.prop == Property.cover_branches:
			xmlstr += f"<maxInductiveStep>{FuSeBMCParams.maxInductiveStep}</maxInductiveStep>"\
			f"<unwind>{FuSeBMCParams.UNWIND}</unwind>"\
			f"<fuzz1Enabled>{int(FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED)}</fuzz1Enabled>"\
			f"<fuzz1time>{FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT}</fuzz1time>"\
			f"<seedsNum>{FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL}</seedsNum>"\
			f"<goalTracer>{int(FuSeBMCParams.FuSeBMC_GoalTracer_ENABLED)}</goalTracer>"\
			f"<globalDepth>{int(FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH)}</globalDepth>"\
			f"<goalSorting>{FuSeBMCParams.goalSorting}</goalSorting>"\
			f"<fuzz2Enabled>{int(FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED)}</fuzz2Enabled>"\
			f"<fuzz2time>{FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT_2}</fuzz2time>"\
			f"<whileLoopEnabled>{int(FuSeBMCParams.COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED)}</whileLoopEnabled>"\
			f"<whileLoopTime>{FuSeBMCParams.COVERBRANCHES_INFINITE_WHILE_TIME_INCREMENT}</whileLoopTime>"\
			f"<selectiveInputEnabled>{int(FuSeBMCParams.COVERBRANCHES_SELECTIVE_INPUTS_ENABLED)}</selectiveInputEnabled>"\
			f"<selectiveInputTime>{FuSeBMCParams.COVERBRANCHES_SELECTIVE_INPUTS_TIME_INCREMENT}</selectiveInputTime>"
		elif self.prop == Property.cover_error_call:
			xmlstr += f"<maxInductiveStep>{FuSeBMCParams.maxInductiveStep}</maxInductiveStep>"\
			f"<fuzz1Enabled>{int(FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_ENABLED)}</fuzz1Enabled>"\
			f"<fuzz1time>{FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT}</fuzz1time>"\
			f"<seedsNum>{FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_SEEDS_NUM}</seedsNum>"\
			f"<fuzz2Enabled>{int(FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED)}</fuzz2Enabled>"\
			f"<fuzz2time>{int(FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT_2)}</fuzz2time>"\
			f"<runtwice>{int(FuSeBMCParams.ERRORCALL_RUNTWICE_ENABLED)}</runtwice>"\
			f"<esbmcRun1time>{FuSeBMCParams.ERRORCALL_ESBMC_RUN1_TIMEOUT}</esbmcRun1time>"\
			f"<whileLoopEnabled>{int(FuSeBMCParams.ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED)}</whileLoopEnabled>"\
			f"<whileLoopTime>{FuSeBMCParams.ERRORCALL_INFINITE_WHILE_TIME_INCREMENT}</whileLoopTime>"\
			f"<selectiveInputEnabled>{int(FuSeBMCParams.ERRORCALL_SELECTIVE_INPUTS_ENABLED)}</selectiveInputEnabled>"\
			f"<selectiveInputTime>{int(FuSeBMCParams.ERRORCALL_SELECTIVE_INPUTS_TIME_INCREMENT)}</selectiveInputTime>"
		elif self.prop == Property.termination or \
			self.prop == Property.unreach_call or \
			self.prop == Property.overflow or \
			self.prop == Property.memcleanup or \
			self.prop == Property.memsafety :
			
			xmlstr += f"<maxInductiveStep>{FuSeBMCParams.maxInductiveStep}</maxInductiveStep>"\
			f"<UNWIND>{FuSeBMCParams.UNWIND}</UNWIND>"\
			f"<addSymexValueSets>{int(FuSeBMCParams.addSymexValueSets)}</addSymexValueSets>"
			
			#f"<contextBoundStep>{FuSeBMCParams.contextBoundStep}</contextBoundStep>"\
			#f"<maxContextBound>{FuSeBMCParams.maxContextBound}</maxContextBound>"\
		else:
			raise Exception(f"property {self.prop} is not supported.")
		xmlstr += '</mlparams>'
		xmlstr = xmlstr.replace('\r','').replace('\n','')
		sys.stderr.write(xmlstr)
		sys.stderr.flush()

	def pickle_loads(self, data):
		if sys.version_info[0] == 3:
			data = data.encode() if isinstance(data, str) else data
			content = pickle.loads(data, encoding="latin1")
		else:
			content = pickle.loads(data)
		return content

	def setFuSeBMCParamsFromBestVect(self, modelType:int, bestVect:list, bestScoreClass:float):
		isClassification = (modelType == ModelType.DTC or modelType == ModelType.SVC)
		if isClassification:
			print('bestClass', bestScoreClass)
		else:
			print('bestScore', bestScoreClass)
		headers = Predictor.getHeaderList(self.prop)[1:]
		print('headers',headers)
		paramsCount = len(headers)
		if bestVect is not None:
			bestParams = bestVect[-paramsCount:]
		print('paramsCount', paramsCount)
		print('bestVect', bestVect)
		print('bestParams', bestParams)
		if bestParams is None:
			print('cannot find the bestParams !!')
			return bestParams
		
		bParamsDic ={}
		for idx,col in enumerate(headers):
			bParamsDic[col] = bestParams[idx]
		print('bParamsDic',bParamsDic)
		del bestParams
		
		if self.prop == Property.cover_branches :
			#'strategy', 'solver', 'encoding', 'kstep', 'contextBound', 'unwind', 'fuzz1Enabled', 'fuzz1Time
			FuSeBMCParams.strategy = self.lsStrategy[bParamsDic['strategy']]
			FuSeBMCParams.solver = self.lsSolver[bParamsDic['solver']]
			FuSeBMCParams.encoding = self.lsEncoding[bParamsDic['encoding']]
			FuSeBMCParams.k_step = bParamsDic['kstep']
			#FuSeBMCParams.MAX_K_STEP = bParamsDic[2]
			#FuSeBMCParams.MAX_K_STEP = -1
			FuSeBMCParams.contextBound = bParamsDic['contextBound']
			#FuSeBMCParams.maxInductiveStep = bParamsDic[4]
			FuSeBMCParams.UNWIND = bParamsDic['unwind']
			
			fuzz1Enabled = (bParamsDic['fuzz1Enabled']==1)
			FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED= fuzz1Enabled
			fuzz1time = bParamsDic['fuzz1Time']
			#FuSeBMCParams.time_out_s
			#25,83,188 || # 10%,33.3%, 75%
			if fuzz1time == 0:
				FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT = 0
			elif fuzz1time == 25:
				FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT = int(FuSeBMCParams.time_out_s * (10/100))
			elif fuzz1time == 83:
				FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT = int(FuSeBMCParams.time_out_s * (33.3/100))
			elif fuzz1time == 188:
				FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT = int(FuSeBMCParams.time_out_s * (75/100))
			else:
				raise Exception(f"fuzz1time {fuzz1time} is not supported.")
				
			#FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_NUM_OF_GENERATED_TESTCASES_TO_RUN_AFL = bestParams[8]
			#Othe values
			#FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED = fuzz1Enabled
			#FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT_2 = FuSeBMCParams.time_out_s - 10
			
			FuSeBMCParams.FuSeBMC_GoalTracer_ENABLED = True
			FuSeBMCParams.goalSorting = GoalSorting.DEPTH_THEN_TYPE
			FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_GLOBAL_DEPTH = True
			
			FuSeBMCParams.COVERBRANCHES_HANDLE_INFINITE_WHILE_LOOP_ENABLED = True
			FuSeBMCParams.COVERBRANCHES_INFINITE_WHILE_TIME_INCREMENT = 1
			FuSeBMCParams.COVERBRANCHES_SELECTIVE_INPUTS_ENABLED = True
			FuSeBMCParams.COVERBRANCHES_SELECTIVE_INPUTS_TIME_INCREMENT = 1
			
			if FuSeBMCParams.SVCOMP24_PRE_RUN:
				if FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED == False:
					FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_ENABLED = True
					FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT = 3
				FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED = True
				FuSeBMCParams.FuSeBMCFuzzerLib_COVERBRANCHES_TIMEOUT_2 = 900

		elif self.prop == Property.cover_error_call :
			#'strategy', 'solver', 'encoding', 'kstep', 'contextBound', 'fuzz1Enabled', 'fuzz1Time'
			FuSeBMCParams.strategy = self.lsStrategy[bParamsDic['strategy']]
			FuSeBMCParams.solver = self.lsSolver[bParamsDic['solver']]
			FuSeBMCParams.encoding = self.lsEncoding[bParamsDic['encoding']]
			FuSeBMCParams.k_step = bParamsDic['kstep']
			#FuSeBMCParams.MAX_K_STEP = bParamsDic[2]
			#FuSeBMCParams.MAX_K_STEP = -1
			FuSeBMCParams.contextBound = bParamsDic['contextBound']
			#FuSeBMCParams.maxInductiveStep = bParamsDic[4]
			fuzz1Enabled = (bParamsDic['fuzz1Enabled']==1)
			FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_ENABLED = fuzz1Enabled
			fuzz1time = bParamsDic['fuzz1Time']
			#FuSeBMCParams.time_out_s
			#25,83,188 || # 10%,33.3%, 75%
			if fuzz1time == 0:
				FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT = 0
			elif fuzz1time == 25:
				FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT = int(FuSeBMCParams.time_out_s * (10/100))
			elif fuzz1time == 83:
				FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT = int(FuSeBMCParams.time_out_s * (33.3/100))
			elif fuzz1time == 188:
				FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT = int(FuSeBMCParams.time_out_s * (75/100))
			else:
				raise Exception(f"fuzz1time {fuzz1time} is not supported.")
				
			#FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_SEEDGEN_SEEDS_NUM = bParamsDic[7]
			#Othe values
			#FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED = fuzz1Enabled
			#FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT_2 = FuSeBMCParams.time_out_s - 50
			FuSeBMCParams.ERRORCALL_RUNTWICE_ENABLED = True
			FuSeBMCParams.ERRORCALL_ESBMC_RUN1_TIMEOUT = 50
			FuSeBMCParams.ERRORCALL_HANDLE_INFINITE_WHILE_LOOP_ENABLED = True
			FuSeBMCParams.ERRORCALL_INFINITE_WHILE_TIME_INCREMENT = 1
			FuSeBMCParams.ERRORCALL_SELECTIVE_INPUTS_ENABLED = True
			FuSeBMCParams.ERRORCALL_SELECTIVE_INPUTS_TIME_INCREMENT = 1
			
			if FuSeBMCParams.SVCOMP24_PRE_RUN:
				if FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_ENABLED == False:
					FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_ENABLED = True
					FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT = 3
				FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED = True
				FuSeBMCParams.FuSeBMCFuzzerLib_ERRORCALL_TIMEOUT_2 = 900
			#sys.exit(0)
		elif self.prop == Property.termination:
			FuSeBMCParams.solver = self.lsSolver[bParamsDic['solver']]
			FuSeBMCParams.encoding = self.lsEncoding[bParamsDic['encoding']]
			FuSeBMCParams.k_step = bParamsDic['kStep']
			FuSeBMCParams.UNWIND = bParamsDic['unwind']
			FuSeBMCParams.addSymexValueSets = (bParamsDic['addSymexValueSets'] == 1)
			
		elif self.prop == Property.unreach_call:
			FuSeBMCParams.strategy = self.lsStrategy[bParamsDic['strategy']]
			FuSeBMCParams.solver = self.lsSolver[bParamsDic['solver']]
			FuSeBMCParams.encoding = self.lsEncoding[bParamsDic['encoding']]
			FuSeBMCParams.k_step = bParamsDic['kStep']
			FuSeBMCParams.contextBound = bParamsDic['contextBound']
			FuSeBMCParams.UNWIND = bParamsDic['unwind']
			FuSeBMCParams.addSymexValueSets = (bParamsDic['addSymexValueSets'] == 1)
			
		elif self.prop == Property.overflow or \
			self.prop == Property.memcleanup or \
			self.prop == Property.memsafety:
			
			FuSeBMCParams.strategy = self.lsStrategy[bParamsDic['strategy']]
			FuSeBMCParams.solver = self.lsSolver[bParamsDic['solver']]
			FuSeBMCParams.encoding = self.lsEncoding[bParamsDic['encoding']]
			FuSeBMCParams.k_step = bParamsDic['kStep']
			#FuSeBMCParams.MAX_K_STEP = -1
			#FuSeBMCParams.contextBound = bestParams[1]
			#FuSeBMCParams.contextBoundStep = bestParams[2]
			#FuSeBMCParams.maxContextBound = bestParams[3]
			
			FuSeBMCParams.UNWIND = bParamsDic['unwind']
			#FuSeBMCParams.maxInductiveStep = bestParams[5]
			FuSeBMCParams.addSymexValueSets = (bParamsDic['addSymexValueSets'] == 1)
		
		else:
			raise Exception(f"property {self.prop} is not supported in ML.")
		#bestScoreClass = bestClass if isClassification else bestScore
		self.printParamsAsXML(isClassification,bestScoreClass)

	def predictParams(self, modelType:int, isMultModel = False, pAllParams:list = None):
		
		dicDirName = {
			ModelType.DTC :'dtc',
			ModelType.SVC :'svc',
			ModelType.NRR :'nnr',
			}
		if modelType in dicDirName:
			print(f"Prediction using {dicDirName[modelType]}")
	
		if modelType == ModelType.MULTI_MODEL:
			print('We are in multimodel')
			bestDtc , bestDtcScore = self.predictParams(ModelType.DTC, True, None)
			bestDtcLen = len(bestDtc)
			print(f"DTC best params = {bestDtcLen}")
			if bestDtcLen > 1:
				bestSvc , bestSvcScore = self.predictParams(ModelType.SVC, True, bestDtc)
				bestSvcLen = len(bestSvc)
				print(f"SVC best params = {bestSvcLen}")
				if bestSvcLen > 1 :
					return self.predictParams(ModelType.NRR, False, bestSvc)
				else:
					self.setFuSeBMCParamsFromBestVect(ModelType.SVC, bestSvc[0], bestSvcScore[0])
					return #must return 
			else:
				self.setFuSeBMCParamsFromBestVect(ModelType.DTC, bestDtc[0], bestDtcScore[0])
				return #must return 
			
			
		
		modelFName = Predictor.getFilenameForProp(self.prop)
		modelFullFile = f"./ml_models/{dicDirName[modelType]}/{modelFName}.sav"
		if not os.path.isfile(modelFullFile):
			raise Exception(f"model {modelFullFile} not found.")
		try:
			model = pickle.load(open(modelFullFile, 'rb'), encoding='latin1')
		except Exception as ex:
			exit(ex)
		bestClass = 1000
		bestScore = float('-inf')
		bestVect = None
		allV = []
		if pAllParams is None:
			allParams = self.getParamsCombinations()
			for vctPara in allParams:
				vect = self.feature.toList() + vctPara
				allV.append(vect)
		else :
			#allParams = pAllParams
			allV = pAllParams
		
		isClassification = (modelType == ModelType.DTC or modelType == ModelType.SVC)
		
		if modelType == ModelType.DTC:
			classifier:DecisionTreeClassifier = model
			predClasses_Scores = classifier.predict(allV)
		elif modelType == ModelType.SVC:
			classifier:SVC = model
			predClasses_Scores = classifier.predict(allV)
		elif modelType == ModelType.NRR:
			regressor:MLPRegressor = model
			predClasses_Scores = regressor.predict(allV)
		else:
			raise Exception(f"modelType {modelType} is not supported.")
		print('predClasses_Scores',predClasses_Scores)
		if isMultModel :
			if isClassification:
				toRetBestVect = []
				toRetBestScore = []
				minClass = min(predClasses_Scores)
				for l_feature_params ,l_class in zip(allV , predClasses_Scores):
					if l_class == minClass :
						toRetBestVect.append(l_feature_params)
						toRetBestScore.append(l_class)
				return toRetBestVect , toRetBestScore

		for l_feature_params ,l_class_score in zip(allV , predClasses_Scores):
			if isClassification:
				isBetter = (l_class_score < bestClass)
				if isBetter: bestClass = l_class_score
			else : #regression
				isBetter = (l_class_score > bestScore)
				if isBetter: bestScore = l_class_score
			if isBetter: bestVect = l_feature_params
		
		bestScoreClass = bestClass if isClassification else bestScore
		self.setFuSeBMCParamsFromBestVect(modelType, bestVect, bestScoreClass)
		
		return bestVect , bestScoreClass

def predictorMain(prop:int):
	
	#predictor = Predictor(Feature(),Property.cover_error_call)
	predictor = Predictor(Feature(),prop)
	lsAll = predictor.getParamsCombinations(None)
	for l in lsAll:
		print(l)
	print('len =', len(lsAll))
	predictor.writeParamsToCSVFile(None,lsAll)
	
	
def main():
	lsProp = ["coverage-error-call", "coverage-branches", "no-overflow","termination",
			"valid-memcleanup", "valid-memsafety", "unreach-call"]
	dicProp = {
			'unreach-call': Property.unreach_call,
			'valid-memsafety': Property.memsafety,
			'no-overflow': Property.overflow,
			'termination': Property.termination,
			'valid-memcleanup': Property.memcleanup,
			'coverage-branches': Property.cover_branches,
			'coverage-error-call': Property.cover_error_call,
			#'': Property.no_data_race,
			}
	parser = argparse.ArgumentParser()
	parser.add_argument('-p',"--property",
		dest ='property',
		#action="store_true",
		help="the property",
		choices= lsProp + ["all","testcomp","svcomp"],
		type=str,
		required=True,
	)
	args = parser.parse_args(sys.argv[1:])
	prop_str = args.property
	if prop_str == 'all':
		lsPropToWorkOn = [dicProp[x] for x in lsProp]
	elif prop_str == 'testcomp':
		lsPropToWorkOn = [Property.cover_error_call, Property.cover_branches]
	elif prop_str == 'svcomp':
		lsPropToWorkOn = [Property.overflow, Property.termination,Property.memcleanup, 
						Property.memsafety, Property.unreach_call]
	else:
		lsPropToWorkOn = [dicProp[prop_str]]
	for prp in lsPropToWorkOn:
		predictorMain(prp)
	
	print(f"len = {len(lsPropToWorkOn)}")
	print('Done !!')

if __name__ == '__main__':
	main()



