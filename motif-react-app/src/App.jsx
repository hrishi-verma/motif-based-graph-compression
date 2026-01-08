import { HashRouter, Routes, Route, Link, Navigate } from 'react-router-dom'
import Home from './pages/Home'
import DataPipeline from './pages/DataPipeline'
import MotifExplorer from './pages/MotifExplorer'
import ClusterAnalysis from './pages/ClusterAnalysis'
import GraphCollapse from './pages/GraphCollapse'
import Statistics from './pages/Statistics'
import './App.css'

function App() {
  return (
    <HashRouter>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>🌐 Graph Motif Compression</h1>
          </div>
          <ul className="nav-links">
            <li><Link to="/">Home</Link></li>
            <li><Link to="/pipeline">Pipeline</Link></li>
            <li><Link to="/motifs">Motifs</Link></li>
            <li><Link to="/clusters">Clusters</Link></li>
            <li><Link to="/collapse">Collapse</Link></li>
            <li><Link to="/stats">Statistics</Link></li>
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/pipeline" element={<DataPipeline />} />
            <Route path="/motifs" element={<MotifExplorer />} />
            <Route path="/clusters" element={<ClusterAnalysis />} />
            <Route path="/collapse" element={<GraphCollapse />} />
            <Route path="/stats" element={<Statistics />} />
            <Route path="*" element={<Navigate replace to="/" />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
  )
}

export default App
