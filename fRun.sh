#!/bin/bash

echo "Hiii"
FUSEBMC_SVCompPlainHome=./../FuSeBMC_svcomp_plain
FUSEBMC_TestCompPlainHome=./../FuSeBMC_testcomp_plain
FUSEBMC_HOME=$(realpath "$(pwd)")

BENCHMARK=./sv-benchmarks
MyHOST=$(hostname)
echo "hostname: ${MyHOST}"
myUID=$(id -u)
if [ "$myUID" != "0" ]; then
	echo "please; run as: sudo $0"
	read -p "Do you want to continue y|n?" answer
	if [ "$answer" != "y" ]; then
		exit 1
	fi
fi
#hostname: a01af3894c6e, servernr=10
#hostname: bdd6976912a3, servernr=11
if [ "$MyHOST" == "a01af3894c6e" ]; then
	echo "I think, this is fm10"
elif [ "$MyHOST" == "bdd6976912a3" ]; then
	echo "I think, this is fm11"
fi
read -p "Is this Server10 or Server11 [10|11]?" servernr

if [ "$servernr" == "10" ]; then
	#has clang
	./fChangeBenchmarkTag.sh testcomp22
	./fCopySetFiles.sh y
	
	#./trainModels.sh termination
	#./trainModels.sh valid-memcleanup
	#./trainModels.sh valid-memsafety
	#./trainModels.sh no-overflow
	
	
	#./trainModels.sh coverage-error-call
	#./trainModels.sh coverage-branches
	
	#DTC testcomp
	#cp ./benchmark-defs/FuSeBMC-testcomp-dtc.xml ./FuSeBMC-testcomp.xml
	#if [ -f "./ml_models/dtc/coverage-error-call.sav" ]; then
	#	./runTrainTest.sh coverage-error-call dtc
	#fi
	#if [ -f "./ml_models/dtc/coverage-branches.sav" ]; then
	#	./runTrainTest.sh coverage-branches dtc
	#fi
	
	#SVC testcomp
	#cp ./benchmark-defs/FuSeBMC-testcomp-svc.xml ./FuSeBMC-testcomp.xml
	#if [ -f "./ml_models/svc/coverage-error-call.sav" ]; then
	#	./runTrainTest.sh coverage-error-call svc
	#fi
	#if [ -f "./ml_models/svc/coverage-branches.sav" ]; then
	#	./runTrainTest.sh coverage-branches svc
	#fi
	
	#NNR testcomp
	cp ./benchmark-defs/FuSeBMC-testcomp-nnr.xml ./FuSeBMC-testcomp.xml
	#if [ -f "./ml_models/nnr/coverage-error-call.sav" ]; then
	#	./runTrainTest.sh coverage-error-call nnr
	#fi
	if [ -f "./ml_models/nnr/coverage-branches.sav" ]; then
		./runTrainTest.sh coverage-branches nnr
	fi
	
	#MULT testcomp
	cp ./benchmark-defs/FuSeBMC-testcomp-mult.xml ./FuSeBMC-testcomp.xml
	#if [ -f "./ml_models/dtc/coverage-error-call.sav" ] && \
	#	[ -f "./ml_models/svc/coverage-error-call.sav" ] && \
	#	[ -f "./ml_models/nnr/coverage-error-call.sav" ]; then
	#	./runTrainTest.sh coverage-error-call mult
	#fi
	if [ -f "./ml_models/dtc/coverage-branches.sav" ] && \
		[ -f "./ml_models/svc/coverage-branches.sav" ] && \
		[ -f "./ml_models/nnr/coverage-branches.sav" ]; then
		./runTrainTest.sh coverage-branches mutl
	fi
	
	
	
	echo "$0 Done ..... !!!"
	exit 0
	
	#palin svcomp
	cd $FUSEBMC_SVCompPlainHome
	cp ./benchmark-defs/FuSeBMC-svcomp-palin.xml ./FuSeBMC-svcomp.xml
	
	./runTrainTest.sh no-overflow plain
	./runTrainTest.sh termination plain
	./runTrainTest.sh valid-memcleanup plain
	./runTrainTest.sh valid-memsafety plain
	./runTrainTest.sh unreach-call plain
	
	#palin testcomp
	./fChangeBenchmarkTag.sh testcomp22
	cd $FUSEBMC_TestCompPlainHome
	cp ./benchmark-defs/FuSeBMC-testcomp-plain.xml ./FuSeBMC-testcomp.xml
	./runTrainTest.sh coverage-error-call plain
	./runTrainTest.sh coverage-branches plain
	
	
	cd $FUSEBMC_HOME
	###############
	
	echo "$0 Done ..... !!!"
	exit 0
	
	./runTrainTestBulk.sh unreach-call 1 576
	./runTrainTestBulk.sh termination 1 72
	./runTrainTestBulk.sh no-overflow 1 144
	./runTrainTestBulk.sh valid-memsafety 1 144
	./runTrainTestBulk.sh valid-memcleanup 1 144
	
