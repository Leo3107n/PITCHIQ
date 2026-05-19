import { useState } from 'react'
import { getOverview } from '../services/analyticsService'

export function useAnalytics() {
  const [overview, setOverview] = useState(null)
  const [similar, setSimilar]   = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  // Returns the fetched data directly so callers don't depend on stale state
  const fetchOverview = async (attrs) => {
    setLoading(true)
    setError(null)
    try {
      const data = await getOverview(attrs)
      setOverview(data)
      // overview endpoint already returns similar_players — no second call needed
      setSimilar(data.similar_players ?? [])
      return data
    } catch (e) {
      const msg = e?.error || (typeof e === 'string' ? e : 'Analytics failed.')
      setError(msg)
      return null
    } finally {
      setLoading(false)
    }
  }

  return { overview, similar, loading, error, fetchOverview }
}
