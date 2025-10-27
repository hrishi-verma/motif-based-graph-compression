#!/usr/bin/env python3
"""
Wasserstein Distance Analysis Tool
Analyzes the computed Wasserstein distances and finds interesting patterns
"""

import json
import math

def load_wasserstein_data():
    """Load Wasserstein distances and persistence data"""
    with open('data/wasserstein_distances.json', 'r') as f:
        distances = json.load(f)
    
    with open('data/persistence_coordinates.json', 'r') as f:
        persistence_data = json.load(f)
    
    return distances, persistence_data

def find_most_similar_motifs(distances, n=10):
    """Find the most similar motif pairs"""
    
    # Get unique pairs (avoid duplicates like "1-2" and "2-1")
    unique_pairs = {}
    for key, distance in distances.items():
        if distance > 0:  # Exclude self-distances
            motif1, motif2 = key.split('-')
            pair_key = f"{min(motif1, motif2)}-{max(motif1, motif2)}"
            if pair_key not in unique_pairs:
                unique_pairs[pair_key] = distance
    
    # Sort by distance
    sorted_pairs = sorted(unique_pairs.items(), key=lambda x: x[1])
    
    print(f"\n=== {n} Most Similar Motif Pairs ===")
    for i, (pair, distance) in enumerate(sorted_pairs[:n]):
        motif1, motif2 = pair.split('-')
        print(f"{i+1:2d}. Motifs {motif1:3s} ↔ {motif2:3s}: {distance:.4f}")
    
    return sorted_pairs[:n]

