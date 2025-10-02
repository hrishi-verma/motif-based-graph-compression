#!/usr/bin/env python3
"""
Motif extraction script for weighted Facebook graph data.
Extracts one-hop motifs where each motif consists of a source node and its direct neighbors.
"""

import csv
import json
import os
from collections import defaultdict

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

def extract_subgraph_motifs(adjacency_list):
    """
    Extract subgraph motifs from the graph.
    Each motif is a complete subgraph containing:
    1. Source node
    2. All neighbors at distance 1 from source
    3. All edges between those neighbors
    """
    motifs = []
    motif_stats = {
        'total_motifs': 0,
        'unique_nodes': set(),
        'total_edges_in_motifs': 0,
        'motif_size_distribution': defaultdict(int)
    }
    
    for source_node, neighbor_list in adjacency_list.items():
        motif_stats['unique_nodes'].add(source_node)
        
        # Get all neighbors of the source node
        neighbors = [n['neighbor'] for n in neighbor_list]
        
        if len(neighbors) == 0:
            continue
            
        # Create the motif subgraph
        motif = {
            'motif_id': f"motif_{source_node}",
            'source_node': source_node,
            'neighbors': neighbors,
            'edges': []
        }
        
        # Add edges from source to all neighbors
        for neighbor_info in neighbor_list:
            neighbor_node = neighbor_info['neighbor']
            weight = neighbor_info['weight']
            
            edge = {
                'from': source_node,
                'to': neighbor_node,
                'weight': weight,
                'edge_type': 'source_to_neighbor'
            }
            motif['edges'].append(edge)
            motif_stats['total_edges_in_motifs'] += 1
        
        # Find edges between neighbors (within the motif)
        neighbor_set = set(neighbors)
        for neighbor in neighbors:
            if neighbor in adjacency_list:
                for neighbor_of_neighbor in adjacency_list[neighbor]:
                    target = neighbor_of_neighbor['neighbor']
                    weight = neighbor_of_neighbor['weight']
                    
                    # If the target is also a neighbor of source (and not source itself)
                    if target in neighbor_set and target != source_node:
                        # Avoid duplicate edges (only add if neighbor < target to prevent A->B and B->A)
                        if neighbor < target:
                            edge = {
                                'from': neighbor,
                                'to': target,
                                'weight': weight,
                                'edge_type': 'neighbor_to_neighbor'
                            }
                            motif['edges'].append(edge)
                            motif_stats['total_edges_in_motifs'] += 1
        
        # Calculate motif statistics
        motif['num_neighbors'] = len(neighbors)
        motif['num_edges'] = len(motif['edges'])
        motif['subgraph_density'] = len(motif['edges']) / max(1, len(neighbors)) if neighbors else 0
        
        motifs.append(motif)
        motif_stats['total_motifs'] += 1
        motif_stats['motif_size_distribution'][len(neighbors)] += 1
    
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
    input_file = "facebook_weighted_filtered.csv"
    output_file = "data/facebook_motifs.json"
    
    print("Starting motif extraction process...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    # Load graph data
    edges = load_graph_data(input_file)
    if edges is None:
        return
    
    # Build adjacency list
    print("Building adjacency list...")
    adjacency_list = build_adjacency_list(edges)
    print(f"Graph has {len(adjacency_list)} unique nodes")
    
    # Extract motifs
    print("Extracting subgraph motifs...")
    motifs_data = extract_subgraph_motifs(adjacency_list)
    
    # Print statistics
    stats = motifs_data['statistics']
    print(f"\nSubgraph Motif Extraction Results:")
    print(f"- Total motifs extracted: {stats['total_motifs']}")
    print(f"- Unique nodes: {stats['total_unique_nodes']}")
    print(f"- Total edges in all motifs: {stats['total_edges_in_motifs']}")
    print(f"- Average motif size: {stats['average_motif_size']:.2f} neighbors")
    print(f"- Motif size distribution: {stats['motif_size_distribution']}")
    
    # Save results
    if save_motifs_to_json(motifs_data, output_file):
        print(f"\nMotif extraction completed successfully!")
        print(f"Results saved to: {output_file}")
    else:
        print("Failed to save motifs to file")

if __name__ == "__main__":
    main()