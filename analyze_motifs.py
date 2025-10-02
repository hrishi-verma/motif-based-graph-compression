#!/usr/bin/env python3
"""
Analyze motifs to identify disconnected components
"""
import json
import numpy as np
import networkx as nx

# Load motif data
with open('facebook_motifs.json', 'r') as f:
    motif_data = json.load(f)

def analyze_motif_connectivity(motif_id, motif_info):
    """Analyze if a motif has disconnected components"""
    nodes = motif_info['nodes']
    adj_matrix = np.array(motif_info['adjacency_matrix'])
    
    # Create NetworkX graph from adjacency matrix
    G = nx.from_numpy_array(adj_matrix)
    
    # Check connectivity
    num_components = nx.number_connected_components(G)
    components = list(nx.connected_components(G))
    
    # Find isolated nodes (degree 0)
    degrees = dict(G.degree())
    isolated_nodes = [i for i, deg in degrees.items() if deg == 0]
    
    return {
        'motif_id': motif_id,
        'num_nodes': len(nodes),
        'num_components': num_components,
        'is_connected': num_components == 1,
        'isolated_nodes': len(isolated_nodes),
        'component_sizes': [len(comp) for comp in components],
        'actual_node_ids': [nodes[i] for i in isolated_nodes] if isolated_nodes else []
    }

# Analyze first 10 motifs
print("Motif Connectivity Analysis:")
print("=" * 60)
disconnected_count = 0
total_analyzed = 0

for motif_id in list(motif_data.keys())[:10]:
    result = analyze_motif_connectivity(motif_id, motif_data[motif_id])
    total_analyzed += 1
    
    if not result['is_connected']:
        disconnected_count += 1
        print(f"Motif {motif_id}: DISCONNECTED")
        print(f"  - {result['num_nodes']} nodes, {result['num_components']} components")
        print(f"  - Component sizes: {result['component_sizes']}")
        print(f"  - Isolated nodes: {result['isolated_nodes']}")
        if result['actual_node_ids']:
            print(f"  - Isolated node IDs: {result['actual_node_ids']}")
        print()
    else:
        print(f"Motif {motif_id}: Connected ({result['num_nodes']} nodes)")

print(f"\nSummary: {disconnected_count}/{total_analyzed} motifs are disconnected")