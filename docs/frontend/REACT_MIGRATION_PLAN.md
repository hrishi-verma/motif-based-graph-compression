# React Migration Plan - Graph Motif Compression

## Overview
Convert the current HTML/D3.js visualization into a modern React application with multiple pages, better state management, and improved user experience.

---

## Proposed Architecture

### Tech Stack
```
Frontend:
- React 18+ (with hooks)
- React Router v6 (for navigation)
- D3.js (keep for visualizations)
- Zustand or Redux Toolkit (state management)
- TailwindCSS or Material-UI (styling)
- Vite (build tool - faster than CRA)

Backend:
- Keep existing Flask server
- Add CORS support (already present)
- Optional: Add WebSocket for real-time updates
```

---

## Application Structure

```
motif-compression-app/
├── public/
│   └── data/                    # Copy existing JSON files here
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   └── StatsCard.jsx
│   │   ├── visualizations/
│   │   │   ├── D3Graph.jsx      # Reusable D3 wrapper
│   │   │   ├── ForceGraph.jsx
│   │   │   ├── MSTViewer.jsx
│   │   │   └── PersistenceDiagram.jsx
│   │   └── controls/
│   │       ├── ClusterSelector.jsx
│   │       ├── ThresholdSlider.jsx
│   │       └── CollapseControls.jsx
│   ├── pages/
│   │   ├── Home.jsx             # Landing page with overview
│   │   ├── DataPipeline.jsx     # Show data flow
│   │   ├── MotifExplorer.jsx    # Browse motifs
│   │   ├── ClusterAnalysis.jsx  # Cluster comparison
│   │   ├── GraphCollapse.jsx    # Main collapsing interface
│   │   └── Statistics.jsx       # Detailed stats
│   ├── hooks/
│   │   ├── useGraphData.js      # Load graph data
│   │   ├── useMotifData.js      # Load motif data
│   │   ├── useClusterData.js    # Load cluster data
│   │   └── useCollapse.js       # Collapse logic
│   ├── store/
│   │   ├── graphStore.js        # Graph state
│   │   ├── clusterStore.js      # Cluster state
│   │   └── uiStore.js           # UI state
│   ├── utils/
│   │   ├── dataLoader.js        # API calls
│   │   ├── collapseLogic.js     # Intelligent collapse
│   │   ├── d3Helpers.js         # D3 utilities
│   │   └── calculations.js      # Math utilities
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
└── vite.config.js
```

---

## Page Breakdown

### 1. Home Page (`/`)
**Purpose:** Landing page with project overview

**Features:**
- Project description
- Quick stats (486 nodes, 50 clusters, etc.)
- Navigation cards to different sections
- Visual pipeline diagram
- Recent activity/changes

**Components:**
```jsx
<Home>
  <Hero />
  <QuickStats />
  <NavigationCards />
  <PipelineDiagram />
</Home>
```

---

### 2. Data Pipeline Page (`/pipeline`)
**Purpose:** Visualize the data processing flow

**Features:**
- Step-by-step pipeline visualization
- Status of each stage (✓ Complete)
- File sizes and statistics
- Download/export options
- Re-run pipeline buttons

**Components:**
```jsx
<DataPipeline>
  <PipelineStep stage="motif-extraction" />
  <PipelineStep stage="mst-computation" />
  <PipelineStep stage="persistence" />
  <PipelineStep stage="wasserstein" />
  <PipelineStep stage="clustering" />
</DataPipeline>
```

---

### 3. Motif Explorer (`/motifs`)
**Purpose:** Browse and explore individual motifs

**Features:**
- Grid view of all 486 motifs
- Filter by size, weight, cluster
- Search by motif ID
- Click to view detailed MST
- Compare multiple motifs side-by-side

**Components:**
```jsx
<MotifExplorer>
  <MotifFilters />
  <MotifGrid>
    <MotifCard motifId={1} />
    <MotifCard motifId={2} />
    ...
  </MotifGrid>
  <MotifDetailModal />
</MotifExplorer>
```

---

### 4. Cluster Analysis (`/clusters`)
**Purpose:** Analyze and compare clusters

**Features:**
- Dropdown to select cluster
- View all MSTs in selected cluster
- Cluster statistics and cohesion metrics
- Compare clusters side-by-side
- Dendrogram visualization

**Components:**
```jsx
<ClusterAnalysis>
  <ClusterSelector />
  <ClusterStats />
  <MSTGrid cluster={selectedCluster} />
  <CohesionMetrics />
  <ClusterComparison />
</ClusterAnalysis>
```

---

### 5. Graph Collapse (`/collapse`) ⭐ Main Feature
**Purpose:** Interactive graph collapsing with intelligent overlap

