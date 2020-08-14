.PHONY: clean datasets networks all us_historical world_historical historical

NETWORK_DIR ?= networks/
N ?= 10000
OUTPUT_DIR ?= datasets/
INCIDENCES ?= 401
BATCH_SIZE ?= 256

all: networks datasets historical
historical: us_historical world_historical

networks:
	$(RM) -R $(NETWORK_DIR)
	mkdir $(NETWORK_DIR)
	bash parallel_graphs.sh

us_historical:
	python fetch_us_historical.py datasets/us_historical.csv

world_historical:
	python fetch_world_historical.py datasets/world_historical.csv

datasets:
	bash parallel_synda.sh $(OUTPUT_DIR) $(N) $(BATCH_SIZE) $(INCIDENCES)

clean:
	$(RM) ./datasets/synda.db
