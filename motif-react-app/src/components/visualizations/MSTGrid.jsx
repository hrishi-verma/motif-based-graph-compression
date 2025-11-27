import { useState } from 'react'
import MiniMST from './MiniMST'
import MotifDetailModal from '../common/MotifDetailModal'

export default function MSTGrid({ motifs }) {
  const [selectedMotif, setSelectedMotif] = useState(null)

  if (!motifs || motifs.length === 0) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '3rem', 
        color: '#666',
        background: 'white',
        borderRadius: '8px'
      }}>
        <p>No motifs in this cluster</p>
      </div>
    )
  }

  return (
    <>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '1rem'
      }}>
        {motifs.map(motif => (
          <div
            key={motif.source_node}
            style={{
              background: 'white',
              borderRadius: '8px',
              padding: '1rem',
              border: '1px solid #e0e0e0',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onClick={() => setSelectedMotif(motif)}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)'
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div style={{ 
              fontWeight: 'bold', 
              marginBottom: '0.5rem',
              fontSize: '1.1rem'
            }}>
              Motif {motif.source_node}
            </div>

            <MiniMST motif={motif} width={180} height={150} />

            <div style={{ 
              marginTop: '0.75rem',
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
                  {(motif.mst?.total_weight || 0).toFixed(0)}
                </div>
              </div>
              <div>
                <div style={{ color: '#666' }}>Density</div>
                <div style={{ fontWeight: 'bold' }}>
                  {motif.density.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedMotif && (
        <MotifDetailModal
          motif={selectedMotif}
          onClose={() => setSelectedMotif(null)}
        />
      )}
    </>
  )
}
