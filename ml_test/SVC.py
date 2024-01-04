#!/usr/bin/env python3
import os
import sys
import io
import pandas as pd
import pickle
if __name__ == "__main__":
	sys.path.append('./../')
from ml_test.common import * # getTrainData_c , getTestData_c, writeBestEstimatorInFile

from sklearn.svm import SVC

from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import median_absolute_error
from sklearn.metrics import classification_report
from sklearn.metrics import zero_one_loss

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import cross_val_score

IsRandomizedSearchCV = False
ISGridSearchCV = False

args = parse_args(sys.argv[1:])
prop = args.property
checkDataDirs(prop)

'''
read training data
X: features; Y: trarget or class
'''

X_train , Y_train = getTrainData_c(prop)
print('X_train:\n', X_train)
print('Y_train:\n',Y_train)
print('Y_train.value_counts:\n', Y_train.value_counts())
'''
read test data
'''

#X_test, Y_test = getTestData_c(prop)
#print('X_test:\n', X_test)
#print('Y_test:\n',Y_test.values)

'''
create the model with suitable parameters.; then fit; try with different weights
'''
svc = SVC(C=1.0, kernel='rbf', degree=3, gamma='auto', coef0=0.0, shrinking=True,
			probability=False, tol=0.001, cache_size=200, class_weight=None,verbose=False,
			max_iter=-1, decision_function_shape='ovr', random_state=5)

#print('svc.get_params = ', svc.get_params())
#svc.fit(X_train , Y_train)
#print('svc.support_ = ', svc.support_)
'''
You can predict
'''
#firstRow = X_test.iloc[:,:]
#print('firstRow:\n',firstRow)
#Y_pred = svc.predict(firstRow)
#print('Y_test:\n', Y_test.values)
#print('Y_pred:\n', Y_pred)

'''
check the Accuracy score with metrics
'''
#print('accuracy_score:\n:', accuracy_score(Y_test, Y_pred, normalize=True))# try with True

#Return the mean accuracy
#svc_score = svc.score(X_test, Y_test)
#print('svc_score =', svc_score)

#conf_matrix = confusion_matrix(Y_test, Y_pred)
#print('conf_matrix:\n',conf_matrix)

#Mean Squared Error : sum of abs difference / n
#MAEValue = mean_absolute_error(Y_test, Y_pred, multioutput='uniform_average')
#print('Mean Absolute Error Value is : ', MAEValue)

#Mean Squared Error : sum of sqr difference / n
#mSqrError = mean_squared_error(Y_test, Y_pred)
#print('mAbsError =', mSqrError)

#mdAbsError = median_absolute_error(Y_test, Y_pred)
#print('mdAbsError =', mdAbsError)

#num of correct
#zeroOneLoss = zero_one_loss(Y_test, Y_pred, normalize=False)
#print('zeroOneLoss=',zeroOneLoss)
#
#classificationRpt = classification_report(Y_test,Y_pred)
#print('classificationRpt:\n', classificationRpt)

'''
hyperparameter using GridSearch
'''
svc_params = {
	'C': [
		1.0,
		10,
		#100,
		#1000
		],
	'kernel' : [
		'linear',
		#'poly',
		'rbf',
		#'sigmoid',
		#'precomputed'#make error
		],
	'gamma':[
		'scale',
		'auto',
		#0.0001,
		#0.001,
		#0.1,
		#0.9,
		],
	'class_weight': [
				'balanced',
				#{0:1, 1:1, 2:1, 3:1, 4:1, 5:1},
				#{0:1, 1:0.5, 2:5, 3:4, 4:2, 5:20},
					]
	

	}
