from dataless.models import KCOL, DISSOC, MDDS, VEDS, MLDS, DOM
from dataless.solvers import SOLVER
import matplotlib.pyplot as plt
import networkx as nx 

class dNN():
    def __init__(self, prob_type:str = 'mdds', graph = None, 
                 use_random= False, nodes=None, edges=None, edge_prob=0.5):
        if use_random:
            self.graph = nx.gnp_random_graph(nodes, edge_prob)
            self.nodes = len(self.graph)
            self.edges = len(self.graph.edges)
        else:
            self.graph = graph
            self.nodes = nodes if nodes != None else len(self.graph)
            self.edges = edges if edges != None else len(self.graph.edges)
        self.NET = {
            'dissociation_set': DISSOC,
            'dominating_set': DOM,
            'k_coloring': KCOL,
            'mdds': MDDS,
            'veds': VEDS,
            'mlds': MLDS
        }[prob_type]
        
    def solve(self, **kwargs):
        dnn = SOLVER(Net=self.NET, G=self.graph, **kwargs)
        dnn.solve()

    def plot(self):
        plt.figure(figsize=(6, 4))
        nx.draw(self.graph, with_labels=True, node_color='lightblue', node_size=500, font_size=10, edge_color='gray')
        plt.show()

if __name__ == '__main__':
    dnn = dNN(use_random=True,nodes=10)
    dnn.solve()







