# Graph Motif Compression

A comprehensive graph analysis and visualization system that identifies recurring structural patterns (motifs) in large networks and enables intelligent compression through hierarchical clustering. The project combines Python-based graph analysis with an interactive React dashboard, allowing researchers to explore, cluster, and visualize motif patterns in social networks while achieving up to 26% compression in graph representation.

**Live Demo:** [https://hrishi-verma.github.io/motif-based-graph-compression](https://hrishi-verma.github.io/motif-based-graph-compression)

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Data Pipeline](#data-pipeline)
- [React Dashboard](#react-dashboard)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Tech Stack](#tech-stack)
- [Credits](#credits)

---

## Features

### Core Analysis Features
- **Motif Extraction**: Automatically identifies 486 unique structural patterns in graph data
- **MST Computation**: Generates minimum spanning trees for each motif using Prim's algorithm
- **Hierarchical Clustering**: Groups motifs into 50 clusters using agglomerative clustering with Wasserstein distance
- **Intelligent Overlap Resolution**: Handles nested and overlapping motif structures during compression
- **Compression Analysis**: Achieves up to 26% reduction in graph representation

### Interactive React Dashboard
- **Motif Explorer**: Browse, filter, and search through 486 motifs with detailed visualizations
- **Cluster Analysis**: Compare structural similarities across 50 clusters with MST grid views
- **Graph Collapse**: Interactive D3.js force-directed graph with real-time collapse/expand
- **Statistics Dashboard**: Comprehensive analytics with heatmap visualizations
- **Responsive Design**: Modern UI with smooth animations and hover effects

### Visualization Tools
- **D3.js Force Graphs**: Interactive node-link diagrams with zoom and drag
- **MST Visualizations**: Minimum spanning tree representations for each motif
- **Heatmap Charts**: Distribution analysis for motif and cluster sizes
- **Real-time Updates**: Position-preserving animations during graph manipulation

---

## Project Structure

```
motif-based-graph-compression/
├── data/                           # Data files (JSON, CSV)
│   ├── facebook_motifs.json        # Extracted motif data
│   ├── facebook_msts.json          # MST data for each motif
│   └── agglomerative_50_cluster_groups.json  # Cluster assignments
├── motif-react-app/                # React dashboard application
│   ├── public/                     # Static assets
│   │   └── data/                   # Data files for production
│   ├── src/
│   │   ├── components/             # Reusable React components
│   │   │   ├── common/             # Shared UI components
│   │   │   ├── controls/           # Form controls and inputs
│   │   │   └── visualizations/     # D3 and chart components
│   │   ├── hooks/                  # Custom React hooks for data loading
│   │   ├── pages/                  # Main application pages
│   │   └── App.jsx                 # Root application component
│   ├── package.json                # Node dependencies
│   └── vite.config.js              # Vite build configuration
├── .github/workflows/              # GitHub Actions for deployment
│   └── deploy.yml                  # Automated deployment workflow
├── extract_motifs.py               # Main motif extraction script
├── compute_mst.py                  # MST computation for motifs
├── generate_clusters.py            # Hierarchical clustering script
├── wasserstein_distance_calculator.py  # Distance metric computation
├── server.py                       # Flask development server
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

### Key Directories

- **`data/`**: Contains all processed graph data, motif information, and cluster assignments
- **`motif-react-app/`**: Complete React application with modern component architecture
- **Python Scripts**: Data processing pipeline for motif extraction and clustering
- **HTML Demos**: Standalone visualization prototypes (legacy)

---

## Prerequisites

### Required Software
- **Python**: 3.8 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher (comes with Node.js)
- **Git**: For version control

### Operating System
- macOS, Linux, or Windows with WSL2

### Python Packages
```
networkx>=3.0
pandas>=1.5.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.2.0
flask>=2.3.0
matplotlib>=3.7.0
```

### Node.js Packages
```
react>=18.2.0
react-router-dom>=6.20.0
d3>=7.8.5
vite>=5.0.8
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/hrishi-verma/motif-based-graph-compression.git
cd motif-based-graph-compression
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up React Application

```bash
cd motif-react-app
npm install
cd ..
```

---

## Usage

### Running the Data Pipeline

#### Step 1: Extract Motifs from Graph Data

```bash
python extract_motifs.py
```

**Output**: `data/facebook_motifs.json` (486 motifs with structural information)

#### Step 2: Compute Minimum Spanning Trees

```bash
python compute_mst.py
```

**Output**: `data/facebook_msts.json` (MST for each motif)

#### Step 3: Generate Clusters

```bash
python generate_clusters.py
```

**Output**: `data/agglomerative_50_cluster_groups.json` (50 clusters with assignments)

#### Step 4: Calculate Wasserstein Distances (Optional)

```bash
python wasserstein_distance_calculator.py
```

**Output**: `wasserstein_distances.json` (pairwise distance matrix)

### Running the React Dashboard Locally

```bash
cd motif-react-app
npm run dev
```

Visit: `http://localhost:3000`

### Building for Production

```bash
cd motif-react-app
npm run build
npm run preview
```

### Running Legacy Flask Server (Optional)

```bash
python server.py
```

Visit: `http://localhost:5000`

---

## Data Pipeline

### Complete Workflow

```
Raw Graph Data (CSV)
    ↓
[extract_motifs.py] → Identify 486 motifs
    ↓
[compute_mst.py] → Generate MSTs for each motif
    ↓
[wasserstein_distance_calculator.py] → Compute similarity matrix
    ↓
[generate_clusters.py] → Hierarchical clustering (50 clusters)
    ↓
JSON Data Files → Used by React Dashboard
```

### Data Files

| File | Description | Size |
|------|-------------|------|
| `facebook_weighted_filtered.csv` | Original graph data (486 nodes, 4000+ edges) |
| `facebook_motifs.json` | Extracted motif information with statistics |
| `facebook_msts.json` | MST data indexed by source node |
| `agglomerative_50_cluster_groups.json` | Cluster assignments and metadata |
| `wasserstein_distances.json` | Pairwise distance matrix (optional) |

---

## React Dashboard

### Available Pages

1. **Home** (`/`)
   - Project overview and navigation

2. **Data Pipeline** (`/pipeline`)
   - Workflow visualization and status

3. **Motif Explorer** (`/motifs`)
   - Browse all 486 motifs
   - Filter by size, cluster, density
   - Search by node ID
   - Detailed modal with MST visualization

4. **Cluster Analysis** (`/clusters`)
   - Compare 50 clusters
   - View cluster statistics
   - MST grid visualization
   - Structural similarity analysis

5. **Graph Collapse** (`/collapse`)
   - Interactive force-directed graph
   - Collapse clusters into supernodes
   - Expand motifs on click
   - Real-time compression statistics

6. **Statistics** (`/stats`)
   - Graph metrics (nodes, edges, density)
   - Motif distribution heatmaps
   - Cluster size analysis
   - Compression potential metrics

### Key Components

- **D3ForceGraph**: Interactive force-directed graph with position memory
- **MSTGrid**: Grid layout for MST visualizations
- **MotifCard**: Reusable motif display component
- **ClusterSelector**: Dropdown for cluster selection
- **StatCard**: Animated statistics cards
- **Heatmap Charts**: Distribution visualizations

---

## Deployment

### GitHub Pages (Automated)

The project is configured for automatic deployment to GitHub Pages using GitHub Actions.

#### Setup

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Select "GitHub Actions"

2. **Push Changes**:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

3. **Automatic Deployment**:
   - Workflow triggers on push to `main` branch
   - Builds React app
   - Deploys to GitHub Pages
   - Available at: `https://hrishi-verma.github.io/motif-based-graph-compression`

#### Manual Trigger

1. Go to repository Actions tab
2. Select "Deploy to GitHub Pages"
3. Click "Run workflow"
4. Select `main` branch
5. Click "Run workflow"

### Local Production Build

```bash
cd motif-react-app
npm run build
npm run preview
```

---

## Configuration

### Environment Variables

No environment variables required for basic usage.

### Vite Configuration

**File**: `motif-react-app/vite.config.js`

```javascript
export default defineConfig({
  plugins: [react()],
  base: '/motif-based-graph-compression/',  // GitHub Pages base path
  server: {
    port: 3000
  }
})
```

### Data Paths

Data files are loaded from `public/data/` in production:

```javascript
const basePath = import.meta.env.BASE_URL
fetch(`${basePath}data/facebook_motifs.json`)
```

---

## Troubleshooting

### Common Issues

#### 1. "Error: Failed to fetch" in React App

**Problem**: Data files not loading

**Solution**:
```bash
# Ensure data files are in public folder
cp -r data motif-react-app/public/data
```

#### 2. Blank Page on GitHub Pages

**Problem**: Incorrect base path

**Solution**: Verify `base` in `vite.config.js` matches repository name

#### 3. 404 on Page Refresh (GitHub Pages)

**Problem**: BrowserRouter doesn't work with GitHub Pages

**Solution**: Use HashRouter instead:
```javascript
import { HashRouter } from 'react-router-dom'
// Use HashRouter instead of BrowserRouter
```

#### 4. Python Module Not Found

**Problem**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt
```

#### 5. Node Modules Error

**Problem**: Outdated or missing packages

**Solution**:
```bash
cd motif-react-app
rm -rf node_modules package-lock.json
npm install
```

#### 6. Graph Animation Too Aggressive

**Problem**: Nodes moving too much on expand/collapse

**Solution**: Already implemented with position memory and low alpha values

---

## Tech Stack

### Backend & Analysis
- **Python 3.8+**: Core language for data processing
- **NetworkX**: Graph analysis and algorithms
- **scikit-learn**: Hierarchical clustering
- **SciPy**: Wasserstein distance computation
- **pandas**: Data manipulation
- **NumPy**: Numerical computations
- **Flask**: Development server (optional)

### Frontend
- **React 18**: UI framework
- **React Router**: Client-side routing
- **D3.js**: Interactive visualizations
- **Vite**: Build tool and dev server
- **Zustand**: State management (optional)

### Deployment
- **GitHub Actions**: CI/CD pipeline
- **GitHub Pages**: Static site hosting

### Development Tools
- **Git**: Version control
- **npm**: Package management
- **ESLint**: Code linting (optional)

---

## Useful Commands

### Python Scripts

```bash
# Extract motifs
python extract_motifs.py

# Compute MSTs
python compute_mst.py

# Generate clusters
python generate_clusters.py

# Calculate distances
python wasserstein_distance_calculator.py

# Analyze specific cluster
python analyze_large_cluster.py

# Run Flask server
python server.py
```

### React Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Install dependencies
npm install

# Update dependencies
npm update
```

### Git Workflow

```bash
# Check status
git status

# Stage changes
git add .

# Commit changes
git commit -m "Description"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

---

## Project Workflow

### Data Flow

1. **Input**: Raw graph CSV file with weighted edges
2. **Processing**: Python scripts extract motifs and compute similarities
3. **Storage**: JSON files store processed data
4. **Visualization**: React app loads JSON and renders interactive views
5. **Interaction**: Users explore, filter, and manipulate graph structures

### Component Interaction

```
User Interface (React)
    ↓
Custom Hooks (useGraphData, useMotifData)
    ↓
Fetch API (Load JSON files)
    ↓
D3.js Visualizations
    ↓
Interactive Graph Manipulation
```

---

## Credits

**Developer**: Hrishi Verma  
**Institution**: University of Utah, Scientific Computing and Imaging (SCI) Institute  
**Advisor**: Dr. Paul Rosen  
**Course**: Independent Study - Graph Visualization and Compression  

### External Resources
- [D3.js Documentation](https://d3js.org/)
- [NetworkX Documentation](https://networkx.org/)
- [React Documentation](https://react.dev/)
- [Wasserstein Distance](https://en.wikipedia.org/wiki/Wasserstein_metric)

### Dataset
- Facebook Social Network (SNAP Dataset)
- 486 nodes, 4000+ edges
- Weighted, undirected graph

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Future Enhancements

- [ ] Real-time motif detection on streaming graphs
- [ ] GPU-accelerated distance computations
- [ ] Machine learning-based motif classification
- [ ] Export compressed graphs in standard formats
- [ ] Multi-graph comparison tools
- [ ] Advanced filtering and query language
- [ ] 3D graph visualization option

---

## Contact

For questions, issues, or contributions:
- **GitHub**: [hrishi-verma](https://github.com/hrishi-verma)
- **Repository**: [motif-based-graph-compression](https://github.com/hrishi-verma/motif-based-graph-compression)

---

**Last Updated**: November 2024
