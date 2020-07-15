#!/bin/sh

if [[ $# -ne 1 ]]; then
	echo "First argument must be path directory"
fi

results_dir="$1"
tar -zcvf datasets/synthetic-"$(date +"%T")".tar.gz "$results_dir"
