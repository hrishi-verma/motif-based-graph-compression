#!/usr/bin/env python3
"""
Compute Maximum Spanning Trees for all motifs and save to JSON.
This pre-computes MSTs to avoid calculating them in real-time during visualization.

Optimized with heap-based Prim's algorithm for better performance.
"""

import json
import argparse
import heapq
from collections import defaultdict

def find_maximum_spanning_tree(motif):
    """
    Find Maximum Spanning Tree using optimized Prim's algorithm with heap.
    Time complexity: O(E log V) instead of O(V^2)
    """
    source_node = motif['source_node']
    all_nodes = [source_node] + motif['neighbors']
    edges = motif['edges']

    if len(all_nodes) <= 1:
        return {
            'source_node': source_node,
            'nodes': all_nodes,
            'mst_edges': [],
            'excluded_edges': edges,
            'total_weight': 0,
            'num_mst_edges': 0,
            'num_excluded_edges': len(edges)
        }

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

    # Heap-based Prim's algorithm for Maximum Spanning Tree
    # Use negative weights because heapq is a min-heap
    mst_edges = []
    visited = {source_node}
    total_weight = 0

    # Initialize heap with edges from source node
    heap = []
    for neighbor in adjacency_list[source_node]:
        heapq.heappush(heap, (-neighbor['weight'], source_node, neighbor['node']))

    while heap and len(visited) < len(all_nodes):
        neg_weight, from_node, to_node = heapq.heappop(heap)

        if to_node in visited:
            continue

        # Add edge to MST
        visited.add(to_node)
        mst_edges.append({
            'from': from_node,
            'to': to_node,
            'weight': -neg_weight
        })
        total_weight += -neg_weight

        # Add edges from newly visited node
        for neighbor in adjacency_list[to_node]:
            if neighbor['node'] not in visited:
                heapq.heappush(heap, (-neighbor['weight'], to_node, neighbor['node']))

    # Find excluded edges
    excluded_edges = []
    mst_edge_set = set()
    for mst_edge in mst_edges:
        mst_edge_set.add((mst_edge['from'], mst_edge['to']))
        mst_edge_set.add((mst_edge['to'], mst_edge['from']))

    for edge in edges:
        if (edge['from'], edge['to']) not in mst_edge_set:
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

def compute_all_msts(hop_distance=1):
    """Compute MSTs for all motifs and save to JSON."""

    # Determine input/output filenames based on hop distance
    if hop_distance == 1:
        input_file = 'data/facebook_motifs.json'
        output_file = 'data/facebook_msts.json'
    else:
        input_file = f'data/facebook_motifs_{hop_distance}hop.json'
        output_file = f'data/facebook_msts_{hop_distance}hop.json'

    print(f"Loading motifs data from {input_file}...")
    with open(input_file, 'r') as f:
        motifs_data = json.load(f)

    motifs = motifs_data['motifs']
    print(f"Computing MSTs for {len(motifs)} {hop_distance}-hop motifs...")

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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Compute MSTs for motif data')
    parser.add_argument('--hop', type=int, default=1, choices=[1, 2, 3],
                        help='Hop distance for motif MST computation (default: 1)')
    args = parser.parse_args()

    # Compute all MSTs
    mst_data = compute_all_msts(hop_distance=args.hop)

    # Verify the results (only for 1-hop)
    if args.hop == 1:
        verify_mst_data()