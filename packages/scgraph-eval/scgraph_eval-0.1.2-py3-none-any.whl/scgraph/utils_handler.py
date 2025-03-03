import numpy as np, pandas as pd
from scipy.stats import trim_mean
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cdist

def calculate_centroids(X, labels):
    centroids = dict()
    for label in labels.unique():
        centroids[label] = np.mean(X[labels == label], axis=0)
    return centroids


def calculate_trimmed_means(X, labels, trim_proportion=0.2, ignore_=[]):
    centroids = dict()
    if isinstance(X, csr_matrix):
        X = X.toarray()
    for label in labels.unique():
        if label in ignore_:
            continue
        centroids[label] = trim_mean(X[labels == label], proportiontocut=trim_proportion, axis=0)
    return centroids


def compute_classwise_distances(centroids):
    centroid_vectors = np.array([centroids[key] for key in sorted(centroids.keys())])
    distances = cdist(centroid_vectors, centroid_vectors, "euclidean")
    return pd.DataFrame(distances, columns=sorted(centroids.keys()), index=sorted(centroids.keys()))
