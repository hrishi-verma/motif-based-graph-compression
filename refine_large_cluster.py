#!/usr/bin/env python3
"""
Post-process large heterogeneous clusters by splitting them into homogeneous subclusters
"""

import json
import numpy as np
from sklearn.cluster import AgglomerativeClustering

def load_data():
    """Load cluster data, MST data, and distances"""
    with open('data/agglomerative_50_cluster_groups.json', 'r') as f:
        clusters = json.load(f)
    
    with open('data/facebook_msts.json', 'r') as f:
        msts = json.load(f)
    
    with open('data/wasserstein_distances.json', 'r') as f:
        distances = json.load(f)
    
    return clusters, msts, distances

def split_heterogeneous_cluster(cluster_motifs, msts, distances, max_cv=0.5):
    """
    Split a heterogeneous cluster into more homogeneous subclusters
    
    Args:
        cluster_motifs: List of motif IDs in the cluster
        msts: MST data
        distances: Wasserstein distances
        max_cv: Maximum coefficient of variation allowed
    
    Returns:
        List of subclusters
    """
    
    # Calculate structural features
    features = []
    valid_motifs = []
    
    for motif_id in cluster_motifs:
        mst = msts.get(str(motif_id))
        if mst:
            node_count = len(mst['nodes'])
            edge_count = mst['num_mst_edges']
            total_weight = mst['total_weight']
            avg_weight = total_weight / max(1, edge_count)
            
            features.append([node_count, edge_count, total_weight, avg_weight])
            valid_motifs.append(motif_id)
    
    features = np.array(features)
    
    # Calculate coefficient of variation for total weight
    cv = np.std(features[:, 2]) / np.mean(features[:, 2]) if np.mean(features[:, 2]) > 0 else 0
    
    print(f"  Cluster CV: {cv:.3f}")
    
    if cv <= max_cv or len(valid_motifs) < 10:
        # Cluster is already homogeneous or too small to split
        return [valid_motifs]
    
    # Build distance matrix for this subset
    n = len(valid_motifs)
    dist_matrix = np.zeros((n, n))
    
    for i, m1 in enumerate(valid_motifs):
        for j, m2 in enumerate(valid_motifs):
            if i != j:
                key = f"{m1}-{m2}"
                dist = distances.get(key, distances.get(f"{m2}-{m1}", 100.0))
                dist_matrix[i][j] = dist
    
    # Determine optimal number of subclusters
    # Use size-based heuristic: aim for ~20-30 motifs per subcluster
    n_subclusters = max(2, min(10, len(valid_motifs) // 25))
    
    print(f"  Splitting into {n_subclusters} subclusters...")
    
    # Perform agglomerative clustering on the subset
    model = AgglomerativeClustering(
        metric='precomputed',
        n_clusters=n_subclusters,
        linkage='average'
    )
    
    labels = model.fit_predict(dist_matrix)
    
    # Group motifs by subcluster
    subclusters = {}
    for idx, label in enumerate(labels):
        if label not in subclusters:
            subclusters[label] = []
        subclusters[label].append(valid_motifs[idx])
    
    result = list(subclusters.values())
    
    print(f"  Created {len(result)} subclusters with sizes: {[len(sc) for sc in result]}")
    
    return result

def refine_clustering(clusters, msts, distances, heterogeneity_threshold=0.5):
    """
    Refine clustering by splitting heterogeneous clusters
    
    Args:
        clusters: Original cluster assignments
        msts: MST data
        distances: Wasserstein distances
        heterogeneity_threshold: CV threshold above which to split clusters
    
    Returns:
        Refined cluster assignments
    """
    
    print("="*80)
    print("REFINING CLUSTERING BY SPLITTING HETEROGENEOUS CLUSTERS")
    print("="*80)
    
    refined_clusters = {}
    cluster_counter = 0
    
    for cluster_key in sorted(clusters.keys(), key=lambda x: int(x.split('_')[1])):
        cluster = clusters[cluster_key]
        motif_ids = cluster['motifs']
        size = cluster['size']
        
        print(f"\nProcessing {cluster_key} ({size} motifs)...")
        
        # Calculate coefficient of variation
        if size > 1:
            weights = []
            for motif_id in motif_ids:
                mst = msts.get(str(motif_id))
                if mst:
                    weights.append(mst['total_weight'])
            
            if weights:
                cv = np.std(weights) / np.mean(weights) if np.mean(weights) > 0 else 0
            else:
                cv = 0
        else:
            cv = 0
        
        # Decide whether to split
        if cv > heterogeneity_threshold and size >= 20:
            print(f"  → Heterogeneous (CV={cv:.3f}), splitting...")
            subclusters = split_heterogeneous_cluster(motif_ids, msts, distances, max_cv=heterogeneity_threshold)
            
            for subcluster in subclusters:
                refined_clusters[f"cluster_{cluster_counter}"] = {
                    "motifs": sorted(subcluster),
                    "size": len(subcluster),
                    "percentage": (len(subcluster) / 486) * 100,
                    "parent_cluster": cluster_key
                }
                cluster_counter += 1
        else:
            print(f"  → Homogeneous (CV={cv:.3f}), keeping as-is")
            refined_clusters[f"cluster_{cluster_counter}"] = {
                "motifs": sorted(motif_ids),
                "size": size,
                "percentage": cluster['percentage'],
                "parent_cluster": cluster_key
            }
            cluster_counter += 1
    
    return refined_clusters

def save_refined_clusters(refined_clusters, output_file='data/agglomerative_refined_cluster_groups.json'):
    """Save refined clusters to file"""
    
    with open(output_file, 'w') as f:
        json.dump(refined_clusters, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"REFINED CLUSTERING SAVED")
    print(f"{'='*80}")
    print(f"Output file: {output_file}")
    print(f"Total clusters: {len(refined_clusters)}")
    
    # Statistics
    sizes = [c['size'] for c in refined_clusters.values()]
    print(f"\nCluster size statistics:")
    print(f"  Mean: {np.mean(sizes):.1f}")
    print(f"  Median: {np.median(sizes):.0f}")
    print(f"  Range: {min(sizes)} - {max(sizes)}")
    print(f"  Std Dev: {np.std(sizes):.1f}")
    
    print(f"\nSize distribution:")
    print(f"  Singletons: {sum(1 for s in sizes if s == 1)}")
    print(f"  Small (2-10): {sum(1 for s in sizes if 2 <= s <= 10)}")
    print(f"  Medium (11-30): {sum(1 for s in sizes if 11 <= s <= 30)}")
    print(f"  Large (>30): {sum(1 for s in sizes if s > 30)}")

def main():
    """Main refinement function"""
    
    print("Loading data...")
    clusters, msts, distances = load_data()
    
    # Refine clustering
    refined_clusters = refine_clustering(clusters, msts, distances, heterogeneity_threshold=0.5)
    
    # Save results
    save_refined_clusters(refined_clusters)
    
    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print(f"{'='*80}")
    print("1. Update cluster_mst_visualizer.html to load:")
    print("   'data/agglomerative_refined_cluster_groups.json'")
    print("2. Refresh your browser to see the refined clusters")
    print("3. Motifs 35 and 36 should now be in different clusters!")

if __name__ == "__main__":
    main()
