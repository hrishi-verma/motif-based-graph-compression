import { useState, useCallback } from 'react'

/**
 * New compression logic with independent motif collapse.
 * 
 * Key change: Each motif becomes its own independent collapsed structure.
 * If a motif's source node was previously collapsed inside another motif,
 * it gets EXTRACTED and becomes visible as the representative of its own motif.
 * 
 * Rules:
 * 1. Source Node Extraction: If source is owned by another motif, extract it
 * 2. Common Nodes Stay: Non-source nodes that are common stay with FIRST owner
 * 3. Unique Nodes Collapse: Nodes unique to current motif collapse under its source
 * 
 * See COMPRESSION_LOGIC_SPEC.md for full documentation.
 */
export function useCollapse(motifData) {
  const [state, setState] = useState({
    collapsedMotifs: new Set(),
    motifOwnership: new Map()  // nodeId -> motifId (which motif owns each node)
  })

  const collapseCluster = useCallback((clusterMotifs) => {
    if (!motifData) return

    setState(prevState => {
      const newCollapsedMotifs = new Set(prevState.collapsedMotifs)
      const newMotifOwnership = new Map(prevState.motifOwnership)

      console.log('=== COLLAPSING CLUSTER (New Independent Logic) ===')
      console.log('Previous state:', newCollapsedMotifs.size, 'motifs,', newMotifOwnership.size, 'owned nodes')
      
      clusterMotifs.forEach((motifId) => {
        const mst = motifData[motifId.toString()]
        if (!mst) return

        const sourceNode = mst.source_node
        const motifNodes = new Set(mst.nodes)

        console.log(`Processing Motif ${motifId} (source: ${sourceNode})`)

        // ============================================
        // STEP 1: Handle source node extraction
        // ============================================
        if (newMotifOwnership.has(sourceNode)) {
          const previousOwner = newMotifOwnership.get(sourceNode)
          // Extract: remove ownership from previous motif
          newMotifOwnership.delete(sourceNode)
          console.log(`  → Extracted source ${sourceNode} from Motif ${previousOwner}`)
        }

        // ============================================
        // STEP 2: Claim nodes for this motif
        // ============================================
        newCollapsedMotifs.add(motifId)
        
        let claimedCount = 0
        let skippedCount = 0
        
        motifNodes.forEach(node => {
          if (node === sourceNode) {
            // Source node: this motif owns it (extracted above if needed)
            newMotifOwnership.set(node, motifId)
            claimedCount++
          } else {
            // Non-source node: only claim if not already owned
            if (!newMotifOwnership.has(node)) {
              newMotifOwnership.set(node, motifId)
              claimedCount++
            } else {
              // Already owned by another motif - leave it there
              skippedCount++
            }
          }
        })

        console.log(`  → Collapsed: claimed ${claimedCount} nodes, skipped ${skippedCount} (already owned)`)
      })

      console.log(`Total collapsed: ${newCollapsedMotifs.size} motifs, ${newMotifOwnership.size} owned nodes`)

      return {
        collapsedMotifs: newCollapsedMotifs,
        motifOwnership: newMotifOwnership
      }
    })
  }, [motifData])

  const expandMotif = useCallback((motifId) => {
    if (!motifData) return

    setState(prevState => {
      const newCollapsedMotifs = new Set(prevState.collapsedMotifs)
      const newMotifOwnership = new Map(prevState.motifOwnership)
      
      // Remove from collapsed set
      newCollapsedMotifs.delete(motifId)

      // Release nodes that this motif owns
      const mst = motifData[motifId.toString()]
      if (mst) {
        let releasedCount = 0
        mst.nodes.forEach(node => {
          if (newMotifOwnership.get(node) === motifId) {
            newMotifOwnership.delete(node)
            releasedCount++
          }
        })
        console.log(`Expanded Motif ${motifId}: released ${releasedCount} nodes`)
      }

      return {
        collapsedMotifs: newCollapsedMotifs,
        motifOwnership: newMotifOwnership
      }
    })
  }, [motifData])

  const reset = useCallback(() => {
    setState({
      collapsedMotifs: new Set(),
      motifOwnership: new Map()
    })
  }, [])

  // Helper to get collapsed nodes set (for backward compatibility)
  const getCollapsedNodes = useCallback(() => {
    return new Set(state.motifOwnership.keys())
  }, [state.motifOwnership])

  return {
    collapsedMotifs: state.collapsedMotifs,
    motifOwnership: state.motifOwnership,
    collapsedNodes: getCollapsedNodes(),  // backward compatibility
    collapseCluster,
    expandMotif,
    reset
  }
}
