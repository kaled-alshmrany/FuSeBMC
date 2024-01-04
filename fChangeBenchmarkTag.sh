#!/bin/bash
BENCHMARK=./sv-benchmarks
if ! [ -d "$BENCHMARK" ]; then
	echo "${BENCHMARK} does not exists or not a directory."
	exit 1
fi
newTag=empty
if [ "$#" -eq 1 ]; then
	newTag=$1
fi

myPWD=$PWD
cd $BENCHMARK
#echo "All Tags:"
#git tag -n
echo "All Branches"
git branch

echo "##########################"
echo "Current Tag:"
git describe --tags
echo "##########################"
if [ "$newTag" == "empty" ]; then
	read -p "Do you want to change the current tag y|n? " answer
	if [ "$answer" == "y" ]; then
		read -p "Enter the new tag: " newTag
		git checkout $newTag -b my${newTag}
		#git switch my${newTag}
		git checkout my${newTag}
	fi
else
	git checkout $newTag -b my${newTag}
	#git switch my${newTag}
	git checkout my${newTag}
fi

echo "##########################"
echo "Current Tag:"
git describe --tags
echo "##########################"
echo "All Branches"
git branch
echo "####### ${0} is Done !!! ###################"
cd $myPWD
exit 0
