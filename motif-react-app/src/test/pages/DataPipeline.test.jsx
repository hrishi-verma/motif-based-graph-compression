import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import DataPipeline from '../../pages/DataPipeline'

// Helper to wrap component with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('DataPipeline Page', () => {
  it('should render page heading', () => {
    renderWithRouter(<DataPipeline />)

    expect(screen.getByText('Data Processing Pipeline')).toBeInTheDocument()
  })

  it('should render page description', () => {
    renderWithRouter(<DataPipeline />)

    expect(screen.getByText('Step-by-step transformation from raw graph to clustered motifs')).toBeInTheDocument()
  })

  it('should render all 6 pipeline steps', () => {
    renderWithRouter(<DataPipeline />)

    expect(screen.getByText('Raw Graph Input')).toBeInTheDocument()
    expect(screen.getByText('Motif Extraction')).toBeInTheDocument()
    expect(screen.getByText('MST Computation')).toBeInTheDocument()
    expect(screen.getByText('Persistence Diagrams')).toBeInTheDocument()
    expect(screen.getByText('Wasserstein Distances')).toBeInTheDocument()
    expect(screen.getByText('Clustering')).toBeInTheDocument()
  })

  it('should render step numbers', () => {
    renderWithRouter(<DataPipeline />)

    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('4')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('6')).toBeInTheDocument()
  })

  it('should render checkmarks for completed steps', () => {
    renderWithRouter(<DataPipeline />)

    const checkmarks = screen.getAllByText('✓ Complete')
    expect(checkmarks.length).toBe(6)
  })

  it('should render file names', () => {
    renderWithRouter(<DataPipeline />)

    expect(screen.getByText('facebook_weighted_filtered.csv')).toBeInTheDocument()
    expect(screen.getByText('facebook_motifs.json')).toBeInTheDocument()
    expect(screen.getByText('facebook_msts.json')).toBeInTheDocument()
    expect(screen.getByText('persistence_coordinates.json')).toBeInTheDocument()
    expect(screen.getByText('wasserstein_distances.json')).toBeInTheDocument()
    expect(screen.getByText('agglomerative_50_cluster_groups.json')).toBeInTheDocument()
  })

  it('should render count information', () => {
    renderWithRouter(<DataPipeline />)

    expect(screen.getByText('486 nodes, 4037 edges')).toBeInTheDocument()
    expect(screen.getByText('486 motifs')).toBeInTheDocument()
    expect(screen.getByText('486 MSTs')).toBeInTheDocument()
    expect(screen.getByText('8,560 points')).toBeInTheDocument()
    expect(screen.getByText('236,196 pairs')).toBeInTheDocument()
    expect(screen.getByText('50 clusters')).toBeInTheDocument()
  })
})
