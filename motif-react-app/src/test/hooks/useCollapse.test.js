import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useCollapse } from '../../hooks/useCollapse'
import { mockMotifDataForCollapse } from '../mockData'

describe('useCollapse hook', () => {
  describe('Initial state', () => {
    it('should initialize with empty collapsedMotifs and motifOwnership', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      expect(result.current.collapsedMotifs.size).toBe(0)
      expect(result.current.motifOwnership.size).toBe(0)
      expect(result.current.collapsedNodes.size).toBe(0)
    })

    it('should provide collapseCluster, expandMotif, and reset functions', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      expect(typeof result.current.collapseCluster).toBe('function')
      expect(typeof result.current.expandMotif).toBe('function')
      expect(typeof result.current.reset).toBe('function')
    })
  })

  describe('collapseCluster', () => {
    it('should add motifs to collapsedMotifs set', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([1])
      })

      expect(result.current.collapsedMotifs.size).toBe(1)
      expect(result.current.collapsedMotifs.has(1)).toBe(true)
    })

    it('should claim nodes for collapsed motif', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([1])
      })

      // Motif 1 has nodes [1, 2, 3]
      expect(result.current.motifOwnership.size).toBe(3)
      expect(result.current.motifOwnership.get(1)).toBe(1)
      expect(result.current.motifOwnership.get(2)).toBe(1)
      expect(result.current.motifOwnership.get(3)).toBe(1)
    })

    it('should claim source node for collapsed motif', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([2])
      })

      // Motif 2 has source_node = 2, nodes [2, 3, 4, 5]
      expect(result.current.motifOwnership.get(2)).toBe(2)
    })

    it('should handle multiple motif collapse', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([1, 2, 3])
      })

      expect(result.current.collapsedMotifs.size).toBe(3)
    })

    it('should skip nodes already owned by another motif', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      // Collapse motif 1 first (nodes: 1, 2, 3)
      act(() => {
        result.current.collapseCluster([1])
      })

      // Collapse motif 2 (nodes: 2, 3, 4, 5)
      // Nodes 2 and 3 are already owned by motif 1
      act(() => {
        result.current.collapseCluster([2])
      })

      // Motif 2 should own node 2 (as source extraction) and 4, 5 (unique)
      // Node 3 stays with motif 1
      expect(result.current.motifOwnership.get(2)).toBe(2) // Extracted as source
      expect(result.current.motifOwnership.get(3)).toBe(1) // Stays with first owner
      expect(result.current.motifOwnership.get(4)).toBe(2)
      expect(result.current.motifOwnership.get(5)).toBe(2)
    })

    it('should do nothing when motifData is null', () => {
      const { result } = renderHook(() => useCollapse(null))

      act(() => {
        result.current.collapseCluster([1])
      })

      expect(result.current.collapsedMotifs.size).toBe(0)
    })

    it('should handle empty cluster array', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([])
      })

      expect(result.current.collapsedMotifs.size).toBe(0)
    })

    it('should handle non-existent motif IDs gracefully', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([999])
      })

      expect(result.current.collapsedMotifs.size).toBe(0)
    })
  })

  describe('expandMotif', () => {
    it('should remove motif from collapsedMotifs', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([1])
      })

      expect(result.current.collapsedMotifs.has(1)).toBe(true)

      act(() => {
        result.current.expandMotif(1)
      })

      expect(result.current.collapsedMotifs.has(1)).toBe(false)
    })

    it('should release nodes owned by expanded motif', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([1])
      })

      expect(result.current.motifOwnership.size).toBe(3)

      act(() => {
        result.current.expandMotif(1)
      })

      expect(result.current.motifOwnership.size).toBe(0)
    })

    it('should smart expand and release common nodes', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      // Collapse motif 1 and 2
      act(() => {
        result.current.collapseCluster([1, 2])
      })

      // Motif 1 owns nodes 1, 2, 3
      // Motif 2 owns node 2 (extracted), 3 (shared), 4, 5

      // Expand motif 1
      act(() => {
        result.current.expandMotif(1)
      })

      // After expanding motif 1, the common node 3 should be released
      // because it's not the source of motif 2
      expect(result.current.motifOwnership.has(3)).toBe(false)
    })

    it('should do nothing when motifData is null', () => {
      const { result } = renderHook(() => useCollapse(null))

      act(() => {
        result.current.collapseCluster([1])
        result.current.expandMotif(1)
      })

      expect(result.current.collapsedMotifs.size).toBe(0)
    })

    it('should handle expanding non-collapsed motif', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.expandMotif(1)
      })

      expect(result.current.collapsedMotifs.size).toBe(0)
    })

    it('should handle non-existent motif ID', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([1])
        result.current.expandMotif(999)
      })

      expect(result.current.collapsedMotifs.size).toBe(1)
    })
  })

  describe('reset', () => {
    it('should clear all collapsed motifs and ownership', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([1, 2, 3])
      })

      expect(result.current.collapsedMotifs.size).toBe(3)
      expect(result.current.motifOwnership.size).toBeGreaterThan(0)

      act(() => {
        result.current.reset()
      })

      expect(result.current.collapsedMotifs.size).toBe(0)
      expect(result.current.motifOwnership.size).toBe(0)
    })
  })

  describe('collapsedNodes', () => {
    it('should return a set of all owned node IDs', () => {
      const { result } = renderHook(() => useCollapse(mockMotifDataForCollapse))

      act(() => {
        result.current.collapseCluster([1])
      })

      const collapsedNodes = result.current.collapsedNodes
      expect(collapsedNodes.has(1)).toBe(true)
      expect(collapsedNodes.has(2)).toBe(true)
      expect(collapsedNodes.has(3)).toBe(true)
    })
  })
})
