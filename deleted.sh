#!/bin/bash -x
#ESBMC=/home/kaled/sdb1/esbmc+python-v6.0.0-linux-static-64/bin/esbmc
ESBMC=/home/kaled/Desktop/esbmc-v6.0/bin/esbmc
#FILE=/home/kaled/sdb1/uFTP/main.c
FILE=./examples/a.cpp
PARAMS='-I/home/kaled/Desktop/experment_10_02_2020/uFTP -I/home/kaled/Desktop/experment_10_02_2020/uFTP/library --no-div-by-zero-check --force-malloc-success --state-hashing --no-align-check --k-step 5 --floatbv --no-slice --show-cex --unwind 4 --max-k-step 10 --context-bound 2 --32 --incremental-bmc --no-pointer-check --no-bounds-check --interval-analysis --no-slice '
#FILE=$1
mypwd=$(pwd)
rm -r ./output/*
#rm -r ./myout/*
mkdir ./output/goals
mkdir ./output/goals_out
mkdir ./output/test-suite

#bin/condtest --spec tool_templates/coverage-branches.prp --testers cpa-tiger  --timelimit-testers 300 --no-cycle --debug $FILE
#bin/condtest --spec tool_templates/coverage-branches.prp --debug $FILE
#-nogoalProFunc
./my_instrument $FILE ./output/instrumented.c ./output/my_goals.txt -nogoalProFunc
ARCH='32'
PROPERTY_FILE=p_reach
#"kinduction", "falsi", "incr"
STRATEGY='incr'
goals_count=$(cat "./output/my_goals.txt") 

echo $goals_count
for goal in $(seq 1 $goals_count);
do
 
  $ESBMC $PARAMS --error-label GOAL_${goal} --witness-output ./output/goals/GOAL_${goal}.graphml ./output/instrumented.c
  ./my_esbmc_wrapper.py --arch $ARCH --strategy $STRATEGY -p $PROPERTY_FILE --witnessfile ./output/goals/GOAL_${goal}.graphml --testcasefile ./output/test-suite/GOAL_${goal}.xml ./output/instrumented.c
done

cd $mypwd
