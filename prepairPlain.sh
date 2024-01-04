#!/bin/bash
FUSEBMC_SVCompPlainHome=./../FuSeBMC_svcomp_plain
FUSEBMC_TestCompPlainHome=./../FuSeBMC_testcomp_plain

# noSymlink for FuSeBMC_instrument

echo "Symlink benchexec-master ..."
ln -s $(realpath "./val_testcov_3.5")  ${FUSEBMC_TestCompPlainHome}/val_testcov_3.5
ln -s $(realpath "./val_testcov_3.5")  ${FUSEBMC_SVCompPlainHome}/val_testcov_3.5

echo "Symlink val_testcov_3.5 ..."
ln -s $(realpath "./benchexec-master") ${FUSEBMC_TestCompPlainHome}/benchexec-master
ln -s $(realpath "./benchexec-master") ${FUSEBMC_SVCompPlainHome}/benchexec-master

echo "Symlink sv-benchmarks ..."
ln -s $(realpath "./sv-benchmarks") ${FUSEBMC_TestCompPlainHome}/sv-benchmarks
ln -s $(realpath "./sv-benchmarks") ${FUSEBMC_SVCompPlainHome}/sv-benchmarks

echo "Symlink FuSeBMC_engines"
ln -s $(realpath "./FuSeBMC_engines") ${FUSEBMC_TestCompPlainHome}/FuSeBMC_engines
ln -s $(realpath "./FuSeBMC_engines") ${FUSEBMC_SVCompPlainHome}/FuSeBMC_engines


cp ./TestCov.xml       ${FUSEBMC_TestCompPlainHome}/
cp ./mergeResult2.py      ${FUSEBMC_TestCompPlainHome}/

filesArr=("./fSetup.sh" "./runTrainTest.sh")
for f in ${filesArr[@]}; do
	cp $f ${FUSEBMC_SVCompPlainHome}/
	cp $f ${FUSEBMC_TestCompPlainHome}/
done


cp ./benchmark-defs/FuSeBMC-svcomp-palin.xml ${FUSEBMC_SVCompPlainHome}/FuSeBMC-svcomp.xml
cp ./benchmark-defs/FuSeBMC-testcomp-plain.xml ${FUSEBMC_TestCompPlainHome}/FuSeBMC-testcomp.xml
#myPWD=$(pwd)

#read -p "Do you want to Setup ${FUSEBMC_SVCompPlainHome} y|n?" answer
#if [ "$answer" == "y" ]; then
#	cd $FUSEBMC_SVCompPlainHome
#	echo "You are in: $(pwd)"
#	./fSetup.sh
#fi
#cd $myPWD
#read -p "Do you want to Setup ${FUSEBMC_TestCompPlainHome} y|n?" answer
#if [ "$answer" == "y" ]; then
#	cd $FUSEBMC_TestCompPlainHome
#	echo "You are in: $(pwd)"
#	./fSetup.sh
#fi
#cd $myPWD
echo "Done ...!!!!!"
exit 0

numOfThreads=1
FUSEBMC_HOME=./
BENCHEXEC_HOME=./benchexec-master
TESTCOV_HOME=./val_testcov_3.5/testcov
#CPACHECKER_HOME=./CPAchecker-2.1-unix
#UAUTOMIZER_HOME=./UAutomizer-linux

ERRORCALL_TIMELIMIT=300s
ERRORCALL_MEMLIMIT=8GB

COVERBRANCHES_TIMELIMIT=300s
COVERBRANCHES_MEMLIMIT=8GB

TESTCOV_ERRORCALL_TIMELIMIT=180s
TESTCOV_ERRORCALL_MEMLIMIT=7GB

TESTCOV_COVERBRANCHES_TIMELIMIT=180s
TESTCOV_COVERBRANCHES_MEMLIMIT=7GB

TIMELIMIT_UNREACH_CALL=300s
MEMLIMIT_UNREACH_CALL=8GB

TIMELIMIT_NO_OVERFLOW=300s
MEMLIMIT_NO_OVERFLOW=8GB

TIMELIMIT_TERMINATION=300s
MEMLIMIT_TERMINATION=8GB

