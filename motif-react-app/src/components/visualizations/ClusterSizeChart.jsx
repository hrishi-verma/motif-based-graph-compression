export default function ClusterSizeChart({ distribution }) {
  const entries = Object.entries(distribution)
    .map(([size, count]) => ({ size: parseInt(size), count }))
    .sort((a, b) => a.size - b.size)
  
  const maxCount = Math.max(...entries.map(e => e.count))
  
  // Get color based on intensity (pink/red gradient)
  const getColor = (count) => {
    const intensity = count / maxCount
    if (intensity > 0.8) return '#c2185b' // Deep pink
    if (intensity > 0.6) return '#d81b60'
    if (intensity > 0.4) return '#ec407a'
    if (intensity > 0.2) return '#f06292'
    if (intensity > 0.1) return '#f48fb1'
    return '#f8bbd0' // Light pink
  }

  // Group into rows of 10
  const cellsPerRow = 10
  const rows = []
  for (let i = 0; i < entries.length; i += cellsPerRow) {
    rows.push(entries.slice(i, i + cellsPerRow))
  }

  return (
    <div style={{ width: '100%' }}>
      <div style={{ marginBottom: '1rem' }}>
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column',
          gap: '4px'
        }}>
          {rows.map((row, rowIdx) => (
            <div key={rowIdx} style={{ display: 'flex', gap: '4px' }}>
              {row.map(({ size, count }) => (
                <div
                  key={size}
                  style={{
                    flex: 1,
                    minWidth: '50px',
                    height: '60px',
                    background: getColor(count),
                    borderRadius: '4px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    border: '2px solid transparent'
                  }}
                  title={`Size ${size}: ${count} clusters`}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.1)'
                    e.currentTarget.style.border = '2px solid #fff'
                    e.currentTarget.style.zIndex = '10'
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)'
                    e.currentTarget.style.border = '2px solid transparent'
                    e.currentTarget.style.zIndex = '1'
                    e.currentTarget.style.boxShadow = 'none'
                  }}
                >
                  <div style={{ fontSize: '0.75rem', fontWeight: 'bold', opacity: 0.8 }}>
                    Size {size}
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>
                    {count}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        gap: '1rem',
        marginTop: '1.5rem',
        padding: '1rem',
        background: '#f5f5f5',
        borderRadius: '8px'
      }}>
        <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#666' }}>
          Frequency:
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', color: '#666' }}>Low</span>
          {['#f8bbd0', '#f48fb1', '#f06292', '#ec407a', '#d81b60', '#c2185b'].map((color, idx) => (
            <div
              key={idx}
              style={{
                width: '30px',
                height: '20px',
                background: color,
                borderRadius: '2px'
              }}
            />
          ))}
          <span style={{ fontSize: '0.75rem', color: '#666' }}>High</span>
        </div>
      </div>
    </div>
  )
}
