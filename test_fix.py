#!/usr/bin/env python3
"""
Test the connectivity fix
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

def build_connected_clusters(labels):
    """Build cluster mapping ensuring each cluster is connected"""
    # Build initial cluster mapping
    initial_cluster_map = {}
    for idx, label in enumerate(labels):
        initial_cluster_map.setdefault(label, []).append(index_node[idx])
    
    # Split disconnected clusters into connected components
    cluster_map = {}
    cluster_counter = 0
    
    for original_cluster_id, nodes in initial_cluster_map.items():
        if len(nodes) == 1:
            cluster_map[cluster_counter] = nodes
            cluster_counter += 1
        else:
            subgraph = G.subgraph(nodes)
            components = list(nx.connected_components(subgraph))
            
            for component in components:
                cluster_map[cluster_counter] = list(component)
                cluster_counter += 1
    
    return cluster_map

def test_connectivity_fix(threshold=0.1):
    """Test that all clusters are now connected"""
    model = AgglomerativeClustering(
        metric='precomputed',
        distance_threshold=threshold,
        n_clusters=None,
        linkage='average'
    )
    labels = model.fit_predict(dist_matrix)
    
    print(f"Testing connectivity fix at threshold {threshold}")
    
    # Test old approach
    old_cluster_map = {}
    for idx, label in enumerate(labels):
        old_cluster_map.setdefault(label, []).append(index_node[idx])
    
    old_disconnected = 0
    for nodes in old_cluster_map.values():
        if len(nodes) > 1:
            subgraph = G.subgraph(nodes)
            if nx.number_connected_components(subgraph) > 1:
                old_disconnected += 1
    
    # Test new approach
    new_cluster_map = build_connected_clusters(labels)
    
    new_disconnected = 0
    for nodes in new_cluster_map.values():
        if len(nodes) > 1:
            subgraph = G.subgraph(nodes)
            if nx.number_connected_components(subgraph) > 1:
                new_disconnected += 1
    
    print(f"Old approach: {old_disconnected}/{len(old_cluster_map)} clusters disconnected")
    print(f"New approach: {new_disconnected}/{len(new_cluster_map)} clusters disconnected")
    print(f"Clusters before fix: {len(old_cluster_map)}")
    print(f"Clusters after fix: {len(new_cluster_map)}")
    
    return new_disconnected == 0

# Test the fix
success = test_connectivity_fix(0.1)
print(f"\nFix successful: {success}")