import { usePlayer } from '../context/PlayerContext'
import { useAnalytics } from '../hooks/useAnalytics'
import { usePrediction } from '../hooks/usePrediction'
import PlayerForm from '../components/forms/PlayerForm'
import RadarChart from '../components/charts/RadarChart'
import BarChart from '../components/charts/BarChart'
import SimilarPlayers from '../components/prediction/SimilarPlayers'
import GapAnalysis from '../components/analysis/GapAnalysis'
import StrengthCard from '../components/analysis/StrengthCard'
import WeaknessCard from '../components/analysis/WeaknessCard'
import Loader from '../components/common/Loader'
import styles from './Analytics.module.css'

export default function Analytics() {
  const { playerAttrs } = usePlayer()
  const { overview, similar, loading, error, fetchOverview } = useAnalytics()
  const { gap, runGapAnalysis } = usePrediction()

  // Fix: use returned data directly — don't rely on stale state
  const handleSubmit = async (attrs) => {
    const data = await fetchOverview(attrs)
    if (data?.top_position) {
      await runGapAnalysis(attrs, data.top_position)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Analytics</h1>
        <p>Deep-dive into your attribute profile and player comparisons.</p>
      </div>

      <div className={styles.layout}>
        <PlayerForm onSubmit={handleSubmit} loading={loading} submitLabel="Analyze" />

        <div className={styles.results}>
          {loading && <Loader />}
          {error && <p className={styles.error}>{error}</p>}

          {overview && !loading && (
            <>
              <div className={styles.grid2}>
                <div className={styles.card}>
                  <div className={styles.cardTitle}>Attribute Radar</div>
                  <RadarChart
                    playerAttrs={playerAttrs}
                    idealAttrs={gap?.gaps ? Object.fromEntries(
                      Object.entries(gap.gaps).map(([k, v]) => [k, v.ideal])
                    ) : null}
                    position={overview.top_position}
                  />
                </div>
                <div className={styles.card}>
                  <div className={styles.cardTitle}>Attribute Breakdown</div>
                  <BarChart playerAttrs={playerAttrs} />
                </div>
              </div>

              {gap && <GapAnalysis data={gap} />}

              {gap && (
                <div className={styles.grid2}>
                  <StrengthCard strengths={gap.strengths} />
                  <WeaknessCard weaknesses={gap.weaknesses} />
                </div>
              )}

              <div className={styles.card}>
                <div className={styles.cardTitle}>Similar Players in Database</div>
                <SimilarPlayers players={similar} />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
