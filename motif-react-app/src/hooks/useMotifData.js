import { useState, useEffect } from 'react'

export function useMotifData(hopDistance = 1) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const basePath = import.meta.env.BASE_URL

    // Determine which data files to load based on hop distance
    const motifsFile = hopDistance === 1
      ? `${basePath}data/facebook_motifs.json`
      : `${basePath}data/facebook_motifs_${hopDistance}hop.json`

    const mstsFile = hopDistance === 1
      ? `${basePath}data/facebook_msts.json`
      : `${basePath}data/facebook_msts_${hopDistance}hop.json`

    // For clustering, we use the 1-hop clusters for now (can be regenerated later)
    const clustersFile = `${basePath}data/agglomerative_50_cluster_groups.json`

    Promise.all([
      fetch(motifsFile).then(r => {
        if (!r.ok) throw new Error(`Failed to load ${motifsFile}`)
        return r.json()
      }),
      fetch(mstsFile).then(r => {
        // MST file might not exist for multi-hop yet - that's OK
        if (r.ok) return r.json()
        console.warn(`MST file not found: ${mstsFile}, will use motif edges instead`)
        return {}
      }).catch(() => {
        // If fetch fails entirely, return empty object
        return {}
      }),
      fetch(clustersFile).then(r => {
        if (!r.ok) throw new Error(`Failed to load ${clustersFile}`)
        return r.json()
      })
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
          clusters: clusters,
          hopDistance: hopDistance
        })
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [hopDistance])

  return { data, loading, error }
}
