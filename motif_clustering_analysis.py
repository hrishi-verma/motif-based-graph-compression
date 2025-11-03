#!/usr/bin/env python3
"""
Motif Clustering Analysis using Wasserstein Distances
Performs agglomerative clustering on motifs based on their topological similarity
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
import pandas as pd

def load_wasserstein_data():
    """Load Wasserstein distance data and convert to distance matrix"""
    
    print("Loading Wasserstein distance data...")
    with open('data/wasserstein_distances.json', 'r') as f:
        distances = json.load(f)
    
    print(f"Loaded {len(distances)} distance pairs")
    
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
    
    for i, motif1 in enumerate(motif_ids):
        for j, motif2 in enumerate(motif_ids):
            if i == j:
                distance_matrix[i, j] = 0.0
            else:
                key = f"{motif1}-{motif2}"
                if key in distances:
                    distance_matrix[i, j] = distances[key]
                else:
                    # Try reverse key
                    key_rev = f"{motif2}-{motif1}"
                    distance_matrix[i, j] = distances[key_rev]
    
    return distance_matrix, motif_ids

def find_optimal_clusters(distance_matrix, max_clusters=20):
    """Find optimal number of clusters using multiple metrics"""
    
    print("Finding optimal number of clusters...")
    
    n_samples = distance_matrix.shape[0]
    max_clusters = min(max_clusters, n_samples - 1)
    
    cluster_range = range(2, max_clusters + 1)
    silhouette_scores = []
    calinski_scores = []
    
    for n_clusters in cluster_range:
        print(f"  Testing {n_clusters} clusters...")
        
        # Perform clustering
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric='precomputed',
            linkage='average'
        )
        
        cluster_labels = clustering.fit_predict(distance_matrix)
        
        # Calculate metrics
        sil_score = silhouette_score(distance_matrix, cluster_labels, metric='precomputed')
        cal_score = calinski_harabasz_score(distance_matrix, cluster_labels)
        
        silhouette_scores.append(sil_score)
        calinski_scores.append(cal_score)
    
    return cluster_range, silhouette_scores, calinski_scores

def perform_clustering(distance_matrix, motif_ids, n_clusters=None):
    """Perform agglomerative clustering with specified number of clusters"""
    
    if n_clusters is None:
        # Find optimal number automatically
        cluster_range, sil_scores, cal_scores = find_optimal_clusters(distance_matrix)
        
        # Choose based on silhouette score
        optimal_idx = np.argmax(sil_scores)
        n_clusters = cluster_range[optimal_idx]
        
        print(f"Optimal number of clusters: {n_clusters} (silhouette score: {sil_scores[optimal_idx]:.3f})")
    
    print(f"Performing clustering with {n_clusters} clusters...")
    
    # Perform final clustering
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        metric='precomputed',
        linkage='average'
    )
    
    cluster_labels = clustering.fit_predict(distance_matrix)
    
    # Calculate final metrics
    sil_score = silhouette_score(distance_matrix, cluster_labels, metric='precomputed')
    
    print(f"Final silhouette score: {sil_score:.3f}")
    
    return cluster_labels, sil_score

def analyze_clusters(cluster_labels, motif_ids, distance_matrix):
    """Analyze the resulting clusters"""
    
    n_clusters = len(np.unique(cluster_labels))
    
    print(f"\n=== Cluster Analysis ===")
    print(f"Number of clusters: {n_clusters}")
    
    cluster_info = []
    
    for cluster_id in range(n_clusters):
        cluster_motifs = [motif_ids[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
        cluster_size = len(cluster_motifs)
        
        # Calculate intra-cluster distances
        cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
        
        if cluster_size > 1:
            intra_distances = []
            for i in range(len(cluster_indices)):
                for j in range(i + 1, len(cluster_indices)):
                    idx1, idx2 = cluster_indices[i], cluster_indices[j]
                    intra_distances.append(distance_matrix[idx1, idx2])
            
            avg_intra_distance = np.mean(intra_distances)
            max_intra_distance = np.max(intra_distances)
        else:
            avg_intra_distance = 0.0
            max_intra_distance = 0.0
        
        cluster_info.append({
            'cluster_id': cluster_id,
            'size': cluster_size,
            'motifs': cluster_motifs,
            'avg_intra_distance': avg_intra_distance,
            'max_intra_distance': max_intra_distance
        })
        
        print(f"\nCluster {cluster_id}:")
        print(f"  Size: {cluster_size} motifs")
        print(f"  Motifs: {cluster_motifs[:10]}{'...' if cluster_size > 10 else ''}")
        print(f"  Avg intra-cluster distance: {avg_intra_distance:.2f}")
        print(f"  Max intra-cluster distance: {max_intra_distance:.2f}")
    
    return cluster_info

def create_visualizations(distance_matrix, motif_ids, cluster_labels):
    """Create visualizations of the clustering results"""
    
    print("\nCreating visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Dendrogram
    plt.subplot(2, 3, 1)
    
    # Convert distance matrix to condensed form for linkage
    condensed_distances = squareform(distance_matrix)
    linkage_matrix = linkage(condensed_distances, method='average')
    
    dendrogram(linkage_matrix, truncate_mode='level', p=10)
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('Motif Index')
    plt.ylabel('Distance')
    
    # 2. Distance Matrix Heatmap (sample for large matrices)
    plt.subplot(2, 3, 2)
    
    # Sample the matrix if it's too large
    n_motifs = len(motif_ids)
    if n_motifs > 100:
        # Sample 100 motifs for visualization
        sample_indices = np.random.choice(n_motifs, 100, replace=False)
        sample_matrix = distance_matrix[np.ix_(sample_indices, sample_indices)]
        sample_motifs = [motif_ids[i] for i in sample_indices]
    else:
        sample_matrix = distance_matrix
        sample_motifs = motif_ids
    
    sns.heatmap(sample_matrix, cmap='viridis', cbar=True)
    plt.title('Wasserstein Distance Matrix (Sample)')
    plt.xlabel('Motif Index')
    plt.ylabel('Motif Index')
    
    # 3. Cluster Size Distribution
    plt.subplot(2, 3, 3)
    
    unique_labels, counts = np.unique(cluster_labels, return_counts=True)
    plt.bar(unique_labels, counts, alpha=0.7)
    plt.title('Cluster Size Distribution')
    plt.xlabel('Cluster ID')
    plt.ylabel('Number of Motifs')
    
    # 4. Silhouette Analysis
    plt.subplot(2, 3, 4)
    
    from sklearn.metrics import silhouette_samples
    silhouette_vals = silhouette_samples(distance_matrix, cluster_labels, metric='precomputed')
    
    y_lower = 10
    for i in range(len(np.unique(cluster_labels))):
        cluster_silhouette_vals = silhouette_vals[cluster_labels == i]
        cluster_silhouette_vals.sort()
        
        size_cluster_i = cluster_silhouette_vals.shape[0]
        y_upper = y_lower + size_cluster_i
        
        color = plt.cm.nipy_spectral(float(i) / len(np.unique(cluster_labels)))
        plt.fill_betweenx(np.arange(y_lower, y_upper), 0, cluster_silhouette_vals,
                         facecolor=color, edgecolor=color, alpha=0.7)
        
        y_lower = y_upper + 10
    
    plt.axvline(x=silhouette_score(distance_matrix, cluster_labels, metric='precomputed'), 
                color="red", linestyle="--", label='Average Score')
    plt.title('Silhouette Analysis')
    plt.xlabel('Silhouette Coefficient Values')
    plt.ylabel('Cluster Label')
    plt.legend()
    
    # 5. Distance Distribution by Cluster
    plt.subplot(2, 3, 5)
    
    cluster_distances = []
    cluster_ids = []
    
    for cluster_id in np.unique(cluster_labels):
        cluster_indices = np.where(cluster_labels == cluster_id)[0]
        
        if len(cluster_indices) > 1:
            for i in range(len(cluster_indices)):
                for j in range(i + 1, len(cluster_indices)):
                    idx1, idx2 = cluster_indices[i], cluster_indices[j]
                    cluster_distances.append(distance_matrix[idx1, idx2])
                    cluster_ids.append(cluster_id)
    
    if cluster_distances:
        df = pd.DataFrame({'Distance': cluster_distances, 'Cluster': cluster_ids})
        sns.boxplot(data=df, x='Cluster', y='Distance')
        plt.title('Intra-cluster Distance Distribution')
        plt.xticks(rotation=45)
    
    # 6. Cluster Scatter Plot (using MDS for 2D projection)
    plt.subplot(2, 3, 6)
    
    from sklearn.manifold import MDS
    
    # Use MDS to project to 2D
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    coords_2d = mds.fit_transform(distance_matrix)
    
    scatter = plt.scatter(coords_2d[:, 0], coords_2d[:, 1], c=cluster_labels, 
                         cmap='tab10', alpha=0.7, s=50)
    plt.colorbar(scatter)
    plt.title('Motif Clusters (MDS Projection)')
    plt.xlabel('MDS Dimension 1')
    plt.ylabel('MDS Dimension 2')
    
    plt.tight_layout()
    plt.savefig('motif_clustering_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Visualizations saved as 'motif_clustering_analysis.png'")

def save_clustering_results(cluster_labels, motif_ids, cluster_info, distance_matrix):
    """Save clustering results to JSON files"""
    
    print("\nSaving clustering results...")
    
    # Prepare results dictionary
    results = {
        'clustering_info': {
            'n_clusters': len(np.unique(cluster_labels)),
            'n_motifs': len(motif_ids),
            'silhouette_score': float(silhouette_score(distance_matrix, cluster_labels, metric='precomputed'))
        },
        'motif_assignments': {
            str(motif_ids[i]): int(cluster_labels[i]) 
            for i in range(len(motif_ids))
        },
        'cluster_details': cluster_info
    }
    
    # Save main results
    with open('data/motif_clusters.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save cluster assignments in a simple format
    cluster_assignments = {}
    for cluster_id in np.unique(cluster_labels):
        cluster_motifs = [motif_ids[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
        cluster_assignments[f"cluster_{cluster_id}"] = cluster_motifs
    
    with open('data/motif_cluster_assignments.json', 'w') as f:
        json.dump(cluster_assignments, f, indent=2)
    
    print("Results saved to:")
    print("  - data/motif_clusters.json (detailed results)")
    print("  - data/motif_cluster_assignments.json (simple assignments)")

def main():
    """Main clustering analysis function"""
    
    print("=== Motif Clustering Analysis ===")
    print("Using Wasserstein distances for agglomerative clustering\n")
    
    # Load data
    distance_matrix, motif_ids = load_wasserstein_data()
    
    # Find optimal clusters and perform clustering
    cluster_labels, silhouette_score_final = perform_clustering(distance_matrix, motif_ids)
    
    # Analyze results
    cluster_info = analyze_clusters(cluster_labels, motif_ids, distance_matrix)
    
    # Create visualizations
    create_visualizations(distance_matrix, motif_ids, cluster_labels)
    
    # Save results
    save_clustering_results(cluster_labels, motif_ids, cluster_info, distance_matrix)
    
    print(f"\n=== Analysis Complete ===")
    print(f"Found {len(np.unique(cluster_labels))} clusters")
    print(f"Silhouette score: {silhouette_score_final:.3f}")
    print("Check the generated files and visualizations for detailed results!")

if __name__ == "__main__":
    main()