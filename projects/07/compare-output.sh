#!/bin/bash

if [ $# -ne 1 ];
    then echo "Please specify a .vm script"
fi

VM_FILENAME=$1
TST_FILENAME=$(dirname $VM_FILENAME)/$(basename $VM_FILENAME .vm).tst
CMP_FILENAME=$(dirname $VM_FILENAME)/$(basename $VM_FILENAME .vm).cmp
OUT_FILENAME=$(dirname $VM_FILENAME)/$(basename $VM_FILENAME .vm).out
ASM_FILENAME=$(dirname $VM_FILENAME)/$(basename $VM_FILENAME .vm).asm

echo "Translating $VM_FILENAME into $ASM_FILENAME"
./VMTranslator $VM_FILENAME
echo "Running $TST_FILENAME and comparing $CMP_FILENAME to $OUT_FILENAME"
../../tools/CPUEmulator.sh $TST_FILENAME

echo '| SP     | LCL    | ARG    | THIS   | THAT   | TEMP   |'
cat $CMP_FILENAME
cat $OUT_FILENAME
