.PHONY: clean discrete continuous

NETWORK_DIR ?= networks/
RESULTS_DIR ?= datasets/synthetic/
N ?= 10000

parallel:
	./parallel_synda.sh $(N)

clean:
	$(RM) -R ./datasets/synthetic

continuous:
	./generate_synda.py -n $(N) -m CONTINUOUS --network-dir $(NETWORK_DIR) --results-dir $(RESULTS_DIR)

discrete:
	./generate_synda.py -n $(N) -m DISCRETE --network-dir $(NETWORK_DIR) --results-dir $(RESULTS_DIR)
