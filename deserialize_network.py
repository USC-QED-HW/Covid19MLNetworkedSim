from simulation import Node

def deserialize_network (adj_list: list):
    nodes = [None] * len(adj_list)
    for i in range(len(adj_list)):
        nodes[i] = new Node (0)
    for i in range(len(adj_list)):
        for j in adj_list[i]:
            nodes[i].add_edge(nodes[j])
    return nodes
