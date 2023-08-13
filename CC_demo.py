from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import numpy as np
from graph_utils import get_sybils_from_CC
import pandas as pd
import random

adjacency_matrix = np.load("adj_matrix_ALL_0x_sample.npy")
graph = csr_matrix(adjacency_matrix)
idxs = graph.indices
coms = pd.read_pickle("communities_labels_CC_ALL_0x.pickle")
addresses = np.load("user_addresses_ALL_0x_sample.npy")

if __name__ == "__main__":
    generate = True
    while generate:
        communities, clusters, user_data = get_sybils_from_CC(coms, 10, addresses, idxs)
        community_randint = random.randint(0, len(communities) - 1)
        random_community = communities[community_randint]
        user_randint = random.randint(0, len(random_community) - 1)
        random_user = random_community[user_randint]
        print("Random sybil user:", random_user)
        ans = input("Generate next address? (y/n)")
        if ans != "y":
            generate = False
