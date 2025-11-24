#!/usr/bin/env python3
"""
Analyze the large heterogeneous cluster to understand why diverse motifs are grouped together
"""

import json
import numpy as np

def load_data():
    """Load cluster data, MST data, and Wasserstein distances"""
    with open('data/agglomerative_50_cluster_groups.json', 'r') as f:
        clusters = json.load(f)
    
    with open('data/facebook_msts.json', 'r') as f:
        msts = json.load(f)
    
    with open('data/wasserstein_distances.json', 'r') as f:
        distances = json.load(f)
    
    return clusters, msts, distances

def analyze_specific_motifs(motif_ids, msts, distances):
    """Analyze specific motifs in detail"""
    
    print("="*80)
    print(f"DETAILED ANALYSIS: Motifs {motif_ids}")
    print("="*80)
    
    for motif_id in motif_ids:
        mst = msts.get(str(motif_id))
        if mst:
            print(f"\nMotif {motif_id}:")
            print(f"  Nodes: {len(mst['nodes'])}")
            print(f"  Edges: {mst['num_mst_edges']}")
            print(f"  Total Weight: {mst['total_weight']:.1f}")
            print(f"  Avg Edge Weight: {mst['total_weight']/max(1, mst['num_mst_edges']):.2f}")
    
    # Calculate pairwise distances
    print(f"\n{'='*80}")
    print("PAIRWISE WASSERSTEIN DISTANCES:")
    print(f"{'='*80}")
    
    for i, m1 in enumerate(motif_ids):
        for j, m2 in enumerate(motif_ids):
            if i < j:
                key = f"{m1}-{m2}"
                dist = distances.get(key, distances.get(f"{m2}-{m1}", "N/A"))
                print(f"  Motif {m1} ↔ Motif {m2}: {dist}")

