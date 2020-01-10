#!/bin/bash

PROJECT_NO=$1

for TEST_FILE in projects/$PROJECT_NO/*.tst ;
do
    echo "Now testing $TEST_FILE";
    tools/HardwareSimulator.sh $TEST_FILE ;
done
