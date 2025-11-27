export default function StatCard({ title, value, subtitle, icon, highlight }) {
  return (
    <div style={{
      background: highlight ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'white',
      color: highlight ? 'white' : '#333',
      padding: '1.5rem',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      transition: 'transform 0.2s, box-shadow 0.2s',
      cursor: 'default'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-2px)'
      e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)'
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)'
      e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '1.5rem' }}>{icon}</span>
        <span style={{ 
          fontSize: '0.875rem', 
          fontWeight: '500',
          opacity: highlight ? 0.9 : 0.7,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {title}
        </span>
      </div>
      <div style={{ 
        fontSize: '2rem', 
        fontWeight: 'bold',
        marginBottom: subtitle ? '0.25rem' : 0
      }}>
        {value}
      </div>
      {subtitle && (
        <div style={{ 
          fontSize: '0.875rem',
          opacity: highlight ? 0.8 : 0.6
        }}>
          {subtitle}
        </div>
      )}
    </div>
  )
}
