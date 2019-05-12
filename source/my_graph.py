import torch
from torch_geometric.data import Data
import torch_geometric.transforms as T
import networkx as nx
import matplotlib.pyplot as plt
import os


class MyGraph():
    # TODO let this class inherit directly from torch_geometric.data.Data

    def __init__(self, config, data=None):
        self.config = config
        self.data = data

    def create_random_graph(self):
        pos = torch.rand(self.config.nodes,
                         self.config.euclidian_dimensionality)

        # connect all edges within distance theta_max O(n^2)
        edges = []
        y = torch.zeros(self.config.nodes, dtype=torch.long)
        x = torch.arange(
            self.config.nodes) % self.config.feature_dimensionality

        for i in range(self.config.nodes):
            for j in range(i + 1 - int(self.config.self_loops),
                           self.config.nodes):
                node1 = pos[i]
                node2 = pos[j]
                # print(torch.dist(node1, node2))
                if torch.dist(node1, node2) < self.config.theta_max:
                    # add bi-directed edges to use directed pseudo-coordinates
                    # in MoNet
                    edges.append([i, j])
                    edges.append([j, i])
                    # if distance < theta, count the nodes as a neighbor in
                    # euclidian space
                    if torch.dist(node1, node2) < self.config.theta:
                        # Only if the two nodes belong to the same node class,
                        # increase the target
                        if x[i] == x[j]:
                            y[i] += 1
                            y[j] += 1

        edge_index = torch.tensor(edges, dtype=torch.long).transpose(0, 1)

        # x = torch.ones(self.config.nodes, self.config.feature_dimensionality)
        # One hot encoded representation might be better, as this is
        # categorical data
        x = torch.nn.functional.one_hot(
            x, self.config.feature_dimensionality).float()

        self.data = Data(x=x, edge_index=edge_index, y=y, pos=pos)

    def plot(self):
        g = nx.Graph(
            incoming_graph_data=self.data.edge_index.transpose(0, 1).tolist())
        # add the positions in euclidian space to the model
        pos_dict = {}
        # prepare the targets to be displayed
        labels_dict = {}

        for i in range(self.data.x.size(0)):
            pos_dict[i] = self.data.x[i].tolist()
            labels_dict[i] = int(self.data.y[i].item())

        self.set_plotting_style()
        nx.draw_networkx(g, pos_dict, labels=labels_dict)
        plt.title("Number of neighbors within euclidian distance {}".format(
            self.config.theta))
        plt.savefig(os.path.join(self.config.run_abs_path, 'graph.png'))
        # plt.show()

    def plot_predictions(self, pred, graph_nr):
        # transpose the edge matrix for format requirements
        g = nx.Graph(
            incoming_graph_data=self.data.edge_index.transpose(0, 1).tolist())
        # add the positions in euclidian space to the model
        pos_dict = {}
        # prepare the targets to be displayed
        labels_dict = {}

        for i in range(self.data.pos.size(0)):
            pos_dict[i] = self.data.pos[i].tolist()
            if self.config.euclidian_dimensionality == 1:
                pos_dict[i].append(0)

            labels_dict[i] = '{};{}'.format(
                int(pred[i]), int(self.data.y[i].item()))

        self.set_plotting_style()
        nx.draw_networkx(g, pos_dict, labels=labels_dict, font_size=10)
        plt.title(
            "Number of neighbors within euclidian distance {}.\nEach node displays 'pred:target'".format(
                self.config.theta))

        self.add_to_plotting_style()
        img_path = os.path.join(self.config.run_abs_path,
                                'graph_with_predictions.png')
        if os.path.isfile(img_path):
            os.remove(img_path)
        plt.savefig(img_path)
        print('plotted the graph with predictions to {}'.format(img_path))
        # plt.show()

    def set_plotting_style(self):
        plt.figure(figsize=(8, 8))
        plt.xlabel('x (euclidian)')
        plt.ylabel('y (euclidian)')
        plt.xlim(-0.2, 1.2)
        plt.ylim(-0.2, 1.2)

    def add_to_plotting_style(self):
        plt.tick_params(axis='x', which='both', bottom=True, labelbottom=True)
        plt.tick_params(axis='y', which='both', left=True, labelleft=True)
        plt.grid(linestyle='--', color='gray')
