import { useState } from 'react'
import { getTrainingPlan } from '../services/trainingService'

export function useTraining() {
  const [plan, setPlan]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const fetchPlan = async (attrs, position = null) => {
    setLoading(true)
    setError(null)
    try {
      const data = await getTrainingPlan(attrs, position)
      setPlan(data)
      return data
    } catch (e) {
      setError(e?.error || (typeof e === 'string' ? e : 'Failed to load training plan.'))
      return null
    } finally {
      setLoading(false)
    }
  }

  return { plan, loading, error, fetchPlan }
}
