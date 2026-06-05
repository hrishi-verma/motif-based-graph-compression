import { useHopStore } from '../../hooks/useHopStore'

export default function HopSelector() {
  const { hopDistance, setHopDistance } = useHopStore()

  return (
    <div className="hop-selector" style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      marginLeft: '1rem',
      padding: '0.25rem 0.5rem',
      background: 'rgba(255,255,255,0.1)',
      borderRadius: '4px'
    }}>
      <span style={{ fontSize: '0.85rem', color: '#ccc' }}>Hop:</span>
      <select
        value={hopDistance}
        onChange={(e) => setHopDistance(parseInt(e.target.value))}
        style={{
          padding: '0.25rem 0.5rem',
          borderRadius: '4px',
          border: '1px solid rgba(255,255,255,0.2)',
          background: '#333',
          color: 'white',
          fontSize: '0.85rem',
          cursor: 'pointer'
        }}
      >
        <option value={1}>1-hop</option>
        <option value={2}>2-hop</option>
        <option value={3}>3-hop</option>
      </select>
    </div>
  )
}
