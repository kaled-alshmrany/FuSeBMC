#!/bin/bash
echo "--------- START $0 $1 ---------------------------------------"
if [ "$#" -ne 1 ]; then
	echo "Illegal number of parameters"
	echo "useage:$0  serverName"
	echo "ex: $0 10"
	exit 1
fi

serverName=$1
if [ "$serverName" != "10" ] && [ "$serverName" != "11" ] && [ "$serverName" != "local" ]; then
	echo "${serverName} is invalid value [10|11|local]"
	exit 1
fi
modelsDir=./ml_models
if [ ! -d "$modelsDir" ]; then
	echo "${modelsDir} is not a valid directory."
	exit 1
fi

rm -f ./${modelsDir}/dtc/*.*
rm -f ./${modelsDir}/svc/*.*
rm -f ./${modelsDir}/nnr/*.*

cp ./${modelsDir}/${serverName}/dtc/*.* ./${modelsDir}/dtc/
cp ./${modelsDir}/${serverName}/svc/*.* ./${modelsDir}/svc/
cp ./${modelsDir}/${serverName}/nnr/*.* ./${modelsDir}/nnr/

echo "$0 is Done ...."
echo "------------------------------------------------------"
exit 0
