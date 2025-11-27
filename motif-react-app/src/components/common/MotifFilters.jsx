export default function MotifFilters({ filters, onFilterChange, onClear, clusters }) {
  return (
    <div style={{
      background: 'white',
      padding: '1.5rem',
      borderRadius: '8px',
      marginBottom: '1.5rem',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1.5rem'
      }}>
        {/* Search */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            Search Motif ID
          </label>
          <input
            type="text"
            placeholder="Enter motif ID..."
            value={filters.searchQuery}
            onChange={(e) => onFilterChange('searchQuery', e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
          />
        </div>

        {/* Cluster Filter */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            Cluster
          </label>
          <select
            value={filters.cluster || ''}
            onChange={(e) => onFilterChange('cluster', e.target.value ? parseInt(e.target.value) : null)}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
          >
            <option value="">All Clusters</option>
            {Array.from({ length: 50 }, (_, i) => (
              <option key={i} value={i}>Cluster {i}</option>
            ))}
          </select>
        </div>

        {/* Sort */}
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            Sort By
          </label>
          <select
            value={filters.sortBy}
            onChange={(e) => onFilterChange('sortBy', e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
          >
            <option value="id">Motif ID</option>
            <option value="size">Size (Nodes)</option>
            <option value="weight">MST Weight</option>
            <option value="cluster">Cluster</option>
            <option value="density">Density</option>
          </select>
        </div>
      </div>

      {/* Size Range */}
      <div style={{ marginTop: '1.5rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
          Size Range: {filters.sizeRange[0]} - {filters.sizeRange[1]} nodes
        </label>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <input
            type="range"
            min="2"
            max="157"
            value={filters.sizeRange[0]}
            onChange={(e) => onFilterChange('sizeRange', [parseInt(e.target.value), filters.sizeRange[1]])}
            style={{ flex: 1 }}
          />
          <input
            type="range"
            min="2"
            max="157"
            value={filters.sizeRange[1]}
            onChange={(e) => onFilterChange('sizeRange', [filters.sizeRange[0], parseInt(e.target.value)])}
            style={{ flex: 1 }}
          />
        </div>
      </div>

      {/* Clear Button */}
      <div style={{ marginTop: '1rem', textAlign: 'right' }}>
        <button 
          onClick={onClear}
          className="secondary"
          style={{ padding: '0.5rem 1rem' }}
        >
          Clear Filters
        </button>
      </div>
    </div>
  )
}
