import { create } from 'zustand'

// Simple store for hop distance selection
// This can be used across the app to share the selected hop distance
export const useHopStore = create((set) => ({
  hopDistance: 1,
  setHopDistance: (distance) => set({ hopDistance: distance }),
}))
