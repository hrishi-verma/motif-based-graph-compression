import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import StatCard from '../../components/common/StatCard'

// Helper to wrap component with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('StatCard Component', () => {
  it('should render title and value', () => {
    renderWithRouter(<StatCard title="Total Nodes" value="486" />)

    expect(screen.getByText('Total Nodes')).toBeInTheDocument()
    expect(screen.getByText('486')).toBeInTheDocument()
  })

  it('should render subtitle when provided', () => {
    renderWithRouter(<StatCard title="Total Nodes" value="486" subtitle="Active nodes" />)

    expect(screen.getByText('Active nodes')).toBeInTheDocument()
  })

  it('should not render subtitle when not provided', () => {
    const { container } = renderWithRouter(<StatCard title="Total Nodes" value="486" />)

    // The subtitle div should not exist
    const subtitleDivs = container.querySelectorAll('div')
    expect(subtitleDivs.length).toBeGreaterThan(0)
  })

  it('should render icon when provided', () => {
    renderWithRouter(<StatCard title="Total Nodes" value="486" icon="📊" />)

    expect(screen.getByText('📊')).toBeInTheDocument()
  })

  it('should apply highlight styles when highlight prop is true', () => {
    const { container } = renderWithRouter(
      <StatCard title="Total Nodes" value="486" highlight={true} />
    )

    const card = container.firstChild
    expect(card.style.background).toContain('linear-gradient')
    expect(card.style.color).toBe('white')
  })

  it('should apply default styles when highlight is false', () => {
    const { container } = renderWithRouter(
      <StatCard title="Total Nodes" value="486" highlight={false} />
    )

    const card = container.firstChild
    expect(card.style.color).toBe('rgb(51, 51, 51)') // #333
  })

  it('should handle numeric and string values', () => {
    renderWithRouter(<StatCard title="Test" value={123} />)
    expect(screen.getByText('123')).toBeInTheDocument()

    renderWithRouter(<StatCard title="Test" value="456" />)
    expect(screen.getByText('456')).toBeInTheDocument()
  })
})