def find_most_different_motifs(distances, n=10):
    """Find the most different motif pairs"""
    
    # Get unique pairs
    unique_pairs = {}
    for key, distance in distances.items():
        if distance > 0:
            motif1, motif2 = key.split('-')
            pair_key = f"{min(motif1, motif2)}-{max(motif1, motif2)}"
            if pair_key not in unique_pairs:
                unique_pairs[pair_key] = distance
    
    # Sort by distance (descending)
    sorted_pairs = sorted(unique_pairs.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n=== {n} Most Different Motif Pairs ===")
    for i, (pair, distance) in enumerate(sorted_pairs[:n]):
        motif1, motif2 = pair.split('-')
        print(f"{i+1:2d}. Motifs {motif1:3s} ↔ {motif2:3s}: {distance:.4f}")
    
    return sorted_pairs[:n]

def analyze_motif_neighborhoods(distances, persistence_data, motif_id, n=5):
    """Find the most similar motifs to a given motif"""
    
    # Get distances for this motif
    motif_distances = []
    for key, distance in distances.items():
        if key.startswith(f"{motif_id}-") and distance > 0:
            other_motif = key.split('-')[1]
            motif_distances.append((other_motif, distance))
    
    # Sort by distance
    motif_distances.sort(key=lambda x: x[1])
    
    print(f"\n=== Motif {motif_id} - Most Similar Neighbors ===")
    motif_stats = persistence_data['motifs'][motif_id]['statistics']
    print(f"Reference motif {motif_id}: {motif_stats['total_points']} points, {motif_stats['mst_edges']} MST edges")
    
    for i, (neighbor_id, distance) in enumerate(motif_distances[:n]):
        neighbor_stats = persistence_data['motifs'][neighbor_id]['statistics']
        print(f"{i+1}. Motif {neighbor_id:3s}: distance = {distance:.4f} "
              f"({neighbor_stats['total_points']} points, {neighbor_stats['mst_edges']} MST edges)")
    
    return motif_distances[:n]

def create_similarity_clusters(distances, threshold=50.0):
    """Group motifs into similarity clusters based on distance threshold"""
    
    # Get all motif IDs
    motif_ids = set()
    for key in distances.keys():
        motif1, motif2 = key.split('-')
        motif_ids.add(motif1)
        motif_ids.add(motif2)
    
    motif_ids = sorted(motif_ids, key=int)
    
    # Build adjacency list for similar motifs
    similar_pairs = set()
    for key, distance in distances.items():
        if 0 < distance <= threshold:
            motif1, motif2 = key.split('-')
            similar_pairs.add((min(motif1, motif2), max(motif1, motif2)))
    
    # Find connected components (clusters)
    clusters = []
    visited = set()
    
    def dfs(motif, cluster):
        if motif in visited:
            return
        visited.add(motif)
        cluster.append(motif)
        
        # Find all similar motifs
        for m1, m2 in similar_pairs:
            if m1 == motif and m2 not in visited:
                dfs(m2, cluster)
            elif m2 == motif and m1 not in visited:
                dfs(m1, cluster)
    
    for motif_id in motif_ids:
        if motif_id not in visited:
            cluster = []
            dfs(motif_id, cluster)
            if len(cluster) > 1:  # Only keep clusters with multiple motifs
                clusters.append(sorted(cluster, key=int))
    
    print(f"\n=== Similarity Clusters (threshold ≤ {threshold}) ===")
    print(f"Found {len(clusters)} clusters with multiple motifs")
    
    for i, cluster in enumerate(clusters):
        if len(cluster) <= 10:  # Show small clusters completely
            print(f"Cluster {i+1}: {cluster}")
        else:  # Show large clusters partially
            print(f"Cluster {i+1}: {cluster[:5]} ... and {len(cluster)-5} more motifs")
    
    return clusters

def generate_distance_summary(distances, persistence_data):
    """Generate a comprehensive summary of the distance analysis"""
    
    summary = {
        'statistics': {},
        'most_similar': [],
        'most_different': [],
        'clusters': [],
        'motif_neighborhoods': {}
    }
    
    # Basic statistics
    distance_values = [d for d in distances.values() if d > 0]
    summary['statistics'] = {
        'total_pairs': len(distance_values),
        'mean_distance': sum(distance_values) / len(distance_values),
        'min_distance': min(distance_values),
        'max_distance': max(distance_values),
        'std_deviation': math.sqrt(sum((d - sum(distance_values) / len(distance_values)) ** 2 
                                     for d in distance_values) / len(distance_values))
    }
    
    # Most similar and different pairs
    unique_pairs = {}
    for key, distance in distances.items():
        if distance > 0:
            motif1, motif2 = key.split('-')
            pair_key = f"{min(motif1, motif2)}-{max(motif1, motif2)}"
            if pair_key not in unique_pairs:
                unique_pairs[pair_key] = distance
    
    sorted_pairs = sorted(unique_pairs.items(), key=lambda x: x[1])
    summary['most_similar'] = sorted_pairs[:10]
    summary['most_different'] = sorted_pairs[-10:]
    
    # Save summary
    with open('data/wasserstein_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nDistance summary saved to data/wasserstein_summary.json")
    
    return summary

def main():
    """Main analysis function"""
    
    print("Loading Wasserstein distance data...")
    distances, persistence_data = load_wasserstein_data()
    
    print(f"Loaded {len(distances)} distance pairs")
    
    # Find most similar and different motifs
    most_similar = find_most_similar_motifs(distances, 10)
    most_different = find_most_different_motifs(distances, 10)
    
    # Analyze specific motifs
    interesting_motifs = ['1', '48', '53', '273']
    for motif_id in interesting_motifs:
        if motif_id in persistence_data['motifs']:
            analyze_motif_neighborhoods(distances, persistence_data, motif_id, 5)
    
    # Find similarity clusters
    clusters = create_similarity_clusters(distances, threshold=50.0)
    
    # Generate comprehensive summary
    summary = generate_distance_summary(distances, persistence_data)
    
    print(f"\n=== Analysis Complete ===")
    print(f"Most similar pair: {most_similar[0][0]} (distance: {most_similar[0][1]:.4f})")
    print(f"Most different pair: {most_different[0][0]} (distance: {most_different[0][1]:.4f})")
    print(f"Found {len(clusters)} similarity clusters")

if __name__ == "__main__":
    main()