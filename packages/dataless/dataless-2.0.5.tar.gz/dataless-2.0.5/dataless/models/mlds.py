import matplotlib.pyplot as plt 
import networkx as nx 
from torch import nn 
import torch 

class Hadamard(nn.Module):
    def __init__(self, in_feature, low_bound:int=0, up_bound:int=1):
        super().__init__()
        self.low_bound = low_bound 
        self.up_bound = up_bound
        self.weight = nn.Parameter(torch.Tensor(in_feature))
    
    def forward(self, x):
        self.weight.data = self.weight.data.clamp(self.low_bound, self.up_bound)
        return x * self.weight
    
class Negation(nn.Module):
    def __init__(self):
        super().__init__()
        self.scaler = nn.Parameter(torch.Tensor([-1.0]))
    
    def forward(self, x):
        return x * self.scaler

class MaxPool(nn.Module):
    def __init__(self, nodes):
        super().__init__()
        self.n = nodes
        self.len = int((self.n**2 - self.n) * 0.5) 
        self.pad = torch.zeros(self.len) 

    def forward(self, x):
        self.pad[:n] = x[self.n:2*self.n]
        print(f'{self.pad}\n{x}')
        x = torch.cat((x[:n], torch.maximum(self.pad, x[2*self.n:]))) 
        return x 
    
class MLDS(nn.Module):
    def __init__(self, G, theta_init=None):
        super().__init__()
        self.graph = G
        self.n = len(self.graph.nodes)
        self.temperature = 0.5
        self.theta_init = theta_init

        self.theta_layer = Hadamard(self.n)
        self.theta_layer.weight = self.theta_weight()
        
        self.layer2 = nn.Linear(in_features=self.n, out_features=3*self.n)
        self.layer2.weight = self.layer2_weight() # W [n, n(n + 3) / 2]
        self.layer2.bias = self.layer2_bias() # b [n(n + 3) / 2]

        self.layer3 = nn.Linear(in_features=2*self.n, out_features=1, bias=False)
        self.layer3.weight = self.layer3_weight() # w [n(n + 1) / 2]

        self.negative = Negation()
        self.pooling = MaxPool(nodes=self.n)
        
        self.layer2.weight.requires_grad_(False) 
        self.layer2.bias.requires_grad_(False)
        self.layer3.weight.requires_grad_(False)
        self.negative.scaler.requires_grad_(False) 

        self.activation = nn.ReLU()

    def forward(self, x):
        with torch.no_grad():
            self.layer2.bias.data[0 : self.n] = -1.0 * self.temperature

        x = self.theta_layer(x)
        x = self.layer2(x)
        x = self.negative(x)
        x = self.pooling(x)
        x = self.activation(x)
        x = self.layer3(x)
        return x 

    def theta_weight(self):
        """ theta parameter vector """
        g = torch.manual_seed(123)
        theta_weight = torch.rand((self.n), generator=g)

        if self.theta_init:
            theta_weight = theta_weight * 0.5
            theta_weight[self.theta_init] = 0.6 + theta_weight[self.theta_init] * 0.2

        return nn.Parameter(theta_weight)

    def layer2_weight(self):
        """ W matrix derived from G """
        len = (self.n ** 2 + 3 * self.n) / 2
        W = torch.zeros([self.n, int(len)])
        W[:, :self.n] = torch.eye(self.n)
        for i in range(self.n):
            W[:, self.n+i] = self.one_hot(self.close_ngh(i))

        idx = 0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                W[:, 2*self.n + idx] = self.make_pairs(i, j)
                idx += 1

        return nn.Parameter(W.T.to_dense())

    def layer2_bias(self):
        """ b vector derived from G """
        # b.shape: n + n + n(n - 1) / 2
        len = (self.n ** 2 + 3 * self.n) / 2
        bias = torch.zeros(int(len)) - 3.0
        bias[:self.n] = -0.5
        bias[self.n:2*self.n] = -2.0

        return nn.Parameter(bias)

    def layer3_weight(self):
        """ w vector derived from G """
        # w.shape: n + n(n - 1) / 2
        len = (self.n**2 + self.n) / 2
        w = torch.zeros(int(len)) + self.n
        w[:self.n] = -1.0
        
        return nn.Parameter(w.to_dense())
    
    def trainable_params(self):
        """ Counting trainable parameters """
        params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f'trainable params: {params}')
        return params
    
    def close_ngh(self, x: int):
        return [x] + list(self.graph.neighbors(x))
    
    def scnd_ngh(self, x: int):
        nghs = [list(self.graph.neighbors(first)) for first in list(self.graph.neighbors(x))]
        res = [i for l in nghs for i in l if i != x]
        return list(set(res))
    
    def one_hot(self, arr):
        res = torch.zeros(self.n)
        res[arr] = 1
        return res

    def make_pairs(self, x, y): 
        arr = torch.bitwise_or(self.one_hot(self.close_ngh(x)).int(), self.one_hot(self.close_ngh(y)).int())
        return arr
    
    def plot(self):
        plt.figure(figsize=(6, 4))
        nx.draw(self.graph, with_labels=True, node_color='lightblue', node_size=500, font_size=10, edge_color='gray')
        plt.show()

    def vanilla_eq(self):
        pass
    
if __name__ == '__main__':
    G = nx.Graph()
    G.add_nodes_from(list(range(5)))
    edges = [(0,1),(1,2),(2,3),(3,4),(2,4),(0,3)] 
    G.add_edges_from(edges) 
    n = len(G.nodes())

    # for i in range(2**n):
    #     theta_init = [int(i) for i in list(format(i, f'0{n}b'))]
    model = MLDS(G, theta_init=[0,1,1,1,1]) 
    print(f'{model(torch.ones(len(G.nodes)))}')
    model.trainable_params()