TIMELIMIT_VALID_MEMCLEANUP=300s
MEMLIMIT_VALID_MEMCLEANUP=8GB

TIMELIMIT_VALID_MEMSAFETY=300s
MEMLIMIT_VALID_MEMSAFETY=8GB
#-----------------------

FUSEBMC_HOME=$(realpath "$FUSEBMC_HOME")
TESTCOV_HOME=$(realpath "$TESTCOV_HOME")
#CPACHECKER_HOME=$(realpath "$CPACHECKER_HOME")
#UAUTOMIZER_HOME=$(realpath "$UAUTOMIZER_HOME")
reqFilesArr=("${FUSEBMC_HOME}/FuSeBMC_engines/ESBMC/esbmc" "${FUSEBMC_HOME}/FuSeBMC_engines/ESBMC_concurrency/esbmc" "${FUSEBMC_HOME}/FuSeBMC_engines/ESBMC_SVCOMP/esbmc")
for fil in ${reqFilesArr[@]}; do
	if [ ! -f "${fil}" ]; then
		echo "-${fil}- does not exist"
		exit 1
	fi
done
(trap - INT; exit 1)  # susceptible to ctrl+c
OUTDIR=./results-verified/run/
if ! [ -d "$FUSEBMC_HOME" ]; then
	echo "'$FUSEBMC_HOME' does not exists or not a directory."
	exit 1
fi
if ! [ -d "$BENCHEXEC_HOME" ]; then
	echo "$BENCHEXEC_HOME does not exists or not a directory."
	exit 1
fi
if ! [ -d "$TESTCOV_HOME" ]; then
	echo "$TESTCOV_HOME does not exists or not a directory."
	exit 1
fi
#if ! [ -d "$CPACHECKER_HOME" ]; then
#	echo "$CPACHECKER_HOME does not exists or not a directory."
#	exit 1
#fi
#if ! [ -d "$UAUTOMIZER_HOME" ]; then
#	echo "$UAUTOMIZER_HOME does not exists or not a directory."
#	exit 1
#fi
if [ "$#" -ne 2 ]; then
	echo "Illegal number of parameters"
	echo "useage:$0 operation runName"
	echo "ex: $0 coverage-error-call 0001"
	exit 1
fi
op=$1
#runName=$2

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


if [ -d "$OUTDIR" ]; then
	echo "'$OUTDIR' exists;........"
	dt=$(date +%d-%m-%y-%H-%M-%S)
	echo "move to: ${dt}"
	mv "${OUTDIR}" "${OUTDIR}/../${dt}"
	#exit 1
fi
FUSEBMC_RUN=$2
re="^[0-9]+$"
if ! [[ "$FUSEBMC_RUN" =~ $re ]] ; then
	echo "${FUSEBMC_RUN} is not a number"
	exit 1
fi
printf -v FUSEBMC_RUN_STR "%05d" $FUSEBMC_RUN
OUTDIR_NEW=./results-verified/${op}_${FUSEBMC_RUN_STR}/
#NEW
mv "${OUTDIR_NEW}" "${OUTDIR}"

CSVFILE=${op}_${FUSEBMC_RUN_STR}.csv
DATASETDIR=./results-verified/dataset/
if ! [ -d "./results-verified/" ]; then
	mkdir ./results-verified/
	echo "Created: ./results-verified/"
fi

if ! [ -d "$DATASETDIR" ]; then
	mkdir $DATASETDIR
fi
echo "dataset directory: $DATASETDIR"
if [ -f "${DATASETDIR}${CSVFILE}" ]; then
	echo "'${DATASETDIR}${CSVFILE}' exists; please rename or move it."
	exit 1
fi
if [ -d "$OUTDIR_NEW" ]; then
	echo "'$OUTDIR_NEW' exists; please rename or move it."
	exit 1
fi
if ! [ -d ./sv-benchmarks ]; then
	echo "'./sv-benchmarks' does not exist; please create a soft link."
	exit 1
fi
if ! [ -f "./sv-benchmarks/c/my_${op}.set" ]; then
	echo "./sv-benchmarks/c/my_${op}.set does not exist"
	exit 1
