#!/bin/bash

set -e 
set -o pipefail


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
        COMPILED_FILE=$(dirname $JACK)/$(basename $JACK .jack).xml
        log "Now comparing (./compilation_engine.py $JACK) to $COMPILED_FILE"
        diff -wBU 3 <(./compilation_engine.py $JACK) <(./reformat-xml.py  $COMPILED_FILE)
    done
else
    log "$FILE_OR_DIR is a file"

    COMPILED_FILE=$(dirname $FILE_OR_DIR)/$(basename $FILE_OR_DIR .jack).xml
    log "Now comparing (./compilation_engine.py $FILE_OR_DIR) to $COMPILED_FILE"
    diff -wBU 3 <(./compilation_engine.py $FILE_OR_DIR) <(./reformat-xml.py $COMPILED_FILE)
fi
