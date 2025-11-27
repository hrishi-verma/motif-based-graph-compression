import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export default function D3ForceGraph({ 
  graphData, 
  motifData, 
  collapsedMotifs, 
  collapsedNodes,
  onNodeClick,
  width = 1000,
  height = 700
}) {
  const svgRef = useRef()
  const nodePositionsRef = useRef(new Map())

  useEffect(() => {
    if (!graphData || !motifData) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const g = svg.append('g')

    // Add zoom
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })
    svg.call(zoom)

    // Filter nodes based on collapsed state
    const visibleNodes = new Set()
    const nodeData = []
    
    // First pass: identify which nodes belong to which collapsed motif
    const nodeToCollapsedMotif = new Map()
    for (const motifId of collapsedMotifs) {
      const mst = motifData[motifId.toString()]
      if (mst) {
        mst.nodes.forEach(nodeId => {
          nodeToCollapsedMotif.set(nodeId, { motifId, sourceNode: mst.source_node })
        })
      }
    }

    graphData.nodes.forEach(node => {
      const nodeId = node.id
      const collapsedInfo = nodeToCollapsedMotif.get(nodeId)
      
      if (collapsedInfo) {
        // Node is part of a collapsed motif
        if (nodeId === collapsedInfo.sourceNode) {
          // This is the source node - show it as collapsed
          visibleNodes.add(nodeId)
          const nodeObj = {
            id: nodeId,
            type: 'collapsed',
            motifId: collapsedInfo.motifId,
            motifSize: motifData[collapsedInfo.motifId.toString()].nodes.length
          }
          
          // Restore previous position if available
          const prevPos = nodePositionsRef.current.get(nodeId)
          if (prevPos) {
            nodeObj.x = prevPos.x
            nodeObj.y = prevPos.y
            nodeObj.vx = 0
            nodeObj.vy = 0
          }
          
          nodeData.push(nodeObj)
        }
        // Other nodes in collapsed motif are hidden
      } else {
        // Regular visible node
        visibleNodes.add(nodeId)
        const nodeObj = { id: nodeId, type: 'regular' }
        
        // Restore previous position if available
        const prevPos = nodePositionsRef.current.get(nodeId)
        if (prevPos) {
          nodeObj.x = prevPos.x
          nodeObj.y = prevPos.y
          nodeObj.vx = 0
          nodeObj.vy = 0
        } else {
          // Check if this node was part of a recently expanded motif
          // If so, position it near the source node
          for (const [sourceNodeId, pos] of nodePositionsRef.current.entries()) {
            const mst = Object.values(motifData).find(m => 
              m.source_node === sourceNodeId && m.nodes.includes(nodeId)
            )
            if (mst) {
              // Position near the source node with some random offset
              const angle = Math.random() * 2 * Math.PI
              const distance = 30 + Math.random() * 20
              nodeObj.x = pos.x + Math.cos(angle) * distance
              nodeObj.y = pos.y + Math.sin(angle) * distance
              nodeObj.vx = 0
              nodeObj.vy = 0
              break
            }
          }
        }
        
        nodeData.push(nodeObj)
      }
    })

    // Process links
    const linkData = []
    const processedLinks = new Set()

    graphData.links.forEach(link => {
      let sourceId = link.source.id || link.source
      let targetId = link.target.id || link.target

      // Redirect to source nodes if collapsed
      for (const motifId of collapsedMotifs) {
        const mst = motifData[motifId.toString()]
        if (mst) {
          if (mst.nodes.includes(sourceId) && sourceId !== mst.source_node) {
            sourceId = mst.source_node
          }
          if (mst.nodes.includes(targetId) && targetId !== mst.source_node) {
            targetId = mst.source_node
          }
        }
      }

      // Skip self-loops
      if (sourceId === targetId) return

      // Skip if nodes not visible
      if (!visibleNodes.has(sourceId) || !visibleNodes.has(targetId)) return

      // Avoid duplicates
      const linkKey = sourceId < targetId ? `${sourceId}-${targetId}` : `${targetId}-${sourceId}`
      if (!processedLinks.has(linkKey)) {
        processedLinks.add(linkKey)
        linkData.push({ source: sourceId, target: targetId, weight: link.weight })
      }
    })

    // Determine if this is a minor update (just expanding/collapsing)
    const hasPositions = nodeData.every(d => d.x !== undefined && d.y !== undefined)
    
    // Create simulation with gentler forces
    const simulation = d3.forceSimulation(nodeData)
      .force('link', d3.forceLink(linkData).id(d => d.id).distance(50))
      .force('charge', d3.forceManyBody().strength(-50))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => d.type === 'collapsed' ? 15 : 5))
      .alpha(hasPositions ? 0.1 : 0.3)  // Very low energy if positions exist
      .alphaDecay(0.05)  // Faster decay for quicker settling

    // Draw links
    const link = g.selectAll('line')
      .data(linkData)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.3)
      .attr('stroke-width', 0.5)

    // Draw nodes
    const node = g.selectAll('circle')
      .data(nodeData)
      .enter().append('circle')
      .attr('r', d => d.type === 'collapsed' ? 12 : 3)
      .attr('fill', d => d.type === 'collapsed' ? '#f4b400' : '#4285f4')
      .attr('stroke', d => d.type === 'collapsed' ? '#e37400' : 'white')
      .attr('stroke-width', d => d.type === 'collapsed' ? 3 : 2)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        if (onNodeClick) {
          onNodeClick(d)
        }
      })
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))

    // Add tooltips
    node.append('title')
      .text(d => {
        if (d.type === 'collapsed') {
          return `Collapsed Motif ${d.motifId}\n${d.motifSize} nodes\nClick to expand`
        }
        return `Node ${d.id}`
      })

    // Labels for ALL nodes
    const label = g.selectAll('text')
      .data(nodeData)
      .enter().append('text')
      .text(d => d.type === 'collapsed' ? `M${d.motifId}` : d.id)
      .attr('font-size', d => d.type === 'collapsed' ? '11px' : '8px')
      .attr('font-weight', d => d.type === 'collapsed' ? 'bold' : 'normal')
      .attr('text-anchor', 'middle')
      .attr('dy', d => d.type === 'collapsed' ? 22 : 15)
      .attr('fill', d => d.type === 'collapsed' ? '#e37400' : '#333')
      .style('pointer-events', 'none')
      .style('user-select', 'none')

    let tickCount = 0
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y)
      
      // Save positions periodically
      tickCount++
      if (tickCount % 10 === 0) {
        nodeData.forEach(d => {
          nodePositionsRef.current.set(d.id, { x: d.x, y: d.y })
        })
      }
    })

    // Save node positions when simulation ends
    simulation.on('end', () => {
      nodeData.forEach(d => {
        nodePositionsRef.current.set(d.id, { x: d.x, y: d.y })
      })
    })

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event, d) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }

    return () => {
      simulation.stop()
    }
  }, [graphData, motifData, collapsedMotifs, collapsedNodes, onNodeClick, width, height])

  return (
    <svg 
      ref={svgRef} 
      width={width} 
      height={height}
      style={{ 
        background: '#fafafa', 
        borderRadius: '8px',
        border: '1px solid #e0e0e0'
      }}
    />
  )
}