fi
function fCleanRun() {
	if [ "$op" != "coverage-error-call" ] || [ "$op" != "coverage-branches" ]; then
		filesArr=("instrumented_afl.c" "*.i" "fuSeBMC_reach_error.txt" "fuSeBMC_reach_error_tcgen.txt" \
		"info.xml" "FuSeBMC_Fuzzer_input_goals.txt" "*.exe" "instrumented_tracer.c" "goals_covered.txt" \
		"selective_inputs.txt")
		for f in ${filesArr[@]}; do
			find $OUTDIR -type f -name "${f}" -exec rm -f {} \;
		done
		dirsArr=("FuSeBMCFuzzerOutput*" "fusebmc_instrument_output" "seeds")
		for d in ${dirsArr[@]}; do
			find $OUTDIR -type d -name "${d}" -exec rm -rf {} \;
		done
	fi

}

function exitIfError() {
	if ! [ $? -eq 0 ]; then
	echo "myERROR: ${1}"
	exit 1
fi
}

#./ParamsInTemplateReplacer.py --property $op --run-num $FUSEBMC_RUN
#exitIfError "ERROR in: ./ParamsInTemplateReplacer.py --property ${op} --run-num ${FUSEBMC_RUN}"

if [ "$op" == "coverage-error-call" ]; then
	#$BENCHEXEC_HOME/bin/benchexec ./FuSeBMC-testcomp.xml --tool-directory $FUSEBMC_HOME/ --no-container --numOfThreads $numOfThreads \
	#	--no-tmpfs --no-compress-results -c -1 -d --timelimit $ERRORCALL_TIMELIMIT --walltimelimit $ERRORCALL_TIMELIMIT \
	#	--memorylimit $ERRORCALL_MEMLIMIT  -r Coverage-Error-Call -t my_coverage-error-call \
	# 
	#	-o $OUTDIR --name $FUSEBMC_RUN_STR
	
	#find $OUTDIR -name "test-suite" -exec  zip -r -j {}/../../test-suite.zip {} \;
	
	$BENCHEXEC_HOME/bin/benchexec  ./TestCov.xml --tool-directory $TESTCOV_HOME/ --no-container --numOfThreads $numOfThreads \
		--no-tmpfs  --no-compress-results -c -1 -d \
		--timelimit $TESTCOV_ERRORCALL_TIMELIMIT --walltimelimit $TESTCOV_ERRORCALL_TIMELIMIT \
		--memorylimit $TESTCOV_ERRORCALL_MEMLIMIT -r Coverage-Error-Call -t my_coverage-error-call \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
		
	./mergeResult2.py \
		${OUTDIR}FuSeBMC*.xml \
		${OUTDIR}TestCov*.xml
fi

if [ "$op" == "coverage-branches" ]; then
	#$BENCHEXEC_HOME/bin/benchexec ./FuSeBMC-testcomp.xml --tool-directory $FUSEBMC_HOME/ --no-container --numOfThreads $numOfThreads \
	#	--no-tmpfs --no-compress-results -c -1 -d --timelimit $COVERBRANCHES_TIMELIMIT --walltimelimit $COVERBRANCHES_TIMELIMIT \
	#	--memorylimit $COVERBRANCHES_MEMLIMIT -r Coverage-Branches -t my_coverage-branches \
	#	-o $OUTDIR --name $FUSEBMC_RUN_STR
	#exitIfError "benchexec"
	#find $OUTDIR -name "test-suite" -exec  zip -r -j {}/../../test-suite.zip {} \;
	
	$BENCHEXEC_HOME/bin/benchexec ./TestCov.xml --tool-directory $TESTCOV_HOME/ --no-container --numOfThreads $numOfThreads \
		--no-tmpfs  --no-compress-results -c -1 -d \
		--timelimit $TESTCOV_COVERBRANCHES_TIMELIMIT --walltimelimit $TESTCOV_COVERBRANCHES_TIMELIMIT \
		--memorylimit $TESTCOV_COVERBRANCHES_MEMLIMIT -r Coverage-Branches -t my_coverage-branches \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
	#exitIfError "benchexec"
	./mergeResult2.py \
		${OUTDIR}FuSeBMC*.xml \
		${OUTDIR}TestCov*.xml
	#exitIfError "mergeResult2.py"


