#!/bin/bash -v
#ESBMC=/home/kaled/sdb1/esbmc+python-v6.0.0-linux-static-64/bin/esbmc
ESBMC=/home/kaled/Desktop/esbmc-v6.0/bin/esbmc
FILE=/home/kaled/Desktop/2020-my-projects/experment_10_02_2020/uFTP/main.c

#FILE=./examples/a.cpp
#ESBMC_PARAMS='-I/home/kaled/Desktop/experment_10_02_2020/uFTPP -I/home/kaled/Desktop/experment_10_02_2020/uFTP/library --no-div-by-zero-check --force-malloc-success --state-hashing --no-align-check --k-step 5 --floatbv --no-slice --show-cex --unwind 4 --max-k-step 10 --context-bound 2 --32 --incremental-bmc --no-pointer-check --no-bounds-check --interval-analysis --no-slice '
ESBMC_PARAMS='-I/home/kaled/Desktop/2020-my-projects/experment_10_02_2020/uFTP -I/home/kaled/Desktop/2020-my-projects/experment_10_02_2020/uFTP/library --no-div-by-zero-check --force-malloc-success --state-hashing --no-align-check --k-step 5 --floatbv --show-cex --unwind 4 --max-k-step 10 --context-bound 2 --32 --incremental-bmc --no-pointer-check --no-bounds-check --interval-analysis --no-slice'
INSTRUMENT_PARAMS='-I/home/kaled/Desktop/2020-my-projects/experment_10_02_2020/uFTP/main.c -I/home/kaled/Desktop/2020-my-projects/experment_10_02_2020/uFTP/main.c/library -DOPENSSL_ENABLED'
#FILE=$1

rm -r ./output/*
#rm -r ./myout/*
mkdir ./output/goals
mkdir ./output/goals_out
mkdir ./output/test-suite

#-nogoalProFunc
./FuSeBMC $FILE ./output/instrumented.c ./output/my_goals.txt ./output/goals_out $INSTRUMENT_PARAMS


func_arr=(
socketPrintf
socketWorkerPrintf
getMaximumSocketFd
createSocket
createPassiveSocket
createActiveSocket
fdInit
fdAdd
closeSocket
closeClient
checkClientConnectionTimeout
flushLoginWrongTriesData
selectWait
getAvailableClientSocketIndex
evaluateClientSocketConnection
authenticateSystem
loginCheck
#loginCheck
configurationRead
applyConfiguration
initFtpData
readConfigurationFile
searchParameter
parseConfigurationFile
isProcessAlreadyRunning
daemonize
respawnProcess
setWatchDogTimeout
updateWatchDogTime
initOpenssl
cleanupOpenssl
createServerContext
createClientContext
configureClientContext
configureContext
ShowCerts
handle_error
locking_function
id_function
thread_setup
printTimeStamp
makeTimeout
ignore_sigpipe
onUftpClose
signalHandlerInstall
report_error
report_error_q
function_conversation
loginCheck
FILE_CompareString
FILE_IsDirectory
FILE_GetAvailableSpace
FILE_GetFileSize
FILE_GetFileSizeFromPath
FILE_IsFile
#FILE_GetDirectoryInodeList
FILE_GetDirectoryInodeCount
FILE_GetStringFromFile
FILE_ReadStringParameters
FILE_StringParametersBinarySearch
FILE_GetFilenameFromPath
checkParentDirectoryPermissions
checkUserFilePermissions
FILE_GetOwner
FILE_GetGroupOwner
FILE_AppendToString
FILE_DirectoryToParent
FILE_LockFile
FILE_doChownFromUidGid
FILE_doChownFromUidGidString
FILE_getUID
#FILE_getGID
FILE_checkAllOpenedFD
cleanDynamicStringDataType
cleanLoginData
setDynamicStringDataType
getSafePath
appendToDynamicStringDataType
setRandomicPort
writeListDataInfoToSocket
searchInLoginFailsVector
deleteLoginFailsData
getListDataInfo
deleteListDataInfoVector
cancelWorker
resetWorkerData
resetClientData
compareStringCaseInsensitive
isCharInString
workerCleanup
connectionWorkerHandle
runFtpServer
processCommand
deallocateMemory
)


for i in ${func_arr[*]}; 
do
    goals_filename=./output/goals_out/$i
    if [ ! -f "$goals_filename" ]; then
        echo "$goals_filename does not exist"
    else
	while read goal; do
            # reading each line
            #echo $goal            
            $ESBMC $ESBMC_PARAMS --function $i --error-label ${goal} --witness-output ./output/goals/${i}_${goal}.graphml ./output/instrumented.c
            ./graph2xml.py --witnessfile ./output/goals/${i}_${goal}.graphml --testcasefile ./output/test-suite/${i}_${goal}.xml ./output/instrumented.c
	done < $goals_filename
    fi
done
