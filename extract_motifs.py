#!/usr/bin/env python3
"""
Motif extraction script for weighted Facebook graph data.
Extracts N-hop motifs where each motif consists of a source node and its neighbors within N hops.
"""

import csv
import json
import os
import argparse
from collections import defaultdict, deque

def load_graph_data(filepath: str):
    """Load the weighted graph data from CSV file."""
    try:
        edges = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f) 
            for row in reader:
                edges.append({
                    'Node1': int(row['Node1']),
                    'Node2': int(row['Node2']),
                    'Weight': float(row['Weight'])
                })
        print(f"Loaded graph with {len(edges)} edges")
        return edges
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def build_adjacency_list(edges):
    """
    Build adjacency list representation of the graph.
    Returns dict where key is node and value is list of connected nodes with weights.
    """
    adjacency_list = defaultdict(list)

    for edge in edges:
        node1, node2, weight = edge['Node1'], edge['Node2'], edge['Weight']

        # Add both directions since it's an undirected graph
        adjacency_list[node1].append({'neighbor': node2, 'weight': weight})
        adjacency_list[node2].append({'neighbor': node1, 'weight': weight})

    return dict(adjacency_list)


def get_nodes_within_hops(adjacency_list, source_node, hop_distance):
    """
    Use BFS to find all nodes within hop_distance from source_node.
    Returns dict: {node_id: hop_level} where hop_level is 1, 2, ..., hop_distance
    """
    if hop_distance < 1:
        return {}

    nodes_at_hops = {source_node: 0}  # source is at hop 0
    queue = deque([(source_node, 0)])
    visited = {source_node}

    while queue:
        current, current_hop = queue.popleft()

        if current_hop >= hop_distance:
            continue

        if current in adjacency_list:
            for neighbor_info in adjacency_list[current]:
                neighbor = neighbor_info['neighbor']
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_hop = current_hop + 1
                    nodes_at_hops[neighbor] = next_hop
                    queue.append((neighbor, next_hop))

    # Remove source node from the result (it stays at hop 0)
    del nodes_at_hops[source_node]
    return nodes_at_hops


