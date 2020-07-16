#!/bin/sh
# -*- coding: utf-8 -*-

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
