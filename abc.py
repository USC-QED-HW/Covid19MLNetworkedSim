import random
from continious_sim import run_model, ModelParameters

LAMBDA_MIN = 0
LAMBDA_MAX = 0.25
TRANSITION_RATE_MIN = 0
TRANSITION_RATE_MAX = 2
RECOVERY_PROB_MIN = 0
RECOVERY_PROB_MAX = 1


def run_ABC(n, epsilon, adj_list, truth):
    results = [None]*n
    i = 0
    while (i < n):
        theta = generate_theta()
        lambdaa = theta[0]
        transition_rate = theta[1]
        recovery_prob = theta[2]
        mp = ModelParamters()
        mp.infectiousness = lambdaa
        mp.i_d = transition_rate
        mp.i_r = recovery_prob
        mp.time = 500
        mp.sample_time = 1
        sim = run_model(mp, adj_list)
        if (mean_square_error(truth, sim) < epsilon):
            results[i] = theta
            i++  
        
def generate_theta():
    return random.randrange(LAMBDA_MIN, LAMBDA_MAX), random.randrange(TRANSITION_RATE_MIN, TRANSITION_RATE_MAX), random.randrange(RECOVERY_PROB_MIN, RECOVERY_PROB_MAX))

def mean_square_error(actual, sim):
