import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import MotifCard from '../../components/common/MotifCard'

// Helper to wrap component with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

// Mock motif data
const mockMotif = {
  source_node: 1,
  num_neighbors: 15,
  num_edges: 10,
  cluster: 5,
  mst: {
    total_weight: 25.5,
    nodes: [1, 2, 3, 4, 5],
    mst_edges: [
      { from: 1, to: 2, weight: 1.0 },
      { from: 2, to: 3, weight: 1.5 },
      { from: 3, to: 4, weight: 2.0 },
      { from: 4, to: 5, weight: 0.5 }
    ]
  }
}

describe('MotifCard Component', () => {
  it('should render motif source node', () => {
    renderWithRouter(<MotifCard motif={mockMotif} onSelect={() => {}} />)

    expect(screen.getByText('Motif 1')).toBeInTheDocument()
  })

  it('should render number of neighbors', () => {
    renderWithRouter(<MotifCard motif={mockMotif} onSelect={() => {}} />)

    expect(screen.getByText('15')).toBeInTheDocument()
  })

  it('should render number of edges', () => {
    renderWithRouter(<MotifCard motif={mockMotif} onSelect={() => {}} />)

    expect(screen.getByText('10')).toBeInTheDocument()
  })

  it('should render cluster label', () => {
    renderWithRouter(<MotifCard motif={mockMotif} onSelect={() => {}} />)

    expect(screen.getByText('C5')).toBeInTheDocument()
  })

  it('should render MST weight', () => {
    renderWithRouter(<MotifCard motif={mockMotif} onSelect={() => {}} />)

    expect(screen.getByText('26')).toBeInTheDocument() // rounded from 25.5
  })

  it('should display "Small" badge for motifs with <= 10 neighbors', () => {
    const smallMotif = { ...mockMotif, num_neighbors: 8 }
    renderWithRouter(<MotifCard motif={smallMotif} onSelect={() => {}} />)

    expect(screen.getByText('Small')).toBeInTheDocument()
  })

  it('should display "Medium" badge for motifs with 11-30 neighbors', () => {
    renderWithRouter(<MotifCard motif={mockMotif} onSelect={() => {}} />)

    expect(screen.getByText('Medium')).toBeInTheDocument()
  })

  it('should display "Large" badge for motifs with 31-50 neighbors', () => {
    const largeMotif = { ...mockMotif, num_neighbors: 40 }
    renderWithRouter(<MotifCard motif={largeMotif} onSelect={() => {}} />)

    expect(screen.getByText('Large')).toBeInTheDocument()
  })

  it('should display "Very Large" badge for motifs with > 50 neighbors', () => {
    const veryLargeMotif = { ...mockMotif, num_neighbors: 60 }
    renderWithRouter(<MotifCard motif={veryLargeMotif} onSelect={() => {}} />)

    expect(screen.getByText('Very Large')).toBeInTheDocument()
  })

  it('should call onSelect with motif when clicked', () => {
    const handleSelect = vi.fn()
    renderWithRouter(<MotifCard motif={mockMotif} onSelect={handleSelect} />)

    const card = screen.getByText('Motif 1').closest('div')
    fireEvent.click(card)

    expect(handleSelect).toHaveBeenCalledTimes(1)
    expect(handleSelect).toHaveBeenCalledWith(mockMotif)
  })

  it('should show selected indicator when isSelected is true', () => {
    const { container } = renderWithRouter(
      <MotifCard motif={mockMotif} onSelect={() => {}} isSelected={true} />
    )

    const checkmark = container.querySelector('div[style*="background: rgb(66, 133, 244)"]')
    expect(checkmark).toBeInTheDocument()
  })

  it('should not show selected indicator when isSelected is false', () => {
    const { container } = renderWithRouter(
      <MotifCard motif={mockMotif} onSelect={() => {}} isSelected={false} />
    )

    const checkmark = container.querySelector('div[style*="background: rgb(66, 133, 244)"]')
    expect(checkmark).not.toBeInTheDocument()
  })

  it('should handle motif without MST data', () => {
    const motifWithoutMst = { ...mockMotif, mst: null }
    renderWithRouter(<MotifCard motif={motifWithoutMst} onSelect={() => {}} />)

    // Should render with 0 as fallback
    expect(screen.getByText('0')).toBeInTheDocument()
  })

  it('should apply hover styles without crashing', () => {
    const { container } = renderWithRouter(
      <MotifCard motif={mockMotif} onSelect={() => {}} />
    )

    const card = screen.getByText('Motif 1').closest('div')

    // Fire mouse events to test hover handlers
    fireEvent.mouseEnter(card)
    fireEvent.mouseLeave(card)

    // Should not throw
    expect(card).toBeInTheDocument()
  })
})
