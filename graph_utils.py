import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np
import json
import networkx as nx
import matplotlib.pyplot as plt


def get_sybils_from_CC(components, threshold, addresses, idxs):
    user_data = {}
    for i, cluster_id in enumerate(components):
        user_idx = idxs[i]
        user_address = addresses[user_idx]
        user_data[user_address] = cluster_id
    clusters = {}
    for address, cluster_id in user_data.items():
        try:
            clusters[int(cluster_id)].append(address)
        except:
            clusters[int(cluster_id)] = [address]
    communities = []
    for c in clusters:
        if len(clusters[c]) > threshold and len(clusters[c]) < 200:
            communities.append(clusters[c])
    return communities, clusters, user_data


def generate_CC_graph(n_components, labels):
    G = nx.from_numpy_matrix(adjacency_matrix)

    # Draw the graph
    pos = nx.spring_layout(G)
    for component in range(n_components):
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=[i for i, x in enumerate(labels) if x == component],
            node_color=plt.cm.jet(float(component) / n_components),
        )

    nx.draw_networkx_edges(G, pos)
    plt.show()


if __name__ == "__main__":
    adjacency_matrix = np.load("adj_matrix_ALL_0x_sample.npy")
    coms = pd.read_pickle("communities_labels_CC_ALL_0x.pickle")
    graph = csr_matrix(adjacency_matrix)
    idxs = graph.indices
    addresses = np.load("user_addresses_ALL_0x_sample.npy")
    communities, clusters, user_data = get_sybils_from_CC(coms, 10, addresses, idxs)
    # with open("connected_components_clusters.json", "w") as json_file:
    #     json.dump(clusters, json_file)
    np.save("connected_components_communities.npy", communities)
