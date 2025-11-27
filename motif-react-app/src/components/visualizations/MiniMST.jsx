import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export default function MiniMST({ motif, width = 150, height = 150 }) {
  const svgRef = useRef()

  useEffect(() => {
    if (!motif || !motif.mst) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const mst = motif.mst
    const nodes = mst.nodes.map(id => ({ id }))
    const links = mst.mst_edges.map(edge => ({
      source: edge.from,
      target: edge.to,
      weight: edge.weight
    }))

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(20))
      .force('charge', d3.forceManyBody().strength(-30))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(5))
      .stop()

    // Run simulation
    for (let i = 0; i < 100; i++) simulation.tick()

    // Draw links
    svg.selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)
      .attr('stroke', '#999')
      .attr('stroke-width', 0.5)

    // Draw nodes
    svg.selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', d => d.id === mst.source_node ? 3 : 2)
      .attr('fill', d => d.id === mst.source_node ? '#f44336' : '#4285f4')

  }, [motif, width, height])

  return (
    <svg 
      ref={svgRef} 
      width={width} 
      height={height}
      style={{ background: '#fafafa', borderRadius: '4px' }}
    />
  )
}
