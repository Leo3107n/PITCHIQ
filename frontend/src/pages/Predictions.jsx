import { useState } from 'react'
import { usePlayer } from '../context/PlayerContext'
import { usePrediction } from '../hooks/usePrediction'
import { useScoutingReport } from '../hooks/useScoutingReport'
import PlayerForm from '../components/forms/PlayerForm'
import PredictionCard from '../components/prediction/PredictionCard'
import GapAnalysis from '../components/analysis/GapAnalysis'
import StrengthCard from '../components/analysis/StrengthCard'
import WeaknessCard from '../components/analysis/WeaknessCard'
import SimilarPlayers from '../components/prediction/SimilarPlayers'
import ScoutingReport from '../components/prediction/ScoutingReport'
import RadarChart from '../components/charts/RadarChart'
import PieChart from '../components/charts/PieChart'
import Loader from '../components/common/Loader'
import styles from './Predictions.module.css'

export default function Predictions() {
  const { playerAttrs, playerName, playerAge } = usePlayer()
  const { predictions, gap, fullResult, loading, error, runFullAnalysis, runGapAnalysis } = usePrediction()
  const { report, loading: reportLoading, error: reportError, generate, regenerate } = useScoutingReport()
  const [selectedPos, setSelectedPos] = useState(null)

  const handleSubmit = (attrs) => {
    setSelectedPos(null)
    runFullAnalysis(attrs, playerName, playerAge)
  }

  const handleSelectPosition = async (pos) => {
    setSelectedPos(pos)
    await runGapAnalysis(playerAttrs, pos)
  }

  const scoutingParams = { attrs: playerAttrs, playerName, playerAge, fullResult }

  // Build ideal attrs from gap data for radar overlay
  const idealAttrs = gap?.gaps
    ? Object.fromEntries(Object.entries(gap.gaps).map(([k, v]) => [k, v.ideal]))
    : null

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Position Prediction</h1>
        <p>Enter your attributes to discover your best positions and improvement areas.</p>
      </div>

      <div className={styles.layout}>
        <PlayerForm onSubmit={handleSubmit} loading={loading} submitLabel="Predict Positions" />

        <div className={styles.results}>
          {loading && <Loader text="Running ML analysis..." />}

          {/* Clean error message — never raw HTML */}
          {error && !loading && (
            <div className={styles.error}>
              {typeof error === 'string' ? error : 'An error occurred. Check that the backend is running.'}
            </div>
          )}

          {predictions && !loading && (
            <>
              <PredictionCard
                predictions={predictions}
                onSelectPosition={handleSelectPosition}
              />
              <PieChart predictions={predictions} />
            </>
          )}

          {gap && !loading && (
            <>
              <RadarChart
                playerAttrs={playerAttrs}
                idealAttrs={idealAttrs}
                position={gap.position}
              />
              <GapAnalysis data={gap} />
              <div className={styles.twoCol}>
                <StrengthCard strengths={gap.strengths} />
                <WeaknessCard weaknesses={gap.weaknesses} />
              </div>
            </>
          )}

          {fullResult?.similar_players?.length > 0 && !loading && (
            <SimilarPlayers players={fullResult.similar_players} />
          )}

          {/* AI Scouting Report — always rendered, isolated from ML results */}
          {(fullResult || report) && !loading && (
            <ScoutingReport
              report={report}
              loading={reportLoading}
              error={reportError}
              canRetry={true}
              hasAnalysis={!!fullResult}
              onGenerate={() => generate(scoutingParams)}
              onRegenerate={() => regenerate(scoutingParams)}
            />
          )}
        </div>
      </div>
    </div>
  )
}
