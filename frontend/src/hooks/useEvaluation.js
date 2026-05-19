import { useState, useCallback } from 'react'
import { getAllModelMetrics, getConfusionMatrix } from '../services/evaluationService'

export function useEvaluation() {
  const [metrics, setMetrics] = useState(null)
  const [matrix,  setMatrix]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  /**
   * Fetches all model metrics.
   * Returns the data directly so callers can chain without stale state.
   */
  const fetchMetrics = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getAllModelMetrics()
      setMetrics(data)
      return data
    } catch (e) {
      setError(e?.error || 'Failed to load model metrics.')
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Fetches the confusion matrix for a specific model.
   * Does NOT set loading — avoids wiping the whole page on matrix switch.
   */
  const fetchMatrix = useCallback(async (modelName = 'best') => {
    try {
      const data = await getConfusionMatrix(modelName)
      setMatrix(data)
      return data
    } catch (e) {
      // Non-fatal — just clear the matrix
      setMatrix(null)
      return null
    }
  }, [])

  return { metrics, matrix, loading, error, fetchMetrics, fetchMatrix }
}
