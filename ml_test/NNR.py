#!/usr/bin/env python3
import os
import sys
import io
import pandas as pd
import pickle

if __name__ == "__main__":
	sys.path.append('./../')

#from ml_test.common import getTrainData_r 

from ml_test.common import * #getTestData_r , getTrainData_r, writeBestEstimatorInFile

from sklearn.neural_network import MLPRegressor


from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import median_absolute_error

from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler

IsRandomizedSearchCV = False
ISGridSearchCV = False
IsTransform = True


args = parse_args(sys.argv[1:])
prop = args.property
checkDataDirs(prop)

'''
read training data
X: features; Y: trarget or class
'''

X_train , Y_train = getTrainData_r(prop)
print('X_train:\n', X_train)
print('Y_train:\n',Y_train)
print('Y_train.value_counts:\n', Y_train.value_counts())

if IsTransform:
	standardScaler=StandardScaler()
	scaler = standardScaler.fit(X_train)
	trainX_scaled = scaler.transform(X_train)
	X_train = trainX_scaled

'''
read test data
'''

#X_test, Y_test = getTestData_r(prop)
#print('X_test:\n', X_test)
#print('Y_test:\n',Y_test.values)


'''
create the model with suitable parameters.; then fit; try with different weights
'''
mlp = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam',
			alpha=0.0001,batch_size='auto', learning_rate='constant',
			learning_rate_init=0.001, power_t=0.5,max_iter=200, shuffle=True,
			random_state=None,tol=0.0001, verbose=False, warm_start=False,
			momentum=0.9, nesterovs_momentum=True,early_stopping=False,
			validation_fraction=0.1,beta_1=0.9, beta_2=0.999, epsilon=1E-08,
			n_iter_no_change=10)
#print('mlp.get_params = ', mlp.get_params())
#mlp.fit(X_train.values , Y_train)

#scores = cross_val_score(DT, X_train, Y_train,cv=3, verbose = 3)
#print('scores =', scores)
#print('scores.mean =',scores.mean())

'''
You can predict
'''
#firstRow = X_test.iloc[:,:]
#print('firstRow:\n',firstRow)
#Y_pred = mlp.predict(firstRow)
#print('Y_test:\n', Y_test.values)
#print('Y_pred:\n', Y_pred)

'''
check the Accuracy score with metrics
'''

#Return the mean accuracy
#mlp_score = mlp.score(X_test, Y_test)
#print('mlp_score =', mlp_score)


#Mean Squared Error : sum of abs difference / n
#MAEValue = mean_absolute_error(Y_test, Y_pred, multioutput='uniform_average')
#print('Mean Absolute Error Value is : ', MAEValue)

#Mean Squared Error : sum of sqr difference / n
#mSqrError = mean_squared_error(Y_test, Y_pred)
#print('mAbsError =', mSqrError)

#mdAbsError = median_absolute_error(Y_test, Y_pred)
#print('mdAbsError =', mdAbsError)

#print('MLPClassifierModel loss is : ' , mlp.loss_)
#print('MLPClassifierModel No. of iterations is : ' , mlp.n_iter_)
#print('MLPClassifierModel No. of layers is : ' , mlp.n_layers_)
#print('MLPClassifierModel last activation is : ' , mlp.out_activation_)
#print('----------------------------------------------------')

'''
hyperparameter using GridSearch
'''

