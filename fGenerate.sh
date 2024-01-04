#!/bin/bash

echo "Hiii"
BENCHEXEC_HOME=./benchexec-master
if [ "$#" -ne 1 ]; then
	echo "Illegal number of parameters"
	echo "useage:$0 operation"
	echo "ex: $0 coverage-error-call"
	exit 1
fi
op=$1
finalResultsDir=/home/hosam/sdc1/final-results/0003

if [ "$op" != "coverage-error-call" ] && \
	[ "$op" != "coverage-branches" ] && \
	[ "$op" != "no-overflow" ] && \
	[ "$op" != "termination" ] && \
	[ "$op" != "valid-memcleanup" ] && \
	[ "$op" != "valid-memsafety" ] && \
	[ "$op" != "unreach-call" ]; then
	echo "invalid value of the first parameter $op"
	echo " must be [coverage-error-call, coverage-branches, no-overflow, termination, valid-memcleanup, valid-memsafety, unreach-call] "
	exit 1
fi
resSubDir=${finalResultsDir}/${op}

isMult=1
if [ "$isMult" == "1" ]; then
	echo "isMult=${isMult}"
	multCoverageErrorCall=${resSubDir}/coverage-error-call_mult/FuSeBMC-testcomp.mult.*.Coverage-Error-Call.my_coverage-error-call.xml.fixed.xml
	multCoverageBranches=${resSubDir}/coverage-branches_mutl/FuSeBMC-testcomp.mutl.*.Coverage-Branches.my_coverage-branches.xml.fixed.xml
	multUnreachCall=${resSubDir}/
	multNoOverflow=${resSubDir}/no-overflow_mult/FuSeBMC-svcomp.mult.*.no-overflow.my_no-overflow.xml
	multTermination=${resSubDir}/termination_mutl/FuSeBMC-svcomp.mutl.*.termination.my_termination.xml
	multValidMemcleanup=${resSubDir}/valid-memcleanup_mutl/FuSeBMC-svcomp.mutl.*.valid-memcleanup.my_valid-memcleanup.xml
	multValidMemsafety=${resSubDir}/valid-memsafety_mutl/FuSeBMC-svcomp.mutl.*.valid-memsafety.my_valid-memsafety.xml
fi
if [ "$op" == "coverage-error-call" ]; then
	$BENCHEXEC_HOME/bin/table-generator --outputpath ${resSubDir}/all \
	${resSubDir}/coverage-error-call_plain/FuSeBMC-testcomp.plain.*.Coverage-Error-Call.my_coverage-error-call.xml.fixed.xml \
	${resSubDir}/coverage-error-call_dtc/FuSeBMC-testcomp.dtc.*.Coverage-Error-Call.my_coverage-error-call.xml.fixed.xml \
	${resSubDir}/coverage-error-call_svc/FuSeBMC-testcomp.svc.*.Coverage-Error-Call.my_coverage-error-call.xml.fixed.xml \
	${resSubDir}/coverage-error-call_nnr/FuSeBMC-testcomp.nnr.*.Coverage-Error-Call.my_coverage-error-call.xml.fixed.xml \
	$multCoverageErrorCall \
	--name ${op}
fi

if [ "$op" == "coverage-branches" ]; then
	$BENCHEXEC_HOME/bin/table-generator --outputpath ${resSubDir}/all \
	${resSubDir}/coverage-branches_plain/FuSeBMC-testcomp.plain.*.Coverage-Branches.my_coverage-branches.xml.fixed.xml \
	${resSubDir}/coverage-branches_dtc/FuSeBMC-testcomp.dtc.*.Coverage-Branches.my_coverage-branches.xml.fixed.xml \
	${resSubDir}/coverage-branches_svc/FuSeBMC-testcomp.svc.*.Coverage-Branches.my_coverage-branches.xml.fixed.xml \
	${resSubDir}/coverage-branches_nnr/FuSeBMC-testcomp.nnr.*.Coverage-Branches.my_coverage-branches.xml.fixed.xml \
	$multCoverageBranches \
	--name ${op}
fi

if [ "$op" == "unreach-call" ]; then
	$BENCHEXEC_HOME/bin/table-generator --outputpath ${resSubDir}/all \
	${resSubDir}/unreach-call_plain/FuSeBMC-svcomp.plain.*.unreach-call.my_unreach-call.xml \
	${resSubDir}/unreach-call_dtcSvcomp/FuSeBMC-svcomp.dtcSvcomp.*.unreach-call.my_unreach-call.xml \
	${resSubDir}/unreach-call_svcSvcomp/FuSeBMC-svcomp.svcSvcomp.*.unreach-call.my_unreach-call.xml \
	${resSubDir}/unreach-call_nnrSvcomp/FuSeBMC-svcomp.nnrSvcomp.*.unreach-call.my_unreach-call.xml \
	$multUnreachCall \
	--name ${op}
