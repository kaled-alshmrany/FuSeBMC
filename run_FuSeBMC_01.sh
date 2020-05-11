#!/bin/bash -v
#ESBMC=/home/kaled/Desktop/esbmc-v6.0/bin/esbmc
ESBMC=/home/kaled/Desktop/ESBMC-6.2.0-Linux/bin/esbmc

FILE=../../sv-benchmarks-testcomp20/c/array-examples/data_structures_set_multi_proc_ground-1.i

ESBMC_PARAMS='--show-cex --unwind 4 --k-step 5 --no-slice --max-k-step 20 '


rm -r ./output/*
#rm -r ./myout/*
mkdir ./output/goals
mkdir ./output/goals_out
mkdir ./output/test-suite

#-nogoalProFunc
#./output/goals_out
./FuSeBMC $FILE ./output/instrumented.c ./output/my_goals.txt  -nogoalProFunc
ARCH='32'
PROPERTY_FILE=p_reach
#PROPERTY_FILE=p_memory
#PROPERTY_FILE=p_overflow
#PROPERTY_FILE=p_reach2
#PROPERTY_FILE=p_termination
#PROPERTY_FILE=p_unknown

#"kinduction", "falsi", "incr"
STRATEGY='incr'
if [ ! -f "./output/my_goals.txt" ]; then
        echo "./output/my_goals.txt does not exist"
else
    goals_count=$(cat "./output/my_goals.txt") 
    echo $goals_count
    for goal in $(seq 1 $goals_count);
    do
        NEW_PARAMS="' $ESBMC_PARAMS --error-label GOAL_${goal}  '"
        echo ./my_esbmc_wrapper.py --arch $ARCH --strategy $STRATEGY -p $PROPERTY_FILE --witnessfile ./output/goals/GOAL_${goal}.graphml --testcasefile ./output/test-suite/GOAL_${goal}.xml --esbmcargs $NEW_PARAMS ./output/instrumented.c
        ./my_esbmc_wrapper.py --arch $ARCH --strategy $STRATEGY -p $PROPERTY_FILE --witnessfile ./output/goals/GOAL_${goal}.graphml --testcasefile ./output/test-suite/GOAL_${goal}.xml --esbmcargs " $NEW_PARAMS " ./output/instrumented.c
    done
fi
