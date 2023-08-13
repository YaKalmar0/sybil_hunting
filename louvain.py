import numpy as np
from communities.algorithms import louvain_method
from communities.visualization import draw_communities

import pickle

am = np.load("adj_matrix_10000_sample.npy")
communities, frames = louvain_method(am)

with open("communities_louvain.pickle", "wb") as handle:
    pickle.dump(communities, handle, protocol=pickle.HIGHEST_PROTOCOL)


with open("frames_louvain.pickle", "wb") as handle:
    pickle.dump(frames, handle, protocol=pickle.HIGHEST_PROTOCOL)

# draw_communities(am, communities, filename="louvain_communities.png")
