# Motif Explorer - Feature Specification

## Overview
The Motif Explorer is a browsing and discovery tool that allows users to explore all 486 motifs, filter them, search, and view detailed information about each motif's structure.

---

## Key Features

### 1. **Grid View of All Motifs** 📊
Display all 486 motifs as cards in a responsive grid.

**Each Card Shows:**
- Motif ID (e.g., "Motif 374")
- Small MST visualization (thumbnail)
- Key stats:
  - Number of nodes
  - Number of edges
  - Total MST weight
  - Cluster assignment
- Visual indicator of motif size (color-coded)

**Interaction:**
- Click card → Opens detailed modal
- Hover → Shows quick preview
- Select multiple → Compare side-by-side

---

### 2. **Advanced Filtering** 🔍

**Filter by Size:**
- Slider: 2-157 nodes
- Presets: Small (2-10), Medium (11-30), Large (31+)

**Filter by Cluster:**
- Dropdown: Select cluster 0-49
- Show only motifs from selected cluster

**Filter by Weight:**
- Slider: 0-4545 (MST weight range)
- Quartiles: Low, Medium, High, Very High

**Filter by Degree:**
- Max degree in motif
- Average degree

**Sort Options:**
- By ID (ascending/descending)
- By size (nodes)
- By weight
- By cluster
- By complexity (edges/nodes ratio)

---

### 3. **Search Functionality** 🔎

**Search by:**
- Motif ID (exact match)
- Node ID (find motifs containing a specific node)
- Cluster number
- Size range

**Search Features:**
- Real-time filtering as you type
- Clear search button
- Search history (recent searches)

---

### 4. **Detailed Motif View** 🔬

When clicking a motif card, open a modal/side panel with:

**Visualization:**
- Large interactive MST graph
- Draggable nodes
- Zoom and pan
- Toggle between MST and full motif view
- Highlight source node

**Statistics:**
- Source node ID
- Total nodes: X
- Total edges: Y
- MST edges: Z
- Excluded edges: W
- Total MST weight: XXX
- Average edge weight: XX.X
- Max degree: X
- Density: X.XX

**Cluster Information:**
- Belongs to Cluster X
- Cluster size: Y motifs
- Other motifs in same cluster (clickable)

**Overlap Analysis:**
- List of motifs that share nodes
- Number of shared nodes with each
- Visualization of overlap

**Export Options:**
- Download as JSON
- Download as PNG (visualization)
- Copy node list
- Copy edge list

---

### 5. **Comparison Mode** ⚖️

**Select Multiple Motifs:**
- Checkbox on each card
- "Compare Selected" button
- Compare up to 4 motifs side-by-side

**Comparison View Shows:**
- Side-by-side MST visualizations
- Comparative statistics table
- Shared nodes highlighted
- Wasserstein distance between them
- Structural similarity score

---

### 6. **Visual Indicators** 🎨

**Color Coding:**
- Small motifs (2-10 nodes): Blue
- Medium motifs (11-30 nodes): Green
- Large motifs (31-50 nodes): Orange
- Very large motifs (51+ nodes): Red

**Badges:**
- "Outlier" badge for singleton clusters
- "Dense" badge for high edge/node ratio
- "Star" badge for star-shaped motifs
- "Clique" badge for fully connected motifs

---

### 7. **Statistics Panel** 📈

**Global Statistics (always visible):**
- Total motifs: 486
- Filtered motifs: X
- Average size: 16.6 nodes
- Size range: 2-157 nodes
- Weight range: 0-4545

**Distribution Charts:**
- Histogram of motif sizes
- Histogram of MST weights
- Cluster distribution pie chart

---

## UI Layout