fi

if [ "$op" == "unreach-call" ]; then
	$BENCHEXEC_HOME/bin/benchexec ./FuSeBMC-svcomp.xml --tool-directory $FUSEBMC_HOME/ --no-container --numOfThreads $numOfThreads \
		--no-tmpfs --no-compress-results -c -1 -d --timelimit $TIMELIMIT_UNREACH_CALL --walltimelimit $TIMELIMIT_UNREACH_CALL \
		--memorylimit $MEMLIMIT_UNREACH_CALL -r unreach-call -t my_unreach-call \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
	
	: '
	$BENCHEXEC_HOME/bin/benchexec  ./cpachecker-validate-correctness-witnesses.xml --tool-directory $CPACHECKER_HOME/ --no-container \
		--no-tmpfs  --no-compress-results -c -1 -d \
		--timelimit $TESTCOV_ERRORCALL_TIMELIMIT --walltimelimit $TESTCOV_ERRORCALL_TIMELIMIT \
		--memorylimit $TESTCOV_ERRORCALL_MEMLIMIT -r unreach-call -t my_unreach-call \
		-o ./results-verified/$FUSEBMC_RUN/ --name $FUSEBMC_RUN
	
	$BENCHEXEC_HOME/bin/benchexec  ./cpachecker-validate-violation-witnesses.xml --tool-directory $CPACHECKER_HOME/ --no-container \
		--no-tmpfs  --no-compress-results -c -1 -d \
		--timelimit $TESTCOV_ERRORCALL_TIMELIMIT --walltimelimit $TESTCOV_ERRORCALL_TIMELIMIT \
		--memorylimit $TESTCOV_ERRORCALL_MEMLIMIT -r unreach-call -t my_unreach-call \
		-o ./results-verified/$FUSEBMC_RUN/ --name $FUSEBMC_RUN
	
	$BENCHEXEC_HOME/bin/benchexec  ./cpa-witness2test-validate-violation-witnesses.xml --tool-directory $CPACHECKER_HOME/ --no-container \
		--no-tmpfs  --no-compress-results -c -1 -d \
		--timelimit $TESTCOV_ERRORCALL_TIMELIMIT --walltimelimit $TESTCOV_ERRORCALL_TIMELIMIT \
		--memorylimit $TESTCOV_ERRORCALL_MEMLIMIT -r unreach-call -t my_unreach-call \
		-o ./results-verified/$FUSEBMC_RUN/ --name $FUSEBMC_RUN
	
	PATH=$PATH:$UAUTOMIZER_HOME
	$BENCHEXEC_HOME/bin/benchexec  ./uautomizer-validate-correctness-witnesses.xml --tool-directory $UAUTOMIZER_HOME/ --no-container \
		--no-tmpfs  --no-compress-results -c -1 -d \
		--timelimit $TESTCOV_ERRORCALL_TIMELIMIT --walltimelimit $TESTCOV_ERRORCALL_TIMELIMIT \
		--memorylimit $TESTCOV_ERRORCALL_MEMLIMIT -r unreach-call -t my_unreach-call \
		-o ./results-verified/$FUSEBMC_RUN/ --name $FUSEBMC_RUN
	'
	#./adjust_results_validators.py \
	#	results-verified/$FUSEBMC_RUN/FuSeBMC*.xml \
	#	results-verified/$FUSEBMC_RUN/cpa-witness2test-validate-violation-witnesses.*.xml \
	#	results-verified/$FUSEBMC_RUN/uautomizer-validate-correctness-witnesses.*.xml
	#	#results-verified/$FUSEBMC_RUN/cpachecker-validate-correctness-witnesses.*.xml
	#	#results-verified/$FUSEBMC_RUN/cpachecker-validate-violation-witnesses.*.xml \
	
