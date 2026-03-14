/**
 * Test utilities and mock data for the React app tests
 */

// Mock graph data (small sample)
export const mockGraphData = {
  nodes: [
    { id: 1, type: 'regular' },
    { id: 2, type: 'regular' },
    { id: 3, type: 'regular' },
    { id: 4, type: 'regular' },
    { id: 5, type: 'regular' }
  ],
  links: [
    { source: 1, target: 2, weight: 1.0 },
    { source: 2, target: 3, weight: 1.5 },
    { source: 3, target: 4, weight: 2.0 },
    { source: 4, target: 5, weight: 0.5 },
    { source: 1, target: 5, weight: 3.0 }
  ]
}

// Mock CSV for parsing tests
export const mockCSVContent = `Node1,Node2,Weight
1,2,1.0
2,3,1.5
3,4,2.0
4,5,0.5
1,5,3.0`

// Mock motif data
export const mockMotifsData = {
  motifs: [
    {
      source_node: 1,
      num_neighbors: 3,
      num_edges: 2,
      cluster: 0
    },
    {
      source_node: 2,
      num_neighbors: 4,
      num_edges: 3,
      cluster: 1
    },
    {
      source_node: 3,
      num_neighbors: 2,
      num_edges: 1,
      cluster: 0
    }
  ],
  statistics: {
    total_motifs: 3,
    avg_neighbors: 3,
    avg_edges: 2
  }
}

// Mock MST data
export const mockMstsData = {
  '1': {
    source_node: 1,
    nodes: [1, 2, 3],
    edges: [[1, 2], [2, 3]],
    total_weight: 2.5
  },
  '2': {
    source_node: 2,
    nodes: [2, 3, 4, 5],
    edges: [[2, 3], [3, 4], [4, 5]],
    total_weight: 4.0
  },
  '3': {
    source_node: 3,
    nodes: [3, 4],
    edges: [[3, 4]],
    total_weight: 2.0
  }
}

// Mock cluster data
export const mockClustersData = {
  cluster_0: {
    cluster_id: 0,
    motifs: [1, 3],
    avg_size: 2.5,
    total_weight: 4.5
  },
  cluster_1: {
    cluster_id: 1,
    motifs: [2],
    avg_size: 4.0,
    total_weight: 4.0
  }
}

// Mock motifData for useCollapse hook (same as MST but keyed by motif ID)
export const mockMotifDataForCollapse = {
  '1': {
    source_node: 1,
    nodes: [1, 2, 3],
    edges: [[1, 2], [2, 3]]
  },
  '2': {
    source_node: 2,
    nodes: [2, 3, 4, 5],
    edges: [[2, 3], [3, 4], [4, 5]]
  },
  '3': {
    source_node: 3,
    nodes: [3, 4],
    edges: [[3, 4]]
  }
}
