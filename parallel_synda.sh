#!/bin/bash
# -*- coding: utf-8 -*-

# This command gets the number of virtual cores (i.e. cores including hyper-threading)
main() {
    if [ $# -eq 0 ]; then
        echo "First argument must be the number of datasets to generate."
        exit 1
    fi

    VIRTUAL_CORES=$(grep -c ^processor /proc/cpuinfo)

    DATASETS_PER_CORE="$(($1 / VIRTUAL_CORES))"
    EXTRA_DATASETS="$(($1 % VIRTUAL_CORES))"

    INPUT_FILE=$(mktemp /tmp/XXXXXX)

    for (( i = 0 ; i <= "$((VIRTUAL_CORES - 1))" ; ++i)); do
        echo "$DATASETS_PER_CORE" >> "$INPUT_FILE"
    done

    echo "$((DATASETS_PER_CORE + EXTRA_DATASETS))" >> "$INPUT_FILE"

    set -x #echo on
    cat "$INPUT_FILE" | parallel --lb -j "$VIRTUAL_CORES" make continuous N={1}
    set +x #echo off
 
    rm "$INPUT_FILE"
}

main "$@"
