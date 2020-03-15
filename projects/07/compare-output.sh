#!/bin/bash

if [ $# -ne 1 ];
    then echo "Please specify a .tst script"
fi

TST_FILENAME=$1
CMP_FILENAME=$(dirname $TST_FILENAME)/$(basename $TST_FILENAME .tst).cmp
OUT_FILENAME=$(dirname $TST_FILENAME)/$(basename $TST_FILENAME .tst).out
ASM_FILENAME=$(dirname $TST_FILENAME)/$(basename $TST_FILENAME .tst).asm

echo "Running $ASM_FILENAME with $TST_FILENAME and comparing $CMP_FILENAME to $OUT_FILENAME"
../../tools/CPUEmulator.sh $TST_FILENAME

echo '| SP     | LCL    | ARG    | THIS   | THAT   | TEMP   |'
cat $CMP_FILENAME
cat $OUT_FILENAME