mlp_params = {
	'hidden_layer_sizes': [
		(100,),
		(200,300),
		#(300,400,500),
		(150,100,50),
		(120,80,40),
		(100,50,30)
		],
	'activation' : [
				#'identity',
				#'logistic',
				'tanh',
				'relu'
				],
	'solver' : [
		'lbfgs',
		'sgd', 
		'adam'
		],
	'alpha' : [0.0001, 0.05],
	'batch_size' : ['auto'],
	'learning_rate' : [
					'constant', 
					#'invscaling',
					'adaptive'
					],
	'learning_rate_init':[0.001],
	'power_t':[0.5],
	'max_iter' : [200,500],
	'tol':[
		0.0001,
		#1e-4,
		#1e-9
		]
	}
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
	randomizedSearchCV = RandomizedSearchCV(mlp, mlp_params, cv=d['cv'], scoring=None, 
							n_iter=d['n_iter'], n_jobs=-1 , random_state=5, return_train_score=False)
	randomizedSearchCV.fit(X_train, Y_train)
	print(randomizedSearchCV.best_score_)
	print(randomizedSearchCV.best_params_)
	sorted(randomizedSearchCV.cv_results_.keys())
	cvResults = randomizedSearchCV.cv_results_
	# Showing Results
	print('All Results are :\n', cvResults)
	print('randomizedSearchCV.cv_results_ =', randomizedSearchCV.cv_results_)
	print('Best Score is :', randomizedSearchCV.best_score_)
	print('Best Parameters are :', randomizedSearchCV.best_params_)
	print('Best Estimator is :', randomizedSearchCV.best_estimator_) # best model
	mlp_best: MLPRegressor = randomizedSearchCV.best_estimator_
	writeBestEstimatorInFile(randomizedSearchCV,f"./NNR_{prop}.txt")
	
elif ISGridSearchCV:
	gridSearchModel = GridSearchCV(mlp, mlp_params, cv=10, scoring='accuracy',
								n_jobs=-1 , return_train_score=True)
	gridSearchModel.fit(X_train, Y_train)
	sorted(gridSearchModel.cv_results_.keys())
	print('gridSearchModel.cv_results_ =', gridSearchModel.cv_results_)
	
	cvResults = pd.DataFrame(gridSearchModel.cv_results_)[['mean_test_score', 'std_test_score', 'params' , 'rank_test_score' , 'mean_fit_time']]

	# Showing Results
	print('All Results are :\n', cvResults)
	print('Best Score is :', gridSearchModel.best_score_)
	print('Best Parameters are :', gridSearchModel.best_params_)
	print('Best Estimator is :', gridSearchModel.best_estimator_) # best model

	mlp_best:MLPRegressor = gridSearchModel.best_estimator_
	writeBestEstimatorInFile(gridSearchModel,f"./NNR_{prop}.txt")
else:
	#sys.exit("must apply best params")
	mlp_best: MLPRegressor = MLPRegressor()
	print('Training with given params..')
	if prop == 'coverage-error-call':
		mlp_best = MLPRegressor(activation='tanh', hidden_layer_sizes=(120, 80, 40),
					learning_rate='adaptive', max_iter=500, solver='sgd', random_state=5)
	elif prop == 'coverage-branches':
		mlp_best = MLPRegressor(activation='tanh', alpha=0.05, hidden_layer_sizes=(100, 50, 30),
					learning_rate='adaptive', max_iter=500, random_state=5)
	elif prop == 'no-overflow':
		mlp_best = MLPRegressor(hidden_layer_sizes=(120, 80, 40), max_iter=500, random_state=5)
	elif prop == 'termination':
		mlp_best = MLPRegressor(activation='tanh', hidden_layer_sizes=(120, 80, 40),
							learning_rate='adaptive', max_iter=500, solver='sgd', random_state=5)
	elif prop == 'valid-memsafety':
		mlp_best = MLPRegressor(activation='tanh', alpha=0.05, hidden_layer_sizes=(100, 50, 30),
							learning_rate='adaptive', max_iter=500, random_state=5)
	elif prop == 'valid-memcleanup':
		mlp_best = MLPRegressor(activation='tanh', alpha=0.05, solver='lbfgs', random_state=5)
	elif prop == 'unreach-call':
		sys.exit("Not implemented")
	else:
		sys.exit(f"unknown property {prop}")
	mlp_best.fit(X_train, Y_train)
pickle_file = f"./../ml_models/nnr/{prop}.sav"
#protocol=1
pickle.dump(mlp_best, open(pickle_file, 'wb'))
print('model is dumped in:', pickle_file)


#Return the mean accuracy
#mlp_score = mlp_best.score(X_test.values, Y_test)
#print('mlp_score =', mlp_score)

print('OK....')
