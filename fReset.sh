#!/bin/bash
#scriptDir=$(dirname "$0")
dirArr=("./../FuSeBMC_svcomp_plain" "./../FuSeBMC_testcomp_plain")
for scriptDir in ${dirArr[@]}; do
	#don't use -r ehrn deleting Symlink
	rm -f "${scriptDir}/sv-benchmarks"
	rm -f "${scriptDir}/benchexec-master"
	rm -f "${scriptDir}/val_testcov_3.5"
	rm -f "${scriptDir}/benchmark-defs"
	rm -f "${scriptDir}/testcomp22_svcomp22"
	rm -f "${scriptDir}/FuSeBMC_engines"
	resFilesCount=$(ls ${scriptDir}/results-verified/* | wc -l)
	echo "${scriptDir}/results-verified/ has ${resFilesCount} files(s)"
	if [ "$resFilesCount" != "0" ]; then
		read -p "Do you want to clear ${scriptDir}/results-verified/* y|n?" answer
		if [ "$answer" == "y" ]; then
			echo "delete ...."
			sudo rm -rf ${scriptDir}/results-verified/*
		fi
	fi
	
	rm -f "${scriptDir}/esbmc"
	rm -f "${scriptDir}/TestCov.xml"
	rm -f "${scriptDir}/mergeResult2.py"
	rm -f "${scriptDir}/fSetup.sh"
	rm -f "${scriptDir}/runTrainTest.sh"
	rm -f "${scriptDir}/FuSeBMC-svcomp.xml"
	rm -f "${scriptDir}/FuSeBMC-testcomp.xml"
done
echo "${0} Done ..... !!!"
exit 0

function isCoverageBranchesIgnore() {
	#echo "Your first params $1"
	ignoreArr=("00008")
	for n in ${ignoreArr[@]}; do
		if [ "$n" == "$1" ]; then
			echo 1
			return 0
		fi
	done
	echo -1
}	
cbArr1=("00463")
	echo "count=${#cbArr1[@]}"
	#exit 0
	i=0
	for f in ${cbArr1[@]}; do
		isIgnore=$(isCoverageBranchesIgnore $FUSEBMC_RUN_STR)
		if [ "$isIgnore" == "-1" ]; then
			i=$((i+1))
			if [ "$i" == "11" ]; then
				i=0
				echo "\"${f}\" \\"
			else
				echo -ne "\"${f}\" "
			fi
			
		fi
	done
	i=0
	for f in ${cbArr2[@]}; do
		i=$((i+1))
		#./runTrainTestBulk.sh coverage-branches $f $f
		echo $i
	done
exit 0
	
while true; do
	# checks if a patch tar file exists and if yes then do patching
	sleep 1
	echo do8
done

exit 0
numOfThreads=5
numOfThreadsTestCov=1
FUSEBMC_HOME=./
BENCHEXEC_HOME=./benchexec-master
TESTCOV_HOME=./val_testcov_3.5/testcov
#CPACHECKER_HOME=./CPAchecker-2.1-unix
#UAUTOMIZER_HOME=./UAutomizer-linux

##### BEGIN DELETE ######
numOfThreads=1
##### END DELETE ######
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

if ! [ -d ./results-verified/ ]; then
	mkdir ./results-verified/
	echo "Created: ./results-verified/"
fi

if [ -d "$OUTDIR" ]; then
	echo "'$OUTDIR' exists; please rename or move it."
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
FUSEBMC_RUN=$((10#$FUSEBMC_RUN))
printf -v FUSEBMC_RUN_STR "%05d" $FUSEBMC_RUN
OUTDIR_NEW=./results-verified/${op}_${FUSEBMC_RUN_STR}/
CSVFILE=${op}_${FUSEBMC_RUN_STR}.csv
DATASETDIR=./results-verified/dataset/


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
function isCoverageBranchesIgnore() {
	#echo "Your first params $1"
	ignoreArr=("00008" "00009" "00010" "00011" "00012" "00013" "00014" "00029" "00030" "00031" "00032" "00033" "00034" "00035" "00050" "00051" "00052" "00053" "00054" "00055" "00056" "00071" "00072" "00073" "00074" "00075" "00076" "00077" "00085" "00086" "00087" "00088" "00089" "00090" "00091" "00092" "00093" "00094" "00095" "00096" "00097" "00098" "00099" "00100" "00101" "00102" "00103" "00104" "00105" "00106" "00107" "00108" "00109" "00110" "00111" "00112" "00113" "00114" "00115" "00116" "00117" "00118" "00119" "00120" "00121" "00122" "00123" "00124" "00125" "00126" "00134" "00135" "00136" "00137" "00138" "00139" "00140" "00155" "00156" "00157" "00158" "00159" "00160" "00161" "00176" "00177" "00178" "00179" "00180" "00181" "00182" "00197" "00198" "00199" "00200" "00201" "00202" "00203" "00218" "00219" "00220" "00221" "00222" "00223" "00224" "00239" "00240" "00241" "00242" "00243" "00244" "00245" "00253" "00254" "00255" "00256" "00257" "00258" "00259" "00260" "00261" "00262" "00263" "00264" "00265" "00266" "00267" "00268" "00269" "00270" "00271" "00272" "00273" "00274" "00275" "00276" "00277" "00278" "00279" "00280" "00281" "00282" "00283" "00284" "00285" "00286" "00287" "00288" "00289" "00290" "00291" "00292" "00293" "00294" "00302" "00303" "00304" "00305" "00306" "00307" "00308" "00323" "00324" "00325" "00326" "00327" "00328" "00329" "00344" "00345" "00346" "00347" "00348" "00349" "00350" "00365" "00366" "00367" "00368" "00369" "00370" "00371" "00386" "00387" "00388" "00389" "00390" "00391" "00392" "00407" "00408" "00409" "00410" "00411" "00412" "00413" "00421" "00422" "00423" "00424" "00425" "00426" "00427" "00428" "00429" "00430" "00431" "00432" "00433" "00434" "00435" "00436" "00437" "00438" "00439" "00440" "00441" "00442" "00443" "00444" "00445" "00446" "00447" "00448" "00449" "00450" "00451" "00452" "00453" "00454" "00455" "00456" "00457" "00458" "00459" "00460" "00461" "00462" "00470" "00471" "00472" "00473" "00474" "00475" "00476" "00491" "00492" "00493" "00494" "00495" "00496" "00497" "00512" "00513" "00514" "00515" "00516" "00517" "00518" "00533" "00534" "00535" "00536" "00537" "00538" "00539" "00554" "00555" "00556" "00557" "00558" "00559" "00560" "00575" "00576" "00577" "00578" "00579" "00580" "00581" "00596" "00597" "00598" "00599" "00600" "00601" "00602" "00617" "00618" "00619" "00620" "00621" "00622" "00623" "00625" "00626" "00627" "00628" "00629" "00630" "00631" "00632" "00633" "00634" "00635" "00636" "00637" "00638" "00639" "00640" "00641" "00642" "00643" "00644" "00645" "00646" "00647" "00648" "00649" "00650" "00651" "00652" "00709" "00710" "00711" "00712" "00713" "00714" "00715" "00716" "00717" "00718" "00719" "00720" "00721" "00722" "00723" "00724" "00725" "00726" "00727" "00728" "00729" "00730" "00731" "00732" "00733" "00734" "00735" "00736" "00793" "00794" "00795" "00796" "00797" "00798" "00799" "00800" "00801" "00802" "00803" "00804" "00805" "00806" "00807" "00808" "00809" "00810" "00811" "00812" "00813" "00814" "00815" "00816" "00817" "00818" "00819" "00820")
	for n in ${ignoreArr[@]}; do
		if [ "$n" == "$1" ]; then
			echo 1
			return 0
		fi
	done
	echo -1
}
if [ "$op" == "coverage-branches" ]; then
	isIgnore=$(isCoverageBranchesIgnore $FUSEBMC_RUN_STR)
	if [ "$isIgnore" == "1" ]; then
		mkdir $OUTDIR_NEW
		echo "${op}_${FUSEBMC_RUN_STR}" > "${OUTDIR_NEW}/ignore.txt"
		echo "must ignore this run:${op}_${FUSEBMC_RUN_STR}"
		exit 0
	fi
fi

#echo "after loop: ${FUSEBMC_RUN_STR}"
#exit -8

function fCleanRun() {
	if [ "$op" == "coverage-error-call" ] || [ "$op" == "coverage-branches" ]; then
		filesArr=("instrumented_afl.c" "*.i" "fuSeBMC_reach_error.txt" "fuSeBMC_reach_error_tcgen.txt" \
		"info.xml" "FuSeBMC_Fuzzer_input_goals.txt" "*.exe" "instrumented_tracer.c" "goals_covered.txt" \
		"FuSeBMC_Fuzzer_output_goals.txt" "selective_inputs.txt")
		for f in ${filesArr[@]}; do
			find $OUTDIR -type f -name "${f}" -exec rm -f {} \;
		done
		dirsArr=("FuSeBMCFuzzerOutput*" "fusebmc_instrument_output" "seeds" "seeds2")
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
	$BENCHEXEC_HOME/bin/benchexec ./FuSeBMC-testcomp.xml --tool-directory $FUSEBMC_HOME/ --no-container --numOfThreads $numOfThreads \
		--no-tmpfs --no-compress-results -c -1 -d --timelimit $ERRORCALL_TIMELIMIT --walltimelimit $ERRORCALL_TIMELIMIT \
		--memorylimit $ERRORCALL_MEMLIMIT  -r Coverage-Error-Call -t my_coverage-error-call \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
	
	find $OUTDIR -type d -name "test-suite" -exec  zip -r -j {}/../../test-suite.zip {} \;
	
	$BENCHEXEC_HOME/bin/benchexec  ./TestCov.xml --tool-directory $TESTCOV_HOME/ --no-container --numOfThreads $numOfThreadsTestCov \
		--no-tmpfs  --no-compress-results -c -1 -d \
		--timelimit $TESTCOV_ERRORCALL_TIMELIMIT --walltimelimit $TESTCOV_ERRORCALL_TIMELIMIT \
		--memorylimit $TESTCOV_ERRORCALL_MEMLIMIT -r Coverage-Error-Call -t my_coverage-error-call \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
		
	./mergeResult2.py \
		${OUTDIR}FuSeBMC*.xml \
		${OUTDIR}TestCov*.xml
fi

if [ "$op" == "coverage-branches" ]; then
	$BENCHEXEC_HOME/bin/benchexec ./FuSeBMC-testcomp.xml --tool-directory $FUSEBMC_HOME/ --no-container --numOfThreads $numOfThreads \
		--no-tmpfs --no-compress-results -c -1 -d --timelimit $COVERBRANCHES_TIMELIMIT --walltimelimit $COVERBRANCHES_TIMELIMIT \
		--memorylimit $COVERBRANCHES_MEMLIMIT -r Coverage-Branches -t my_coverage-branches \
		-o $OUTDIR --name $FUSEBMC_RUN_STR
	exitIfError "benchexec"
	find $OUTDIR -type d -name "test-suite" -exec  zip -r -j {}/../../test-suite.zip {} \;
	
	$BENCHEXEC_HOME/bin/benchexec ./TestCov.xml --tool-directory $TESTCOV_HOME/ --no-container --numOfThreads $numOfThreadsTestCov \
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
