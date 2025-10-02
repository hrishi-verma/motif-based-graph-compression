# Maximum Spanning Tree Data

## Overview
This file contains pre-computed Maximum Spanning Trees (MSTs) for all motifs in the Facebook graph dataset.

## File: facebook_msts.json

### Structure
```json
{
  "source_node_id": {
    "source_node": int,
    "nodes": [int],           // All nodes in the motif
    "mst_edges": [            // Edges included in MST
      {
        "from": int,
        "to": int,
        "weight": float
      }
    ],
    "excluded_edges": [       // Edges not in MST
      {
        "from": int,
        "to": int,
        "weight": float,
        "edge_type": string
      }
    ],
    "total_weight": float,    // Sum of MST edge weights
    "num_mst_edges": int,     // Number of edges in MST
    "num_excluded_edges": int // Number of excluded edges
  }
}
```

## Algorithm
- **Prim's Algorithm**: Used to find Maximum Spanning Tree
- **Starting Point**: Always begins from the source node
- **Selection Criteria**: Selects highest weight edges at each step
- **Result**: Spanning tree with maximum total edge weight

## Statistics
- **Total MSTs**: 486 (one per motif)
- **Average MST Weight**: 526.11
- **Maximum MST Weight**: 4545.00
- **Minimum MST Weight**: 0.00

## Usage
This pre-computed data is used by the motif visualizer to avoid real-time MST calculations, improving performance significantly.

## Benefits of Pre-computation
1. **Performance**: No need to calculate MSTs during visualization
2. **Consistency**: Same MST results every time
3. **Analysis**: Can analyze MST patterns across all motifs
4. **Scalability**: Handles large datasets efficiently