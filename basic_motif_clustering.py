#!/usr/bin/env python3
"""
Basic Motif Clustering Analysis
Pure Python implementation without external dependencies
"""

import json
import math
from collections import defaultdict

def load_distance_data():
    """Load Wasserstein distances and create motif list"""
    
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
    
    # Create distance lookup for easy access
    distance_lookup = {}
    for key, distance in distances.items():
        motif1, motif2 = map(int, key.split('-'))
        distance_lookup[(motif1, motif2)] = distance
        distance_lookup[(motif2, motif1)] = distance  # Symmetric
    
    # Add self-distances
    for motif in motif_ids:
        distance_lookup[(motif, motif)] = 0.0
    
    return motif_ids, distance_lookup

def get_distance(motif1, motif2, distance_lookup):
    """Get distance between two motifs"""
    return distance_lookup.get((motif1, motif2), float('inf'))

def calculate_cluster_distance(cluster1, cluster2, distance_lookup, linkage='average'):
    """Calculate distance between two clusters using specified linkage"""
    
    if linkage == 'average':
        total_distance = 0
        count = 0
        for m1 in cluster1:
            for m2 in cluster2:
                total_distance += get_distance(m1, m2, distance_lookup)
                count += 1
        return total_distance / count if count > 0 else float('inf')
    
    elif linkage == 'single':
        min_distance = float('inf')
        for m1 in cluster1:
            for m2 in cluster2:
                distance = get_distance(m1, m2, distance_lookup)
                min_distance = min(min_distance, distance)
        return min_distance
    
    elif linkage == 'complete':
        max_distance = 0
        for m1 in cluster1:
            for m2 in cluster2:
                distance = get_distance(m1, m2, distance_lookup)
                max_distance = max(max_distance, distance)
        return max_distance

def agglomerative_clustering(motif_ids, distance_lookup, n_clusters, linkage='average'):
    """Perform agglomerative clustering"""
    
    print(f"Performing agglomerative clustering with {linkage} linkage...")
    
    # Initialize: each motif is its own cluster
    clusters = [[motif] for motif in motif_ids]
    
    print(f"Starting with {len(clusters)} clusters, target: {n_clusters}")
    
    # Merge clusters until we reach target number
    while len(clusters) > n_clusters:
        min_distance = float('inf')
        merge_i, merge_j = -1, -1
        
        # Find closest pair of clusters
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                distance = calculate_cluster_distance(clusters[i], clusters[j], distance_lookup, linkage)
                
                if distance < min_distance:
                    min_distance = distance
                    merge_i, merge_j = i, j
        
        # Merge the closest clusters
        if merge_i != -1 and merge_j != -1:
            clusters[merge_i].extend(clusters[merge_j])
            clusters.pop(merge_j)
            
            if len(clusters) % 50 == 0:
                print(f"  Clusters remaining: {len(clusters)}")
    
    return clusters

def calculate_silhouette_score(clusters, distance_lookup):
    """Calculate silhouette score for clustering quality"""
    
    print("Calculating silhouette score...")
    
    # Create motif to cluster mapping
    motif_to_cluster = {}
    for cluster_id, cluster in enumerate(clusters):
        for motif in cluster:
            motif_to_cluster[motif] = cluster_id
    
    silhouette_scores = []
    
    for cluster_id, cluster in enumerate(clusters):
        for motif in cluster:
            # Calculate average intra-cluster distance
            if len(cluster) > 1:
                intra_distances = []
                for other_motif in cluster:
                    if other_motif != motif:
                        intra_distances.append(get_distance(motif, other_motif, distance_lookup))
                avg_intra = sum(intra_distances) / len(intra_distances)
            else:
                avg_intra = 0
            
            # Calculate average inter-cluster distance to nearest cluster
            min_inter = float('inf')
            for other_cluster_id, other_cluster in enumerate(clusters):
                if other_cluster_id != cluster_id:
                    inter_distances = []
                    for other_motif in other_cluster:
                        inter_distances.append(get_distance(motif, other_motif, distance_lookup))
                    avg_inter = sum(inter_distances) / len(inter_distances)
                    min_inter = min(min_inter, avg_inter)
            
            # Calculate silhouette score for this motif
            if max(avg_intra, min_inter) > 0:
                silhouette = (min_inter - avg_intra) / max(avg_intra, min_inter)
            else:
                silhouette = 0
            
            silhouette_scores.append(silhouette)
    
    return sum(silhouette_scores) / len(silhouette_scores) if silhouette_scores else 0

