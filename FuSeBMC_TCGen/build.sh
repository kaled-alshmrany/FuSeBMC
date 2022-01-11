#!/bin/sh
make clean all concurrency=0
make clean all concurrency=1
echo "Done !!!"
