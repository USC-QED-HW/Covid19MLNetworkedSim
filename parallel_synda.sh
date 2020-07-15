#!/bin/sh
# -*- coding: utf-8 -*-

# This command gets the number of virtual cores (i.e. cores including hyper-threading)
# main() {
#     if [ $# -eq 0 ]; then
#         echo "First argument must be the number of datasets to generate."
#         exit 1
#     fi

#     VIRTUAL_CORES=$(grep -c ^processor /proc/cpuinfo)

#     DATASETS_PER_CORE="$(($1 / VIRTUAL_CORES))"
#     EXTRA_DATASETS="$(($1 % VIRTUAL_CORES))"

#     INPUT_FILE=$(mktemp /tmp/XXXXXX)

#     for (( i = 0 ; i < "$((VIRTUAL_CORES - 1))" ; ++i)); do
#         echo "$DATASETS_PER_CORE" >> "$INPUT_FILE"
#     done

#     echo "$((DATASETS_PER_CORE + EXTRA_DATASETS))" >> "$INPUT_FILE"

#     set -x #echo on
#     cat "$INPUT_FILE" | parallel -j "$VIRTUAL_CORES" make discrete N={1}
#     set +x #echo off

#     rm "$INPUT_FILE"
# }

# main "$@"

virtual_cores=$(grep -c ^processor /proc/cpuinfo)
networks_dir="networks/"

usage() {
	TAB=$(printf "\t")
	cat <<- EOF
	Usage: parallel_synda.sh [output_directory] [per_graph]

	output_directory:
	${TAB}The output directory for synthetic data.

	per_graph:
	${TAB}How many synthetic datasets to generate per graph.
	EOF
	exit 1
}

if [ $# -ne 2 ]; then
	usage
fi

output_dir="$1"
per_graph="$2"

parallel --bar -j"$virtual_cores" python generate_synda.py \
	-R "$output_dir" -N "$per_graph" -M CONTINUOUS -G {1} ::: \
		$(ls -1q "$networks_dir")
