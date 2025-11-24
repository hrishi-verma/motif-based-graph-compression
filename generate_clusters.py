#!/usr/bin/env python3
"""
Generate 30 clusters using agglomerative clustering
"""

import json
import numpy as np
from sklearn.cluster import AgglomerativeClustering

def load_data():
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
    
    # Create node indexing
    node_index = {node: i for i, node in enumerate(motif_ids)}
    index_node = {i: node for node, i in node_index.items()}
    
    # Build distance matrix
    N = len(motif_ids)
    dist_matrix = np.full((N, N), fill_value=100.0)
    
    for pair, dist in distances.items():
        n1, n2 = map(int, pair.split("-"))
        i, j = node_index[n1], node_index[n2]
        dist_matrix[i][j] = dist
        dist_matrix[j][i] = dist
    
    np.fill_diagonal(dist_matrix, 0.0)
    
    return motif_ids, node_index, index_node, dist_matrix

def perform_clustering(dist_matrix, index_node, n_clusters=30):
    """Perform agglomerative clustering with specified number of clusters"""
    
    print(f"\nPerforming agglomerative clustering with {n_clusters} clusters...")
    
    model = AgglomerativeClustering(
        metric='precomputed',
        n_clusters=n_clusters,
        linkage='average'
    )
    
    labels = model.fit_predict(dist_matrix)
    
    print(f"Clustering complete! Generated {len(set(labels))} clusters")
    
    # Build cluster mapping
    cluster_map = {}
    for idx, label in enumerate(labels):
        motif_id = index_node[idx]
        if label not in cluster_map:
            cluster_map[label] = []
        cluster_map[label].append(motif_id)
    
    return cluster_map, labels

def analyze_clusters(cluster_map, dist_matrix, node_index):
    """Analyze cluster quality and characteristics"""
    
    print(f"\n{'='*80}")
    print(f"CLUSTER ANALYSIS - {len(cluster_map)} Clusters")
    print(f"{'='*80}")
    
    total_motifs = sum(len(motifs) for motifs in cluster_map.values())
    
    for cluster_id in sorted(cluster_map.keys()):
        motifs = cluster_map[cluster_id]
        size = len(motifs)
        percentage = (size / total_motifs) * 100
        
        # Calculate intra-cluster distances
        if size > 1:
            intra_distances = []
            for i in range(len(motifs)):
                for j in range(i + 1, len(motifs)):
                    idx_i = node_index[motifs[i]]
                    idx_j = node_index[motifs[j]]
                    intra_distances.append(dist_matrix[idx_i][idx_j])
            
            avg_intra = np.mean(intra_distances)
            std_intra = np.std(intra_distances)
            min_intra = np.min(intra_distances)
            max_intra = np.max(intra_distances)
        else:
            avg_intra = std_intra = min_intra = max_intra = 0.0
        
        print(f"\nCluster {cluster_id}:")
        print(f"  Size: {size} motifs ({percentage:.1f}%)")
        if size <= 15:
            print(f"  Motifs: {sorted(motifs)}")
        else:
            print(f"  Motifs: {sorted(motifs)[:10]} ... and {size - 10} more")
        
        if size > 1:
            print(f"  Intra-cluster distance: {avg_intra:.2f} ± {std_intra:.2f}")
            print(f"  Distance range: {min_intra:.2f} - {max_intra:.2f}")

def save_results(cluster_map, labels, index_node, n_clusters):
    """Save clustering results to JSON files"""
    
    print(f"\n{'='*80}")
    print("SAVING RESULTS")
    print(f"{'='*80}")
    
    total_motifs = sum(len(motifs) for motifs in cluster_map.values())
    
    # Format for visualization (cluster_groups format)
    cluster_groups = {}
    for cluster_id in sorted(cluster_map.keys()):
        motifs = sorted(cluster_map[cluster_id])
        size = len(motifs)
        percentage = (size / total_motifs) * 100
        
        cluster_groups[f"cluster_{cluster_id}"] = {
            "motifs": motifs,
            "size": size,
            "percentage": percentage
        }
    
    # Save cluster groups
    output_file = f'data/agglomerative_{n_clusters}_cluster_groups.json'
    with open(output_file, 'w') as f:
        json.dump(cluster_groups, f, indent=2)
    print(f"✓ Saved cluster groups to: {output_file}")
    
    # Create motif to cluster mapping
    motif_to_cluster = {}
    for idx, label in enumerate(labels):
        motif_id = index_node[idx]
        motif_to_cluster[str(motif_id)] = int(label)
    
    # Calculate cluster statistics
    cluster_sizes = [len(motifs) for motifs in cluster_map.values()]
    
    # Save detailed results
    results = {
        "clustering_summary": {
            "n_clusters": len(cluster_map),
            "n_motifs": total_motifs,
            "algorithm": "agglomerative_clustering",
            "linkage": "average",
            "metric": "precomputed_wasserstein"
        },
        "cluster_statistics": {
            "mean_size": float(np.mean(cluster_sizes)),
            "median_size": float(np.median(cluster_sizes)),
            "min_size": int(np.min(cluster_sizes)),
            "max_size": int(np.max(cluster_sizes)),
            "std_size": float(np.std(cluster_sizes))
        },
        "motif_to_cluster": motif_to_cluster,
        "cluster_sizes": {f"cluster_{i}": len(motifs) for i, motifs in cluster_map.items()}
    }
    
    results_file = f'data/agglomerative_{n_clusters}_clusters_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Saved detailed results to: {results_file}")
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total clusters: {len(cluster_map)}")
    print(f"Total motifs: {total_motifs}")
    print(f"Cluster size statistics:")
    print(f"  Mean: {np.mean(cluster_sizes):.1f}")
    print(f"  Median: {np.median(cluster_sizes):.0f}")
    print(f"  Range: {np.min(cluster_sizes)} - {np.max(cluster_sizes)}")
    print(f"  Std Dev: {np.std(cluster_sizes):.1f}")
    
    # Show size distribution
    print(f"\nCluster size distribution:")
    size_counts = {}
    for size in cluster_sizes:
        size_counts[size] = size_counts.get(size, 0) + 1
    
    for size in sorted(size_counts.keys(), reverse=True)[:10]:
        count = size_counts[size]
        print(f"  {count} cluster(s) with {size} motif(s)")

def main(n_clusters=30):
    """Main function to generate clusters"""
    
    print("="*80)
    print(f"AGGLOMERATIVE CLUSTERING - {n_clusters} CLUSTERS")
    print("="*80)
    
    # Load data
    motif_ids, node_index, index_node, dist_matrix = load_data()
    
    # Perform clustering
    cluster_map, labels = perform_clustering(dist_matrix, index_node, n_clusters=n_clusters)
    
    # Analyze clusters
    analyze_clusters(cluster_map, dist_matrix, node_index)
    
    # Save results
    save_results(cluster_map, labels, index_node, n_clusters=n_clusters)
    
    print(f"\n{'='*80}")
    print("CLUSTERING COMPLETE!")
    print(f"{'='*80}")
    print("\nYou can now visualize the results using:")
    print("  1. Update cluster_mst_visualizer.html to load the new file")
    print("  2. Run: python analyze_cluster_similarity.py (update the filename)")

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    main(n_clusters=n)
