.PHONY: clean datasets networks all us_historical world_historical

NETWORK_DIR ?= networks/
RESULTS_DIR ?= datasets/synthetic/
N ?= 10000

all: clean networks datasets

networks:
	$(RM) -R $(NETWORK_DIR)
	mkdir $(NETWORK_DIR)
	./parallel_graphs.sh

us_historical:
	python fetch_us_historical.py datasets/us_historical.csv

world_historical:
	python fetch_world_historical.py datasets/world_historical.csv

datasets: $(NETWORK_DIR)
	$(RM) -R $(RESULTS_DIR)
	mkdir $(RESULTS_DIR)
	./parallel_synda.sh $(RESULTS_DIR) $(N)
	./create_tar.sh $(RESULTS_DIR)

clean:
	$(RM) -R ./$(NETWORK_DIR)
	$(RM) -R ./$(RESULTS_DIR)
