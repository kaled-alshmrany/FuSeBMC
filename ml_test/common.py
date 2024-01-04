import os
import sys
import io
import argparse
import glob
import datetime

import pandas as pd
import sklearn
from sklearn.model_selection import GridSearchCV

'''
_c : classification
_r: regression
'''
lsProp = ["coverage-error-call","coverage-branches","no-overflow", 
		"termination", "valid-memcleanup","valid-memsafety", "unreach-call"]

#trainDataDir = './../dataset/train/'
#testDataDir = './../dataset/test/'
datasetDir = './../dataset/'

def checkDataDirs(prop:str)->None:
	trainDataDir = f"{datasetDir}/{prop}/train/"
	testDataDir = f"{datasetDir}/{prop}/test/"
	if not os.path.isdir(trainDataDir):
		sys.exit(f"dir does not exist:{trainDataDir}")
	if not os.path.isdir(testDataDir):
		sys.exit(f"dir does not exist:{testDataDir}")

#def getFilesList(pDir:str,prop:str)->list:
#	return glob.glob(f"{pDir}/{prop}_*.csv")

def getTrainData_c(prop:str):
	trainDataDir = f"{datasetDir}/{prop}/train/"
	files = glob.glob(f"{trainDataDir}/{prop}_*.csv")
	print('TrainData files:')
	for f in sorted(files): print(f)
	data = pd.concat(map(pd.read_csv, files), ignore_index=True)
	#data = pd.read_csv('./features_train.csv')
	X_train = data.drop(columns=['name','origScore', 'wallCpuTime', 'resultTimeLimit','ourScore', 'ClassifyClass'])
	Y_train = data['ClassifyClass']
	return X_train , Y_train

def getTestData_c(prop:str):
	testDataDir = f"{datasetDir}/{prop}/test/"
	files = glob.glob(f"{testDataDir}/{prop}_*.csv")
	print('TestData files:')
	for f in sorted(files): print(f)
	data = pd.concat(map(pd.read_csv, files), ignore_index=True)
	#data = pd.read_csv('./features_test.csv')
	X_test = data.drop(columns=['name','origScore', 'wallCpuTime', 'resultTimeLimit','ourScore', 'ClassifyClass'])
	Y_test = data['ClassifyClass']
	return X_test , Y_test

def getTrainData_r(prop:str):
	trainDataDir = f"{datasetDir}/{prop}/train/"
	files = glob.glob(f"{trainDataDir}/{prop}_*.csv")
	print('TrainData files:')
	for f in sorted(files): print(f)
	data = pd.concat(map(pd.read_csv, files), ignore_index=True)
	X_train = data.drop(columns=['name','origScore', 'wallCpuTime', 'resultTimeLimit','ourScore', 'ClassifyClass'])
	Y_train = data['ourScore']
	return X_train , Y_train

def getTestData_r(prop:str):
	testDataDir = f"{datasetDir}/{prop}/test/"
	files = glob.glob(f"{testDataDir}/{prop}_*.csv")
	print('TestData files:')
	for f in sorted(files): print(f)
	data = pd.concat(map(pd.read_csv, files), ignore_index=True)
	X_test = data.drop(columns=['name','origScore', 'wallCpuTime', 'resultTimeLimit','ourScore', 'ClassifyClass'])
	Y_test = data['ourScore']
	return X_test , Y_test

def writeBestEstimatorInFile(gridSearchModel: GridSearchCV,filename:str):
	append_write = 'w'
	if os.path.exists(filename):
		append_write = 'a'
	with open(filename,append_write) as f:
		f.write(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y\n"))
		f.write(f"sklearn.version={sklearn.__version__}\n")
		f.write('Best Score is :\n')
		f.write(str(gridSearchModel.best_score_))
		f.write('\n')
		f.write('Best Parameters are :\n')
		f.write(str(gridSearchModel.best_params_))
		f.write('\n')
		f.write('Best Estimator is :\n')
		f.write(str(gridSearchModel.best_estimator_))
		f.write('\n------------------------------\n')
	print('Best Estimator is written in:',os.path.abspath(filename))

def parse_args(argv):
	def check_positive(value: int)-> int:
		ivalue = int(value)
		if ivalue <= 0:
			raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
		return ivalue
	
	parser = argparse.ArgumentParser()
	parser.add_argument('-p',
		"--property",
		dest ='property',
		#action="store_true",
		help="the property",
		choices= lsProp,
		type=str,
		required=True,
	)
	return parser.parse_args(argv)
