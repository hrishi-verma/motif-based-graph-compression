#!/usr/bin/env python3
"""
Analyze structural similarity of MSTs within each cluster
Provides quantitative metrics to validate clustering quality
"""

import json
import numpy as np
from collections import defaultdict

def load_data(n_clusters=30):
    """Load cluster assignments and MST data"""
    filename = f'data/agglomerative_{n_clusters}_cluster_groups.json'
    print(f"Loading from: {filename}")
    with open(filename, 'r') as f:
        clusters = json.load(f)
    
    with open('data/facebook_msts.json', 'r') as f:
        msts = json.load(f)
    
    return clusters, msts

def calculate_mst_features(mst_data):
    """Extract structural features from an MST"""
    features = {
        'num_nodes': len(mst_data['nodes']),
        'num_edges': mst_data['num_mst_edges'],
        'total_weight': mst_data['total_weight'],
        'avg_edge_weight': mst_data['total_weight'] / max(1, mst_data['num_mst_edges']),
        'max_edge_weight': 0,
        'min_edge_weight': float('inf'),
        'weight_std': 0,
        'degree_distribution': defaultdict(int)
    }
    
    # Calculate edge weight statistics
    if mst_data['mst_edges']:
        weights = [edge['weight'] for edge in mst_data['mst_edges']]
        features['max_edge_weight'] = max(weights)
        features['min_edge_weight'] = min(weights)
        features['weight_std'] = np.std(weights)
    
    # Calculate degree distribution
    degree_count = defaultdict(int)
    for edge in mst_data['mst_edges']:
        degree_count[edge['from']] += 1
        degree_count[edge['to']] += 1
    
    for degree in degree_count.values():
        features['degree_distribution'][degree] += 1
    
    # Calculate max degree
    features['max_degree'] = max(degree_count.values()) if degree_count else 0
    features['avg_degree'] = sum(degree_count.values()) / len(degree_count) if degree_count else 0
    
    return features

def calculate_cluster_cohesion(cluster_motifs, msts):
    """Calculate how similar MSTs are within a cluster"""
    features_list = []
    
    for motif_id in cluster_motifs:
        mst_data = msts.get(str(motif_id))
        if mst_data:
            features = calculate_mst_features(mst_data)
            features_list.append(features)
    
    if not features_list:
        return None
    
    # Calculate statistics for each feature
    cohesion = {
        'num_motifs': len(features_list),
        'node_count': {
            'mean': np.mean([f['num_nodes'] for f in features_list]),
            'std': np.std([f['num_nodes'] for f in features_list]),
            'min': min([f['num_nodes'] for f in features_list]),
            'max': max([f['num_nodes'] for f in features_list])
        },
        'edge_count': {
            'mean': np.mean([f['num_edges'] for f in features_list]),
            'std': np.std([f['num_edges'] for f in features_list]),
            'min': min([f['num_edges'] for f in features_list]),
            'max': max([f['num_edges'] for f in features_list])
        },
        'total_weight': {
            'mean': np.mean([f['total_weight'] for f in features_list]),
            'std': np.std([f['total_weight'] for f in features_list]),
            'min': min([f['total_weight'] for f in features_list]),
            'max': max([f['total_weight'] for f in features_list])
        },
        'avg_edge_weight': {
            'mean': np.mean([f['avg_edge_weight'] for f in features_list]),
            'std': np.std([f['avg_edge_weight'] for f in features_list]),
            'min': min([f['avg_edge_weight'] for f in features_list]),
            'max': max([f['avg_edge_weight'] for f in features_list])
        },
        'max_degree': {
            'mean': np.mean([f['max_degree'] for f in features_list]),
            'std': np.std([f['max_degree'] for f in features_list]),
            'min': min([f['max_degree'] for f in features_list]),
            'max': max([f['max_degree'] for f in features_list])
        }
    }
    
    # Calculate coefficient of variation (CV) as a measure of cohesion
    # Lower CV = more similar structures
    cohesion['cv_total_weight'] = cohesion['total_weight']['std'] / cohesion['total_weight']['mean'] if cohesion['total_weight']['mean'] > 0 else 0
    cohesion['cv_node_count'] = cohesion['node_count']['std'] / cohesion['node_count']['mean'] if cohesion['node_count']['mean'] > 0 else 0
    
    return cohesion

