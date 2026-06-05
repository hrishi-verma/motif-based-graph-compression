import { useState, useMemo } from 'react'
import { useGraphData } from '../hooks/useGraphData'
import { useMotifData } from '../hooks/useMotifData'
import { useCollapse } from '../hooks/useCollapse'
import { useHopStore } from '../hooks/useHopStore'
import LoadingSpinner from '../components/common/LoadingSpinner'
import D3ForceGraph from '../components/visualizations/D3ForceGraph'

export default function GraphCollapse() {
  const { hopDistance } = useHopStore()
  const { data: graphData, loading: graphLoading } = useGraphData()
  const { data: motifData, loading: motifLoading } = useMotifData(hopDistance)
  const [selectedCluster, setSelectedCluster] = useState(null)

  // Convert motif data to MST lookup
  const mstData = useMemo(() => {
    if (!motifData) return null
    const lookup = {}
    motifData.motifs.forEach(motif => {
      if (motif.mst) {
        lookup[motif.source_node] = motif.mst
      }
    })
    return lookup
  }, [motifData])

  const { collapsedMotifs, motifOwnership, collapsedNodes, collapseCluster, expandMotif, reset } = useCollapse(mstData)

  const handleCollapseSelected = () => {
    if (selectedCluster === null || !motifData) return

    const clusterKey = `cluster_${selectedCluster}`
    const cluster = motifData.clusters[clusterKey]
    if (cluster) {
      collapseCluster(cluster.motifs)
    }
  }

  const handleNodeClick = (node) => {
    if (node.type === 'collapsed') {
      expandMotif(node.motifId)
    }
  }

  const stats = useMemo(() => {
    if (!graphData) return null

    const totalNodes = graphData.nodes.length
    const ownedNodes = motifOwnership.size
    const sourceNodes = collapsedMotifs.size  // Each collapsed motif has 1 visible source
    const hiddenNodes = ownedNodes - sourceNodes
    const visibleNodes = totalNodes - hiddenNodes
    const compressionRatio = ((hiddenNodes / totalNodes) * 100).toFixed(1)

    return {
      totalNodes,
      visibleNodes,
      hiddenNodes,
      collapsedStructures: collapsedMotifs.size,
      compressionRatio
    }
  }, [graphData, collapsedMotifs, motifOwnership])

  if (graphLoading || motifLoading) {
    return <LoadingSpinner message="Loading graph data..." />
  }

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 100px)', gap: '1rem' }}>
      {/* Sidebar */}
      <div style={{ 
        width: '320px', 
        background: 'white', 
        borderRadius: '8px',
        padding: '1.5rem',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        <div>
          <h2 style={{ margin: '0 0 0.5rem 0' }}>Graph Collapse ({hopDistance}-hop)</h2>
          <p style={{ color: '#666', fontSize: '0.9rem', margin: 0 }}>
            Intelligent motif collapsing with {hopDistance}-hop neighborhoods
          </p>
        </div>

        {/* Cluster Selector */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            Select Cluster
          </label>
          <select
            value={selectedCluster === null ? '' : selectedCluster}
            onChange={(e) => setSelectedCluster(e.target.value ? parseInt(e.target.value) : null)}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
          >
            <option value="">-- Select a cluster --</option>
            {motifData && Array.from({ length: 50 }, (_, i) => {
              const clusterKey = `cluster_${i}`
              const cluster = motifData.clusters[clusterKey]
              return (
                <option key={i} value={i}>
                  Cluster {i} ({cluster?.size || 0} motifs)
                </option>
              )
            })}
          </select>
        </div>

        {/* Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <button 
            onClick={handleCollapseSelected}
            disabled={selectedCluster === null}
            style={{ width: '100%' }}
          >
            Collapse Selected Cluster
          </button>
          <button 
            onClick={reset}
            className="secondary"
            style={{ width: '100%' }}
          >
            Reset Graph
          </button>
        </div>

        {/* Statistics */}
        {stats && (
          <div style={{
            background: '#f5f5f5',
            padding: '1rem',
            borderRadius: '8px'
          }}>
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem' }}>Statistics</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <StatRow label="Total Nodes" value={stats.totalNodes} />
              <StatRow label="Visible Nodes" value={stats.visibleNodes} />
              <StatRow label="Hidden Nodes" value={stats.hiddenNodes} />
              <StatRow label="Collapsed Structures" value={stats.collapsedStructures} />
              <StatRow 
                label="Compression Ratio" 
                value={`${stats.compressionRatio}%`}
                highlight
              />
            </div>
          </div>
        )}

        {/* Legend */}
        <div style={{
          background: '#e3f2fd',
          padding: '1rem',
          borderRadius: '8px',
          fontSize: '0.85rem'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>Legend</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ 
                width: '12px', 
                height: '12px', 
                borderRadius: '50%', 
                background: '#4285f4' 
              }} />
              <span>Regular Node</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ 
                width: '16px', 
                height: '16px', 
                borderRadius: '50%', 
                background: '#f4b400',
                border: '2px solid #e37400'
              }} />
              <span>Collapsed Motif (click to expand)</span>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div style={{ fontSize: '0.85rem', color: '#666' }}>
          <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>💡 How to use:</div>
          <ol style={{ margin: 0, paddingLeft: '1.5rem', lineHeight: '1.6' }}>
            <li>Select a cluster from dropdown</li>
            <li>Click "Collapse Selected Cluster"</li>
            <li>Click yellow nodes to expand</li>
            <li>Drag nodes to rearrange</li>
            <li>Scroll to zoom</li>
          </ol>
        </div>
      </div>

      {/* Main Graph */}
      <div style={{ 
        flex: 1, 
        background: 'white',
        borderRadius: '8px',
        padding: '1rem',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {graphData && mstData ? (
          <D3ForceGraph
            graphData={graphData}
            motifData={mstData}
            collapsedMotifs={collapsedMotifs}
            motifOwnership={motifOwnership}
            collapsedNodes={collapsedNodes}
            onNodeClick={handleNodeClick}
            width={1000}
            height={700}
          />
        ) : (
          <div style={{ color: '#666' }}>Loading graph...</div>
        )}
      </div>
    </div>
  )
}

function StatRow({ label, value, highlight }) {
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'space-between',
      padding: '0.5rem',
      background: highlight ? '#e3f2fd' : 'white',
      borderRadius: '4px'
    }}>
      <span style={{ color: '#666' }}>{label}</span>
      <span style={{ 
        fontWeight: 'bold',
        color: highlight ? '#1565c0' : '#333'
      }}>
        {value}
      </span>
    </div>
  )
}
