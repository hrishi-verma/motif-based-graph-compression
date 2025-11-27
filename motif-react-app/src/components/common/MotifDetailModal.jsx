import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export default function MotifDetailModal({ motif, onClose }) {
  const svgRef = useRef()

  useEffect(() => {
    if (!motif || !motif.mst) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 600
    const height = 500

    const g = svg.append('g')

    // Add zoom
    const zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })
    svg.call(zoom)

    const mst = motif.mst
    const nodes = mst.nodes.map(id => ({ id }))
    const links = mst.mst_edges.map(edge => ({
      source: edge.from,
      target: edge.to,
      weight: edge.weight
    }))

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(60))
      .force('charge', d3.forceManyBody().strength(-100))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(15))

    // Draw links
    const link = g.selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-width', d => Math.max(1, d.weight / 10))

    // Draw nodes
    const node = g.selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('r', d => d.id === mst.source_node ? 8 : 5)
      .attr('fill', d => d.id === mst.source_node ? '#f44336' : '#4285f4')
      .attr('stroke', 'white')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))

    // Add labels
    const label = g.selectAll('text')
      .data(nodes)
      .enter().append('text')
      .text(d => d.id)
      .attr('font-size', '10px')
      .attr('text-anchor', 'middle')
      .attr('dy', -12)

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
  }, [motif])

  if (!motif) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '2rem'
    }} onClick={onClose}>
      <div style={{
        background: 'white',
        borderRadius: '12px',
        maxWidth: '900px',
        width: '100%',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
      }} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{
          padding: '1.5rem',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h2 style={{ margin: 0 }}>Motif {motif.source_node}</h2>
          <button onClick={onClose} style={{
            background: 'none',
            border: 'none',
            fontSize: '1.5rem',
            cursor: 'pointer',
            padding: '0.5rem'
          }}>×</button>
        </div>

        {/* Content */}
        <div style={{ display: 'flex', gap: '2rem', padding: '1.5rem' }}>
          {/* Visualization */}
          <div style={{ flex: 1 }}>
            <h3>Maximum Spanning Tree</h3>
            <svg 
              ref={svgRef} 
              width={600} 
              height={500}
              style={{ 
                background: '#fafafa', 
                borderRadius: '8px',
                border: '1px solid #e0e0e0'
              }}
            />
            <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
              💡 Drag nodes to rearrange • Scroll to zoom
            </p>
          </div>

          {/* Statistics */}
          <div style={{ width: '250px' }}>
            <h3>Statistics</h3>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '1rem' 
            }}>
              <StatItem label="Source Node" value={motif.source_node} />
              <StatItem label="Total Nodes" value={motif.num_neighbors} />
              <StatItem label="Total Edges" value={motif.num_edges} />
              <StatItem label="MST Edges" value={motif.mst?.num_mst_edges || 0} />
              <StatItem label="Excluded Edges" value={motif.mst?.num_excluded_edges || 0} />
              <StatItem label="MST Weight" value={(motif.mst?.total_weight || 0).toFixed(1)} />
              <StatItem label="Avg Edge Weight" value={motif.avgEdgeWeight.toFixed(2)} />
              <StatItem label="Density" value={motif.density.toFixed(2)} />
              <StatItem label="Cluster" value={`Cluster ${motif.cluster}`} highlight />
            </div>

            <div style={{ marginTop: '2rem' }}>
              <button style={{ width: '100%', marginBottom: '0.5rem' }}>
                Export JSON
              </button>
              <button className="secondary" style={{ width: '100%' }}>
                Export PNG
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatItem({ label, value, highlight }) {
  return (
    <div style={{
      padding: '0.75rem',
      background: highlight ? '#e3f2fd' : '#f5f5f5',
      borderRadius: '6px'
    }}>
      <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.25rem' }}>
        {label}
      </div>
      <div style={{ 
        fontSize: '1.1rem', 
        fontWeight: 'bold',
        color: highlight ? '#1565c0' : '#333'
      }}>
        {value}
      </div>
    </div>
  )
}
