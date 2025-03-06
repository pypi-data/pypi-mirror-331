from dataless.solvers.base import Base
from torch import Tensor
import networkx as nx
import pickle
import torch
import time 
import csv 
import os

class EarlyStopping:
    def __init__(self, patience=5, min_delta=0):
        """
        Args:
            patience (int): How many epochs to wait before stopping when validation loss is not improving.
            min_delta (float): Minimum change in the monitored metric to qualify as an improvement.
        """
        self.patience = patience
        self.min_delta = min_delta
        self.best_score = None
        self.counter = 0
        self.early_stop = False

    def __call__(self, val_loss):
        if self.best_score is None:
            self.best_score = val_loss
        elif val_loss >= self.best_score - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = val_loss
            self.counter = 0


class SOLVER(Base):
    def __init__(self, Net, G, params = {}):
        """
        Initializing the solver with graph G and params
        """
        super().__init__()
        self.selection_criteria = params.get("selection_criteria", 0.5)
        self.learning_rate = params.get("learning_rate", 0.0001)
        self.max_steps = params.get("max_steps", 100000)
        self.runtime = params.get("runtime", False)
        self.sg = params.get('store_graph', False)

        params['theta_init'] = params.get('theta_init', [])
        params['out_dir'] = params.get('out_dir', os.path.join(os.getcwd(), 'output'))
        os.makedirs(params['out_dir'], exist_ok=True)
        

        self.graph = G
        self.vertices = len(G.nodes)
        self.edges = len(G.edges)

        self.model = Net(G, theta_init=params['theta_init'])
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.loss_fn = lambda predicted, desired: predicted - desired
        
        self.x = torch.ones(self.vertices)
        self.objective = torch.tensor(-(self.vertices) / 2)
        self.solution = {}

        self.early_stopping = EarlyStopping()
        self.columns = ["nodes", "edges", "iterations", "prob_type", "mdds", "time"]
        gtime = str(time.time())[-5:]
        self.csv_filename = os.path.join(params['out_dir'], params.get('out_filename', f'output-{gtime}.csv'))
        self.write_header = False if os.path.exists(self.csv_filename) else True
        
        if self.sg:
            params['graph_dir'] = params.get('graph_dir', os.path.join(os.getcwd(), 'graphs'))
            os.makedirs(params['graph_dir'], exist_ok=True)
            self.pkl_filename = os.path.join(params['graph_dir'], params.get('graph_filename', f'graph-{gtime}.pkl'))

    def solve(self):
        """
        Trains the neural network
        """
        device = torch.device("cuda:0" if torch.cuda.is_available() and not self.runtime else "cpu")
        print("using device: ", device)

        self.model = self.model.to(device)
        self.x = self.x.to(device)
        self.objective = self.objective.to(device)

        self._start_timer()
        iterations = 0

        for i in range(self.max_steps):
            iterations = i
            self.optimizer.zero_grad()

            predicted: Tensor = self.model(self.x)

            output = self.loss_fn(predicted, self.objective)

            output.backward()
            self.optimizer.step()

            if i % 500 == 0:
                self.early_stopping(predicted)
                if self.early_stopping.early_stop:
                    print('Stopping Early due to loss plateau')
                    break 
                print(
                    f"Training step: {i}, Output: {predicted.item():.4f}, Desired Output: {self.objective.item():.4f}"
                )

        self._stop_timer()

        self.solution["graph_probabilities"] = self.model.theta_layer.weight.detach().tolist()

        graph_mask = [0 if x < self.selection_criteria else 1 for x in self.solution["graph_probabilities"]]
        indices = [i for i, x in enumerate(graph_mask) if x == 1]

        subgraph = self.graph.subgraph(indices)
        subgraph = nx.Graph(subgraph)
        while len(subgraph) > 0:
            degrees = dict(subgraph.degree())
            max_degree_nodes = [
                node
                for node, degree in degrees.items()
                if degree == max(degrees.values())
            ]

            if (
                len(max_degree_nodes) == 0
                or subgraph.degree(max_degree_nodes[0]) == 0
            ):
                break 

            subgraph.remove_node(max_degree_nodes[0])
        size = len(subgraph)
        MDDS_size = sum([i for i in graph_mask if i == 1])
        MDDS_mask = graph_mask
        print(f"Found MDDS of size: {MDDS_size}")
        print(f"theta vector: {MDDS_mask}")

        self.solution["graph_mask"] = MDDS_mask
        self.solution["size"] = MDDS_size
        self.solution["number_of_steps"] = i
        self.solution["steps_to_best_MIS"] = 0
        self.solution['convergence_time'] = self.solution_time

        data = [{
            "nodes": self.vertices,
            "edges": self.edges,
            "iterations": iterations,
            "prob_type": 'mdds',
            "mdds": indices, 
            "time": self.solution_time 
        }]
        print(f'saving output data: {self.csv_filename}')
        if self.sg:
            print(f'saving graph: {self.pkl_filename}')
            with open(self.pkl_filename, 'wb') as f:
                pickle.dump(self.graph, f, pickle.HIGHEST_PROTOCOL)
        with open(self.csv_filename, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.columns)
            if self.write_header:
                writer.writeheader()
            writer.writerows(data)  
            print(data)
        print('Done')