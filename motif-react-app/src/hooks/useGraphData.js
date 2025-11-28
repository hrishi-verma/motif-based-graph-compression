import { useState, useEffect } from 'react'
import * as d3 from 'd3'

export function useGraphData() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const basePath = import.meta.env.BASE_URL
    fetch(`${basePath}facebook_weighted_filtered.csv`)
      .then(response => response.text())
      .then(csvText => {
        const parsed = d3.csvParse(csvText)
        
        // Build graph
        const nodes = new Set()
        const links = []
        
        parsed.forEach(row => {
          const source = parseInt(row.Node1)
          const target = parseInt(row.Node2)
          const weight = parseFloat(row.Weight)
          
          nodes.add(source)
          nodes.add(target)
          links.push({ source, target, weight })
        })
        
        setData({
          nodes: Array.from(nodes).map(id => ({ id, type: 'regular' })),
          links: links
        })
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  return { data, loading, error }
}
