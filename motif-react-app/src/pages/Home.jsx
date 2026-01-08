import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="page">
      <div className="page-header">
        <h2>Welcome to Graph Motif Compression</h2>
        <p>Explore and compress large network graphs using intelligent motif clustering</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginTop: '2rem' }}>
        <div className="card">
          <h3>📊 486 Nodes</h3>
          <p>Facebook social network graph</p>
        </div>
        <div className="card">
          <h3>🌳 486 Motifs</h3>
          <p>One-hop neighborhoods extracted</p>
        </div>
        <div className="card">
          <h3>🎯 50 Clusters</h3>
          <p>Grouped by structural similarity</p>
        </div>
        <div className="card">
          <h3>📉 57% Compression</h3>
          <p>With intelligent collapsing</p>
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}>
        <h3>Quick Start</h3>
        <ol style={{ marginTop: '1rem', marginLeft: '2rem', lineHeight: '2' }}>
          <li>View the <Link to="/pipeline">Data Pipeline</Link> to understand the processing flow</li>
          <li>Explore individual <Link to="/motifs">Motifs</Link> and their structures</li>
          <li>Analyze <Link to="/clusters">Clusters</Link> and compare similarities</li>
          <li>Try the <Link to="/collapse">Graph Collapse</Link> feature (main functionality)</li>
          <li>View detailed <Link to="/stats">Statistics</Link> and analytics</li>
        </ol>
      </div>
    </div >
  )
}