**Features:**
- Full graph visualization
- Cluster selector dropdown
- Collapse/expand controls
- Real-time statistics
- Animation of collapse process
- Export collapsed graph

**Components:**
```jsx
<GraphCollapse>
  <ControlPanel>
    <ClusterSelector />
    <CollapseControls />
    <StatisticsPanel />
  </ControlPanel>
  <GraphVisualization>
    <D3ForceGraph />
    <NodeTooltip />
    <EdgeTooltip />
  </GraphVisualization>
  <MotifGallery />
</GraphCollapse>
```

---

### 6. Statistics Dashboard (`/stats`)
**Purpose:** Comprehensive statistics and analytics

**Features:**
- Cluster size distribution charts
- Wasserstein distance heatmap
- Compression ratio over different thresholds
- Persistence diagram overview
- Export data as CSV/JSON

**Components:**
```jsx
<Statistics>
  <ChartGrid>
    <BarChart data={clusterSizes} />
    <Heatmap data={distances} />
    <LineChart data={compressionRatios} />
    <ScatterPlot data={persistence} />
  </ChartGrid>
  <ExportPanel />
</Statistics>
```

---

## Key React Patterns to Use

### 1. Custom Hooks for Data Loading
```jsx
// hooks/useGraphData.js
export function useGraphData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/facebook_weighted_filtered.csv')
      .then(response => response.text())
      .then(csv => d3.csvParse(csv))
      .then(data => {
        setData(processGraphData(data));
        setLoading(false);
      })
      .catch(err => setError(err));
  }, []);

  return { data, loading, error };
}
```

### 2. D3 Integration with React
```jsx
// components/visualizations/D3Graph.jsx
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export function D3Graph({ data, onNodeClick }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data) return;

    const svg = d3.select(svgRef.current);
    // D3 code here
    
    return () => {
      // Cleanup
      svg.selectAll('*').remove();
    };
  }, [data]);

  return <svg ref={svgRef} width={800} height={600} />;
}
```

### 3. State Management with Zustand
```jsx
// store/graphStore.js
import create from 'zustand';

export const useGraphStore = create((set) => ({
  nodes: [],
  links: [],
  collapsedMotifs: new Set(),
  collapsedNodes: new Set(),
  
  collapseMotif: (motifId) => set((state) => ({
    collapsedMotifs: new Set([...state.collapsedMotifs, motifId])
  })),
  
  expandMotif: (motifId) => set((state) => {
    const newSet = new Set(state.collapsedMotifs);
    newSet.delete(motifId);
    return { collapsedMotifs: newSet };
  }),
  
  reset: () => set({
    collapsedMotifs: new Set(),
    collapsedNodes: new Set()
  })
}));
```

### 4. Routing
```jsx
// App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pipeline" element={<DataPipeline />} />
          <Route path="/motifs" element={<MotifExplorer />} />
          <Route path="/motifs/:id" element={<MotifDetail />} />
          <Route path="/clusters" element={<ClusterAnalysis />} />
          <Route path="/collapse" element={<GraphCollapse />} />
          <Route path="/stats" element={<Statistics />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
```

---

## Migration Steps

### Phase 1: Setup (1-2 days)
1. Create React app with Vite
   ```bash
   npm create vite@latest motif-app -- --template react
   cd motif-app
   npm install
   ```

2. Install dependencies
   ```bash
   npm install react-router-dom d3 zustand
   npm install -D tailwindcss postcss autoprefixer
   ```

3. Setup project structure
4. Configure routing
5. Setup state management

### Phase 2: Core Components (2-3 days)
1. Create reusable D3 wrapper components
2. Build common UI components (Header, Sidebar, Cards)
3. Implement data loading hooks
4. Setup API service layer

### Phase 3: Page Implementation (5-7 days)
1. **Day 1:** Home page + Data Pipeline page
2. **Day 2:** Motif Explorer page
3. **Day 3:** Cluster Analysis page
4. **Day 4-5:** Graph Collapse page (most complex)
5. **Day 6:** Statistics Dashboard
6. **Day 7:** Polish and bug fixes

### Phase 4: Advanced Features (2-3 days)
1. Add animations for collapse/expand
2. Implement export functionality
3. Add keyboard shortcuts
4. Optimize performance (virtualization for large lists)
5. Add dark mode

### Phase 5: Testing & Deployment (2-3 days)
1. Unit tests for utilities
2. Integration tests for key flows
3. Performance testing
4. Build optimization
5. Deploy to Vercel/Netlify

**Total Estimated Time: 12-18 days**

---

## Code Examples