def analyze_all_clusters(clusters, msts):
    """Analyze all clusters and generate report"""
    
    print("=" * 80)
    print("CLUSTER SIMILARITY ANALYSIS")
    print("=" * 80)
    print()
    
    cluster_analyses = {}
    
    for cluster_key in sorted(clusters.keys(), key=lambda x: int(x.split('_')[1])):
        cluster_idx = int(cluster_key.split('_')[1])
        cluster = clusters[cluster_key]
        
        print(f"\n{'=' * 80}")
        print(f"CLUSTER {cluster_idx}")
        print(f"{'=' * 80}")
        print(f"Size: {cluster['size']} motifs ({cluster['percentage']:.1f}%)")
        print(f"Motif IDs: {cluster['motifs'][:10]}{'...' if len(cluster['motifs']) > 10 else ''}")
        
        cohesion = calculate_cluster_cohesion(cluster['motifs'], msts)
        
        if cohesion:
            cluster_analyses[cluster_idx] = cohesion
            
            print(f"\nStructural Similarity Metrics:")
            print(f"  Node Count:        {cohesion['node_count']['mean']:.1f} ± {cohesion['node_count']['std']:.1f} (CV: {cohesion['cv_node_count']:.2f})")
            print(f"                     Range: {cohesion['node_count']['min']:.0f} - {cohesion['node_count']['max']:.0f}")
            
            print(f"  Edge Count:        {cohesion['edge_count']['mean']:.1f} ± {cohesion['edge_count']['std']:.1f}")
            print(f"                     Range: {cohesion['edge_count']['min']:.0f} - {cohesion['edge_count']['max']:.0f}")
            
            print(f"  Total MST Weight:  {cohesion['total_weight']['mean']:.1f} ± {cohesion['total_weight']['std']:.1f} (CV: {cohesion['cv_total_weight']:.2f})")
            print(f"                     Range: {cohesion['total_weight']['min']:.1f} - {cohesion['total_weight']['max']:.1f}")
            
            print(f"  Avg Edge Weight:   {cohesion['avg_edge_weight']['mean']:.2f} ± {cohesion['avg_edge_weight']['std']:.2f}")
            print(f"                     Range: {cohesion['avg_edge_weight']['min']:.2f} - {cohesion['avg_edge_weight']['max']:.2f}")
            
            print(f"  Max Degree:        {cohesion['max_degree']['mean']:.1f} ± {cohesion['max_degree']['std']:.1f}")
            print(f"                     Range: {cohesion['max_degree']['min']:.0f} - {cohesion['max_degree']['max']:.0f}")
            
            # Interpret cohesion
            print(f"\nCohesion Assessment:")
            if cohesion['cv_total_weight'] < 0.3:
                print(f"  ✓ HIGHLY COHESIVE - Very similar MST structures (CV: {cohesion['cv_total_weight']:.2f})")
            elif cohesion['cv_total_weight'] < 0.5:
                print(f"  ✓ MODERATELY COHESIVE - Similar MST structures (CV: {cohesion['cv_total_weight']:.2f})")
            elif cohesion['cv_total_weight'] < 0.8:
                print(f"  ~ SOMEWHAT COHESIVE - Some variation in structures (CV: {cohesion['cv_total_weight']:.2f})")
            else:
                print(f"  ✗ LOW COHESION - High variation in structures (CV: {cohesion['cv_total_weight']:.2f})")
    
    # Summary statistics
    print(f"\n{'=' * 80}")
    print("OVERALL SUMMARY")
    print(f"{'=' * 80}")
    
    cvs = [c['cv_total_weight'] for c in cluster_analyses.values()]
    print(f"\nCoefficient of Variation (CV) across clusters:")
    print(f"  Mean CV: {np.mean(cvs):.3f}")
    print(f"  Median CV: {np.median(cvs):.3f}")
    print(f"  Min CV: {min(cvs):.3f} (most cohesive)")
    print(f"  Max CV: {max(cvs):.3f} (least cohesive)")
    
    highly_cohesive = sum(1 for cv in cvs if cv < 0.3)
    moderately_cohesive = sum(1 for cv in cvs if 0.3 <= cv < 0.5)
    somewhat_cohesive = sum(1 for cv in cvs if 0.5 <= cv < 0.8)
    low_cohesion = sum(1 for cv in cvs if cv >= 0.8)
    
    print(f"\nCluster Quality Distribution:")
    print(f"  Highly cohesive:      {highly_cohesive} clusters")
    print(f"  Moderately cohesive:  {moderately_cohesive} clusters")
    print(f"  Somewhat cohesive:    {somewhat_cohesive} clusters")
    print(f"  Low cohesion:         {low_cohesion} clusters")
    
    # Find best and worst clusters
    best_cluster = min(cluster_analyses.items(), key=lambda x: x[1]['cv_total_weight'])
    worst_cluster = max(cluster_analyses.items(), key=lambda x: x[1]['cv_total_weight'])
    
    print(f"\nMost cohesive cluster: Cluster {best_cluster[0]} (CV: {best_cluster[1]['cv_total_weight']:.3f})")
    print(f"Least cohesive cluster: Cluster {worst_cluster[0]} (CV: {worst_cluster[1]['cv_total_weight']:.3f})")
    
    # Save detailed analysis
    output = {
        'cluster_analyses': {str(k): v for k, v in cluster_analyses.items()},
        'summary': {
            'mean_cv': float(np.mean(cvs)),
            'median_cv': float(np.median(cvs)),
            'min_cv': float(min(cvs)),
            'max_cv': float(max(cvs)),
            'highly_cohesive_count': highly_cohesive,
            'moderately_cohesive_count': moderately_cohesive,
            'somewhat_cohesive_count': somewhat_cohesive,
            'low_cohesion_count': low_cohesion,
            'best_cluster': best_cluster[0],
            'worst_cluster': worst_cluster[0]
        }
    }
    
    with open('data/cluster_similarity_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print("Analysis saved to: data/cluster_similarity_analysis.json")
    print(f"{'=' * 80}")

def compare_specific_motifs(motif_ids, msts):
    """Compare specific motifs in detail"""
    print(f"\n{'=' * 80}")
    print(f"DETAILED COMPARISON: Motifs {motif_ids}")
    print(f"{'=' * 80}")
    
    for motif_id in motif_ids:
        mst_data = msts.get(str(motif_id))
        if mst_data:
            features = calculate_mst_features(mst_data)
            print(f"\nMotif {motif_id}:")
            print(f"  Nodes: {features['num_nodes']}")
            print(f"  Edges: {features['num_edges']}")
            print(f"  Total Weight: {features['total_weight']:.1f}")
            print(f"  Avg Edge Weight: {features['avg_edge_weight']:.2f}")
            print(f"  Weight Range: {features['min_edge_weight']:.1f} - {features['max_edge_weight']:.1f}")
            print(f"  Max Degree: {features['max_degree']}")

def main(n_clusters=30):
    """Main analysis function"""
    print("Loading data...")
    clusters, msts = load_data(n_clusters=n_clusters)
    
    print(f"Loaded {len(clusters)} clusters and {len(msts)} MSTs\n")
    
    # Analyze all clusters
    analyze_all_clusters(clusters, msts)
    
    # Example: Compare specific motifs from cluster 0
    print("\n\nEXAMPLE: Comparing first 5 motifs from Cluster 0:")
    cluster_0_motifs = clusters['cluster_0']['motifs'][:5]
    compare_specific_motifs(cluster_0_motifs, msts)

if __name__ == "__main__":
    main()
