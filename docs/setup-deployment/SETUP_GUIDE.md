# React App Setup Guide

## Prerequisites

You need to install Node.js first. Here's how:

### Install Node.js on macOS

```bash
# Using Homebrew (recommended)
brew install node

# Or download from https://nodejs.org/
```

Verify installation:
```bash
node --version  # Should show v18.x or higher
npm --version   # Should show v9.x or higher
```

## Installation Steps

### 1. Navigate to the React app directory
```bash
cd motif-react-app
```

### 2. Install dependencies
```bash
npm install
```

This will install:
- React 18
- React Router (for navigation)
- D3.js (for visualizations)
- Zustand (for state management)
- Vite (build tool)

### 3. Copy data files
```bash
# Copy JSON data files to public directory
cp ../data/*.json public/data/
cp ../facebook_weighted_filtered.csv public/
```

### 4. Start development server
```bash
npm run dev
```

The app will open at: **http://localhost:3000**

## Project Structure

```
motif-react-app/
├── public/
│   └── data/                    # JSON data files (copy here)
├── src/
│   ├── components/
│   │   ├── common/              # Reusable UI components
│   │   ├── visualizations/      # D3 visualization components
│   │   └── controls/            # Control components
│   ├── pages/
│   │   ├── Home.jsx             # ✅ Created
│   │   ├── DataPipeline.jsx     # ✅ Created
│   │   ├── MotifExplorer.jsx    # ✅ Created
│   │   ├── ClusterAnalysis.jsx  # ✅ Created
│   │   ├── GraphCollapse.jsx    # ✅ Created
│   │   └── Statistics.jsx       # ✅ Created
│   ├── hooks/                   # Custom React hooks (to be created)
│   ├── store/                   # State management (to be created)
│   ├── utils/                   # Utility functions (to be created)
│   ├── App.jsx                  # ✅ Main app with routing
│   ├── App.css                  # ✅ Styles
│   ├── main.jsx                 # ✅ Entry point
│   └── index.css                # ✅ Global styles
├── index.html                   # ✅ HTML template
├── package.json                 # ✅ Dependencies
├── vite.config.js               # ✅ Vite configuration
└── README.md                    # ✅ Documentation
```

## Current Status

### ✅ Completed
- Project structure created
- Basic routing setup (6 pages)
- Navigation bar
- Home page with overview
- Data Pipeline page with steps
- Placeholder pages for other features

### 🚧 To Be Implemented
- D3 visualization components
- Data loading hooks
- State management with Zustand
- Graph Collapse functionality
- Motif Explorer grid
- Cluster Analysis tools
- Statistics dashboard

## Next Steps

### Phase 1: Data Loading (Priority)
Create hooks to load data:

```jsx
// src/hooks/useGraphData.js
// src/hooks/useMotifData.js
// src/hooks/useClusterData.js
```

### Phase 2: D3 Components
Create reusable D3 visualization components:

```jsx
// src/components/visualizations/D3ForceGraph.jsx
// src/components/visualizations/MSTViewer.jsx
```

### Phase 3: Graph Collapse Page
Implement the main feature:
- Cluster selector dropdown
- Collapse/expand controls
- Real-time statistics
- Interactive graph visualization

### Phase 4: Other Pages
- Motif Explorer with grid view
- Cluster Analysis with comparison
- Statistics dashboard with charts

## Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

### Port already in use
If port 3000 is busy, edit `vite.config.js`:
```js
server: {
  port: 3001  // Change to different port
}
```

### Data files not loading
Make sure data files are in `public/data/` directory:
```bash
ls public/data/
# Should show: facebook_motifs.json, facebook_msts.json, etc.
```

## Integration with Flask Backend

The Flask server should run on port 5000. Vite is configured to proxy API requests:

```js
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  }
}
```

Start both servers:
```bash
# Terminal 1: Flask backend
python server.py

# Terminal 2: React frontend
cd motif-react-app && npm run dev
```

## Resources

- [React Documentation](https://react.dev/)
- [React Router](https://reactrouter.com/)
- [D3.js](https://d3js.org/)
- [Vite](https://vitejs.dev/)
- [Zustand](https://github.com/pmndrs/zustand)