fi
if [ "$op" == "no-overflow" ]; then
	$BENCHEXEC_HOME/bin/table-generator --outputpath ${resSubDir}/all \
	${resSubDir}/no-overflow_plain/FuSeBMC-svcomp.plain.*.no-overflow.my_no-overflow.xml \
	${resSubDir}/no-overflow_dtc/FuSeBMC-svcomp.dtc.*.no-overflow.my_no-overflow.xml \
	${resSubDir}/no-overflow_svc/FuSeBMC-svcomp.svc.*.no-overflow.my_no-overflow.xml \
	${resSubDir}/no-overflow_nnr/FuSeBMC-svcomp.nnr.*.no-overflow.my_no-overflow.xml \
	$multNoOverflow \
	--name ${op}
fi
if [ "$op" == "termination" ]; then
	$BENCHEXEC_HOME/bin/table-generator --outputpath ${resSubDir}/all \
	${resSubDir}/termination_plain/FuSeBMC-svcomp.plain.*.termination.my_termination.xml \
	${resSubDir}/termination_dtc/FuSeBMC-svcomp.dtc.*.termination.my_termination.xml \
	${resSubDir}/termination_svc/FuSeBMC-svcomp.svc.*.termination.my_termination.xml \
	${resSubDir}/termination_nnr/FuSeBMC-svcomp.nnr.*.termination.my_termination.xml \
	$multTermination \
	--name ${op}
fi
if [ "$op" == "valid-memcleanup" ]; then
	#unrecognized params
	$BENCHEXEC_HOME/bin/table-generator --outputpath ${resSubDir}/all \
	${resSubDir}/valid-memcleanup_plain/FuSeBMC-svcomp.plain.*.valid-memcleanup.my_valid-memcleanup.xml \
	${resSubDir}/valid-memcleanup_dtc/FuSeBMC-svcomp.dtc.*.valid-memcleanup.my_valid-memcleanup.xml \
	${resSubDir}/valid-memcleanup_svc/FuSeBMC-svcomp.svc.*.valid-memcleanup.my_valid-memcleanup.xml \
	${resSubDir}/valid-memcleanup_nnr/FuSeBMC-svcomp.nnr.*.valid-memcleanup.my_valid-memcleanup.xml \
	$multValidMemcleanup \
	--name ${op}
fi
if [ "$op" == "valid-memsafety" ]; then
	$BENCHEXEC_HOME/bin/table-generator --outputpath ${resSubDir}/all \
	${resSubDir}/valid-memsafety_plain/FuSeBMC-svcomp.plain.*.valid-memsafety.my_valid-memsafety.xml \
	${resSubDir}/valid-memsafety_dtc/FuSeBMC-svcomp.dtc.*.valid-memsafety.my_valid-memsafety.xml \
	${resSubDir}/valid-memsafety_svc/FuSeBMC-svcomp.svc.*.valid-memsafety.my_valid-memsafety.xml \
	${resSubDir}/valid-memsafety_nnr/FuSeBMC-svcomp.nnr.*.valid-memsafety.my_valid-memsafety.xml \
	$multValidMemsafety \
	--name ${op}
fi
echo "$0 Done ...."

exit


FUSEBMC_SVCompPlainHome=./../FuSeBMC_svcomp_plain
FUSEBMC_TestCompPlainHome=./../FuSeBMC_testcomp_plain
FUSEBMC_HOME=$(realpath $(pwd))

BENCHMARK=./sv-benchmarks
MyHOST=$(hostname)
echo "hostname: ${MyHOST}"



read -p "Is this Server10 or Server11 [10|11]?" servernr

if [ "$servernr" == "10" ]; then
	#has clang
	./fCopySetFiles.sh full
	
	#must uncomment
	./runTrainTestBulkOnlyTestCov.sh coverage-branches
	
	echo "$0 Done ..."
	exit 0

	#./runTrainTestBulkOnlyTestCov.sh coverage-error-call
	./fCopySetFiles.sh x
	cbArr1=("00380")
	for f in ${cbArr1[@]}; do
		#./runTrainTestBulk.sh coverage-branches $f $f
		# I don't know how many are done!! waiting for results from server
		echo must run coverage-branches_${f}
		
	done
	
	#./runTrainTestBulk.sh coverage-error-call 39 39
	#./runTrainTestBulk.sh coverage-error-call 40 40
	
	# must copy set files
	./fCopySetFiles.sh y
	
	#palin testcomp
	cd $FUSEBMC_TestCompPlainHome
	cp ./benchmark-defs/FuSeBMC-testcomp-plain.xml ./FuSeBMC-testcomp.xml
	./runBenchmark.sh coverage-error-call plain
	./runBenchmark.sh coverage-branches plain
	
	
	cd $FUSEBMC_HOME
	
	#palin svcomp
	cd $FUSEBMC_SVCompPlainHome
	cp ./benchmark-defs/FuSeBMC-svcomp-palin.xml ./FuSeBMC-svcomp.xml
	
	./runBenchmark.sh no-overflow plain
	./runBenchmark.sh termination plain
	./runBenchmark.sh valid-memcleanup plain
	./runBenchmark.sh valid-memsafety plain
	./runBenchmark.sh unreach-call plain

	
