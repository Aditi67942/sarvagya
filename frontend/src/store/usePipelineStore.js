// src/store/usePipelineStore.js
import { create } from 'zustand'

const usePipelineStore = create((set) => ({
  // State
  file: null,
  loading: false,
  error: null,
  result: null,

  // Actions
  setFile: (file) => set({ file, error: null }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error, loading: false }),

  setResult: (result) => set({ result, loading: false, error: null }),

  reset: () => set({ file: null, loading: false, error: null, result: null }),
}))

export default usePipelineStore