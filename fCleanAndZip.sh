#!/bin/bash
echo "Hiii"
resultVeriDir=./results-verified

MyHOST=$(hostname)
echo "hostname: ${MyHOST}"
read -p "Is this Server10 or Server11 [10|11]?" servernr
echo "hostname: ${MyHOST}, servernr=${servernr}">${resultVeriDir}/myhost.txt
cp ./errorlog.log ${resultVeriDir}/
cp -r ./ml_test ${resultVeriDir}/
cp -r ./ml_models ${resultVeriDir}/

ZIPFILE=${resultVeriDir}/../fm${servernr}-$(date +%d-%m-%y.zip)
ZIPFILE=$(realpath "${ZIPFILE}")
echo "Zipping into ${ZIPFILE} ....."
zip -r ${ZIPFILE} ${resultVeriDir}
echo "----------------------"
echo "please, upload '${ZIPFILE}' to your local PC."
echo "${0} Done ..... !!!"
exit 0


if [ "$servernr" == "10" ]; then
	#has clang
	./runTrainTestBulkOnlyTestCov.sh coverage-branches
	#./runTrainTestBulkOnlyTestCov.sh coverage-error-call
	cbArr1=("00162" "00163" "00164" "00165" "00166" "00167" "00168" "00169" "00170" "00171" "00172")
	for f in ${cbArr1[@]}; do
		./runTrainTestBulk.sh coverage-branches $f $f
	done
	
	#./runTrainTestBulk.sh coverage-error-call 39 39
	./runTrainTestBulk.sh coverage-error-call 40 40
	
	# must copy set files
	setFilesArr=("my_coverage-error-call.set" "my_termination.set" "my_valid-memcleanup.set" "my_coverage-branches.set" "my_no-overflow.set" "my_unreach-call.set" "my_valid-memsafety.set")
	for fil in ${setFilesArr[@]}; do
		echo "cp ./testcomp22_svcomp22/y/${fil}" "${BENCHMARK}/c/"
		cp "./testcomp22_svcomp22/y/${fil}" "${BENCHMARK}/c/"
	done
	
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
	
elif [ "$servernr" == "11" ]; then
	#"00381" "00382" "00383" "00384" "00385" "00386" "00387" "00388" "00389" "00390" \
	#"00391" "00392" "00393" "00394" "00395" "00396" "00397" "00398" "00399" \
	#"00400" "00401" "00402" "00403" "00404" "00405" "00406" "00407" "00408" "00409" \
	#"00410" "00411" "00412" "00413" "00414" "00415" "00416" "00417" "00418" "00419" \
	#"00420" "00421" "00422" "00423" "00424" "00425" "00426" "00427" \
	#"00463" "00464" "00465" "00466" "00467" "00468"
	#80
	cbArr2=(\
	"00469" "00477" "00478" "00479" "00480")
	for f in ${cbArr2[@]}; do
		./runTrainTestBulk.sh coverage-branches $f $f
	done
	#./trainModels.sh ya
	# must copy set files
	setFilesArr=("my_coverage-error-call.set" "my_termination.set" "my_valid-memcleanup.set" "my_coverage-branches.set" "my_no-overflow.set" "my_unreach-call.set" "my_valid-memsafety.set")
	for fil in ${setFilesArr[@]}; do
		echo "cp ./testcomp22_svcomp22/y/${fil}" "${BENCHMARK}/c/"
		cp "./testcomp22_svcomp22/y/${fil}" "${BENCHMARK}/c/"
	done
	#DTC svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-dtc.xml ./FuSeBMC-svcomp.xml
	./runBenchmark.sh no-overflow dtc
	./runBenchmark.sh termination dtc
	./runBenchmark.sh valid-memcleanup dtc
	./runBenchmark.sh valid-memsafety dtc
	./runBenchmark.sh unreach-call dtc
	
	#SVC svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-svc.xml ./FuSeBMC-svcomp.xml
	./runBenchmark.sh no-overflow svc
	./runBenchmark.sh termination svc
	./runBenchmark.sh valid-memcleanup svc
	./runBenchmark.sh valid-memsafety svc
	./runBenchmark.sh unreach-call svc
	
	#NNR svcomp
	cp ./benchmark-defs/FuSeBMC-svcomp-nnr.xml ./FuSeBMC-svcomp.xml
	./runBenchmark.sh no-overflow nnr
	./runBenchmark.sh termination nnr
	./runBenchmark.sh valid-memcleanup nnr
	./runBenchmark.sh valid-memsafety nnr
	./runBenchmark.sh unreach-call nnr
	
else
	echo "${servernr} is not a valid value."
fi

#./runTrainTestBulk.sh coverage-error-call 625 378


echo "Done ..... !!!"
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