### Example: Intelligent Collapse Hook
```jsx
// hooks/useCollapse.js
import { useState, useCallback } from 'react';

export function useCollapse(motifData) {
  const [collapsedMotifs, setCollapsedMotifs] = useState(new Set());
  const [collapsedNodes, setCollapsedNodes] = useState(new Set());

  const collapseCluster = useCallback((clusterMotifs) => {
    const newCollapsedMotifs = new Set();
    const newCollapsedNodes = new Set();

    clusterMotifs.forEach((motifId) => {
      const mst = motifData[motifId];
      const sourceNode = mst.source_node;
      const motifNodes = new Set(mst.nodes);

      if (newCollapsedNodes.has(sourceNode)) {
        // Merge unique nodes
        motifNodes.forEach(node => {
          if (!newCollapsedNodes.has(node)) {
            newCollapsedNodes.add(node);
          }
        });
      } else {
        // Full or partial collapse
        newCollapsedMotifs.add(motifId);
        motifNodes.forEach(node => newCollapsedNodes.add(node));
      }
    });

    setCollapsedMotifs(newCollapsedMotifs);
    setCollapsedNodes(newCollapsedNodes);
  }, [motifData]);

  const expandMotif = useCallback((motifId) => {
    setCollapsedMotifs(prev => {
      const newSet = new Set(prev);
      newSet.delete(motifId);
      return newSet;
    });
    // Update collapsed nodes accordingly
  }, []);

  const reset = useCallback(() => {
    setCollapsedMotifs(new Set());
    setCollapsedNodes(new Set());
  }, []);

  return {
    collapsedMotifs,
    collapsedNodes,
    collapseCluster,
    expandMotif,
    reset
  };
}
```

### Example: Graph Collapse Page
```jsx
// pages/GraphCollapse.jsx
import { useState } from 'react';
import { useGraphData, useMotifData, useClusterData } from '../hooks';
import { useCollapse } from '../hooks/useCollapse';
import { D3ForceGraph } from '../components/visualizations/D3ForceGraph';
import { ClusterSelector } from '../components/controls/ClusterSelector';
import { StatsPanel } from '../components/common/StatsPanel';

export function GraphCollapse() {
  const { data: graphData, loading: graphLoading } = useGraphData();
  const { data: motifData, loading: motifLoading } = useMotifData();
  const { data: clusterData, loading: clusterLoading } = useClusterData();
  
  const [selectedCluster, setSelectedCluster] = useState(null);
  const { collapsedMotifs, collapsedNodes, collapseCluster, expandMotif, reset } = 
    useCollapse(motifData);

  const handleCollapseSelected = () => {
    if (selectedCluster) {
      const cluster = clusterData[selectedCluster];
      collapseCluster(cluster.motifs);
    }
  };

  if (graphLoading || motifLoading || clusterLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="flex h-screen">
      <aside className="w-80 bg-gray-100 p-4">
        <h2 className="text-xl font-bold mb-4">Controls</h2>
        
        <ClusterSelector
          clusters={clusterData}
          selected={selectedCluster}
          onChange={setSelectedCluster}
        />
        
        <div className="mt-4 space-y-2">
          <button onClick={handleCollapseSelected}>
            Collapse Selected
          </button>
          <button onClick={reset}>Reset</button>
        </div>
        
        <StatsPanel
          totalNodes={graphData.nodes.length}
          visibleNodes={graphData.nodes.length - collapsedNodes.size + collapsedMotifs.size}
          collapsedStructures={collapsedMotifs.size}
        />
      </aside>
      
      <main className="flex-1">
        <D3ForceGraph
          graphData={graphData}
          motifData={motifData}
          collapsedMotifs={collapsedMotifs}
          collapsedNodes={collapsedNodes}
          onNodeClick={(node) => {
            if (node.type === 'collapsed') {
              expandMotif(node.motifId);
            }
          }}
        />
      </main>
    </div>
  );
}
```

---

## Benefits of React Migration

### 1. **Better Code Organization**
- Reusable components
- Separation of concerns
- Easier to maintain

### 2. **Improved State Management**
- Centralized state
- Predictable updates
- Better debugging

### 3. **Enhanced User Experience**
- Smooth page transitions
- Better loading states
- Responsive design

### 4. **Developer Experience**
- Hot module replacement
- Better debugging tools
- TypeScript support (optional)

### 5. **Scalability**
- Easy to add new features
- Component library
- Testing infrastructure

---

## Recommended Libraries

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "d3": "^7.8.5",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.12.0",
    "recharts": "^2.10.0",
    "framer-motion": "^10.16.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

---

## Next Steps

1. **Decide on styling approach** (TailwindCSS vs Material-UI)
2. **Choose state management** (Zustand vs Redux Toolkit)
3. **Setup development environment**
4. **Start with Phase 1** (project setup)
5. **Migrate one page at a time** (start with simplest)

Would you like me to:
1. Generate the initial React project structure?
2. Create starter code for specific components?
3. Build a proof-of-concept for the Graph Collapse page?
