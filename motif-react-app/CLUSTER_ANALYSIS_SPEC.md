# Cluster Analysis - Feature Specification

## Overview
The Cluster Analysis page allows users to explore the 50 clusters, view all MSTs within each cluster, compare cluster characteristics, and understand structural similarities.

---

## Key Features

### 1. **Cluster Selector** 🎯
- Dropdown to select cluster (0-49)
- Shows cluster size and percentage
- Quick stats preview

### 2. **Cluster Overview** 📊
- Cluster statistics card
- Size, percentage, cohesion metrics
- Average node count, edge count, weight
- Coefficient of variation (CV)

### 3. **MST Grid View** 🌳
- Display all MSTs in selected cluster
- Side-by-side comparison
- Interactive visualizations
- Hover to highlight
- Click to expand

### 4. **Cluster Comparison** ⚖️
- Select 2-4 clusters to compare
- Side-by-side statistics
- Distribution charts
- Similarity metrics

### 5. **Cohesion Metrics** 📈
- Intra-cluster distance
- Size variance
- Weight variance
- Structural similarity score

### 6. **Dendrogram View** 🌲
- Hierarchical clustering visualization
- Show how clusters were formed
- Interactive exploration

---

## Implementation

### Components
- ClusterSelector
- ClusterStatsCard
- MSTGrid
- ClusterComparison
- CohesionMetrics
- DendrogramView (optional)

### Data Sources
- agglomerative_50_cluster_groups.json
- facebook_msts.json
- cluster_similarity_analysis.json (if available)
