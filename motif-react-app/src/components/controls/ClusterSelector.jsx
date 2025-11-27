export default function ClusterSelector({ 
  clusters, 
  selectedCluster, 
  onSelect,
  comparisonClusters = [],
  onToggleComparison 
}) {
  const sortedClusters = Object.keys(clusters).sort((a, b) => {
    return parseInt(a.split('_')[1]) - parseInt(b.split('_')[1])
  })

  return (
    <div style={{
      background: 'white',
      borderRadius: '8px',
      padding: '1rem',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      position: 'sticky',
      top: '1rem'
    }}>
      <h3 style={{ marginBottom: '1rem' }}>Select Cluster</h3>
      
      <div style={{ 
        maxHeight: '70vh', 
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        {sortedClusters.map(clusterKey => {
          const clusterNum = parseInt(clusterKey.split('_')[1])
          const cluster = clusters[clusterKey]
          const isSelected = selectedCluster === clusterNum
          const isInComparison = comparisonClusters.includes(clusterNum)

          return (
            <div
              key={clusterKey}
              style={{
                padding: '0.75rem',
                borderRadius: '6px',
                border: isSelected ? '2px solid #4285f4' : '1px solid #e0e0e0',
                background: isSelected ? '#e3f2fd' : 'white',
                cursor: 'pointer',
                transition: 'all 0.2s',
                position: 'relative'
              }}
              onClick={() => onSelect(clusterNum)}
              onMouseEnter={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.background = '#f5f5f5'
                }
              }}
              onMouseLeave={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.background = 'white'
                }
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                    Cluster {clusterNum}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#666' }}>
                    {cluster.size} motifs ({cluster.percentage.toFixed(1)}%)
                  </div>
                </div>
                
                {onToggleComparison && (
                  <input
                    type="checkbox"
                    checked={isInComparison}
                    onChange={(e) => {
                      e.stopPropagation()
                      onToggleComparison(clusterNum)
                    }}
                    style={{ cursor: 'pointer' }}
                  />
                )}
              </div>
            </div>
          )
        })}
      </div>

      {comparisonClusters.length > 0 && (
        <div style={{ 
          marginTop: '1rem', 
          padding: '0.75rem', 
          background: '#e3f2fd',
          borderRadius: '6px'
        }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
            Selected for Comparison:
          </div>
          <div style={{ fontSize: '0.85rem' }}>
            {comparisonClusters.join(', ')}
          </div>
        </div>
      )}
    </div>
  )
}
