#!/usr/bin/env python3
import os
import sys
import io
import pandas as pd
import pickle
if __name__ == "__main__":
	sys.path.append('./../')

from ml_test.common import * #checkDataDirs, getTrainData_c, getTestData_c, writeBestEstimatorInFile

from sklearn.tree import DecisionTreeClassifier


from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import median_absolute_error
from sklearn.metrics import classification_report
from sklearn.metrics import zero_one_loss

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score

from sklearn.model_selection import RandomizedSearchCV

ISGridSearchCV = not True

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
DTC = DecisionTreeClassifier(min_samples_split=4, min_samples_leaf=3, 
					#class_weight={0:weight0, 1:weight1, 2:weight2, 3:weight3, 4:weight4, 5:weight5},
					class_weight={0: 2.197, 1: 3.611, 2: 6.545, 3: 2.014, 4: 1, 5: 17.636},
					random_state=5
					)
print('DTC.get_params = ', DTC.get_params())
#DTC.fit(X_train , Y_train)

#scores = cross_val_score(DT, X_train, Y_train,cv=3, verbose = 3)
#print('scores =', scores)
#print('scores.mean =',scores.mean())

'''
You can predict
'''
#firstRow = X_test.iloc[:,:]
#print('firstRow:\n',firstRow)
#Y_pred = DTC.predict(firstRow)
#print('Y_test:\n', Y_test.values)
#print('Y_pred:\n', Y_pred)

'''
check the Accuracy score with metrics
'''
#print('accuracy_score:\n:', accuracy_score(Y_test, Y_pred, normalize=True))# try with True

#Return the mean accuracy
#dtc_score = DTC.score(X_test, Y_test)
#print('dtc_score =', dtc_score)

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
# 4 * 3 * 2 = 24
DTC_params = {
	'min_samples_split': [2,3,4,5,6,7],
	'min_samples_leaf' : [2,3,4,5,6,7],
	'class_weight': [
				'balanced',
				{0:1, 1:1, 2:1, 3:1, 4:1, 5:1},
				{0:1, 1:0.5, 2:5, 3:4, 4:2, 5:20},
				{0: 2.197, 1: 3.611, 2: 6.545, 3: 2.014, 4: 1, 5: 17.636}
					]
	}

#randomizedSearchCV = RandomizedSearchCV(DTC, DTC_params, cv=10, scoring='accuracy', 
#						n_iter=5, return_train_score=False)
#randomizedSearchCV.fit(X_train, Y_train)
#print(randomizedSearchCV.best_score_)
#print(randomizedSearchCV.best_params_)
#sorted(randomizedSearchCV.cv_results_.keys())
#print('gridSearchModel.cv_results_ =', randomizedSearchCV.cv_results_)
#print("Done....")
#exit(0)
if ISGridSearchCV:
	gridSearchModel = GridSearchCV(DTC, DTC_params, cv=10,return_train_score=True)
	gridSearchModel.fit(X_train, Y_train)
	sorted(gridSearchModel.cv_results_.keys())
	print('gridSearchModel.cv_results_ =', gridSearchModel.cv_results_)
	
	gridSearchResults = pd.DataFrame(gridSearchModel.cv_results_)[['mean_test_score', 'std_test_score', 'params' , 'rank_test_score' , 'mean_fit_time']]
	
	# Showing Results
	print('All Results are :\n', gridSearchResults)
	print('Best Score is :', gridSearchModel.best_score_)
	print('Best Parameters are :', gridSearchModel.best_params_)
	print('Best Estimator is :', gridSearchModel.best_estimator_) # best model
	
	DTC_best: DecisionTreeClassifier = gridSearchModel.best_estimator_
	#DTC_best.fit(X_train , Y_train)
	writeBestEstimatorInFile(gridSearchModel,f"./DTC_{prop}.txt")
else:
	DTC_best: DecisionTreeClassifier
	print('Training with given params..')
	if prop == 'coverage-error-call':
		DTC_best = DecisionTreeClassifier(class_weight={0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1},
										min_samples_leaf=6, min_samples_split=2, random_state=5)
	elif prop == 'coverage-branches':
		DTC_best = DecisionTreeClassifier(class_weight={0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1},
										min_samples_leaf=7, min_samples_split=2, random_state=5)
	elif prop == 'no-overflow':
		DTC_best = DecisionTreeClassifier(class_weight={0: 1, 1: 0.5, 2: 5, 3: 4, 4: 2, 5: 20},
										min_samples_leaf=5, random_state=5)
	elif prop == 'termination':
		DTC_best = DecisionTreeClassifier(class_weight={0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1},
										min_samples_leaf=6, random_state=5)
	elif prop == 'valid-memsafety':
		DTC_best = DecisionTreeClassifier(class_weight={0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1},
										min_samples_leaf=7, random_state=5)
	elif prop == 'valid-memcleanup':
		DTC_best = DecisionTreeClassifier(class_weight='balanced', min_samples_leaf=3,random_state=5)
	elif prop == 'unreach-call':
		sys.exit("Not implemented")
	else:
		sys.exit(f"unknown property {prop}")
	DTC_best.fit(X_train, Y_train)
pickle_file = f"./../ml_models/dtc/{prop}.sav"
#protocol=1
pickle.dump(DTC_best, open(pickle_file, 'wb'))
print('model is dumped in:', pickle_file)
#Y_pred = DTC_best.predict(X_test)
#print('accuracy_score:\n:', accuracy_score(Y_test, Y_pred, normalize=True))

#Return the mean accuracy
#dtc_score = DTC_best.score(X_test, Y_test)
#print('dtc_score =', dtc_score)
#print('get_params',DTC_best.get_params())
print('OK....')
