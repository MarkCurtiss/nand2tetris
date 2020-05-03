#!/bin/bash

if [ $# -ne 1 ];
    then echo "Please specify a .jack file"
fi

function log() {
    MESSAGE=$1
    TIMESTAMP=$( date +'%Y-%m-%d %T' )
    FILENAME=$0
    echo $TIMESTAMP [$0] INFO: $MESSAGE
}

JACK_FILE=$1
TEST_MODULE=$(basename $JACK_FILE .jack)
TEST_DIR="$TEST_MODULE""Test/"

log "Our file under test is $JACK_FILE and our test module is $TEST_MODULE and our test dir is $TEST_DIR"

cp $JACK_FILE $TEST_DIR
../../tools/JackCompiler.sh $TEST_DIR
../../tools/VMEmulator.sh
echo "(load $TEST_DIR)"
echo "(load $TEST_DIR/$TEST_MODULE"".tst)"
