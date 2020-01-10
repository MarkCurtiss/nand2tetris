#!/bin/bash

set -e

if [ $# -eq 0 ]
then
    echo "Please provide the project directory you wish to test (e.g. 01)"
    exit
fi

PROJECT_NO=$1

for TEST_FILE in projects/$PROJECT_NO/*.tst ;
do
    echo "Now testing $TEST_FILE";
    tools/HardwareSimulator.sh $TEST_FILE ;
done