'''
no-overflow : 10 seconds
'''
if IsRandomizedSearchCV:
	paramDic={
		"coverage-error-call":{'cv':5, 'n_iter':8},
		"coverage-branches":{'cv':5, 'n_iter':8},
		"no-overflow":{'cv':5, 'n_iter':8},
		"termination":{'cv':5, 'n_iter':8},
		"valid-memcleanup":{'cv':5, 'n_iter':8},
		"valid-memsafety":{'cv':5, 'n_iter':8},
		"unreach-call":{'cv':5, 'n_iter':8}
		}
	d = paramDic[prop]
	randomizedSearchCV = RandomizedSearchCV(svc, svc_params, cv=d['cv'], scoring='accuracy', 
							n_iter=d['n_iter'], n_jobs=-1 , random_state=5, return_train_score=False)
	randomizedSearchCV.fit(X_train, Y_train)
	print(randomizedSearchCV.best_score_)
	print(randomizedSearchCV.best_params_)
	sorted(randomizedSearchCV.cv_results_.keys())
	cvResults = pd.DataFrame(randomizedSearchCV.cv_results_)[['mean_test_score', 'std_test_score', 'params' , 'rank_test_score' , 'mean_fit_time']]
	
	# Showing Results
	print('All Results are :\n', cvResults)
	print('randomizedSearchCV.cv_results_ =', randomizedSearchCV.cv_results_)
	print('Best Score is :', randomizedSearchCV.best_score_)
	print('Best Parameters are :', randomizedSearchCV.best_params_)
	print('Best Estimator is :', randomizedSearchCV.best_estimator_) # best model
	svc_best: SVC = randomizedSearchCV.best_estimator_
	writeBestEstimatorInFile(randomizedSearchCV,f"./SVC_{prop}.txt")
	
elif ISGridSearchCV:
	gridSearchModel = GridSearchCV(svc, svc_params, cv=10, 
								n_jobs=-1 , return_train_score=True)
	gridSearchModel.fit(X_train.values, Y_train)
	sorted(gridSearchModel.cv_results_.keys())
	print('gridSearchModel.cv_results_ =', gridSearchModel.cv_results_)

	cvResults = pd.DataFrame(gridSearchModel.cv_results_)[['mean_test_score', 'std_test_score', 'params' , 'rank_test_score' , 'mean_fit_time']]
	
	# Showing Results
	print('All Results are :\n', cvResults)
	print('Best Score is :', gridSearchModel.best_score_)
	print('Best Parameters are :', gridSearchModel.best_params_)
	print('Best Estimator is :', gridSearchModel.best_estimator_) # best model
	svc_best: SVC = gridSearchModel.best_estimator_
	writeBestEstimatorInFile(gridSearchModel,f"./SVC_{prop}.txt")
else:
	print('Training with given params..')
	svc_best: SVC = SVC()
	#sys.exit("must apply best params")
	if prop == 'coverage-error-call':
		svc_best = SVC(kernel='rbf', gamma='auto', class_weight='balanced', C=10, random_state=5)
	elif prop == 'coverage-branches':
		svc_best = SVC(kernel='rbf', gamma='auto', class_weight='balanced', C=10, random_state=5)
	elif prop == 'no-overflow':
		svc_best = SVC(C=10, class_weight='balanced', gamma='auto', random_state=5)
	elif prop == 'termination':
		svc_best = SVC(kernel='rbf', gamma='auto', class_weight='balanced',C=10, random_state=5)
	elif prop == 'valid-memsafety':
		svc_best = SVC(class_weight='balanced', kernel='linear',gamma='scale', C=1.0, random_state=5)
	elif prop == 'valid-memcleanup':
		svc_best = SVC(kernel='rbf', gamma='auto', class_weight='balanced', C=10, random_state=5)
	elif prop == 'unreach-call':
		sys.exit("Not implemented")
	else:
		sys.exit(f"unknown property {prop}")
		
	svc_best.fit(X_train, Y_train)

pickle_file = f"./../ml_models/svc/{prop}.sav"
#protocol=1
pickle.dump(svc_best, open(pickle_file, 'wb'))
print('model is dumped in:', pickle_file)

#Y_pred = svc_best.predict(X_test.values)
#print('accuracy_score:\n:', accuracy_score(Y_test.values, Y_pred, normalize=True))

#Return the mean accuracy
#dtc_score = svc_best.score(X_test.values, Y_test)
#print('dtc_score =', dtc_score)

print('OK....')