def extract_subgraph_motifs(adjacency_list, hop_distance=1):
    """
    Extract subgraph motifs from the graph.
    Each motif is a complete subgraph containing:
    1. Source node
    2. All neighbors within hop_distance from source
    3. All edges between those nodes
    """
    motifs = []
    motif_stats = {
        'total_motifs': 0,
        'unique_nodes': set(),
        'total_edges_in_motifs': 0,
        'motif_size_distribution': defaultdict(int),
        'hop_distance': hop_distance
    }

    for source_node in adjacency_list.keys():
        motif_stats['unique_nodes'].add(source_node)

        # Get all nodes within hop_distance using BFS
        nodes_at_hops = get_nodes_within_hops(adjacency_list, source_node, hop_distance)

        if len(nodes_at_hops) == 0:
            continue

        # Get list of all nodes in the motif (source + neighbors within N hops)
        motif_nodes = list(nodes_at_hops.keys())
        # Include source node in the set for edge detection
        motif_node_set = set(motif_nodes) | {source_node}

        # Create the motif subgraph
        motif = {
            'motif_id': f"motif_{source_node}",
            'source_node': source_node,
            'hop_distance': hop_distance,
            'neighbors': motif_nodes,
            'edges': []
        }

        # Add edges from source to its neighbors (direct edges)
        if source_node in adjacency_list:
            for neighbor_info in adjacency_list[source_node]:
                target = neighbor_info['neighbor']
                weight = neighbor_info['weight']

                if target in motif_node_set:
                    edge = {
                        'from': source_node,
                        'to': target,
                        'weight': weight,
                        'edge_type': 'source_to_neighbor',
                        'from_hop': 0,
                        'to_hop': nodes_at_hops.get(target, 0)
                    }
                    motif['edges'].append(edge)
                    motif_stats['total_edges_in_motifs'] += 1

        # Add edges between all other nodes in the motif
        for node in motif_nodes:
            if node in adjacency_list:
                for neighbor_info in adjacency_list[node]:
                    target = neighbor_info['neighbor']
                    weight = neighbor_info['weight']

                    # Only include edges where both endpoints are in the motif
                    if target in motif_node_set and target != source_node:
                        hop_level = nodes_at_hops[node]
                        target_hop = nodes_at_hops.get(target, 0)  # 0 if target is source

                        # Classify edge type based on hop levels
                        if target == source_node or node == source_node:
                            edge_type = 'source_to_neighbor'
                        elif abs(hop_level - target_hop) == 0:
                            edge_type = 'neighbor_to_neighbor'
                        elif abs(hop_level - target_hop) == 1:
                            edge_type = 'hop_to_hop'
                        else:
                            edge_type = 'extended_edge'

                        # Avoid duplicate edges (only add if node < target)
                        if node < target:
                            edge = {
                                'from': node,
                                'to': target,
                                'weight': weight,
                                'edge_type': edge_type,
                                'from_hop': hop_level,
                                'to_hop': target_hop
                            }
                            motif['edges'].append(edge)
                            motif_stats['total_edges_in_motifs'] += 1

        # Calculate motif statistics
        motif['num_neighbors'] = len(motif_nodes)
        motif['num_edges'] = len(motif['edges'])
        motif['subgraph_density'] = len(motif['edges']) / max(1, len(motif_nodes)) if motif_nodes else 0

        # Add hop level distribution
        hop_counts = defaultdict(int)
        for node, hop in nodes_at_hops.items():
            hop_counts[hop] += 1
        motif['hop_distribution'] = dict(hop_counts)

        motifs.append(motif)
        motif_stats['total_motifs'] += 1
        motif_stats['motif_size_distribution'][len(motif_nodes)] += 1

    # Convert set to list for JSON serialization
    motif_stats['unique_nodes'] = list(motif_stats['unique_nodes'])
    motif_stats['total_unique_nodes'] = len(motif_stats['unique_nodes'])
    motif_stats['motif_size_distribution'] = dict(motif_stats['motif_size_distribution'])
    motif_stats['average_motif_size'] = sum(len(m['neighbors']) for m in motifs) / len(motifs) if motifs else 0

    return {
        'motifs': motifs,
        'statistics': motif_stats
    }

def save_motifs_to_json(motifs_data, output_path):
    """Save extracted motifs to JSON file."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(motifs_data, f, indent=2)
        
        print(f"Motifs successfully saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error saving motifs: {e}")
        return False

def main():
    """Main function to orchestrate motif extraction process."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract N-hop motifs from graph data')
    parser.add_argument('--hop', type=int, default=1, choices=[1, 2, 3],
                        help='Hop distance for motif extraction (default: 1)')
    args = parser.parse_args()

    hop_distance = args.hop

    input_file = "facebook_weighted_filtered.csv"

    # Output filename based on hop distance
    if hop_distance == 1:
        output_file = "data/facebook_motifs.json"
    else:
        output_file = f"data/facebook_motifs_{hop_distance}hop.json"

    print("Starting motif extraction process...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Hop distance: {hop_distance}")

    # Load graph data
    edges = load_graph_data(input_file)
    if edges is None:
        return

    # Build adjacency list
    print("Building adjacency list...")
    adjacency_list = build_adjacency_list(edges)
    print(f"Graph has {len(adjacency_list)} unique nodes")

    # Extract motifs
    print(f"Extracting {hop_distance}-hop subgraph motifs...")
    motifs_data = extract_subgraph_motifs(adjacency_list, hop_distance=hop_distance)

    # Print statistics
    stats = motifs_data['statistics']
    print(f"\n{hop_distance}-hop Motif Extraction Results:")
    print(f"- Total motifs extracted: {stats['total_motifs']}")
    print(f"- Unique nodes: {stats['total_unique_nodes']}")
    print(f"- Total edges in all motifs: {stats['total_edges_in_motifs']}")
    print(f"- Average motif size: {stats['average_motif_size']:.2f} nodes")
    print(f"- Motif size distribution: {stats['motif_size_distribution']}")

    # Save results
    if save_motifs_to_json(motifs_data, output_file):
        print(f"\nMotif extraction completed successfully!")
        print(f"Results saved to: {output_file}")
    else:
        print("Failed to save motifs to file")


if __name__ == "__main__":
    main()