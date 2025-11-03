#!/usr/bin/env python3
"""
Simple Motif Clustering Analysis
Basic agglomerative clustering using only numpy and built-in libraries
"""

import json
import numpy as np
from collections import defaultdict

def load_distance_matrix():
    """Load Wasserstein distances and create distance matrix"""
    
    print("Loading Wasserstein distance data...")
    with open('data/wasserstein_distances.json', 'r') as f:
        distances = json.load(f)
    
    # Extract unique motif IDs
    motif_ids = set()
    for key in distances.keys():
        motif1, motif2 = key.split('-')
        motif_ids.add(int(motif1))
        motif_ids.add(int(motif2))
    
    motif_ids = sorted(list(motif_ids))
    n_motifs = len(motif_ids)
    
    print(f"Found {n_motifs} unique motifs")
    
    # Create distance matrix
    distance_matrix = np.zeros((n_motifs, n_motifs))
    motif_to_idx = {motif: i for i, motif in enumerate(motif_ids)}
    
    for key, distance in distances.items():
        motif1, motif2 = map(int, key.split('-'))
        i, j = motif_to_idx[motif1], motif_to_idx[motif2]
        distance_matrix[i, j] = distance
    
    return distance_matrix, motif_ids

def simple_agglomerative_clustering(distance_matrix, n_clusters):
    """Simple implementation of agglomerative clustering"""
    
    n_samples = distance_matrix.shape[0]
    
    # Initialize: each point is its own cluster
    clusters = [[i] for i in range(n_samples)]
    cluster_distances = distance_matrix.copy()
    
    print(f"Starting with {n_samples} clusters, target: {n_clusters}")
    
    # Merge clusters until we reach the target number
    while len(clusters) > n_clusters:
        # Find the closest pair of clusters
        min_dist = float('inf')
        merge_i, merge_j = -1, -1
        
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                # Calculate average linkage distance
                total_dist = 0
                count = 0
                
                for idx1 in clusters[i]:
                    for idx2 in clusters[j]:
                        total_dist += distance_matrix[idx1, idx2]
                        count += 1
                
                avg_dist = total_dist / count if count > 0 else float('inf')
                
                if avg_dist < min_dist:
                    min_dist = avg_dist
                    merge_i, merge_j = i, j
        
        # Merge the closest clusters
        if merge_i != -1 and merge_j != -1:
            clusters[merge_i].extend(clusters[merge_j])
            clusters.pop(merge_j)
            
            if len(clusters) % 50 == 0:
                print(f"  Clusters remaining: {len(clusters)}")
    
    # Convert to cluster labels
    cluster_labels = np.zeros(n_samples, dtype=int)
    for cluster_id, cluster_members in enumerate(clusters):
        for member in cluster_members:
            cluster_labels[member] = cluster_id
    
    return cluster_labels

def analyze_clustering_quality(distance_matrix, cluster_labels):
    """Analyze the quality of clustering"""
    
    n_clusters = len(np.unique(cluster_labels))
    
    # Calculate silhouette-like score manually
    silhouette_scores = []
    
    for i in range(len(cluster_labels)):
        # Intra-cluster distance (average distance to same cluster)
        same_cluster = cluster_labels == cluster_labels[i]
        same_cluster[i] = False  # Exclude self
        
        if np.sum(same_cluster) > 0:
            intra_dist = np.mean(distance_matrix[i, same_cluster])
        else:
            intra_dist = 0
        
        # Inter-cluster distance (average distance to nearest other cluster)
        min_inter_dist = float('inf')
        
        for cluster_id in np.unique(cluster_labels):
            if cluster_id != cluster_labels[i]:
                other_cluster = cluster_labels == cluster_id
                if np.sum(other_cluster) > 0:
                    inter_dist = np.mean(distance_matrix[i, other_cluster])
                    min_inter_dist = min(min_inter_dist, inter_dist)
        
        # Silhouette score for this point
        if max(intra_dist, min_inter_dist) > 0:
            silhouette = (min_inter_dist - intra_dist) / max(intra_dist, min_inter_dist)
        else:
            silhouette = 0
        
        silhouette_scores.append(silhouette)
    
    avg_silhouette = np.mean(silhouette_scores)
    
    return avg_silhouette

