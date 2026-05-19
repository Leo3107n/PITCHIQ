import { useState } from 'react'
import { useTraining } from '../hooks/useTraining'
import PlayerForm from '../components/forms/PlayerForm'
import TrainingSuggestions from '../components/training/TrainingSuggestions'
import GapAnalysis from '../components/analysis/GapAnalysis'
import StrengthCard from '../components/analysis/StrengthCard'
import WeaknessCard from '../components/analysis/WeaknessCard'
import Loader from '../components/common/Loader'
import styles from './Training.module.css'

export default function Training() {
  const { plan, loading, error, fetchPlan } = useTraining()
  const [selectedPos, setSelectedPos] = useState(null)

  // PlayerForm calls onSubmit(attrs) — we forward to fetchPlan(attrs, position)
  const handleSubmit = (attrs) => {
    fetchPlan(attrs, selectedPos || null)
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Training Plan</h1>
        <p>Get a personalised weekly training plan based on your attribute gaps.</p>
      </div>

      <div className={styles.layout}>
        <div className={styles.formCol}>
          <PlayerForm onSubmit={handleSubmit} loading={loading} submitLabel="Generate Plan" />

          {/* Optional position override */}
          <div className={styles.posSelect}>
            <label htmlFor="posOverride">Target Position (optional)</label>
            <select
              id="posOverride"
              value={selectedPos || ''}
              onChange={e => setSelectedPos(e.target.value || null)}
            >
              <option value="">Auto-detect from attributes</option>
              {['GK','CB','LB','RB','CDM','CM','CAM','LW','RW','ST','CF'].map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
        </div>

        <div className={styles.results}>
          {loading && <Loader text="Building your training plan..." />}
          {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

          {plan && !loading && (
            <>
              <div className={styles.twoCol}>
                <StrengthCard strengths={plan.gap_analysis?.strengths} />
                <WeaknessCard weaknesses={plan.gap_analysis?.weaknesses} />
              </div>
              <GapAnalysis data={plan.gap_analysis} />
              <TrainingSuggestions plan={plan} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