elif [ "$servernr" == "11" ]; then
	./fChangeBenchmarkTag.sh svcomp22
	./fCopySetFiles.sh y
	#up
	#./runTrainTestBulk.sh coverage-branches 1 384
	#./runTrainTestBulk.sh coverage-error-call 1 192
	
	#./runTrainTestBulk.sh unreach-call 1 281
	./trainModels.sh unreach-call
	
	#DTC svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-dtc.xml ./FuSeBMC-svcomp.xml
	#if [ -f "./ml_models/dtc/no-overflow.sav" ]; then
	#	./runTrainTest.sh no-overflow dtc
	#fi
	#if [ -f "./ml_models/dtc/termination.sav" ]; then
	#	./runTrainTest.sh termination dtc
	#fi
	#if [ -f "./ml_models/dtc/valid-memcleanup.sav" ]; then
	#	./runTrainTest.sh valid-memcleanup dtc
	#fi
	#if [ -f "./ml_models/dtc/valid-memsafety.sav" ]; then
	#	./runTrainTest.sh valid-memsafety dtc
	#fi
	
	if [ -f "./ml_models/dtc/unreach-call.sav" ]; then
		#echo "not ready for this run"
		./runTrainTest.sh unreach-call dtc
	fi

	
	#SVC svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-svc.xml ./FuSeBMC-svcomp.xml
	#if [ -f "./ml_models/svc/no-overflow.sav" ]; then
	#	./runTrainTest.sh no-overflow svc
	#fi
	#if [ -f "./ml_models/svc/termination.sav" ]; then
	#	./runTrainTest.sh termination svc
	#fi
	#if [ -f "./ml_models/svc/valid-memcleanup.sav" ]; then
	#	./runTrainTest.sh valid-memcleanup svc
	#fi
	#if [ -f "./ml_models/svc/valid-memsafety.sav" ]; then
	#	./runTrainTest.sh valid-memsafety svc
	#fi
	if [ -f "./ml_models/svc/unreach-call.sav" ]; then
		#echo "not ready for this run"
		./runTrainTest.sh unreach-call svc
	fi
	
	
	#NNR svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-nnr.xml ./FuSeBMC-svcomp.xml
	#if [ -f "./ml_models/nnr/no-overflow.sav" ]; then
	#	./runTrainTest.sh no-overflow nnr
	#fi
	#if [ -f "./ml_models/nnr/termination.sav" ]; then
	#	./runTrainTest.sh termination nnr
	#fi
	#if [ -f "./ml_models/nnr/valid-memcleanup.sav" ]; then
	#	./runTrainTest.sh valid-memcleanup nnr
	#fi
	#if [ -f "./ml_models/nnr/valid-memsafety.sav" ]; then
	#	./runTrainTest.sh valid-memsafety nnr
	#fi
	if [ -f "./ml_models/nnr/unreach-call.sav" ]; then
		#echo "not ready for this run"
		./runTrainTest.sh unreach-call nnr
	fi
	
	
	
	#MULI svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-mult.xml ./FuSeBMC-svcomp.xml
	#if [ -f "./ml_models/dtc/no-overflow.sav" ] && \
	#	[ -f "./ml_models/svc/no-overflow.sav" ] && \
	#	[ -f "./ml_models/nnr/no-overflow.sav" ]; then
	#	./runTrainTest.sh no-overflow mult
	#fi
	#if [ -f "./ml_models/dtc/termination.sav" ] && \
	#	[ -f "./ml_models/svc/termination.sav" ] && \
	#	[ -f "./ml_models/nnr/termination.sav" ]; then
	#	./runTrainTest.sh termination mutl
	#fi
	#if [ -f "./ml_models/dtc/valid-memcleanup.sav" ] && \
	#	[ -f "./ml_models/svc/valid-memcleanup.sav" ] && \
	#	[ -f "./ml_models/nnr/valid-memcleanup.sav" ]; then
	#	./runTrainTest.sh valid-memcleanup mutl
	#fi
	#if [ -f "./ml_models/dtc/valid-memsafety.sav" ] && \
	#	[ -f "./ml_models/svc/valid-memsafety.sav" ] && \
	#	[ -f "./ml_models/nnr/valid-memsafety.sav" ]; then
	#	./runTrainTest.sh valid-memsafety mutl
	#fi
	if [ -f "./ml_models/dtc/unreach-call.sav" ] && \
		[ -f "./ml_models/svc/unreach-call.sav" ] && \
		[ -f "./ml_models/nnr/unreach-call.sav" ]; then
		#echo "not ready for this run"
		./runTrainTest.sh unreach-call mutl
	fi
	echo "Done !!!"
	exit 0
	./fCopySetFiles.sh x
	i=192
	while [ $i -ge 1 ]
	do
		./runTrainTestBulk.sh coverage-error-call $i $i
		i=$((i-1))
	done
	
	i=384
	while [ $i -ge 1 ]
	do
		./runTrainTestBulk.sh coverage-branches $i $i
		i=$((i-1))
	done
	
	echo "$0 Done ..... !!!"
	exit 0
	
	i=144
	while [ $i -ge 1 ]
	do
		./runTrainTestBulk.sh valid-memcleanup $i $i
		i=$((i-1))
	done
	
	i=144
	while [ $i -ge 1 ]
	do
		./runTrainTestBulk.sh valid-memsafety $i $i
		i=$((i-1))
	done
	
	i=144
	while [ $i -ge 1 ]
	do
		./runTrainTestBulk.sh no-overflow $i $i
		i=$((i-1))
	done
	
	i=72
	while [ $i -ge 1 ]
	do
		./runTrainTestBulk.sh termination $i $i
		i=$((i-1))
	done
	
	i=576
	while [ $i -ge 1 ]
	do
		./runTrainTestBulk.sh unreach-call $i $i
		i=$((i-1))
	done
	
else
	echo "${servernr} is not a valid value."
fi

#./runTrainTestBulk.sh coverage-error-call 625 378


echo "$0 Done ..... !!!"
exit 0