def find_optimal_clusters(distance_matrix, max_clusters=15):
    """Find optimal number of clusters by testing different values"""
    
    print("Finding optimal number of clusters...")
    
    n_samples = distance_matrix.shape[0]
    max_clusters = min(max_clusters, n_samples // 2)
    
    best_score = -1
    best_n_clusters = 2
    scores = []
    
    for n_clusters in range(2, max_clusters + 1):
        print(f"Testing {n_clusters} clusters...")
        
        cluster_labels = simple_agglomerative_clustering(distance_matrix, n_clusters)
        score = analyze_clustering_quality(distance_matrix, cluster_labels)
        
        scores.append((n_clusters, score))
        
        if score > best_score:
            best_score = score
            best_n_clusters = n_clusters
        
        print(f"  Silhouette score: {score:.3f}")
    
    print(f"\nOptimal number of clusters: {best_n_clusters} (score: {best_score:.3f})")
    
    return best_n_clusters, scores

def analyze_clusters(cluster_labels, motif_ids, distance_matrix):
    """Analyze the resulting clusters"""
    
    n_clusters = len(np.unique(cluster_labels))
    
    print(f"\n=== Cluster Analysis ===")
    print(f"Number of clusters: {n_clusters}")
    
    cluster_info = {}
    
    for cluster_id in range(n_clusters):
        cluster_motifs = [motif_ids[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
        cluster_size = len(cluster_motifs)
        
        # Calculate intra-cluster statistics
        cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
        
        if cluster_size > 1:
            intra_distances = []
            for i in range(len(cluster_indices)):
                for j in range(i + 1, len(cluster_indices)):
                    idx1, idx2 = cluster_indices[i], cluster_indices[j]
                    intra_distances.append(distance_matrix[idx1, idx2])
            
            avg_intra_distance = np.mean(intra_distances)
            max_intra_distance = np.max(intra_distances)
            min_intra_distance = np.min(intra_distances)
        else:
            avg_intra_distance = 0.0
            max_intra_distance = 0.0
            min_intra_distance = 0.0
        
        cluster_info[cluster_id] = {
            'size': cluster_size,
            'motifs': cluster_motifs,
            'avg_intra_distance': float(avg_intra_distance),
            'max_intra_distance': float(max_intra_distance),
            'min_intra_distance': float(min_intra_distance)
        }
        
        print(f"\nCluster {cluster_id}:")
        print(f"  Size: {cluster_size} motifs")
        if cluster_size <= 20:
            print(f"  Motifs: {cluster_motifs}")
        else:
            print(f"  Motifs: {cluster_motifs[:10]} ... and {cluster_size - 10} more")
        print(f"  Avg intra-cluster distance: {avg_intra_distance:.2f}")
        print(f"  Distance range: {min_intra_distance:.2f} - {max_intra_distance:.2f}")
    
    return cluster_info

def save_results(cluster_labels, motif_ids, cluster_info, silhouette_score):
    """Save clustering results to JSON files"""
    
    print("\nSaving clustering results...")
    
    # Main results
    results = {
        'clustering_summary': {
            'n_clusters': len(np.unique(cluster_labels)),
            'n_motifs': len(motif_ids),
            'silhouette_score': float(silhouette_score),
            'algorithm': 'agglomerative_clustering',
            'linkage': 'average'
        },
        'motif_to_cluster': {
            str(motif_ids[i]): int(cluster_labels[i]) 
            for i in range(len(motif_ids))
        },
        'cluster_details': cluster_info
    }
    
    with open('data/motif_clustering_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Simple cluster assignments
    cluster_assignments = {}
    for cluster_id in np.unique(cluster_labels):
        cluster_motifs = [motif_ids[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
        cluster_assignments[f"cluster_{cluster_id}"] = {
            'motifs': cluster_motifs,
            'size': len(cluster_motifs)
        }
    
    with open('data/motif_cluster_groups.json', 'w') as f:
        json.dump(cluster_assignments, f, indent=2)
    
    print("Results saved to:")
    print("  - data/motif_clustering_results.json")
    print("  - data/motif_cluster_groups.json")

def main():
    """Main function"""
    
    print("=== Simple Motif Clustering Analysis ===")
    
    # Load data
    distance_matrix, motif_ids = load_distance_matrix()
    
    # Find optimal number of clusters
    optimal_n_clusters, scores = find_optimal_clusters(distance_matrix)
    
    # Perform final clustering
    print(f"\nPerforming final clustering with {optimal_n_clusters} clusters...")
    cluster_labels = simple_agglomerative_clustering(distance_matrix, optimal_n_clusters)
    
    # Calculate final quality score
    final_score = analyze_clustering_quality(distance_matrix, cluster_labels)
    
    # Analyze clusters
    cluster_info = analyze_clusters(cluster_labels, motif_ids, distance_matrix)
    
    # Save results
    save_results(cluster_labels, motif_ids, cluster_info, final_score)
    
    print(f"\n=== Clustering Complete ===")
    print(f"Final configuration: {optimal_n_clusters} clusters")
    print(f"Final silhouette score: {final_score:.3f}")
    
    # Print cluster size summary
    cluster_sizes = [len([i for i in cluster_labels if i == c]) for c in np.unique(cluster_labels)]
    print(f"Cluster sizes: {sorted(cluster_sizes, reverse=True)}")

if __name__ == "__main__":
    main()