def find_optimal_clusters(motif_ids, distance_lookup, max_clusters=15):
    """Find optimal number of clusters"""
    
    print("Finding optimal number of clusters...")
    
    n_motifs = len(motif_ids)
    max_clusters = min(max_clusters, n_motifs // 2)
    
    best_score = -1
    best_n_clusters = 2
    scores = []
    
    for n_clusters in range(2, max_clusters + 1):
        print(f"\nTesting {n_clusters} clusters...")
        
        clusters = agglomerative_clustering(motif_ids, distance_lookup, n_clusters)
        score = calculate_silhouette_score(clusters, distance_lookup)
        
        scores.append((n_clusters, score))
        print(f"  Silhouette score: {score:.3f}")
        
        if score > best_score:
            best_score = score
            best_n_clusters = n_clusters
    
    print(f"\nOptimal number of clusters: {best_n_clusters} (score: {best_score:.3f})")
    
    return best_n_clusters, scores

def analyze_clusters(clusters, distance_lookup):
    """Analyze cluster characteristics"""
    
    print(f"\n=== Cluster Analysis ===")
    print(f"Number of clusters: {len(clusters)}")
    
    cluster_info = {}
    
    for cluster_id, cluster in enumerate(clusters):
        cluster_size = len(cluster)
        
        # Calculate intra-cluster statistics
        if cluster_size > 1:
            intra_distances = []
            for i in range(len(cluster)):
                for j in range(i + 1, len(cluster)):
                    distance = get_distance(cluster[i], cluster[j], distance_lookup)
                    intra_distances.append(distance)
            
            avg_intra = sum(intra_distances) / len(intra_distances)
            max_intra = max(intra_distances)
            min_intra = min(intra_distances)
        else:
            avg_intra = max_intra = min_intra = 0.0
        
        cluster_info[cluster_id] = {
            'size': cluster_size,
            'motifs': sorted(cluster),
            'avg_intra_distance': avg_intra,
            'max_intra_distance': max_intra,
            'min_intra_distance': min_intra
        }
        
        print(f"\nCluster {cluster_id}:")
        print(f"  Size: {cluster_size} motifs")
        if cluster_size <= 15:
            print(f"  Motifs: {sorted(cluster)}")
        else:
            print(f"  Motifs: {sorted(cluster)[:10]} ... and {cluster_size - 10} more")
        print(f"  Avg intra-cluster distance: {avg_intra:.2f}")
        if cluster_size > 1:
            print(f"  Distance range: {min_intra:.2f} - {max_intra:.2f}")
    
    return cluster_info

def compare_with_threshold_clustering(clusters, distance_lookup, threshold=50.0):
    """Compare with simple threshold-based clustering"""
    
    print(f"\n=== Comparison with Threshold Clustering (≤ {threshold}) ===")
    
    # Create threshold-based clusters using connected components
    motif_ids = []
    for cluster in clusters:
        motif_ids.extend(cluster)
    
    # Build adjacency list for threshold clustering
    adjacency = defaultdict(set)
    for i, motif1 in enumerate(motif_ids):
        for j, motif2 in enumerate(motif_ids):
            if i < j:
                distance = get_distance(motif1, motif2, distance_lookup)
                if distance <= threshold:
                    adjacency[motif1].add(motif2)
                    adjacency[motif2].add(motif1)
    
    # Find connected components
    visited = set()
    threshold_clusters = []
    
    def dfs(motif, component):
        if motif in visited:
            return
        visited.add(motif)
        component.append(motif)
        for neighbor in adjacency[motif]:
            if neighbor not in visited:
                dfs(neighbor, component)
    
    for motif in motif_ids:
        if motif not in visited:
            component = []
            dfs(motif, component)
            if len(component) > 1:
                threshold_clusters.append(component)
    
    print(f"Threshold clustering: {len(threshold_clusters)} clusters")
    print(f"Agglomerative clustering: {len(clusters)} clusters")
    
    # Show size distributions
    threshold_sizes = [len(c) for c in threshold_clusters]
    agglom_sizes = [len(c) for c in clusters]
    
    print(f"Threshold cluster sizes: {sorted(threshold_sizes, reverse=True)}")
    print(f"Agglomerative cluster sizes: {sorted(agglom_sizes, reverse=True)}")

def save_results(clusters, cluster_info, silhouette_score, scores):
    """Save clustering results"""
    
    print("\nSaving results...")
    
    # Create motif to cluster mapping
    motif_to_cluster = {}
    for cluster_id, cluster in enumerate(clusters):
        for motif in cluster:
            motif_to_cluster[str(motif)] = cluster_id
    
    results = {
        'clustering_summary': {
            'n_clusters': len(clusters),
            'n_motifs': sum(len(c) for c in clusters),
            'silhouette_score': silhouette_score,
            'algorithm': 'agglomerative_clustering',
            'linkage': 'average'
        },
        'optimization_scores': [{'n_clusters': n, 'silhouette_score': score} for n, score in scores],
        'motif_to_cluster': motif_to_cluster,
        'cluster_details': cluster_info
    }
    
    with open('data/agglomerative_clustering_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Simple cluster assignments
    cluster_assignments = {}
    for cluster_id, cluster in enumerate(clusters):
        cluster_assignments[f"cluster_{cluster_id}"] = {
            'motifs': sorted(cluster),
            'size': len(cluster)
        }
    
    with open('data/agglomerative_cluster_groups.json', 'w') as f:
        json.dump(cluster_assignments, f, indent=2)
    
    print("Results saved to:")
    print("  - data/agglomerative_clustering_results.json")
    print("  - data/agglomerative_cluster_groups.json")

def main():
    """Main function"""
    
    print("=== Agglomerative Motif Clustering Analysis ===")
    
    # Load data
    motif_ids, distance_lookup = load_distance_data()
    
    # Find optimal number of clusters
    optimal_n_clusters, scores = find_optimal_clusters(motif_ids, distance_lookup)
    
    # Perform final clustering
    print(f"\nPerforming final clustering with {optimal_n_clusters} clusters...")
    final_clusters = agglomerative_clustering(motif_ids, distance_lookup, optimal_n_clusters)
    
    # Calculate final quality
    final_score = calculate_silhouette_score(final_clusters, distance_lookup)
    
    # Analyze clusters
    cluster_info = analyze_clusters(final_clusters, distance_lookup)
    
    # Compare with threshold method
    compare_with_threshold_clustering(final_clusters, distance_lookup)
    
    # Save results
    save_results(final_clusters, cluster_info, final_score, scores)
    
    print(f"\n=== Analysis Complete ===")
    print(f"Agglomerative clustering: {len(final_clusters)} clusters")
    print(f"Final silhouette score: {final_score:.3f}")
    
    cluster_sizes = [len(c) for c in final_clusters]
    print(f"Cluster sizes: {sorted(cluster_sizes, reverse=True)}")

if __name__ == "__main__":
    main()