fi
if [ "$op" == "no-overflow" ]; then
	$BENCHEXEC_HOME/bin/benchexec ./FuSeBMC-svcomp.xml --tool-directory $FUSEBMC_HOME/ --no-container --numOfThreads $numOfThreads \
		--no-tmpfs --no-compress-results -c -1 -d --timelimit $TIMELIMIT_NO_OVERFLOW --walltimelimit $TIMELIMIT_NO_OVERFLOW \
		--memorylimit $MEMLIMIT_NO_OVERFLOW -r no-overflow -t my_no-overflow \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
fi
if [ "$op" == "termination" ]; then
	$BENCHEXEC_HOME/bin/benchexec ./FuSeBMC-svcomp.xml --tool-directory $FUSEBMC_HOME/ --no-container --numOfThreads $numOfThreads \
		--no-tmpfs --no-compress-results -c -1 -d --timelimit $TIMELIMIT_TERMINATION --walltimelimit $TIMELIMIT_TERMINATION \
		--memorylimit $MEMLIMIT_TERMINATION -r termination -t my_termination \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
fi
if [ "$op" == "valid-memcleanup" ]; then
	$BENCHEXEC_HOME/bin/benchexec ./FuSeBMC-svcomp.xml --tool-directory $FUSEBMC_HOME/ --no-container --numOfThreads $numOfThreads \
		--no-tmpfs --no-compress-results -c -1 -d --timelimit $TIMELIMIT_VALID_MEMCLEANUP --walltimelimit $TIMELIMIT_VALID_MEMCLEANUP \
		--memorylimit $MEMLIMIT_VALID_MEMCLEANUP -r valid-memcleanup -t my_valid-memcleanup \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
fi
if [ "$op" == "valid-memsafety" ]; then
	$BENCHEXEC_HOME/bin/benchexec ./FuSeBMC-svcomp.xml --tool-directory $FUSEBMC_HOME/ --no-container --numOfThreads $numOfThreads \
		--no-tmpfs --no-compress-results -c -1 -d --timelimit $TIMELIMIT_VALID_MEMSAFETY --walltimelimit $TIMELIMIT_VALID_MEMSAFETY \
		--memorylimit $MEMLIMIT_VALID_MEMSAFETY -r valid-memsafety -t my_valid-memsafety \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
fi

exitIfError "benchexec"

if [ "$op" == "coverage-error-call" ] || [ "$op" == "coverage-branches" ]; then
	
	./FeatureFromXMLResultExtractor.py ${OUTDIR}FuSeBMC*.xml.fixed.xml \
		--hide-fusebmc-features yes --csvFeaturesFile ${OUTDIR}${CSVFILE}
	exitIfError "FeatureFromXMLResultExtractor"
	
	$BENCHEXEC_HOME/bin/table-generator --outputpath $OUTDIR \
	${OUTDIR}FuSeBMC*.xml.fixed.xml \
	${OUTDIR}TestCov.*.xml \
	--name ${op}_${FUSEBMC_RUN_STR}_res
	
elif [ "$op" == "no-overflow" ] || \
	[ "$op" == "termination" ] || \
	[ "$op" == "valid-memcleanup" ] || \
	[ "$op" == "valid-memsafety" ] || \
	[ "$op" == "unreach-call" ]; then
	
	./FeatureFromXMLResultExtractor.py ${OUTDIR}/FuSeBMC*.xml \
		--hide-fusebmc-features yes --csvFeaturesFile ${OUTDIR}${CSVFILE}
	
	exitIfError "FeatureFromXMLResultExtractor"
	
	find $OUTDIR -type f -name "*.graphml" -execdir cp -t ../../ {} +
	
	$BENCHEXEC_HOME/bin/table-generator --outputpath $OUTDIR \
	${OUTDIR}FuSeBMC*.xml \
	--name ${op}_${FUSEBMC_RUN_STR}_res

fi
	
rm -f ./instrumented_*.gcov harness.c.gcov

cp ${OUTDIR}${CSVFILE} $DATASETDIR
fCleanRun
mv $OUTDIR $OUTDIR_NEW
echo "results in: $OUTDIR_NEW"
echo "Dataset: ${DATASETDIR}${CSVFILE}"
echo "Done !!!"
