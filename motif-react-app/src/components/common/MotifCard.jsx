import MiniMST from '../visualizations/MiniMST'

export default function MotifCard({ motif, onSelect, isSelected }) {
  const getSizeColor = (nodeCount) => {
    if (nodeCount <= 10) return '#4285f4'
    if (nodeCount <= 30) return '#34a853'
    if (nodeCount <= 50) return '#fbbc04'
    return '#ea4335'
  }

  const getSizeBadge = (nodeCount) => {
    if (nodeCount <= 10) return 'Small'
    if (nodeCount <= 30) return 'Medium'
    if (nodeCount <= 50) return 'Large'
    return 'Very Large'
  }

  return (
    <div 
      className="motif-card"
      onClick={() => onSelect(motif)}
      style={{
        background: 'white',
        borderRadius: '8px',
        padding: '1rem',
        cursor: 'pointer',
        border: isSelected ? '3px solid #4285f4' : '1px solid #e0e0e0',
        transition: 'all 0.2s',
        position: 'relative'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)'
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {isSelected && (
        <div style={{
          position: 'absolute',
          top: '8px',
          right: '8px',
          background: '#4285f4',
          color: 'white',
          borderRadius: '50%',
          width: '24px',
          height: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 'bold'
        }}>
          ✓
        </div>
      )}

      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '0.5rem'
      }}>
        <h3 style={{ fontSize: '1.1rem', margin: 0 }}>
          Motif {motif.source_node}
        </h3>
        <span style={{
          fontSize: '0.75rem',
          padding: '2px 8px',
          borderRadius: '12px',
          background: getSizeColor(motif.num_neighbors),
          color: 'white',
          fontWeight: 'bold'
        }}>
          {getSizeBadge(motif.num_neighbors)}
        </span>
      </div>

      <div style={{ marginBottom: '0.75rem' }}>
        <MiniMST motif={motif} />
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr',
        gap: '0.5rem',
        fontSize: '0.85rem'
      }}>
        <div>
          <div style={{ color: '#666' }}>Nodes</div>
          <div style={{ fontWeight: 'bold' }}>{motif.num_neighbors}</div>
        </div>
        <div>
          <div style={{ color: '#666' }}>Edges</div>
          <div style={{ fontWeight: 'bold' }}>{motif.num_edges}</div>
        </div>
        <div>
          <div style={{ color: '#666' }}>Weight</div>
          <div style={{ fontWeight: 'bold' }}>
            {motif.mst?.total_weight?.toFixed(0) || 0}
          </div>
        </div>
        <div>
          <div style={{ color: '#666' }}>Cluster</div>
          <div style={{ 
            fontWeight: 'bold',
            color: '#4285f4'
          }}>
            C{motif.cluster}
          </div>
        </div>
      </div>
    </div>
  )
}
