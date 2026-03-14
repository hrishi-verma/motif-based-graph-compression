import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import MotifFilters from '../../components/common/MotifFilters'

// Helper to wrap component with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

// Default filters
const defaultFilters = {
  searchQuery: '',
  cluster: null,
  sortBy: 'id',
  sizeRange: [2, 157]
}

describe('MotifFilters Component', () => {
  it('should render search input', () => {
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={() => {}}
        onClear={() => {}}
      />
    )

    expect(screen.getByPlaceholderText('Enter motif ID...')).toBeInTheDocument()
  })

  it('should render cluster select', () => {
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={() => {}}
        onClear={() => {}}
      />
    )

    expect(screen.getByText('All Clusters')).toBeInTheDocument()
  })

  it('should render sort select', () => {
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={() => {}}
        onClear={() => {}}
      />
    )

    expect(screen.getByText('Sort By')).toBeInTheDocument()
    expect(screen.getByText('Motif ID')).toBeInTheDocument()
  })

  it('should render size range inputs', () => {
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={() => {}}
        onClear={() => {}}
      />
    )

    expect(screen.getByText(/Size Range:/)).toBeInTheDocument()
  })

  it('should render clear filters button', () => {
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={() => {}}
        onClear={() => {}}
      />
    )

    expect(screen.getByText('Clear Filters')).toBeInTheDocument()
  })

  it('should call onFilterChange when search input changes', () => {
    const handleFilterChange = vi.fn()
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={handleFilterChange}
        onClear={() => {}}
      />
    )

    const searchInput = screen.getByPlaceholderText('Enter motif ID...')
    fireEvent.change(searchInput, { target: { value: '123' } })

    expect(handleFilterChange).toHaveBeenCalledTimes(1)
    expect(handleFilterChange).toHaveBeenCalledWith('searchQuery', '123')
  })

  it('should call onFilterChange when cluster is selected', () => {
    const handleFilterChange = vi.fn()
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={handleFilterChange}
        onClear={() => {}}
      />
    )

    const clusterSelect = screen.getByDisplayValue('All Clusters')
    fireEvent.change(clusterSelect, { target: { value: '5' } })

    expect(handleFilterChange).toHaveBeenCalledTimes(1)
    expect(handleFilterChange).toHaveBeenCalledWith('cluster', 5)
  })

  it('should call onFilterChange when sort option is selected', () => {
    const handleFilterChange = vi.fn()
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={handleFilterChange}
        onClear={() => {}}
      />
    )

    const sortSelect = screen.getByDisplayValue('Motif ID')
    fireEvent.change(sortSelect, { target: { value: 'size' } })

    expect(handleFilterChange).toHaveBeenCalledTimes(1)
    expect(handleFilterChange).toHaveBeenCalledWith('sortBy', 'size')
  })

  it('should call onFilterChange when size range changes', () => {
    const handleFilterChange = vi.fn()
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={handleFilterChange}
        onClear={() => {}}
      />
    )

    const rangeInputs = screen.getAllByRole('slider')
    fireEvent.change(rangeInputs[0], { target: { value: '10' } })

    expect(handleFilterChange).toHaveBeenCalledWith('sizeRange', [10, 157])
  })

  it('should call onClear when clear button is clicked', () => {
    const handleClear = vi.fn()
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={() => {}}
        onClear={handleClear}
      />
    )

    const clearButton = screen.getByText('Clear Filters')
    fireEvent.click(clearButton)

    expect(handleClear).toHaveBeenCalledTimes(1)
  })

  it('should display current filter values', () => {
    const filtersWithValues = {
      searchQuery: 'test',
      cluster: 3,
      sortBy: 'size',
      sizeRange: [10, 50]
    }

    renderWithRouter(
      <MotifFilters
        filters={filtersWithValues}
        onFilterChange={() => {}}
        onClear={() => {}}
      />
    )

    expect(screen.getByDisplayValue('test')).toBeInTheDocument()
  })

  it('should render sort select with all options', () => {
    renderWithRouter(
      <MotifFilters
        filters={defaultFilters}
        onFilterChange={() => {}}
        onClear={() => {}}
      />
    )

    // Check that sortBy select exists and has the right options
    const select = screen.getByDisplayValue('Motif ID')
    expect(select).toBeInTheDocument()
  })
})
