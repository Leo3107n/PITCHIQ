import { useState } from 'react'
import { generateScoutingReport } from '../services/scoutingService'

export function useScoutingReport() {
  const [report,  setReport]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  /**
   * Build the full payload from existing ML results and request an AI report.
   * Never re-runs ML analysis — purely a summarisation layer.
   */
  const generate = async ({ attrs, playerName, playerAge, fullResult }) => {
    if (!fullResult) return
    setLoading(true)
    setError(null)
    try {
      const payload = {
        ...attrs,
        player_name:     playerName || '',
        player_age:      playerAge  || 0,
        predictions:     fullResult.predictions,
        gap_analysis:    fullResult.gap_analysis,
        similar_players: fullResult.similar_players || [],
        session_token:   fullResult.session_token   || null,
      }
      const data = await generateScoutingReport(payload)
      setReport(data.report)
      return data.report
    } catch (e) {
      setError(e?.error || 'Failed to generate scouting report.')
      return null
    } finally {
      setLoading(false)
    }
  }

  const regenerate = (params) => {
    setReport(null)
    return generate(params)
  }

  return { report, loading, error, generate, regenerate }
}
