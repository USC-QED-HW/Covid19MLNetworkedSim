#!/bin/bash
# -*- coding: utf-8 -*-

virtual_cores=$(grep -c ^processor /proc/cpuinfo)
networks_dir="networks/"

output_dir="$1"
N="$2"
batch_size="$3"
incidences="$4"

database_name="datasets/synda.db"
table_name="DATASET_${N}"

# Create proper table for insertion
sqlite3 "$database_name" <<EOF
DROP TABLE IF EXISTS ${table_name};

CREATE TABLE ${table_name} (
    [case] TEXT PRIMARY KEY, 
    population INTEGER,
    backend TEXT,
    initial_infected INTEGER,
    network TEXT,
    k INTEGER,
    infectiousness REAL,
    i_out REAL,
    i_rec_prop REAL,
    timeseries TEXT
);
EOF

parallel --bar -j"$virtual_cores" \
	python generate_synda.py --model CONTINUOUS \
	--incidences "$incidences" --index {1} --graph-type {2} \
	--batch_size "$batch_size" --max "$N" \
	--database-name "$database_name" --table-name "$table_name" ::: \
	$(seq 0 "$batch_size" "$N") ::: \
	$(ls -1q "$networks_dir")

# Output whole thing to csv
(
sqlite3 -header -csv "$database_name"<<EOF
SELECT [case],
	population,
	initial_infected,
	network,
	k,
	infectiousness,
	i_out,
	i_rec_prop,
	timeseries 
FROM DATASET_100
EOF
) > "$output_dir"synthetic-dataset-${N}.csv

# gzip to max compression (hopefully to fit in github file)
gzip -9 "$output_dir"synthetic-dataset-${N}.csv