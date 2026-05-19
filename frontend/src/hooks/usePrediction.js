import { useState } from 'react'
import { predictPositions, gapAnalysis, fullAnalysis } from '../services/predictionService'

export function usePrediction() {
  const [predictions, setPredictions] = useState(null)
  const [gap, setGap]                 = useState(null)
  const [fullResult, setFullResult]   = useState(null)
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState(null)

  const predict = async (attrs) => {
    setLoading(true)
    setError(null)
    try {
      const data = await predictPositions(attrs)
      setPredictions(data.predictions)
      // Auto-run gap analysis for top position
      if (data.predictions?.length) {
        const topPos = data.predictions[0].position
        const gapData = await gapAnalysis(attrs, topPos)
        setGap(gapData)
      }
    } catch (e) {
      setError(e?.error || (typeof e === 'string' ? e : 'Prediction failed.'))
    } finally {
      setLoading(false)
    }
  }

  const runGapAnalysis = async (attrs, position) => {
    setLoading(true)
    setError(null)
    try {
      const data = await gapAnalysis(attrs, position)
      setGap(data)
      return data
    } catch (e) {
      setError(e?.error || (typeof e === 'string' ? e : 'Gap analysis failed.'))
      return null
    } finally {
      setLoading(false)
    }
  }

  const runFullAnalysis = async (attrs, playerName, playerAge) => {
    setLoading(true)
    setError(null)
    try {
      const data = await fullAnalysis(attrs, playerName, playerAge, true)
      setFullResult(data)
      setPredictions(data.predictions)
      setGap(data.gap_analysis)
      return data
    } catch (e) {
      setError(e?.error || (typeof e === 'string' ? e : 'Analysis failed.'))
      return null
    } finally {
      setLoading(false)
    }
  }

  return { predictions, gap, fullResult, loading, error, predict, runGapAnalysis, runFullAnalysis }
}
