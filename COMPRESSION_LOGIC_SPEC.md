# Motif Compression Logic Specification

## Overview

This document specifies the new compression/expansion algorithm for motif-based graph compression. The key change is that each motif should become an **independent collapsed structure**, even when motifs share nodes.

---

## Current Behavior (Problem)

### How It Works Now

1. Motifs are compressed sequentially within a cluster
2. When compressing a motif:
   - If the source node is NOT already collapsed → collapse the motif normally
   - If the source node IS already collapsed (part of a previous motif) → **merge** unique nodes into the existing collapse

### The Problem

When Motif 2's source was part of Motif 1:
- Motif 2 never becomes its own independent structure
- Motif 2's nodes get "absorbed" into Motif 1
- Only Motif 1's source node is visible

```
Example:
  Motif 1: source=A, nodes=[A, B, C, D]
  Motif 2: source=B, nodes=[B, E, F]

Current Result:
  - Compress M1 → A visible, [B,C,D] hidden
  - Compress M2 → B already collapsed, just add [E,F] to hidden nodes
  - Final: Only 1 visible structure (A), nodes [B,C,D,E,F] all hidden
```

---

## New Behavior (Solution)

### Core Principle

**Every motif becomes its own independent collapsed structure with its source node visible.**

If a motif's source node was previously collapsed inside another motif, it gets **extracted** and becomes visible as the representative of its own motif.

### Rules

1. **Source Node Extraction**: If the source node of the current motif is owned by a previous motif, extract it
2. **Common Nodes Stay**: Non-source nodes that are common to multiple motifs stay with the **first motif** that claimed them
3. **Unique Nodes Collapse**: Nodes unique to the current motif collapse under its source

```
Example (same as above):
  Motif 1: source=A, nodes=[A, B, C, D]
  Motif 2: source=B, nodes=[B, E, F]

New Result:
  - Compress M1 → A visible, [B,C,D] hidden under A, ownership: {A→M1, B→M1, C→M1, D→M1}
  - Compress M2 → B was owned by M1, so:
    1. Extract B from M1 (B no longer owned by M1)
    2. Collapse M2 → B visible, [E,F] hidden under B
    3. Ownership: {A→M1, C→M1, D→M1, B→M2, E→M2, F→M2}
  - Final: 2 visible structures (A and B)
```

---

## Data Structures

### Current Data Structures

```javascript
collapsedMotifs: Set<motifId>      // Which motifs are collapsed
collapsedNodes: Set<nodeId>        // Which nodes are hidden (flat set)
```

### New Data Structures

```javascript
collapsedMotifs: Set<motifId>           // Which motifs are collapsed
motifOwnership: Map<nodeId, motifId>    // Which motif "owns" each collapsed node
```

The `motifOwnership` map replaces `collapsedNodes` and provides:
- Direct lookup of which motif owns a node
- Easy extraction (just delete the entry)
- Clear semantics for rendering

---

## Compression Algorithm

### Main Function: `collapseCluster(clusterMotifs)`

```javascript
function collapseCluster(clusterMotifs) {
  clusterMotifs.forEach(motifId => {
    collapseMotif(motifId)
  })
}
```

### Core Function: `collapseMotif(motifId)`

```javascript
function collapseMotif(motifId) {
  const mst = motifData[motifId]
  if (!mst) return
  
  const sourceNode = mst.source_node
  const motifNodes = new Set(mst.nodes)
  
  // ============================================
  // STEP 1: Handle source node extraction
  // ============================================
  // If source node is owned by another motif, extract it
  if (motifOwnership.has(sourceNode)) {
    const previousOwner = motifOwnership.get(sourceNode)
    
    // Extract: remove ownership from previous motif
    motifOwnership.delete(sourceNode)
    
    console.log(`Extracted node ${sourceNode} from Motif ${previousOwner}`)
  }
  
  // ============================================
  // STEP 2: Claim nodes for this motif
  // ============================================
  // Add this motif to collapsed set
  collapsedMotifs.add(motifId)
  
  // Claim ownership of nodes
  motifNodes.forEach(node => {
    if (node === sourceNode) {
      // Source node: this motif owns it (extracted above if needed)
      motifOwnership.set(node, motifId)
    } else {
      // Non-source node: only claim if not already owned
      if (!motifOwnership.has(node)) {
        motifOwnership.set(node, motifId)
      }
      // If already owned by another motif, leave it there (Rule #2)
    }
  })
  
  console.log(`Collapsed Motif ${motifId} (source: ${sourceNode})`)
}
```

