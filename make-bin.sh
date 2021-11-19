#!/bin/sh
if [ "$#" -ne 1 ]; then
	echo "Illegal number of parameters"
	echo "useage:$0 release_dir"
	echo "ex: $0 /home/rel1"
	return
fi
dest=$1
if [ ! -d "$dest" ]; then
	echo "$dest is not a valid directory."
	return
fi
echo "Go ..."

mkdir $dest/FuSeBMC_engines
mkdir $dest/FuSeBMC_engines/ESBMC
mkdir $dest/FuSeBMC_engines/AFL
cp ./FuSeBMC_engines/ESBMC/esbmc $dest/FuSeBMC_engines/ESBMC/

cp ./FuSeBMC_engines/AFL/LICENSE $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/README.md $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-clang-fast $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-clang-fast++ $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-llvm-pass.so $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-llvm-rt.o $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-llvm-rt-32.o $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-llvm-rt-64.o $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-clang $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-clang++ $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-g++ $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-gcc $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-as $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/as $dest/FuSeBMC_engines/AFL/
cp ./FuSeBMC_engines/AFL/afl-fuzz $dest/FuSeBMC_engines/AFL/


mkdir $dest/FuSeBMC_FuzzerLib
cp ./FuSeBMC_FuzzerLib/libFuSeBMC_FuzzerLib_32.a $dest/FuSeBMC_FuzzerLib/
cp ./FuSeBMC_FuzzerLib/libFuSeBMC_FuzzerLib_64.a $dest/FuSeBMC_FuzzerLib/

mkdir $dest/FuSeBMC_TCGen
cp ./FuSeBMC_TCGen/libFuSeBMC_TCGen_32.a $dest/FuSeBMC_TCGen/
cp ./FuSeBMC_TCGen/libFuSeBMC_TCGen_64.a $dest/FuSeBMC_TCGen/

mkdir $dest/FuSeBMC_GoalTracerLib
cp ./FuSeBMC_GoalTracerLib/libFuSeBMC_GoalTracerLib_32.a $dest/FuSeBMC_GoalTracerLib/
cp ./FuSeBMC_GoalTracerLib/libFuSeBMC_GoalTracerLib_64.a $dest/FuSeBMC_GoalTracerLib/

mkdir $dest/FuSeBMC_instrument
cp -r ./FuSeBMC_instrument/external_include $dest/FuSeBMC_instrument/
cp ./FuSeBMC_instrument/myincludes.txt $dest/FuSeBMC_instrument/
cp ./FuSeBMC_instrument/FuSeBMC_instrument $dest/FuSeBMC_instrument/

mkdir $dest/FuSeBMC_SeedGenLib
cp ./FuSeBMC_SeedGenLib/libFuSeBMC_SeedGenLib_32.a $dest/FuSeBMC_SeedGenLib/
cp ./FuSeBMC_SeedGenLib/libFuSeBMC_SeedGenLib_64.a $dest/FuSeBMC_SeedGenLib/

cp -r ./fusebmc_util/ $dest
rm -rf $dest/fusebmc_util/__pycache__/*.*

echo "'./properties' folder will be not copied !!!"

cp ./fusebmc.py $dest
echo "'fusebmc_non_repeated_testcases.py' will be not copied !!!"
echo "Please; put 'LICENSE.TXT' file in $dest"
echo "Please; disable:\n\t IS_DEBUG,\n\t SHOW_ME_OUTPUT,\n\t RUN_TESTCOV.\n\t COVERBRANCHES_SHOW_UNIQUE_TESTCASES."
echo "Please; enable: \n\t COVERBRANCHES_HANDLE_REPEATED_TESTCASES_ENABLED,\n\t FuSeBMCFuzzerLib_ERRORCALL_RUN2_ENABLED, \n\t FuSeBMCFuzzerLib_COVERBRANCHES_RUN2_ENABLED."
echo "Please, make a test for this version !!!"
echo "Done !!!"
