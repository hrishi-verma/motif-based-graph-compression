import { useState, useEffect } from 'react'

export function useMotifData() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      fetch('/data/facebook_motifs.json').then(r => r.json()),
      fetch('/data/facebook_msts.json').then(r => r.json()),
      fetch('/data/agglomerative_50_cluster_groups.json').then(r => r.json())
    ])
      .then(([motifs, msts, clusters]) => {
        // Build motif to cluster mapping
        const motifToCluster = {}
        Object.keys(clusters).forEach(clusterKey => {
          const clusterNum = parseInt(clusterKey.split('_')[1])
          clusters[clusterKey].motifs.forEach(motifId => {
            motifToCluster[motifId] = clusterNum
          })
        })

        // Combine data
        const enrichedMotifs = motifs.motifs.map(motif => {
          const mst = msts[motif.source_node.toString()]
          return {
            ...motif,
            mst: mst,
            cluster: motifToCluster[motif.source_node] || 0,
            density: motif.num_edges / Math.max(1, motif.num_neighbors),
            avgEdgeWeight: motif.num_edges > 0 ? (mst?.total_weight || 0) / motif.num_edges : 0
          }
        })

        setData({
          motifs: enrichedMotifs,
          statistics: motifs.statistics,
          clusters: clusters
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
