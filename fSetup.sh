#!/bin/bash

echo "Hiii"
VERSION=012
prevVersionDir=/tool/IAA/FuSeBMC_gui_015
MyHOST=$(hostname)
echo "hostname: ${MyHOST}"


myDF=$(df -h)
echo -e "Disk free:\n${myDF}"
echo "-----------------"
myFM=$(free -m)
echo -e  "Free mem:\n${myFM}"
echo "-----------------"

if ! [ -d "$prevVersionDir" ]; then
	echo "'${prevVersionDir}' does not exists or not a directory."
	exit 1
else
	echo "prevVersionDir=${prevVersionDir} is ok ..."
fi

#read -p "Do you want to replace 'val_testcov_3.5' in '${prevVersionDir}' y|n?" answer
#if [ "$answer" == "y" ]; then
#	myDT=$(date +%d-%m-%y)
#	mv ${prevVersionDir}/val_testcov_3.5 ${prevVersionDir}/val_testcov_3.5_single_thread_${myDT}
#	echo "moved to: ${prevVersionDir}/val_testcov_3.5_single_thread_${myDT}"
#	cp -r ./val_testcov_3.5 ${prevVersionDir}/
#	rm -rf ./val_testcov_3.5
#fi

read -p "Do you want to check 'clang-tidy' y|n?" answer
if [ "$answer" == "y" ]; then
	clang-tidy
fi
read -p "Do you want to kill esbmc,afl-fuzz proc. y|n?" answer
if [ "$answer" == "y" ]; then
	procArr=("esbmc" "afl-fuzz" "afl.exe" "tcgen.exe" "tracer.exe" "seedGenExe.exe")
	for p in "${procArr[@]}"; do
		myProc=$(ps -A | grep $p)
		if [ "$myProc" != "" ]; then
			echo "$myProc"
			killall $p
		else
			echo "no ${p} is running"
		fi
	done
fi


read -p "create Symlink for benchexec-master. y|n?" answer
if [ "$answer" == "y" ]; then
	echo "Symlink for benchexec-master ..."
	ln -s ${prevVersionDir}/benchexec-master ./benchexec-master
fi

read -p "create Symlink for FuSeBMC_engines. y|n?" answer
if [ "$answer" == "y" ]; then
	echo "Symlink for FuSeBMC_engines ..."
	ln -s ${prevVersionDir}/FuSeBMC_engines ./FuSeBMC_engines
fi

read -p "create Symlink for val_testcov_3.5. y|n?" answer
if [ "$answer" == "y" ]; then
	echo "Symlink for val_testcov_3.5 ..."
	ln -s ${prevVersionDir}/val_testcov_3.5 ./val_testcov_3.5
fi
read -p "create Symlink for FuSeBMC_instrument. y|n?" answer
if [ "$answer" == "y" ]; then
	echo "Symlink for FuSeBMC_instrument ..."
	ln -s ${prevVersionDir}/FuSeBMC_instrument ./FuSeBMC_instrument
fi

BENCHMARK=./sv-benchmarks
if ! [ -d "$BENCHMARK" ]; then
	echo "'${BENCHMARK}' does not exists or not a directory."
	read -p "Do you want to create Symbolic link from '/tool/sv-benchmarks/' y|n?" answer
	if [ "$answer" == "y" ]; then
		ln -s /tool/sv-benchmarks/ "${BENCHMARK}"
	fi
fi

if ! [ -d "$BENCHMARK" ]; then
	echo "'${BENCHMARK}' does not exists or not a directory."
	exit 1
fi

if ! [ -d "./results-verified/" ]; then
	mkdir ./results-verified/
	echo "Created: ./results-verified/"
fi

sklearnV=$(python3 -c "import sklearn; print (sklearn.__version__)")
sklearnVRoot=$(sudo python3 -c "import sklearn; print (sklearn.__version__)")
echo "sklearnV -> ${sklearnV}" > ./results-verified/sklearnV.txt
echo "sklearnVRoot -> ${sklearnVRoot}" >> ./results-verified/sklearnV.txt
cat ./results-verified/sklearnV.txt

read -p "check branch testcomp22. y|n?" answer
if [ "$answer" == "y" ]; then
	./fChangeBenchmarkTag.sh testcomp22
fi

read -p "check branch svcomp22. y|n?" answer
if [ "$answer" == "y" ]; then
	./fChangeBenchmarkTag.sh svcomp22
fi
echo "cp -r ./fvs ./sv-benchmarks/c/"
cp -r ./fvs ./sv-benchmarks/c/

if [ "$MyHOST" == "a01af3894c6e" ]; then
	echo "I think, this is fm10"
elif [ "$MyHOST" == "bdd6976912a3" ]; then
	echo "I think, this is fm11"
fi
read -p "Is this Server10 or Server11 [10|11]?" servernr

if [ "$servernr" == "10" ]; then
	read -p "prepair plain. y|n?" answer
	if [ "$answer" == "y" ]; then
		./prepairPlain.sh
	fi
elif [ "$servernr" == "11" ]; then
	echo "hello ${servernr} .."
fi
#read -p "Do you want to install \"scikit-learn\" and \"pandas\" as root? y|n? " answer
#if [ "$answer" == "y" ]; then
#	sudo -H pip3 install scikit-learn pandas
#fi


#read -p "Do you want to trainModels as root? y|n? " answer
#if [ "$answer" == "y" ]; then
#	sudo ./trainModels.sh
#fi

echo "$0 Done ..... !!!"
exit 0