```
┌─────────────────────────────────────────────────────────┐
│  Motif Explorer                                         │
│  Browse and explore all 486 motifs                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Search: ___________] [🔍]                             │
│                                                          │
│  Filters:                                               │
│  Size: [====●====] 2-157 nodes                         │
│  Cluster: [All Clusters ▼]                             │
│  Weight: [====●====] 0-4545                            │
│  Sort by: [Size ▼]                                     │
│                                                          │
│  [Clear Filters]  [Compare Selected (0)]               │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  Showing 486 motifs                                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐        │
│  │ M1   │ │ M2   │ │ M3   │ │ M4   │ │ M5   │        │
│  │ [MST]│ │ [MST]│ │ [MST]│ │ [MST]│ │ [MST]│        │
│  │17 n  │ │10 n  │ │12 n  │ │10 n  │ │13 n  │        │
│  │16 e  │ │ 9 e  │ │11 e  │ │ 9 e  │ │12 e  │        │
│  │C0    │ │C0    │ │C1    │ │C0    │ │C0    │        │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘        │
│                                                          │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐        │
│  │ M6   │ │ M7   │ │ M8   │ │ M9   │ │ M10  │        │
│  │ ...  │ │ ...  │ │ ...  │ │ ...  │ │ ...  │        │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘        │
│                                                          │
│  [Load More] or [Infinite Scroll]                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Priority

### Phase 1: Basic Grid View (Day 1)
- Load all motifs from JSON
- Display as cards in grid
- Show basic info (ID, size, cluster)
- Click to view details

### Phase 2: Filtering & Search (Day 2)
- Size filter slider
- Cluster dropdown
- Search by ID
- Sort options

### Phase 3: Detailed View (Day 3)
- Modal with large MST visualization
- Complete statistics
- D3 interactive graph

### Phase 4: Advanced Features (Day 4)
- Comparison mode
- Overlap analysis
- Export functionality
- Visual indicators

---

## Data Requirements

**Load from:**
- `facebook_motifs.json` - Motif structure data
- `facebook_msts.json` - MST data
- `agglomerative_50_cluster_groups.json` - Cluster assignments
- `wasserstein_distances.json` - For similarity comparisons

**Computed on-the-fly:**
- Density (edges/nodes)
- Degree statistics
- Overlap with other motifs

---

## User Stories

1. **As a researcher**, I want to browse all motifs so I can understand the variety of structures in the graph.

2. **As a data analyst**, I want to filter motifs by size so I can focus on specific complexity levels.

3. **As a user**, I want to search for a specific motif ID so I can quickly find and examine it.

4. **As a researcher**, I want to compare multiple motifs side-by-side so I can understand their structural differences.

5. **As a user**, I want to see which motifs overlap so I can understand the graph's connectivity patterns.

6. **As a researcher**, I want to export motif data so I can use it in external analysis tools.

---

## Technical Considerations

### Performance
- **Virtualization**: Use `react-window` or `react-virtualized` for efficient rendering of 486 cards
- **Lazy loading**: Load MST visualizations only when cards are visible
- **Memoization**: Cache computed statistics

### State Management
```jsx
// Store structure
{
  motifs: [...],           // All motif data
  filters: {
    sizeRange: [2, 157],
    cluster: null,
    weightRange: [0, 4545],
    searchQuery: ''
  },
  sortBy: 'id',
  selectedMotifs: [],      // For comparison
  detailView: null         // Currently viewed motif
}
```

### Components
```
MotifExplorer/
├── MotifGrid.jsx          # Grid container
├── MotifCard.jsx          # Individual card
├── MotifFilters.jsx       # Filter controls
├── MotifSearch.jsx        # Search bar
├── MotifDetail.jsx        # Detail modal
├── MotifComparison.jsx    # Comparison view
└── MotifStats.jsx         # Statistics panel
```

---

## Example Card Component

```jsx
function MotifCard({ motif, onSelect, isSelected }) {
  return (
    <div className="motif-card" onClick={() => onSelect(motif.id)}>
      <div className="card-header">
        <h3>Motif {motif.source_node}</h3>
        {isSelected && <span className="selected-badge">✓</span>}
      </div>
      
      <div className="card-visualization">
        <MiniMST data={motif} />
      </div>
      
      <div className="card-stats">
        <div className="stat">
          <span className="label">Nodes:</span>
          <span className="value">{motif.nodes.length}</span>
        </div>
        <div className="stat">
          <span className="label">Edges:</span>
          <span className="value">{motif.num_edges}</span>
        </div>
        <div className="stat">
          <span className="label">Weight:</span>
          <span className="value">{motif.total_weight.toFixed(1)}</span>
        </div>
        <div className="stat">
          <span className="label">Cluster:</span>
          <span className="value badge">C{motif.cluster}</span>
        </div>
      </div>
    </div>
  )
}
```

---

## Summary

The Motif Explorer should be:
- **Comprehensive**: Show all 486 motifs
- **Filterable**: Multiple filter options
- **Searchable**: Quick access to specific motifs
- **Interactive**: Click to explore details
- **Comparative**: Compare multiple motifs
- **Informative**: Rich statistics and visualizations
- **Performant**: Handle large dataset efficiently

This makes it a powerful tool for exploring and understanding the motif structure of the graph!
