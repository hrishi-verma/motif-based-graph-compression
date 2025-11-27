export default function ClusterStatsCard({ stats, clusterId }) {
  const getCohesionColor = (cohesion) => {
    if (cohesion === 'High') return '#4caf50'
    if (cohesion === 'Moderate') return '#ff9800'
    return '#f44336'
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '8px',
      padding: '1.5rem',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '1.5rem'
      }}>
        <h3 style={{ margin: 0 }}>Cluster {clusterId} Statistics</h3>
        <div style={{
          padding: '0.5rem 1rem',
          borderRadius: '20px',
          background: getCohesionColor(stats.cohesion),
          color: 'white',
          fontWeight: 'bold',
          fontSize: '0.9rem'
        }}>
          {stats.cohesion} Cohesion
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '1rem'
      }}>
        <StatBox label="Size" value={stats.size} subtitle={`${stats.percentage.toFixed(1)}% of total`} />
        <StatBox label="Avg Nodes" value={stats.avgNodes} subtitle={`Range: ${stats.nodeRange}`} />
        <StatBox label="Avg Edges" value={stats.avgEdges} />
        <StatBox label="Avg Weight" value={stats.avgWeight} subtitle={`Range: ${stats.weightRange}`} />
        <StatBox label="Node Std Dev" value={stats.stdNodes} subtitle={`CV: ${stats.cvNodes}`} />
        <StatBox label="Weight Std Dev" value={stats.stdWeight} subtitle={`CV: ${stats.cvWeight}`} />
      </div>

      <div style={{ 
        marginTop: '1.5rem', 
        padding: '1rem', 
        background: '#f5f5f5',
        borderRadius: '6px'
      }}>
        <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>
          <strong>Cohesion Assessment:</strong>
        </div>
        <div style={{ fontSize: '0.9rem' }}>
          {stats.cohesion === 'High' && (
            <span>✓ Highly cohesive cluster with very similar MST structures (CV: {stats.cvWeight})</span>
          )}
          {stats.cohesion === 'Moderate' && (
            <span>~ Moderately cohesive cluster with some variation in structures (CV: {stats.cvWeight})</span>
          )}
          {stats.cohesion === 'Low' && (
            <span>✗ Low cohesion cluster with high variation in structures (CV: {stats.cvWeight})</span>
          )}
        </div>
      </div>
    </div>
  )
}

function StatBox({ label, value, subtitle }) {
  return (
    <div style={{
      padding: '1rem',
      background: '#fafafa',
      borderRadius: '6px',
      border: '1px solid #e0e0e0'
    }}>
      <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.5rem' }}>
        {label}
      </div>
      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#333', marginBottom: '0.25rem' }}>
        {value}
      </div>
      {subtitle && (
        <div style={{ fontSize: '0.75rem', color: '#999' }}>
          {subtitle}
        </div>
      )}
    </div>
  )
}
