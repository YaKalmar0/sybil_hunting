from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import numpy as np
import pickle

adjacency_matrix = np.load("adj_matrix_ALL_0x_sample.npy")
graph = csr_matrix(adjacency_matrix)
n_components, labels = connected_components(
    csgraph=graph, directed=False, return_labels=True
)
print("Identified {} communities".format(n_components))

with open("communities_labels_CC_ALL_0x.pickle", "wb") as handle:
    pickle.dump(labels, handle, protocol=pickle.HIGHEST_PROTOCOL)
