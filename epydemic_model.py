#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import epydemic
import epyc
import networkx as nx
from dataclasses import *
from enum import Enum
import pandas as pd

m = None

class GraphType(Enum):
    ERDOS_RENYI = 0
    WATTS_STROGATZ = 1
    BARABASI_ALBERT = 2
    
class MonitoredSIR(epydemic.SIR, epydemic.Monitor):
     def __init__(self):
         super(MonitoredSIR, self).__init__()

     def build(self, params):
         super(MonitoredSIR, self).build(params)
         
         self.trackNodesInCompartment(epydemic.SIR.SUSCEPTIBLE)
         self.trackNodesInCompartment(epydemic.SIR.REMOVED)

@dataclass
class ModelParameters:
    population: int
    graph_type: GraphType
    
    # Graph parameters
    graph_params: list
    
    # Initially infected population
    patients0: int
    
    # Probability of becoming infected
    alpha: float
    
    # Probability of being removed from population
    beta: float
    

def run_model(params: ModelParameters):
    pInfected = float(params.patients0 / params.population)
    pInfect = params.alpha
    pRemove = params.beta
    
    model_params = dict()
    model_params[epydemic.SIR.P_INFECT] = pInfect
    model_params[epydemic.SIR.P_INFECTED] = pInfected
    model_params[epydemic.SIR.P_REMOVE] = pRemove
    
    # capture every 10 days
    model_params[epydemic.Monitor.DELTA] = 10
    
    g = None
    
    N = params.population
    
    if params.graph_type == GraphType.ERDOS_RENYI:
        g = nx.erdos_renyi_graph(N, *params.graph_params)
    else:
        raise NotImplementedError("Only Erdos-Reyni graph has been implemented.")
    
    # Runs continous time simulation (i.e. stochastically)
    e = epydemic.StochasticDynamics(m, g)
    
    # Set maxmimum run time to 1000 days
    e.process().setMaximumTime(1000)
    
    rc = e.set(model_params).run()
    
    I = rc['results'][epydemic.Monitor.TIMESERIES][epydemic.SIR.INFECTED];
    R = rc['results'][epydemic.Monitor.TIMESERIES][epydemic.SIR.REMOVED];
    S = rc['results'][epydemic.Monitor.TIMESERIES][epydemic.SIR.SUSCEPTIBLE];
    
    SF = rc['results'][epydemic.SIR.SUSCEPTIBLE]
    IF = rc['results'][epydemic.SIR.INFECTED]
    RF = rc['results'][epydemic.SIR.REMOVED]
    
    data = [[ts * 10, S[ts], I[ts], R[ts]] for ts in range(len(S))]
    
    data.append([len(data) * 10, SF, IF, RF])
    
    df = pd.DataFrame(data, columns=['timestamp', 'susceptible', 'infected', 'recovered'])
    
    return df

def setup():
    global m
    if m is None:
        m = MonitoredSIR()
        return True
    else:
        return False

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    setup()
    
    kmean = 3
    N = 10_000
    
    test_params = ModelParameters(population=N,
                                  graph_type=GraphType.ERDOS_RENYI,
                                  graph_params=[(kmean + 0.0) / N],
                                  patients0=int(0.01 * N),
                                  alpha=0.02, 
                                  beta=0.002)
    
    df = run_model(test_params)
    exclude = ['timestamp']
    df.loc[:, df.columns.difference(exclude)].plot()
    plt.show()