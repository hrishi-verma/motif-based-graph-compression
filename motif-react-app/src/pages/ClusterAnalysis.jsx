import { useState, useMemo } from 'react'
import { useMotifData } from '../hooks/useMotifData'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ClusterSelector from '../components/controls/ClusterSelector'
import ClusterStatsCard from '../components/common/ClusterStatsCard'
import MSTGrid from '../components/visualizations/MSTGrid'

export default function ClusterAnalysis() {
  const { data, loading, error } = useMotifData()
  const [selectedCluster, setSelectedCluster] = useState(0)
  const [comparisonClusters, setComparisonClusters] = useState([])

  const clusterStats = useMemo(() => {
    if (!data || selectedCluster === null) return null

    const clusterKey = `cluster_${selectedCluster}`
    const cluster = data.clusters[clusterKey]
    if (!cluster) return null

    // Get motifs in this cluster
    const clusterMotifs = data.motifs.filter(m => m.cluster === selectedCluster)

    // Calculate statistics
    const nodeCounts = clusterMotifs.map(m => m.num_neighbors)
    const edgeCounts = clusterMotifs.map(m => m.num_edges)
    const weights = clusterMotifs.map(m => m.mst?.total_weight || 0)

    const avgNodes = nodeCounts.reduce((a, b) => a + b, 0) / nodeCounts.length
    const avgEdges = edgeCounts.reduce((a, b) => a + b, 0) / edgeCounts.length
    const avgWeight = weights.reduce((a, b) => a + b, 0) / weights.length

    // Calculate standard deviation
    const stdNodes = Math.sqrt(nodeCounts.reduce((sum, val) => sum + Math.pow(val - avgNodes, 2), 0) / nodeCounts.length)
    const stdWeight = Math.sqrt(weights.reduce((sum, val) => sum + Math.pow(val - avgWeight, 2), 0) / weights.length)

    // Coefficient of variation
    const cvNodes = avgNodes > 0 ? stdNodes / avgNodes : 0
    const cvWeight = avgWeight > 0 ? stdWeight / avgWeight : 0

    return {
      cluster,
      clusterMotifs,
      size: cluster.size,
      percentage: cluster.percentage,
      avgNodes: avgNodes.toFixed(1),
      avgEdges: avgEdges.toFixed(1),
      avgWeight: avgWeight.toFixed(1),
      stdNodes: stdNodes.toFixed(1),
      stdWeight: stdWeight.toFixed(1),
      cvNodes: cvNodes.toFixed(3),
      cvWeight: cvWeight.toFixed(3),
      nodeRange: `${Math.min(...nodeCounts)} - ${Math.max(...nodeCounts)}`,
      weightRange: `${Math.min(...weights).toFixed(0)} - ${Math.max(...weights).toFixed(0)}`,
      cohesion: cvWeight < 0.3 ? 'High' : cvWeight < 0.5 ? 'Moderate' : 'Low'
    }
  }, [data, selectedCluster])

  const toggleComparison = (clusterId) => {
    setComparisonClusters(prev => {
      if (prev.includes(clusterId)) {
        return prev.filter(id => id !== clusterId)
      } else if (prev.length < 4) {
        return [...prev, clusterId]
      }
      return prev
    })
  }

  if (loading) return <LoadingSpinner message="Loading cluster data..." />
  if (error) return <div className="page"><p style={{ color: 'red' }}>Error: {error}</p></div>

  return (
    <div className="page">
      <div className="page-header">
        <h2>Cluster Analysis</h2>
        <p>Explore and compare the 50 clusters</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '1.5rem' }}>
        {/* Sidebar */}
        <div>
          <ClusterSelector
            clusters={data.clusters}
            selectedCluster={selectedCluster}
            onSelect={setSelectedCluster}
            comparisonClusters={comparisonClusters}
            onToggleComparison={toggleComparison}
          />
        </div>

        {/* Main Content */}
        <div>
          {clusterStats && (
            <>
              <ClusterStatsCard stats={clusterStats} clusterId={selectedCluster} />
              
              <div style={{ marginTop: '1.5rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>
                  Motifs in Cluster {selectedCluster} ({clusterStats.size} motifs)
                </h3>
                <MSTGrid motifs={clusterStats.clusterMotifs} />
              </div>
            </>
          )}

          {comparisonClusters.length > 0 && (
            <div style={{ marginTop: '2rem' }}>
              <h3>Cluster Comparison</h3>
              <p style={{ color: '#666' }}>
                Comparing {comparisonClusters.length} clusters - Coming soon
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