elif [ "$servernr" == "11" ]; then
	./fCopySetFiles.sh x
	cbArr2=("00708")
	# new full nonDoneCB without to ignore
	cbArr2=("00227" "00228")
	for f in ${cbArr2[@]}; do
		# I don't know how many are done!! waiting for results from server
		#echo must run coverage-branches_${f}
		./runTrainTestBulk.sh coverage-branches $f $f
	done
	echo "$0 Done ...."
	exit 0
	#./trainModels.sh ya
	# must copy set files
	./fCopySetFiles.sh y
	
	#DTC svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-dtc.xml ./FuSeBMC-svcomp.xml
	./runBenchmark.sh no-overflow dtcSvcomp
	./runBenchmark.sh termination dtcSvcomp
	./runBenchmark.sh valid-memcleanup dtcSvcomp
	./runBenchmark.sh valid-memsafety dtcSvcomp
	./runBenchmark.sh unreach-call dtcSvcomp

	
	#SVC svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-svc.xml ./FuSeBMC-svcomp.xml
	./runBenchmark.sh no-overflow svcSvcomp
	./runBenchmark.sh termination svcSvcomp
	./runBenchmark.sh valid-memcleanup svcSvcomp
	./runBenchmark.sh valid-memsafety svcSvcomp
	./runBenchmark.sh unreach-call svcSvcomp
	
	
	#NNR svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-nnr.xml ./FuSeBMC-svcomp.xml
	./runBenchmark.sh no-overflow nnrSvcomp
	./runBenchmark.sh termination nnrSvcomp
	./runBenchmark.sh valid-memcleanup nnrSvcomp
	./runBenchmark.sh valid-memsafety nnrSvcomp
	./runBenchmark.sh unreach-call nnrSvcomp
	
	#DTC testcomp
	cp ./benchmark-defs/FuSeBMC-testcomp-dtc.xml ./FuSeBMC-testcomp.xml
	./runBenchmark.sh coverage-error-call dtcTestcomp
	#./runBenchmark.sh coverage-branches dtcTestcomp
	
	
	
	#SVC testcomp
	cp ./benchmark-defs/FuSeBMC-testcomp-svc.xml ./FuSeBMC-testcomp.xml
	./runBenchmark.sh coverage-error-call svcTestcomp
	#./runBenchmark.sh coverage-branches svcTestcomp
	

	
	#NNR testcomp
	cp ./benchmark-defs/FuSeBMC-testcomp-nnr.xml ./FuSeBMC-testcomp.xml
	./runBenchmark.sh coverage-error-call nnrTestcomp
	#./runBenchmark.sh coverage-branches nnrTestcomp
	
else
	echo "${servernr} is not a valid value."
fi

#./runTrainTestBulk.sh coverage-error-call 625 378


echo "$0 Done ..... !!!"
exit 0



#------------------------


if [ "$VERSION" == "012" ]; then
	echo "We are in Version ${VERSION}"
	CurrentPWD=$(pwd)
	echo "We are in ${CurrentPWD}"
	cd ./FuSeBMC_engines
	ls
	cd $CurrentPWD
	
	#palin testcomp
	cp ./benchmark-defs/FuSeBMC-testcomp-plain.xml ./FuSeBMC-testcomp.xml
	./runBenchmark.sh coverage-error-call plain
	./runBenchmark.sh coverage-branches plain
	
	#palin svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-palin.xml ./FuSeBMC-svcomp.xml
	./runBenchmark.sh no-overflow plain
	./runBenchmark.sh termination plain
	./runBenchmark.sh valid-memcleanup plain
	./runBenchmark.sh valid-memsafety plain
	./runBenchmark.sh unreach-call plain
	
	#DTC testcomp
	cp ./benchmark-defs/FuSeBMC-testcomp-dtc.xml ./FuSeBMC-testcomp.xml
	./runBenchmark.sh coverage-error-call dtc
	./runBenchmark.sh coverage-branches dtc
	
	
	
	#SVC testcomp
	cp ./benchmark-defs/FuSeBMC-testcomp-svc.xml ./FuSeBMC-testcomp.xml
	./runBenchmark.sh coverage-error-call svc
	./runBenchmark.sh coverage-branches svc
	

	
	#NNR testcomp
	cp ./benchmark-defs/FuSeBMC-testcomp-nnr.xml ./FuSeBMC-testcomp.xml
	./runBenchmark.sh coverage-error-call nnr
	./runBenchmark.sh coverage-branches nnr
	
	
fi

echo "Done ..... !!!"
exit 0
