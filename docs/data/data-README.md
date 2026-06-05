# Subgraph Motif Extraction Results

## Overview
This directory contains the extracted subgraph motifs from the Facebook weighted graph data for motif-based graph compression research.

## Files
- `facebook_motifs.json` - Complete subgraph motif dataset with statistics

## Motif Definition
Each motif represents a **complete subgraph** centered on a source node, containing:
- **Source node**: The central node of the motif
- **All neighbors**: All nodes directly connected to the source (distance = 1)
- **Internal edges**: All edges between the neighbors themselves
- **Edge weights**: Preserved for all edges in the subgraph

## Dataset Statistics
- **Total motifs**: 486 (one per node)
- **Total edges in all motifs**: 62,143
- **Average neighbors per motif**: 16.61
- **Motifs with internal connections**: 437 (90%)
- **Motifs without internal connections**: 49 (10% - star patterns)

## Data Structure
```json
{
  "motifs": [
    {
      "motif_id": "motif_1",
      "source_node": 1,
      "neighbors": [48, 53, 54, 73, ...],
      "edges": [
        {
          "from": 1,
          "to": 48,
          "weight": 9.0,
          "edge_type": "source_to_neighbor"
        },
        {
          "from": 48,
          "to": 53,
          "weight": 7.0,
          "edge_type": "neighbor_to_neighbor"
        }
      ],
      "num_neighbors": 16,
      "num_edges": 25,
      "subgraph_density": 1.56
    }
  ],
  "statistics": {
    "total_motifs": 486,
    "total_edges_in_motifs": 62143,
    "average_motif_size": 16.61,
    "motif_size_distribution": {...}
  }
}
```

## Usage
This motif data can be used for:
1. Graph compression algorithms
2. Pattern analysis
3. Community detection
4. Network structure analysis

## Next Steps
The extracted motifs are ready for the next phase of motif-based graph compression research.