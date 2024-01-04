#!/bin/bash
echo "------------------------------------------------"
answer=empty
if [ "$#" -eq 1 ]; then
	if [ "$1" != "x" ] && \
		[ "$1" != "y" ] && \
		[ "$1" != "min" ] && \
		[ "$1" != "full" ]; then
		echo "${1} is invalid value[x|y|min|full]"
		exit 1
	fi
	answer=$1
fi
BENCHMARK=./sv-benchmarks
if [ "$answer" == "empty" ]; then
	read -p "copy from x|y|min|full? " answer
fi

if [ "$answer" != "x" ] && [ "$answer" != "y" ] && [ "$answer" != "min" ] && [ "$answer" != "full" ]; then
	echo "${answer} is invalid value[x|y|min|full]"
	exit 1
fi
setFilesArr=("my_coverage-error-call.set" "my_termination.set" "my_valid-memcleanup.set" \
			"my_coverage-branches.set" "my_no-overflow.set" "my_unreach-call.set" "my_valid-memsafety.set")
	for fil in ${setFilesArr[@]}; do
		echo "cp ./testcomp22_svcomp22/${answer}/${fil}" "${BENCHMARK}/c/"
		cp "./testcomp22_svcomp22/${answer}/${fil}" "${BENCHMARK}/c/"
	done
echo "$0 is Done ...."
echo "------------------------------------------------"
exit 0
