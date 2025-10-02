#!/usr/bin/env python3
"""
Debug the clustering process to find why disconnected motifs appear
"""
import json
import numpy as np
import networkx as nx
import pandas as pd
from sklearn.cluster import AgglomerativeClustering

# Load data (same as server.py)
df = pd.read_csv("facebook_weighted_filtered.csv")
G = nx.Graph()
for _, row in df.iterrows():
    G.add_edge(int(row[0]), int(row[1]), weight=float(row[2]))

with open('wasserstein_distances.json', 'r') as f:
    wasserstein_data = json.load(f)

with open('facebook_motifs.json', 'r') as f:
    motif_data = json.load(f)

# Build distance matrix (same as server.py)
all_nodes = sorted(set(int(k.split("-")[0]) for k in wasserstein_data.keys()) |
                   set(int(k.split("-")[1]) for k in wasserstein_data.keys()))
node_index = {node: i for i, node in enumerate(all_nodes)}
index_node = {i: node for node, i in node_index.items()}

N = len(all_nodes)
dist_matrix = np.full((N, N), fill_value=100.0)
for pair, dist in wasserstein_data.items():
    n1, n2 = map(int, pair.split("-"))
    i, j = node_index[n1], node_index[n2]
    dist_matrix[i][j] = dist
    dist_matrix[j][i] = dist
np.fill_diagonal(dist_matrix, 0.0)

def analyze_cluster_connectivity(threshold=0.0):
    """Analyze connectivity of clusters formed at given threshold"""
    model = AgglomerativeClustering(
        metric='precomputed',
        distance_threshold=threshold,
        n_clusters=None,
        linkage='average'
    )
    labels = model.fit_predict(dist_matrix)

    cluster_map = {}
    for idx, label in enumerate(labels):
        cluster_map.setdefault(label, []).append(index_node[idx])

    print(f"Analysis for threshold {threshold}:")
    print(f"Total clusters: {len(cluster_map)}")
    print()

    disconnected_clusters = 0
    for cluster_id, nodes in cluster_map.items():
        if len(nodes) > 1:  # Only check multi-node clusters
            subgraph = G.subgraph(nodes)
            num_components = nx.number_connected_components(subgraph)
            
            if num_components > 1:
                disconnected_clusters += 1
                components = list(nx.connected_components(subgraph))
                print(f"Cluster {cluster_id}: DISCONNECTED")
                print(f"  - Nodes: {nodes}")
                print(f"  - {len(nodes)} nodes, {num_components} components")
                print(f"  - Component sizes: {[len(comp) for comp in components]}")
                
                # Show which actual nodes are in each component
                # components already contain the actual node IDs
                for i, comp in enumerate(components):
                    comp_nodes = sorted(list(comp))
                    print(f"  - Component {i+1}: {comp_nodes}")
                print()

    print(f"Summary: {disconnected_clusters} disconnected clusters found")
    return disconnected_clusters

# Test different thresholds
for threshold in [0.0, 0.1, 0.5, 1.0]:
    analyze_cluster_connectivity(threshold)
    print("-" * 60)