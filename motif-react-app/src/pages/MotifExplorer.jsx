import { useState, useMemo } from 'react'
import { useMotifData } from '../hooks/useMotifData'
import LoadingSpinner from '../components/common/LoadingSpinner'
import MotifCard from '../components/common/MotifCard'
import MotifFilters from '../components/common/MotifFilters'
import MotifDetailModal from '../components/common/MotifDetailModal'

export default function MotifExplorer() {
  const { data, loading, error } = useMotifData()
  const [filters, setFilters] = useState({
    searchQuery: '',
    cluster: null,
    sizeRange: [2, 157],
    sortBy: 'id'
  })
  const [selectedMotif, setSelectedMotif] = useState(null)
  const [selectedForComparison, setSelectedForComparison] = useState([])

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleClearFilters = () => {
    setFilters({
      searchQuery: '',
      cluster: null,
      sizeRange: [2, 157],
      sortBy: 'id'
    })
  }

  const filteredMotifs = useMemo(() => {
    if (!data) return []

    let filtered = data.motifs

    // Search filter
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase()
      filtered = filtered.filter(m => 
        m.source_node.toString().includes(query) ||
        m.motif_id.toLowerCase().includes(query)
      )
    }

    // Cluster filter
    if (filters.cluster !== null) {
      filtered = filtered.filter(m => m.cluster === filters.cluster)
    }

    // Size range filter
    filtered = filtered.filter(m => 
      m.num_neighbors >= filters.sizeRange[0] && 
      m.num_neighbors <= filters.sizeRange[1]
    )

    // Sort
    filtered.sort((a, b) => {
      switch (filters.sortBy) {
        case 'id':
          return a.source_node - b.source_node
        case 'size':
          return b.num_neighbors - a.num_neighbors
        case 'weight':
          return (b.mst?.total_weight || 0) - (a.mst?.total_weight || 0)
        case 'cluster':
          return a.cluster - b.cluster
        case 'density':
          return b.density - a.density
        default:
          return 0
      }
    })

    return filtered
  }, [data, filters])

  if (loading) return <LoadingSpinner message="Loading motifs..." />
  if (error) return <div className="page"><p style={{ color: 'red' }}>Error: {error}</p></div>

  return (
    <div className="page">
      <div className="page-header">
        <h2>Motif Explorer</h2>
        <p>Browse and explore all 486 motifs</p>
      </div>

      <MotifFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onClear={handleClearFilters}
        clusters={data.clusters}
      />

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem',
        padding: '1rem',
        background: 'white',
        borderRadius: '8px'
      }}>
        <div>
          <strong>Showing {filteredMotifs.length}</strong> of {data.motifs.length} motifs
        </div>
        {selectedForComparison.length > 0 && (
          <button>
            Compare Selected ({selectedForComparison.length})
          </button>
        )}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '1rem'
      }}>
        {filteredMotifs.map(motif => (
          <MotifCard
            key={motif.source_node}
            motif={motif}
            onSelect={setSelectedMotif}
            isSelected={selectedForComparison.includes(motif.source_node)}
          />
        ))}
      </div>

      {filteredMotifs.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '3rem',
          color: '#666'
        }}>
          <p style={{ fontSize: '1.2rem' }}>No motifs found matching your filters</p>
          <button onClick={handleClearFilters} style={{ marginTop: '1rem' }}>
            Clear Filters
          </button>
        </div>
      )}

      {selectedMotif && (
        <MotifDetailModal
          motif={selectedMotif}
          onClose={() => setSelectedMotif(null)}
        />
      )}
    </div>
  )
}