### Key Logic Breakdown

| Node Type | Already Owned? | Action |
|-----------|----------------|--------|
| Source node | No | Claim ownership |
| Source node | Yes (by other motif) | **Extract** from other motif, claim ownership |
| Non-source node | No | Claim ownership |
| Non-source node | Yes (by other motif) | **Leave it** with the other motif |

---

## Expansion Algorithm

### Core Function: `expandMotif(motifId)`

```javascript
function expandMotif(motifId) {
  const mst = motifData[motifId]
  if (!mst) return
  
  // Remove from collapsed set
  collapsedMotifs.delete(motifId)
  
  // Release nodes that this motif owns
  mst.nodes.forEach(node => {
    if (motifOwnership.get(node) === motifId) {
      motifOwnership.delete(node)
    }
  })
  
  console.log(`Expanded Motif ${motifId}`)
}
```

### Important Note for Future: Common Nodes on Expansion

When expanding a motif, nodes that were **common** but stayed with another motif will NOT be restored to the expanded motif's visualization. This is expected behavior for now.

**Future Enhancement Consideration:**
If desired, when expanding M2, we could check if any of M2's nodes are still owned by other motifs and potentially restore them. This would require:
1. Checking each node in the expanding motif
2. If owned by another motif that is still collapsed, decide whether to:
   - Leave it collapsed (current plan)
   - Force-expand that portion (complex, not recommended)
   - Show a visual indicator that the node is still collapsed elsewhere

---

## Rendering Algorithm

### Function: `getVisibleNodes()`

```javascript
function getVisibleNodes() {
  const visibleNodes = []
  const hiddenNodes = new Set(motifOwnership.keys())
  
  // All graph nodes
  graphData.nodes.forEach(node => {
    const nodeId = node.id
    
    if (motifOwnership.has(nodeId)) {
      // Node is owned by a collapsed motif
      const ownerMotifId = motifOwnership.get(nodeId)
      const ownerMst = motifData[ownerMotifId]
      
      if (nodeId === ownerMst.source_node) {
        // This is a source node - show it as collapsed representative
        visibleNodes.push({
          id: nodeId,
          type: 'collapsed',
          motifId: ownerMotifId,
          motifSize: ownerMst.nodes.length
        })
      }
      // Non-source owned nodes are hidden (not added to visibleNodes)
    } else {
      // Node is not owned by any motif - show as regular
      visibleNodes.push({
        id: nodeId,
        type: 'regular'
      })
    }
  })
  
  return visibleNodes
}
```

### Edge Redirection

When drawing edges, redirect edges from hidden nodes to their owner's source node:

```javascript
function processEdges() {
  const processedEdges = []
  
  graphData.links.forEach(link => {
    let sourceId = link.source
    let targetId = link.target
    
    // Redirect source if owned
    if (motifOwnership.has(sourceId)) {
      const ownerMotifId = motifOwnership.get(sourceId)
      const ownerMst = motifData[ownerMotifId]
      if (sourceId !== ownerMst.source_node) {
        sourceId = ownerMst.source_node
      }
    }
    
    // Redirect target if owned
    if (motifOwnership.has(targetId)) {
      const ownerMotifId = motifOwnership.get(targetId)
      const ownerMst = motifData[ownerMotifId]
      if (targetId !== ownerMst.source_node) {
        targetId = ownerMst.source_node
      }
    }
    
    // Skip self-loops
    if (sourceId === targetId) return
    
    processedEdges.push({ source: sourceId, target: targetId })
  })
  
  return deduplicateEdges(processedEdges)
}
```

