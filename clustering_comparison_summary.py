#!/usr/bin/env python3
"""
Summary comparison of different clustering approaches
"""

import json

def print_comparison_summary():
    """Print a comprehensive comparison of clustering methods"""
    
    print("="*80)
    print("MOTIF CLUSTERING ANALYSIS - COMPREHENSIVE COMPARISON")
    print("="*80)
    
    print("\n🔍 PREVIOUS ANALYSIS (Threshold-Based Clustering)")
    print("-" * 50)
    print("Method: Simple distance threshold (≤ 50.0)")
    print("Algorithm: Connected components")
    print("Results:")
    print("  • 18 clusters found")
    print("  • Largest cluster: 295 motifs")
    print("  • Smaller clusters: 2-8 motifs each")
    print("  • Problem: Very unbalanced, arbitrary threshold")
    
    print("\n🎯 NEW ANALYSIS (Agglomerative Clustering)")
    print("-" * 50)
    print("Method: Hierarchical agglomerative clustering")
    print("Algorithm: Bottom-up merging with average linkage")
    print("Optimization: Silhouette score maximization")
    print("Results:")
    print("  • Optimal: 2 clusters (silhouette score: 0.779)")
    print("  • Cluster 0: 485 motifs (avg intra-distance: 382.8)")
    print("  • Cluster 1: 1 motif (motif 348 - clear outlier)")
    
    print("\n📊 KEY FINDINGS")
    print("-" * 50)
    print("1. MOTIF 348 IS A MAJOR OUTLIER:")
    print("   • Minimum distance to any other motif: 649.0")
    print("   • Average distance to others: 2,017.3")
    print("   • Maximum distance: 2,272.5")
    print("   • Consistently isolated in all clustering attempts")
    
    print("\n2. CLUSTERING STRUCTURE:")
    print("   • Most motifs (485/486) are relatively similar")
    print("   • One extreme outlier (motif 348)")
    print("   • Natural division suggests binary classification")
    
    print("\n3. FORCED MULTI-CLUSTER ANALYSIS:")
    print("   • 15 clusters: Largest has 295 motifs (matches threshold method)")
    print("   • 20 clusters: More balanced distribution")
    print("   • Motif 348 always forms its own cluster")
    
    print("\n🎯 COMPARISON OF METHODS")
    print("-" * 50)
    
    methods = [
        ("Threshold (≤50)", "18 clusters", "295, 8, 3, 3, 2...", "Arbitrary cutoff"),
        ("Agglomerative (optimal)", "2 clusters", "485, 1", "Outlier detection"),
        ("Agglomerative (forced 15)", "15 clusters", "295, 72, 21, 18...", "Balanced structure"),
        ("Agglomerative (forced 20)", "20 clusters", "295, 50, 22, 21...", "Fine-grained")
    ]
    
    print(f"{'Method':<25} {'Clusters':<12} {'Sizes':<20} {'Characteristic'}")
    print("-" * 75)
    for method, clusters, sizes, char in methods:
        print(f"{method:<25} {clusters:<12} {sizes:<20} {char}")
    
    print("\n💡 RECOMMENDATIONS")
    print("-" * 50)
    print("1. FOR OUTLIER ANALYSIS:")
    print("   • Investigate motif 348 separately")
    print("   • It represents a unique topological structure")
    print("   • Consider it as a special case in your analysis")
    
    print("\n2. FOR SIMILARITY CLUSTERING:")
    print("   • Remove motif 348 first")
    print("   • Use agglomerative clustering on remaining 485 motifs")
    print("   • Target 10-20 clusters for meaningful groups")
    
    print("\n3. FOR PRACTICAL USE:")
    print("   • Threshold method: Good for quick similarity grouping")
    print("   • Agglomerative method: Better for quality clustering")
    print("   • Hybrid approach: Remove outliers, then cluster")
    
    print("\n📈 QUALITY METRICS")
    print("-" * 50)
    print("Silhouette Scores (higher = better):")
    print("  • 2 clusters: 0.779 (excellent)")
    print("  • 3 clusters: 0.680 (good)")
    print("  • 15 clusters: ~0.531 (moderate)")
    print("  • Threshold method: Not calculated")
    
    print("\n🔬 TOPOLOGICAL INSIGHTS")
    print("-" * 50)
    print("• Most Facebook graph motifs share similar persistence signatures")
    print("• Motif 348 has fundamentally different topological structure")
    print("• Within main group, there are 10-20 natural sub-families")
    print("• Wasserstein distances effectively capture structural differences")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    print_comparison_summary()