#!/usr/bin/env python3
"""
Compute Maximum Spanning Trees for all motifs and save to JSON.
This pre-computes MSTs to avoid calculating them in real-time during visualization.
"""

import json
from collections import defaultdict

def find_maximum_spanning_tree(motif):
    """
    Find Maximum Spanning Tree using Prim's algorithm starting from source node.
    
    Args:
        motif: Motif data containing source_node, neighbors, and edges
        
    Returns:
        dict: MST data with nodes, edges, total_weight, and excluded_edges
    """
    source_node = motif['source_node']
    all_nodes = [source_node] + motif['neighbors']
    edges = motif['edges']
    
    # Create adjacency list with weights
    adjacency_list = defaultdict(list)
    for edge in edges:
        adjacency_list[edge['from']].append({
            'node': edge['to'], 
            'weight': edge['weight']
        })
        adjacency_list[edge['to']].append({
            'node': edge['from'], 
            'weight': edge['weight']
        })
    
    # Prim's algorithm for Maximum Spanning Tree
    mst_edges = []
    visited = {source_node}
    total_weight = 0
    
    while len(visited) < len(all_nodes):
        max_edge = None
        max_weight = -1
        
        # Find maximum weight edge from visited to unvisited nodes
        for visited_node in visited:
            for neighbor in adjacency_list[visited_node]:
                if neighbor['node'] not in visited and neighbor['weight'] > max_weight:
                    max_weight = neighbor['weight']
                    max_edge = {
                        'from': visited_node,
                        'to': neighbor['node'],
                        'weight': neighbor['weight']
                    }
        
        if max_edge:
            mst_edges.append(max_edge)
            visited.add(max_edge['to'])
            total_weight += max_edge['weight']
    
    # Find excluded edges
    excluded_edges = []
    for edge in edges:
        is_in_mst = any(
            (mst_edge['from'] == edge['from'] and mst_edge['to'] == edge['to']) or
            (mst_edge['from'] == edge['to'] and mst_edge['to'] == edge['from'])
            for mst_edge in mst_edges
        )
        if not is_in_mst:
            excluded_edges.append(edge)
    
    return {
        'source_node': source_node,
        'nodes': all_nodes,
        'mst_edges': mst_edges,
        'excluded_edges': excluded_edges,
        'total_weight': total_weight,
        'num_mst_edges': len(mst_edges),
        'num_excluded_edges': len(excluded_edges)
    }

def compute_all_msts():
    """Compute MSTs for all motifs and save to JSON."""
    
    print("Loading motifs data...")
    with open('data/facebook_motifs.json', 'r') as f:
        motifs_data = json.load(f)
    
    motifs = motifs_data['motifs']
    print(f"Computing MSTs for {len(motifs)} motifs...")
    
    mst_data = {}
    
    for i, motif in enumerate(motifs):
        source_node = motif['source_node']
        
        # Skip motifs with only one node (no edges to form MST)
        if len(motif['neighbors']) == 0:
            print(f"Skipping motif {source_node}: no neighbors")
            continue
        
        # Compute MST
        mst = find_maximum_spanning_tree(motif)
        mst_data[str(source_node)] = mst
        
        # Progress indicator
        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1}/{len(motifs)} motifs...")
    
    # Save MST data
    output_file = 'data/facebook_msts.json'
    with open(output_file, 'w') as f:
        json.dump(mst_data, f, indent=2)
    
    print(f"\nMST computation completed!")
    print(f"Results saved to: {output_file}")
    print(f"Total MSTs computed: {len(mst_data)}")
    
    # Calculate some statistics
    total_weights = [mst['total_weight'] for mst in mst_data.values()]
    avg_weight = sum(total_weights) / len(total_weights) if total_weights else 0
    max_weight = max(total_weights) if total_weights else 0
    min_weight = min(total_weights) if total_weights else 0
    
    print(f"\nMST Statistics:")
    print(f"- Average MST weight: {avg_weight:.2f}")
    print(f"- Maximum MST weight: {max_weight:.2f}")
    print(f"- Minimum MST weight: {min_weight:.2f}")
    
    return mst_data

def verify_mst_data():
    """Verify the computed MST data by checking a few examples."""
    
    try:
        with open('data/facebook_msts.json', 'r') as f:
            mst_data = json.load(f)
        
        print(f"\nVerification: Loaded {len(mst_data)} MSTs")
        
        # Show example MST
        if mst_data:
            example_key = list(mst_data.keys())[0]
            example_mst = mst_data[example_key]
            
            print(f"\nExample MST for source node {example_key}:")
            print(f"- Nodes: {len(example_mst['nodes'])}")
            print(f"- MST edges: {example_mst['num_mst_edges']}")
            print(f"- Excluded edges: {example_mst['num_excluded_edges']}")
            print(f"- Total weight: {example_mst['total_weight']}")
            
            print(f"- MST edges:")
            for edge in example_mst['mst_edges'][:5]:  # Show first 5
                print(f"  {edge['from']} ↔ {edge['to']} (weight: {edge['weight']})")
            if len(example_mst['mst_edges']) > 5:
                print(f"  ... and {len(example_mst['mst_edges']) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"Error verifying MST data: {e}")
        return False

if __name__ == "__main__":
    # Compute all MSTs
    mst_data = compute_all_msts()
    
    # Verify the results
    verify_mst_data()