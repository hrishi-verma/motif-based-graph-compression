#!/usr/bin/env python3
"""
Create size-aware clustering that prevents grouping motifs with very different sizes
"""

import json
import numpy as np
from sklearn.cluster import AgglomerativeClustering

def load_data():
    """Load MST data and Wasserstein distances"""
    with open('data/facebook_msts.json', 'r') as f:
        msts = json.load(f)
    
    with open('data/wasserstein_distances.json', 'r') as f:
        distances = json.load(f)
    
    return msts, distances

def create_composite_distance_matrix(msts, distances, size_weight=0.3):
    """
    Create a composite distance matrix that combines:
    1. Wasserstein distance (topological similarity)
    2. Size difference penalty (structural similarity)
    
    Args:
        msts: MST data
        distances: Wasserstein distances
        size_weight: Weight for size difference (0-1, higher = more size-aware)
    
    Returns:
        motif_ids, composite_distance_matrix
    """
    
    # Get all motif IDs
    motif_ids = sorted([int(k) for k in msts.keys()])
    n = len(motif_ids)
    
    print(f"Creating composite distance matrix for {n} motifs...")
    print(f"Size weight: {size_weight} (0=pure Wasserstein, 1=pure size-based)")
    
    # Extract sizes
    sizes = {}
    for motif_id in motif_ids:
        mst = msts[str(motif_id)]
        sizes[motif_id] = len(mst['nodes'])
    
    # Build composite distance matrix
    dist_matrix = np.zeros((n, n))
    
    for i, m1 in enumerate(motif_ids):
        for j, m2 in enumerate(motif_ids):
            if i != j:
                # Get Wasserstein distance
                key = f"{m1}-{m2}"
                wass_dist = distances.get(key, distances.get(f"{m2}-{m1}", 100.0))
                
                # Calculate size difference penalty
                # Normalize by average size to make it comparable to Wasserstein distance
                size_diff = abs(sizes[m1] - sizes[m2])
                avg_size = (sizes[m1] + sizes[m2]) / 2
                size_penalty = (size_diff / max(1, avg_size)) * 100  # Scale to ~0-100 range
                
                # Composite distance
                composite = (1 - size_weight) * wass_dist + size_weight * size_penalty
                dist_matrix[i][j] = composite
    
    return motif_ids, dist_matrix

def perform_size_aware_clustering(motif_ids, dist_matrix, n_clusters=60):
    """Perform agglomerative clustering with composite distance"""
    
    print(f"\nPerforming size-aware clustering with {n_clusters} clusters...")
    
    model = AgglomerativeClustering(
        metric='precomputed',
        n_clusters=n_clusters,
        linkage='average'
    )
    
    labels = model.fit_predict(dist_matrix)
    
    # Build cluster mapping
    cluster_map = {}
    for idx, label in enumerate(labels):
        motif_id = motif_ids[idx]
        if label not in cluster_map:
            cluster_map[label] = []
        cluster_map[label].append(motif_id)
    
    return cluster_map, labels

def analyze_size_aware_clusters(cluster_map, msts):
    """Analyze the size-aware clustering results"""
    
    print(f"\n{'='*80}")
    print(f"SIZE-AWARE CLUSTERING ANALYSIS")
    print(f"{'='*80}")
    
    for cluster_id in sorted(cluster_map.keys())[:10]:  # Show first 10
        motifs = cluster_map[cluster_id]
        sizes = [len(msts[str(m)]['nodes']) for m in motifs]
        weights = [msts[str(m)]['total_weight'] for m in motifs]
        
        print(f"\nCluster {cluster_id}: {len(motifs)} motifs")
        print(f"  Size range: {min(sizes)} - {max(sizes)} nodes (mean: {np.mean(sizes):.1f}, std: {np.std(sizes):.1f})")
        print(f"  Weight range: {min(weights):.1f} - {max(weights):.1f} (mean: {np.mean(weights):.1f})")
        print(f"  Size CV: {np.std(sizes)/np.mean(sizes):.3f}")
        
        if len(motifs) <= 15:
            print(f"  Motifs: {sorted(motifs)}")

def save_size_aware_clusters(cluster_map, msts, output_file='data/agglomerative_size_aware_cluster_groups.json'):
    """Save size-aware clusters to file"""
    
    cluster_groups = {}
    total_motifs = sum(len(motifs) for motifs in cluster_map.values())
    
    for cluster_id in sorted(cluster_map.keys()):
        motifs = sorted(cluster_map[cluster_id])
        size = len(motifs)
        percentage = (size / total_motifs) * 100
        
        cluster_groups[f"cluster_{cluster_id}"] = {
            "motifs": motifs,
            "size": size,
            "percentage": percentage
        }
    
    with open(output_file, 'w') as f:
        json.dump(cluster_groups, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"SIZE-AWARE CLUSTERING SAVED")
    print(f"{'='*80}")
    print(f"Output file: {output_file}")
    print(f"Total clusters: {len(cluster_groups)}")
    
    # Statistics
    sizes = [len(motifs) for motifs in cluster_map.values()]
    print(f"\nCluster size statistics:")
    print(f"  Mean: {np.mean(sizes):.1f}")
    print(f"  Median: {np.median(sizes):.0f}")
    print(f"  Range: {min(sizes)} - {max(sizes)}")
    print(f"  Largest cluster: {max(sizes)} motifs ({max(sizes)/total_motifs*100:.1f}%)")

def main():
    """Main function"""
    
    print("="*80)
    print("SIZE-AWARE CLUSTERING")
    print("="*80)
    print("\nThis approach combines:")
    print("  • Wasserstein distance (topological similarity)")
    print("  • Size difference penalty (prevents grouping very different sizes)")
    print()
    
    # Load data
    msts, distances = load_data()
    
    # Create composite distance matrix
    motif_ids, dist_matrix = create_composite_distance_matrix(msts, distances, size_weight=0.3)
    
    # Perform clustering
    cluster_map, labels = perform_size_aware_clustering(motif_ids, dist_matrix, n_clusters=60)
    
    # Analyze results
    analyze_size_aware_clusters(cluster_map, msts)
    
    # Check motifs 35 and 36
    print(f"\n{'='*80}")
    print("CHECKING MOTIFS 35 AND 36:")
    print(f"{'='*80}")
    
    for cluster_id, motifs in cluster_map.items():
        if 35 in motifs:
            print(f"Motif 35 (2 nodes, weight 1.0) is in cluster {cluster_id} with {len(motifs)} motifs")
            sizes = [len(msts[str(m)]['nodes']) for m in motifs]
            print(f"  Cluster size range: {min(sizes)} - {max(sizes)} nodes")
        if 36 in motifs:
            print(f"Motif 36 (11 nodes, weight 127.0) is in cluster {cluster_id} with {len(motifs)} motifs")
            sizes = [len(msts[str(m)]['nodes']) for m in motifs]
            print(f"  Cluster size range: {min(sizes)} - {max(sizes)} nodes")
    
    # Save results
    save_size_aware_clusters(cluster_map, msts)
    
    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print(f"{'='*80}")
    print("1. Update cluster_mst_visualizer.html to load:")
    print("   'data/agglomerative_size_aware_cluster_groups.json'")
    print("2. Refresh your browser to see the size-aware clusters")

if __name__ == "__main__":
    main()
