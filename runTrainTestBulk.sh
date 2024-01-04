#!/bin/bash

if [ "$#" -ne 3 ]; then
	echo "Illegal number of parameters"
	echo "useage:$0 operation runNum1 runNum2"
	echo "ex: $0 coverage-error-call 1 33"
	exit 1
fi
op=$1

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

FUSEBMC_RUN1=$2
FUSEBMC_RUN2=$3
FUSEBMC_RUN1=$((10#$FUSEBMC_RUN1))
FUSEBMC_RUN2=$((10#$FUSEBMC_RUN2))
re="^[0-9]+$"
if ! [[ "$FUSEBMC_RUN1" =~ $re ]] ; then
	echo "${FUSEBMC_RUN1} is not a number"
	exit 1
fi
if ! [[ "$FUSEBMC_RUN2" =~ $re ]] ; then
	echo "${FUSEBMC_RUN2} is not a number"
	exit 1
fi

#echo "FUSEBMC_RUN1=${FUSEBMC_RUN1}"
#echo "FUSEBMC_RUN2=${FUSEBMC_RUN2}"
#exit 0

if (( $FUSEBMC_RUN1 > $FUSEBMC_RUN2 )); then
	echo "Error: ${FUSEBMC_RUN1} is greater than ${FUSEBMC_RUN2}"
	exit 1
fi
function exitIfError() {
	if ! [ $? -eq 0 ]; then
	echo "myERROR: ${1}"
	exit 1
fi
}


for (( c=$FUSEBMC_RUN1; c<=$FUSEBMC_RUN2; c++ ))
do
	./ParamsInTemplateReplacer.py --property $op --run-num $c
	#exitIfError "ERROR in: ./ParamsInTemplateReplacer.py --property ${op} --run-num ${c}"
	if [ $? -eq 0 ]; then
		./runTrainTest.sh $op $c
	fi
	#exitIfError "./runTrainTest.sh ${op} ${c}"

done

echo "$0 Done !!!"
