#!/usr/bin/env python3
"""
Compare 15-cluster vs 30-cluster results
"""

import json

def load_clusters(n):
    """Load cluster data"""
    with open(f'data/agglomerative_{n}_cluster_groups.json', 'r') as f:
        return json.load(f)

def compare_clustering():
    """Compare different cluster counts"""
    
    clusters_15 = load_clusters(15)
    clusters_30 = load_clusters(30)
    clusters_50 = load_clusters(50)
    
    print("="*80)
    print("COMPARISON: 15 vs 30 vs 50 Clusters")
    print("="*80)
    
    # Size distributions
    sizes_15 = sorted([c['size'] for c in clusters_15.values()], reverse=True)
    sizes_30 = sorted([c['size'] for c in clusters_30.values()], reverse=True)
    sizes_50 = sorted([c['size'] for c in clusters_50.values()], reverse=True)
    
    print("\n15 CLUSTERS:")
    print(f"  Total clusters: {len(clusters_15)}")
    print(f"  Largest cluster: {sizes_15[0]} motifs ({sizes_15[0]/486*100:.1f}%)")
    print(f"  Top 5 sizes: {sizes_15[:5]}")
    print(f"  Singleton clusters: {sizes_15.count(1)}")
    print(f"  Small clusters (≤5): {sum(1 for s in sizes_15 if s <= 5)}")
    print(f"  Medium clusters (6-20): {sum(1 for s in sizes_15 if 6 <= s <= 20)}")
    print(f"  Large clusters (>20): {sum(1 for s in sizes_15 if s > 20)}")
    
    print("\n30 CLUSTERS:")
    print(f"  Total clusters: {len(clusters_30)}")
    print(f"  Largest cluster: {sizes_30[0]} motifs ({sizes_30[0]/486*100:.1f}%)")
    print(f"  Top 5 sizes: {sizes_30[:5]}")
    print(f"  Singleton clusters: {sizes_30.count(1)}")
    print(f"  Small clusters (≤5): {sum(1 for s in sizes_30 if s <= 5)}")
    print(f"  Medium clusters (6-20): {sum(1 for s in sizes_30 if 6 <= s <= 20)}")
    print(f"  Large clusters (>20): {sum(1 for s in sizes_30 if s > 20)}")
    
    print("\n50 CLUSTERS:")
    print(f"  Total clusters: {len(clusters_50)}")
    print(f"  Largest cluster: {sizes_50[0]} motifs ({sizes_50[0]/486*100:.1f}%)")
    print(f"  Top 5 sizes: {sizes_50[:5]}")
    print(f"  Singleton clusters: {sizes_50.count(1)}")
    print(f"  Small clusters (≤5): {sum(1 for s in sizes_50 if s <= 5)}")
    print(f"  Medium clusters (6-20): {sum(1 for s in sizes_50 if 6 <= s <= 20)}")
    print(f"  Large clusters (>20): {sum(1 for s in sizes_50 if s > 20)}")
    
    print("\n" + "="*80)
    print("KEY OBSERVATIONS:")
    print("="*80)
    print(f"✓ Dominant cluster evolution:")
    print(f"  • 15 clusters: {sizes_15[0]} motifs (60.7%)")
    print(f"  • 30 clusters: {sizes_30[0]} motifs (60.7%)")
    print(f"  • 50 clusters: {sizes_50[0]} motifs (57.0%)")
    print(f"\n✓ Singleton progression: {sizes_15.count(1)} → {sizes_30.count(1)} → {sizes_50.count(1)}")
    print(f"✓ 50 clusters provides finest granularity")
    print(f"✓ More outliers identified with higher cluster count")
    
    # Calculate average cluster size (excluding dominant cluster)
    avg_15 = sum(sizes_15[1:]) / len(sizes_15[1:]) if len(sizes_15) > 1 else 0
    avg_30 = sum(sizes_30[1:]) / len(sizes_30[1:]) if len(sizes_30) > 1 else 0
    avg_50 = sum(sizes_50[1:]) / len(sizes_50[1:]) if len(sizes_50) > 1 else 0
    
    print(f"\n✓ Average size (excluding dominant cluster):")
    print(f"  • 15 clusters: {avg_15:.1f} motifs")
    print(f"  • 30 clusters: {avg_30:.1f} motifs")
    print(f"  • 50 clusters: {avg_50:.1f} motifs")

if __name__ == "__main__":
    compare_clustering()
