import { useMemo } from 'react'
import { useGraphData } from '../hooks/useGraphData'
import { useMotifData } from '../hooks/useMotifData'
import { useHopStore } from '../hooks/useHopStore'
import LoadingSpinner from '../components/common/LoadingSpinner'
import StatCard from '../components/common/StatCard'
import MotifSizeChart from '../components/visualizations/MotifSizeChart'
import ClusterSizeChart from '../components/visualizations/ClusterSizeChart'

export default function Statistics() {
  const { hopDistance } = useHopStore()
  const { data: graphData, loading: graphLoading } = useGraphData()
  const { data: motifData, loading: motifLoading } = useMotifData(hopDistance)

  const stats = useMemo(() => {
    if (!graphData || !motifData) return null

    // Graph statistics
    const totalNodes = graphData.nodes.length
    const totalEdges = graphData.links.length
    const avgDegree = (2 * totalEdges / totalNodes).toFixed(2)
    const density = (2 * totalEdges / (totalNodes * (totalNodes - 1))).toFixed(4)

    // Motif statistics
    const motifs = motifData.motifs
    const totalMotifs = motifs.length
    const motifSizes = motifs.map(m => m.mst.nodes.length)
    const avgMotifSize = (motifSizes.reduce((a, b) => a + b, 0) / totalMotifs).toFixed(2)
    const minMotifSize = Math.min(...motifSizes)
    const maxMotifSize = Math.max(...motifSizes)
    
    // Motif size distribution
    const sizeDistribution = {}
    motifSizes.forEach(size => {
      sizeDistribution[size] = (sizeDistribution[size] || 0) + 1
    })

    // Cluster statistics
    const clusters = Object.values(motifData.clusters)
    const totalClusters = clusters.length
    const clusterSizes = clusters.map(c => c.size)
    const avgClusterSize = (clusterSizes.reduce((a, b) => a + b, 0) / totalClusters).toFixed(2)
    const minClusterSize = Math.min(...clusterSizes)
    const maxClusterSize = Math.max(...clusterSizes)

    // Cluster size distribution
    const clusterDistribution = {}
    clusterSizes.forEach(size => {
      clusterDistribution[size] = (clusterDistribution[size] || 0) + 1
    })

    // Coverage analysis
    const nodesInMotifs = new Set()
    motifs.forEach(m => {
      m.mst.nodes.forEach(node => nodesInMotifs.add(node))
    })
    const motifCoverage = ((nodesInMotifs.size / totalNodes) * 100).toFixed(1)

    // Compression potential
    const totalMotifNodes = motifSizes.reduce((a, b) => a + b, 0)
    const compressionRatio = ((1 - totalMotifs / totalMotifNodes) * 100).toFixed(1)

    return {
      graph: {
        totalNodes,
        totalEdges,
        avgDegree,
        density
      },
      motifs: {
        totalMotifs,
        avgMotifSize,
        minMotifSize,
        maxMotifSize,
        sizeDistribution,
        motifCoverage,
        compressionRatio
      },
      clusters: {
        totalClusters,
        avgClusterSize,
        minClusterSize,
        maxClusterSize,
        clusterDistribution
      }
    }
  }, [graphData, motifData])

  if (graphLoading || motifLoading) {
    return <LoadingSpinner message="Loading statistics..." />
  }

  if (!stats) return null

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ margin: '0 0 0.5rem 0' }}>Statistics Dashboard ({hopDistance}-hop)</h1>
        <p style={{ color: '#666', margin: 0 }}>
          Comprehensive analysis of {hopDistance}-hop motif structure and clusters
        </p>
      </div>

      {/* Graph Statistics */}
      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>Graph Statistics</h2>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem'
        }}>
          <StatCard 
            title="Total Nodes" 
            value={stats.graph.totalNodes}
            icon="🔵"
          />
          <StatCard 
            title="Total Edges" 
            value={stats.graph.totalEdges}
            icon="🔗"
          />
          <StatCard 
            title="Average Degree" 
            value={stats.graph.avgDegree}
            icon="📊"
          />
          <StatCard 
            title="Graph Density" 
            value={stats.graph.density}
            icon="🌐"
          />
        </div>
      </section>

      {/* Motif Statistics */}
      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>Motif Statistics</h2>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem',
          marginBottom: '1.5rem'
        }}>
          <StatCard 
            title="Total Motifs" 
            value={stats.motifs.totalMotifs}
            icon="🔶"
          />
          <StatCard 
            title="Average Size" 
            value={stats.motifs.avgMotifSize}
            subtitle="nodes per motif"
            icon="📏"
          />
          <StatCard 
            title="Size Range" 
            value={`${stats.motifs.minMotifSize} - ${stats.motifs.maxMotifSize}`}
            subtitle="min - max nodes"
            icon="📐"
          />
          <StatCard 
            title="Node Coverage" 
            value={`${stats.motifs.motifCoverage}%`}
            subtitle="nodes in motifs"
            icon="🎯"
            highlight
          />
        </div>
        
        <div style={{ 
          background: 'white', 
          padding: '1.5rem', 
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Motif Size Distribution</h3>
          <MotifSizeChart distribution={stats.motifs.sizeDistribution} />
        </div>
      </section>

      {/* Cluster Statistics */}
      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem' }}>Cluster Statistics</h2>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem',
          marginBottom: '1.5rem'
        }}>
          <StatCard 
            title="Total Clusters" 
            value={stats.clusters.totalClusters}
            icon="🗂️"
          />
          <StatCard 
            title="Average Size" 
            value={stats.clusters.avgClusterSize}
            subtitle="motifs per cluster"
            icon="📊"
          />
          <StatCard 
            title="Size Range" 
            value={`${stats.clusters.minClusterSize} - ${stats.clusters.maxClusterSize}`}
            subtitle="min - max motifs"
            icon="📏"
          />
          <StatCard 
            title="Compression Potential" 
            value={`${stats.motifs.compressionRatio}%`}
            subtitle="node reduction"
            icon="🗜️"
            highlight
          />
        </div>

        <div style={{ 
          background: 'white', 
          padding: '1.5rem', 
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Cluster Size Distribution</h3>
          <ClusterSizeChart distribution={stats.clusters.clusterDistribution} />
        </div>
      </section>

      {/* Summary */}
      <section style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '2rem',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ margin: '0 0 1rem 0', fontSize: '1.5rem' }}>Summary</h2>
        <div style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
          <p style={{ margin: '0 0 0.5rem 0' }}>
            📊 The graph contains <strong>{stats.graph.totalNodes} nodes</strong> and <strong>{stats.graph.totalEdges} edges</strong>
          </p>
          <p style={{ margin: '0 0 0.5rem 0' }}>
            🔶 Identified <strong>{stats.motifs.totalMotifs} motifs</strong> covering <strong>{stats.motifs.motifCoverage}%</strong> of nodes
          </p>
          <p style={{ margin: '0 0 0.5rem 0' }}>
            🗂️ Organized into <strong>{stats.clusters.totalClusters} clusters</strong> with average size of <strong>{stats.clusters.avgClusterSize} motifs</strong>
          </p>
          <p style={{ margin: '0' }}>
            🗜️ Compression potential: <strong>{stats.motifs.compressionRatio}%</strong> reduction in representation
          </p>
        </div>
      </section>
    </div>
  )
}
