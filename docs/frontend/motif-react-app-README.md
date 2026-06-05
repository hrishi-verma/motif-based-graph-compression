# Graph Motif Compression - React App

React-based frontend for the Graph Motif Compression project.

## Setup

### Prerequisites
- Node.js 18+ and npm

### Installation

```bash
cd motif-react-app
npm install
```

### Development

```bash
npm run dev
```

Open http://localhost:3000

### Build

```bash
npm run build
```

## Project Structure

```
motif-react-app/
├── src/
│   ├── components/
│   │   ├── common/          # Reusable UI components
│   │   ├── visualizations/  # D3 visualization components
│   │   └── controls/        # Control components
│   ├── pages/               # Page components
│   ├── hooks/               # Custom React hooks
│   ├── store/               # State management
│   ├── utils/               # Utility functions
│   ├── App.jsx              # Main app component
│   └── main.jsx             # Entry point
├── public/
│   └── data/                # JSON data files
└── package.json
```

## Pages

- **Home** (`/`) - Landing page with overview
- **Data Pipeline** (`/pipeline`) - Processing flow visualization
- **Motif Explorer** (`/motifs`) - Browse all motifs
- **Cluster Analysis** (`/clusters`) - Compare clusters
- **Graph Collapse** (`/collapse`) - Main collapsing interface
- **Statistics** (`/stats`) - Analytics dashboard

## Next Steps

1. Install dependencies: `npm install`
2. Copy data files to `public/data/`
3. Implement D3 visualization components
4. Add state management with Zustand
5. Build out each page incrementally
