#!/bin/bash

if [ $# -ne 1 ];
    then echo "Please specify a .vm script"
fi

function log() {
    MESSAGE=$1
    TIMESTAMP=$( date +'%Y-%m-%d %T' )
    FILENAME=$0
    echo $TIMESTAMP [$0] INFO: $MESSAGE
}

# this needs to know if it is a directory for a filename :(
VM_FILENAME=$1
TST_FILENAME=$(dirname $VM_FILENAME)/$(basename $VM_FILENAME .vm).tst
CMP_FILENAME=$(dirname $VM_FILENAME)/$(basename $VM_FILENAME .vm).cmp
OUT_FILENAME=$(dirname $VM_FILENAME)/$(basename $VM_FILENAME .vm).out
ASM_FILENAME=$(dirname $VM_FILENAME)/$(basename $VM_FILENAME .vm).asm

log "Translating $VM_FILENAME into $ASM_FILENAME"
./VMTranslator $VM_FILENAME
log "Running $TST_FILENAME and comparing $CMP_FILENAME to $OUT_FILENAME"
../../tools/CPUEmulator.sh $TST_FILENAME

# echo '| SP     | LCL    | ARG    | THIS   | THAT   | TEMP   |'
cat $CMP_FILENAME
cat $OUT_FILENAME
