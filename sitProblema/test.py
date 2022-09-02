import networkx as nx

di = nx.DiGraph()

edge_dict = [[(20,30), (30,30), 5],
            [(30,30), (30,20), 5],
            [(30,20), (20,20), 5],
            [(20,20), (20,30), 5]]

for edge in edge_dict:
    di.add_edge(edge[0], edge[1], weight=0)

print(len(di[(20,30)]))

"""for nb in di.neighbors((20,30)):
    print(nb)"""

