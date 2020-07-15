#!/bin/sh
# -*- coding: utf-8 -*-

virtual_cores=$(grep -c ^processor /proc/cpuinfo)
output_dir="networks/"
params_dir="params/"

parallel -j"$virtual_cores" python generate_graphs.py -O "$output_dir"\
	-G {1} -K {2} -N {3} :::                                          \
	$(cat "$params_dir"GRAPH) :::                                     \
	$(cat "$params_dir"K) :::                                         \
	$(cat "$params_dir"N)
