#!/usr/bin/env python3
"""
Explore different clustering configurations
"""

import json

def load_distance_data():
    """Load Wasserstein distances"""
    with open('data/wasserstein_distances.json', 'r') as f:
        distances = json.load(f)
    
    motif_ids = set()
    for key in distances.keys():
        motif1, motif2 = key.split('-')
        motif_ids.add(int(motif1))
        motif_ids.add(int(motif2))
    
    motif_ids = sorted(list(motif_ids))
    
    distance_lookup = {}
    for key, distance in distances.items():
        motif1, motif2 = map(int, key.split('-'))
        distance_lookup[(motif1, motif2)] = distance
        distance_lookup[(motif2, motif1)] = distance
    
    for motif in motif_ids:
        distance_lookup[(motif, motif)] = 0.0
    
    return motif_ids, distance_lookup

def analyze_motif_348(motif_ids, distance_lookup):
    """Analyze why motif 348 is an outlier"""
    
    print("=== Analysis of Motif 348 (Outlier) ===")
    
    # Get distances from motif 348 to all others
    distances_from_348 = []
    for motif in motif_ids:
        if motif != 348:
            distance = distance_lookup.get((348, motif), float('inf'))
            distances_from_348.append((motif, distance))
    
    # Sort by distance
    distances_from_348.sort(key=lambda x: x[1])
    
    print(f"Closest motifs to 348:")
    for i, (motif, distance) in enumerate(distances_from_348[:10]):
        print(f"  {i+1}. Motif {motif}: {distance:.1f}")
    
    print(f"\nFarthest motifs from 348:")
    for i, (motif, distance) in enumerate(distances_from_348[-10:]):
        print(f"  {i+1}. Motif {motif}: {distance:.1f}")
    
    # Statistics
    distances_only = [d for _, d in distances_from_348]
    avg_distance = sum(distances_only) / len(distances_only)
    min_distance = min(distances_only)
    max_distance = max(distances_only)
    
    print(f"\nMotif 348 distance statistics:")
    print(f"  Average distance to other motifs: {avg_distance:.1f}")
    print(f"  Minimum distance: {min_distance:.1f}")
    print(f"  Maximum distance: {max_distance:.1f}")
    
    return min_distance

def force_more_clusters(motif_ids, distance_lookup, n_clusters=10):
    """Force clustering into more clusters to see structure"""
    
    print(f"\n=== Forcing {n_clusters} Clusters ===")
    
    # Simple agglomerative clustering
    clusters = [[motif] for motif in motif_ids]
    
    while len(clusters) > n_clusters:
        min_distance = float('inf')
        merge_i, merge_j = -1, -1
        
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                # Calculate average distance between clusters
                total_distance = 0
                count = 0
                for m1 in clusters[i]:
                    for m2 in clusters[j]:
                        total_distance += distance_lookup.get((m1, m2), float('inf'))
                        count += 1
                avg_distance = total_distance / count if count > 0 else float('inf')
                
                if avg_distance < min_distance:
                    min_distance = avg_distance
                    merge_i, merge_j = i, j
        
        if merge_i != -1 and merge_j != -1:
            clusters[merge_i].extend(clusters[merge_j])
            clusters.pop(merge_j)
    
    # Analyze the clusters
    print(f"Forced clustering into {len(clusters)} clusters:")
    
    cluster_info = []
    for i, cluster in enumerate(clusters):
        cluster_size = len(cluster)
        
        # Calculate intra-cluster distance
        if cluster_size > 1:
            intra_distances = []
            for j in range(len(cluster)):
                for k in range(j + 1, len(cluster)):
                    distance = distance_lookup.get((cluster[j], cluster[k]), float('inf'))
                    intra_distances.append(distance)
            avg_intra = sum(intra_distances) / len(intra_distances)
        else:
            avg_intra = 0.0
        
        cluster_info.append({
            'id': i,
            'size': cluster_size,
            'motifs': sorted(cluster),
            'avg_intra_distance': avg_intra
        })
        
        print(f"\nCluster {i}:")
        print(f"  Size: {cluster_size}")
        if cluster_size <= 10:
            print(f"  Motifs: {sorted(cluster)}")
        else:
            print(f"  Motifs: {sorted(cluster)[:5]} ... {sorted(cluster)[-5:]}")
        print(f"  Avg intra-distance: {avg_intra:.1f}")
    
    return cluster_info

def compare_clustering_methods():
    """Compare different clustering approaches"""
    
    print("=== Clustering Method Comparison ===")
    
    motif_ids, distance_lookup = load_distance_data()
    
    # Analyze the outlier
    min_dist_348 = analyze_motif_348(motif_ids, distance_lookup)
    
    # Try different numbers of forced clusters
    for n_clusters in [5, 10, 15, 20]:
        print(f"\n" + "="*50)
        cluster_info = force_more_clusters(motif_ids, distance_lookup, n_clusters)
        
        # Find which cluster contains motif 348
        for cluster in cluster_info:
            if 348 in cluster['motifs']:
                print(f"Motif 348 is in cluster {cluster['id']} with {cluster['size']} motifs")
                break
    
    # Suggest better threshold
    print(f"\n=== Recommendations ===")
    print(f"Motif 348 minimum distance to others: {min_dist_348:.1f}")
    print(f"This suggests motif 348 is a true outlier")
    print(f"For meaningful clustering, consider:")
    print(f"  1. Remove motif 348 as an outlier")
    print(f"  2. Use threshold clustering with threshold around {min_dist_348/2:.0f}")
    print(f"  3. Force agglomerative clustering to 10-20 clusters")

if __name__ == "__main__":
    compare_clustering_methods()