def analyze_large_cluster(cluster_id, clusters, msts, distances):
    """Analyze why a large cluster contains diverse motifs"""
    
    cluster_key = f"cluster_{cluster_id}"
    cluster = clusters[cluster_key]
    motif_ids = cluster['motifs']
    
    print("="*80)
    print(f"ANALYZING CLUSTER {cluster_id}")
    print("="*80)
    print(f"Size: {cluster['size']} motifs ({cluster['percentage']:.1f}%)")
    
    # Calculate structural diversity
    node_counts = []
    edge_counts = []
    total_weights = []
    avg_weights = []
    
    for motif_id in motif_ids:
        mst = msts.get(str(motif_id))
        if mst:
            node_counts.append(len(mst['nodes']))
            edge_counts.append(mst['num_mst_edges'])
            total_weights.append(mst['total_weight'])
            avg_weights.append(mst['total_weight'] / max(1, mst['num_mst_edges']))
    
    print(f"\nStructural Diversity:")
    print(f"  Node count: {min(node_counts)} - {max(node_counts)} (mean: {np.mean(node_counts):.1f}, std: {np.std(node_counts):.1f})")
    print(f"  Edge count: {min(edge_counts)} - {max(edge_counts)} (mean: {np.mean(edge_counts):.1f}, std: {np.std(edge_counts):.1f})")
    print(f"  Total weight: {min(total_weights):.1f} - {max(total_weights):.1f} (mean: {np.mean(total_weights):.1f}, std: {np.std(total_weights):.1f})")
    print(f"  Avg edge weight: {min(avg_weights):.2f} - {max(avg_weights):.2f} (mean: {np.mean(avg_weights):.2f}, std: {np.std(avg_weights):.2f})")
    
    # Calculate intra-cluster distances
    print(f"\nCalculating intra-cluster Wasserstein distances...")
    intra_distances = []
    
    for i, m1 in enumerate(motif_ids[:100]):  # Sample first 100 for speed
        for j, m2 in enumerate(motif_ids[:100]):
            if i < j:
                key = f"{m1}-{m2}"
                dist = distances.get(key, distances.get(f"{m2}-{m1}", None))
                if dist is not None:
                    intra_distances.append(dist)
    
    if intra_distances:
        print(f"  Intra-cluster distance: {np.mean(intra_distances):.2f} ± {np.std(intra_distances):.2f}")
        print(f"  Distance range: {min(intra_distances):.2f} - {max(intra_distances):.2f}")
        print(f"  Median distance: {np.median(intra_distances):.2f}")
    
    # Find subclusters within this large cluster
    print(f"\n{'='*80}")
    print("IDENTIFYING SUBCLUSTERS:")
    print(f"{'='*80}")
    
    # Group by size
    size_groups = {}
    for motif_id in motif_ids:
        mst = msts.get(str(motif_id))
        if mst:
            size = len(mst['nodes'])
            size_bin = (size // 5) * 5  # Group into bins of 5
            if size_bin not in size_groups:
                size_groups[size_bin] = []
            size_groups[size_bin].append(motif_id)
    
    print("\nMotifs grouped by size (bins of 5 nodes):")
    for size_bin in sorted(size_groups.keys()):
        count = len(size_groups[size_bin])
        print(f"  {size_bin}-{size_bin+4} nodes: {count} motifs")
        if count <= 10:
            print(f"    Motifs: {size_groups[size_bin]}")
    
    # Find extreme examples
    print(f"\n{'='*80}")
    print("EXTREME EXAMPLES:")
    print(f"{'='*80}")
    
    # Smallest motifs
    smallest_indices = np.argsort(node_counts)[:5]
    print("\n5 Smallest motifs in cluster:")
    for idx in smallest_indices:
        motif_id = motif_ids[idx]
        mst = msts.get(str(motif_id))
        print(f"  Motif {motif_id}: {node_counts[idx]} nodes, {edge_counts[idx]} edges, weight {total_weights[idx]:.1f}")
    
    # Largest motifs
    largest_indices = np.argsort(node_counts)[-5:]
    print("\n5 Largest motifs in cluster:")
    for idx in reversed(largest_indices):
        motif_id = motif_ids[idx]
        mst = msts.get(str(motif_id))
        print(f"  Motif {motif_id}: {node_counts[idx]} nodes, {edge_counts[idx]} edges, weight {total_weights[idx]:.1f}")
    
    return size_groups

def explain_clustering_behavior():
    """Explain why diverse motifs end up in the same cluster"""
    
    print("\n" + "="*80)
    print("WHY ARE DIVERSE MOTIFS IN THE SAME CLUSTER?")
    print("="*80)
    
    print("""
The large cluster (Cluster 40 with 277 motifs) is a "catch-all" cluster that forms
because of how agglomerative clustering works:

1. RELATIVE vs ABSOLUTE SIMILARITY:
   • Clustering groups motifs that are MORE SIMILAR TO EACH OTHER than to other groups
   • This doesn't mean they are ABSOLUTELY similar
   • Motifs 35 and 36 may be different, but they're both "small/simple" compared to
     the highly structured motifs in other clusters

2. HIERARCHICAL MERGING:
   • Agglomerative clustering starts with each motif as its own cluster
   • It repeatedly merges the CLOSEST pair of clusters
   • Small, simple motifs (like 35 and 36) get merged early because they have
     relatively low distances to each other
   • This creates a "snowball effect" where the cluster keeps growing

3. WASSERSTEIN DISTANCE CHARACTERISTICS:
   • Wasserstein distance measures topological similarity (persistence diagrams)
   • Small motifs with few features have simpler persistence diagrams
   • They may have low distances to each other even if structurally different
   • The distance captures "topological complexity" not "size"

4. THE "DEFAULT" CLUSTER PROBLEM:
   • This cluster contains motifs that don't fit well into specialized groups
   • They're the "everything else" category
   • Common in real-world clustering when there's a dominant pattern

SOLUTIONS:
-----------
1. INCREASE CLUSTER COUNT (already tried - 15→30→50)
   • Helps but doesn't fully solve the problem
   • The large cluster persists (295→295→277 motifs)

2. USE DISTANCE THRESHOLD instead of fixed cluster count
   • Set a maximum distance threshold
   • Only merge clusters if distance < threshold
   • This prevents merging dissimilar motifs

3. ADD SIZE CONSTRAINTS to clustering
   • Penalize merging motifs with very different sizes
   • Use a composite distance: Wasserstein + size_difference

4. POST-PROCESS: Split large heterogeneous clusters
   • After initial clustering, identify large clusters with high variance
   • Re-cluster them separately with stricter criteria

5. USE DIFFERENT FEATURES:
   • Current: Wasserstein distance on persistence diagrams
   • Alternative: Include node count, edge count, degree distribution
   • Multi-objective clustering

Let me implement option 4 (post-processing) to split Cluster 40...
""")

def main():
    """Main analysis function"""
    
    print("Loading data...")
    clusters, msts, distances = load_data()
    
    # Analyze motifs 35 and 36 specifically
    analyze_specific_motifs([35, 36], msts, distances)
    
    # Analyze the large cluster
    size_groups = analyze_large_cluster(40, clusters, msts, distances)
    
    # Explain the behavior
    explain_clustering_behavior()
    
    print("\n" + "="*80)
    print("RECOMMENDATION:")
    print("="*80)
    print("""
For your use case, I recommend:

1. Use the 50-cluster solution as a baseline
2. Post-process Cluster 40 by splitting it into size-based subclusters
3. This will give you ~60-70 final clusters with better homogeneity

Would you like me to implement this post-processing step?
""")

if __name__ == "__main__":
    main()
