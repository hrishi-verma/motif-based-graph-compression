export default function DataPipeline() {
  const steps = [
    { name: 'Raw Graph Input', file: 'facebook_weighted_filtered.csv', status: 'complete', count: '486 nodes, 4037 edges' },
    { name: 'Motif Extraction', file: 'facebook_motifs.json', status: 'complete', count: '486 motifs' },
    { name: 'MST Computation', file: 'facebook_msts.json', status: 'complete', count: '486 MSTs' },
    { name: 'Persistence Diagrams', file: 'persistence_coordinates.json', status: 'complete', count: '8,560 points' },
    { name: 'Wasserstein Distances', file: 'wasserstein_distances.json', status: 'complete', count: '236,196 pairs' },
    { name: 'Clustering', file: 'agglomerative_50_cluster_groups.json', status: 'complete', count: '50 clusters' }
  ]

  return (
    <div className="page">
      <div className="page-header">
        <h2>Data Processing Pipeline</h2>
        <p>Step-by-step transformation from raw graph to clustered motifs</p>
      </div>

      <div style={{ marginTop: '2rem' }}>
        {steps.map((step, index) => (
          <div key={index} style={{
            display: 'flex',
            alignItems: 'center',
            padding: '1.5rem',
            background: 'white',
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            marginBottom: '1rem'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: '#4caf50',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              marginRight: '1.5rem'
            }}>
              {index + 1}
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ marginBottom: '0.5rem' }}>{step.name}</h3>
              <p style={{ color: '#666', fontSize: '0.9rem' }}>{step.file}</p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ color: '#4caf50', fontWeight: 'bold', marginBottom: '0.25rem' }}>✓ Complete</div>
              <div style={{ color: '#666', fontSize: '0.9rem' }}>{step.count}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
