.PHONY: clean datasets networks all us_historical world_historical historical

NETWORK_DIR ?= networks/
RESULTS_DIR ?= datasets/synthetic/
N ?= 10000

all: clean networks datasets
historical: us_historical world_historical

networks:
	$(RM) -R $(NETWORK_DIR)
	mkdir $(NETWORK_DIR)
	bash parallel_graphs.sh

us_historical:
	python fetch_us_historical.py datasets/us_historical.csv

world_historical:
	python fetch_world_historical.py datasets/world_historical.csv

datasets: $(NETWORK_DIR)
	$(RM) -R $(RESULTS_DIR)
	mkdir $(RESULTS_DIR)
	bash parallel_synda.sh $(RESULTS_DIR) $(N)
	python aggregate_synda.py $(RESULTS_DIR)

clean:
	$(RM) -R ./$(NETWORK_DIR)
	$(RM) -R ./$(RESULTS_DIR)
