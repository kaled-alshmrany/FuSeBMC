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
cp -r ./FuSeBMC_engines/AFL/ $dest/FuSeBMC_engines


cp -r ./examples/ $dest
rm $dest/examples/*.o
rm $dest/examples/*.exe

cp -r ./FuSeBMC_FuzzerLib/ $dest
rm $dest/FuSeBMC_FuzzerLib/obj32/*.o
rm $dest/FuSeBMC_FuzzerLib/obj64/*.o

cp -r ./FuSeBMC_TCGen/ $dest
rm $dest/FuSeBMC_TCGen/obj32/*.o
rm $dest/FuSeBMC_TCGen/obj64/*.o

cp -r ./FuSeBMC_GoalTracerLib/ $dest
rm $dest/FuSeBMC_GoalTracerLib/obj32/*.o
rm $dest/FuSeBMC_GoalTracerLib/obj64/*.o

cp -r ./FuSeBMC_instrument/ $dest
rm -rf $dest/FuSeBMC_instrument/build/*

cp -r ./FuSeBMC_SeedGenLib/ $dest
rm -rf $dest/FuSeBMC_SeedGenLib/obj32/*.o
rm -rf $dest/FuSeBMC_SeedGenLib/obj64/*.o

cp -r ./fusebmc_util/ $dest

#cp -r ./promc/ $dest

cp -r ./properties $dest
#cp -r ./seeds_extra $dest

cp ./fusebmc.py $dest
#cp ./fusebmc_cbmc_seed_gen.py $dest
cp ./fusebmc_compare_testcases.py $dest
cp ./fusebmc_getinput_from_testcase.py $dest
cp ./fusebmc_non_repeated_testcases.py $dest
cp ./fusebmc_seed_gen.py $dest
cp -r ./notes $dest
#cp -r ./ESBMC_last $dest
cp ./make-release.sh $dest
cp ./make-bin.sh $dest
echo "Done !!!"
