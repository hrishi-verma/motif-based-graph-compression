import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import LoadingSpinner from '../../components/common/LoadingSpinner'

// Helper to wrap component with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('LoadingSpinner Component', () => {
  it('should render with default message', () => {
    renderWithRouter(<LoadingSpinner />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('should render with custom message', () => {
    renderWithRouter(<LoadingSpinner message="Fetching data..." />)

    expect(screen.getByText('Fetching data...')).toBeInTheDocument()
  })

  it('should render spinner element', () => {
    const { container } = renderWithRouter(<LoadingSpinner />)

    const spinner = container.querySelector('div[style*="border-radius: 50%"]')
    expect(spinner).toBeInTheDocument()
  })

  it('should render container with correct styles', () => {
    const { container } = renderWithRouter(<LoadingSpinner />)

    const wrapper = container.firstChild
    expect(wrapper.style.display).toBe('flex')
    expect(wrapper.style.flexDirection).toBe('column')
  })

  it('should render message paragraph', () => {
    const { container } = renderWithRouter(<LoadingSpinner message="Please wait" />)

    const paragraph = container.querySelector('p')
    expect(paragraph).toBeInTheDocument()
    expect(paragraph.textContent).toBe('Please wait')
  })
})
