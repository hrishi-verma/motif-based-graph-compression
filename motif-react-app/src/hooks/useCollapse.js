import { useState, useCallback } from 'react'

export function useCollapse(motifData) {
  const [state, setState] = useState({
    collapsedMotifs: new Set(),
    collapsedNodes: new Set()
  })

  const collapseCluster = useCallback((clusterMotifs) => {
    if (!motifData) return

    setState(prevState => {
      const newCollapsedMotifs = new Set(prevState.collapsedMotifs)
      const newCollapsedNodes = new Set(prevState.collapsedNodes)

      console.log('=== COLLAPSING CLUSTER ===')
      console.log('Previous state:', newCollapsedMotifs.size, 'motifs,', newCollapsedNodes.size, 'nodes')
      
      clusterMotifs.forEach((motifId) => {
        const mst = motifData[motifId.toString()]
        if (!mst) return

        const sourceNode = mst.source_node
        const motifNodes = new Set(mst.nodes)

        console.log(`Processing Motif ${motifId} (source: ${sourceNode})`)

        // Check if source node is already collapsed
        const sourceAlreadyCollapsed = newCollapsedNodes.has(sourceNode)

        if (sourceAlreadyCollapsed) {
          // Merge unique nodes only
          let uniqueCount = 0
          motifNodes.forEach(node => {
            if (!newCollapsedNodes.has(node)) {
              newCollapsedNodes.add(node)
              uniqueCount++
            }
          })
          console.log(`  → Source already collapsed. Added ${uniqueCount} unique nodes.`)
        } else {
          // Check for overlap
          let sharedCount = 0
          motifNodes.forEach(node => {
            if (newCollapsedNodes.has(node)) {
              sharedCount++
            }
          })

          // Collapse this motif
          newCollapsedMotifs.add(motifId)
          motifNodes.forEach(node => newCollapsedNodes.add(node))

          if (sharedCount === 0) {
            console.log(`  → Full collapse: ${mst.nodes.length} nodes`)
          } else {
            console.log(`  → Partial collapse: shared ${sharedCount} nodes`)
          }
        }
      })

      console.log(`Total collapsed: ${newCollapsedMotifs.size} motifs, ${newCollapsedNodes.size} nodes`)

      return {
        collapsedMotifs: newCollapsedMotifs,
        collapsedNodes: newCollapsedNodes
      }
    })
  }, [motifData])

  const expandMotif = useCallback((motifId) => {
    if (!motifData) return

    setState(prevState => {
      const newCollapsedMotifs = new Set(prevState.collapsedMotifs)
      const newCollapsedNodes = new Set(prevState.collapsedNodes)
      
      newCollapsedMotifs.delete(motifId)

      // Remove nodes from collapsed set (but keep if in other motifs)
      const mst = motifData[motifId.toString()]
      if (mst) {
        const nodesToRemove = new Set(mst.nodes)

        nodesToRemove.forEach(node => {
          let inOtherMotif = false
          for (const otherMotifId of newCollapsedMotifs) {
            const otherMst = motifData[otherMotifId.toString()]
            if (otherMst && otherMst.nodes.includes(node)) {
              inOtherMotif = true
              break
            }
          }
          if (!inOtherMotif) {
            newCollapsedNodes.delete(node)
          }
        })
      }

      return {
        collapsedMotifs: newCollapsedMotifs,
        collapsedNodes: newCollapsedNodes
      }
    })
  }, [motifData])

  const reset = useCallback(() => {
    setState({
      collapsedMotifs: new Set(),
      collapsedNodes: new Set()
    })
  }, [])

  return {
    collapsedMotifs: state.collapsedMotifs,
    collapsedNodes: state.collapsedNodes,
    collapseCluster,
    expandMotif,
    reset
  }
}