---

## Complete Example Walkthrough

### Setup

```
Cluster contains motifs in order: [M1, M2, M3]

M1: source=10, nodes=[10, 20, 30, 40]
M2: source=20, nodes=[20, 50, 60]       // 20 is in M1!
M3: source=50, nodes=[50, 70, 30]       // 50 is in M2! 30 is in M1!
```

### Step-by-Step Compression

**Initial State:**
```
collapsedMotifs: {}
motifOwnership: {}
```

**Step 1: Collapse M1**
```
- Source 10 not owned → claim it
- Nodes [20, 30, 40] not owned → claim them

collapsedMotifs: {M1}
motifOwnership: {10→M1, 20→M1, 30→M1, 40→M1}
Visible: [10] (as collapsed)
Hidden: [20, 30, 40]
```

**Step 2: Collapse M2**
```
- Source 20 IS owned by M1 → EXTRACT from M1, claim for M2
- Node 50 not owned → claim it
- Node 60 not owned → claim it

collapsedMotifs: {M1, M2}
motifOwnership: {10→M1, 30→M1, 40→M1, 20→M2, 50→M2, 60→M2}
Visible: [10, 20] (both as collapsed)
Hidden: [30, 40, 50, 60]
```

**Step 3: Collapse M3**
```
- Source 50 IS owned by M2 → EXTRACT from M2, claim for M3
- Node 70 not owned → claim it
- Node 30 IS owned by M1 → LEAVE with M1 (common node rule)

collapsedMotifs: {M1, M2, M3}
motifOwnership: {10→M1, 30→M1, 40→M1, 20→M2, 60→M2, 50→M3, 70→M3}
Visible: [10, 20, 50] (all as collapsed)
Hidden: [30, 40, 60, 70]
```

### Final Result

| Visible Node | Represents | Owns Nodes |
|--------------|------------|------------|
| 10 | M1 | 10, 30, 40 |
| 20 | M2 | 20, 60 |
| 50 | M3 | 50, 70 |

Note: Node 30 is in M1 AND M3, but stays with M1 (first owner).

---

## Statistics Calculation

```javascript
function getCompressionStats() {
  const totalNodes = graphData.nodes.length
  const ownedNodes = motifOwnership.size
  const sourceNodes = collapsedMotifs.size  // Each collapsed motif has 1 visible source
  const hiddenNodes = ownedNodes - sourceNodes
  const visibleNodes = totalNodes - hiddenNodes
  const compressionRatio = (hiddenNodes / totalNodes) * 100
  
  return {
    totalNodes,
    visibleNodes,
    hiddenNodes,
    collapsedStructures: collapsedMotifs.size,
    compressionRatio: compressionRatio.toFixed(1) + '%'
  }
}
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `motif-react-app/src/hooks/useCollapse.js` | Replace `collapsedNodes` Set with `motifOwnership` Map, implement new collapse/expand logic |
| `full_cluster_collapse.js` | Same changes for vanilla JS version |
| `motif-react-app/src/components/visualizations/D3ForceGraph.jsx` | Update node filtering to use `motifOwnership` map |

---

## Edge Cases

| Case | Handling |
|------|----------|
| Motif with no shared nodes | Normal collapse, all nodes claimed |
| Source already extracted by later motif | Cannot happen - we process sequentially |
| Circular dependencies (A→B→C→A) | Each extraction is independent, works correctly |
| Empty motif | Skip (guard clause) |
| Single-node motif (source only) | Collapse shows source, no hidden nodes |
| All motifs share one node | Node stays with first motif, others extract their sources |

---

## Future Considerations

### 1. Expansion with Shared Nodes
When expanding a motif, consider whether to also expand related motifs that share nodes. Currently, we only release nodes this motif owns.

### 2. Visual Indicators for Shared Nodes
Could show visual indicators when a collapsed structure has "lost" some nodes to other structures.

### 3. Bidirectional Compression
Could allow compressing motifs in any order with different results.

### 4. Undo/Redo Support
Track compression history to support undo operations.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-26 | Initial specification |
