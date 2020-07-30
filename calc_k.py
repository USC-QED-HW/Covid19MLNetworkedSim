import numpy
import scipy.integrate as integrate
from random import random
from numpy import sqrt, arcsin, sin, arccos, pi, exp

def integrand_edges (x, r):
    return (r ** 2) * ((pi - phi(x, r) / 2) + sin(phi(x, r)) / 2) 

def phi (x, r):
    return 2 * arcsin(sqrt((r ** 2) - (x ** 2)) / r)

def integrand_corners(x, y, r):
    return (x * y / 2) + (r ** 2) / 2 * (arccos(theta(x, y, r) - sqrt(1 - theta(x, y, r) ** 2)))

def theta (x, y, r):
    return 1 - ((x ** 2 + y ** 2) / (2 * r ** 2))

def center (r):
    return pi * (r ** 2) * ((1 - 2 * r) ** 2)

def edges (r):
    ntgrl = integrate.quad(integrand_edges, 0, r, args = (r,))
    #print("estimated error for edges: " + str(ntgrl[1]))
    return 4 * (1 - 2 * r) * ntgrl[0]

def corners (r):
    ntgrl = integrate.dblquad(integrand_corners, 0,  r, 0, r, args = (r, ))
    #print("estimated error for corners: " + str(ntgrl[1]))
    return 4 * ntgrl[0] 

def calc_k (n, r):
    return (n - 1) * (center(r) + edges(r) + corners(r))


def dist(node1: tuple, node2: tuple):
    return ((node1[0] - node2[0])**2 + (node1[1] - node2[1])**2)**(1/2)

def get_k(n, r):
    nodes = [None] * n
    for i in range (n):
        nodes[i] = random(), random()
    edges = [None] * n
    for i in range(n):
        edges[i] = []
    for i in range(n):
        for j in range(i+1, n):
            if (dist(nodes[i], nodes[j]) < r):
                edges[i].append(j)
                edges[j].append(i)
    total = 0
    for i in range(n):
        total += len(edges[i])
    return total/n

def get_ks(n, r, runs):
    total = 0
    for i in range(runs):
        total += get_k(n, r)
    return total/runs

def dumb_math(n, r):
    return (n-1) * (pi * (r ** 2))

def sigmoid (x):
    return 1 / (1 + exp(-x))
    

#n = 1000
#r = 0.05
#print("actual")
#print(get_ks(n, r, 100))
#print("wrong math")
#print(dumb_math(n, r))
#print("math")
#print(calc_k(n, r))

def approx_r (n, k, accepted):
    loss = 100
    r = 0.5
    while abs(loss) > accepted: 
        val = calc_k(n, r)
        loss = k - val
        r += (sigmoid(loss) - 0.5) / 100
    return r
    
approx_r (1000, 6, 0.0001)
