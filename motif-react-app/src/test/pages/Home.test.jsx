import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Home from '../../pages/Home'

// Helper to wrap component with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('Home Page', () => {
  it('should render without crashing', () => {
    renderWithRouter(<Home />)
    // Page should render without errors
  })

  it('should render welcome heading', () => {
    renderWithRouter(<Home />)

    expect(screen.getByText('Welcome to Graph Motif Compression')).toBeInTheDocument()
  })

  it('should render project description', () => {
    renderWithRouter(<Home />)

    expect(screen.getByText('Explore and compress large network graphs using intelligent motif clustering')).toBeInTheDocument()
  })

  it('should render Quick Start heading', () => {
    renderWithRouter(<Home />)

    expect(screen.getByText('Quick Start')).toBeInTheDocument()
  })

  it('should render list items for navigation', () => {
    renderWithRouter(<Home />)

    const listItems = screen.getAllByRole('listitem')
    expect(listItems.length).toBe(5)
  })

  it('should contain links to other pages', () => {
    renderWithRouter(<Home />)

    const links = screen.getAllByRole('link')
    expect(links.length).toBeGreaterThan(0)
  })

  it('should render main heading', () => {
    renderWithRouter(<Home />)

    expect(screen.getByRole('heading', { level: 2 })).toBeInTheDocument()
  })
})
