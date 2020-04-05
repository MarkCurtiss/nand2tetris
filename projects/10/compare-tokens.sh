#!/bin/bash

if [ $# -ne 1 ];
    then echo "Please specify a .jack file or a directory"
fi

function log() {
    MESSAGE=$1
    TIMESTAMP=$( date +'%Y-%m-%d %T' )
    FILENAME=$0
    echo $TIMESTAMP [$0] INFO: $MESSAGE
}

FILE_OR_DIR=$1

if [[ -d $FILE_OR_DIR ]]; then
    log "$FILE_OR_DIR is a directory"
    for JACK in $FILE_OR_DIR/*.jack; do
        TOKEN_FILE=$(dirname $JACK)/$(basename $JACK .jack)T.xml
        log "Now comparing (./tokenizer.py $JACK) to $TOKEN_FILE"
        diff -wB <(./tokenizer.py $JACK) <(cat $TOKEN_FILE)
    done
else
    log "$FILE_OR_DIR is a file"

    TOKEN_FILE=$(dirname $FILE_OR_DIR)/$(basename $FILE_OR_DIR .jack)T.xml
    log "Now comparing (./tokenizer.py $FILE_OR_DIR) to $TOKEN_FILE"
    diff -wB <(./tokenizer.py $FILE_OR_DIR) <(cat $TOKEN_FILE)
fi
