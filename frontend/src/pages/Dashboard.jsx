import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { usePlayer } from '../context/PlayerContext'
import { useAnalytics } from '../hooks/useAnalytics'
import { overallRating } from '../utils/calculations'
import { POSITION_LABELS } from '../utils/constants'
import RadarChart from '../components/charts/RadarChart'
import BarChart from '../components/charts/BarChart'
import SimilarPlayers from '../components/prediction/SimilarPlayers'
import Loader from '../components/common/Loader'
import Button from '../components/common/Button'
import styles from './Dashboard.module.css'

export default function Dashboard() {
  const { playerAttrs, playerName } = usePlayer()
  const { overview, similar, loading, error, fetchOverview } = useAnalytics()
  const overall = overallRating(playerAttrs)
  const hasFetched = useRef(false)

  // Fetch once on mount — ref guard prevents double-fire in StrictMode
  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true
      fetchOverview(playerAttrs)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Dashboard{playerName ? ` — ${playerName}` : ''}</h1>
        <p>Your player overview and performance snapshot.</p>
      </div>

      <div className={styles.statsRow}>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Overall Rating</span>
          <span className={styles.statValue}>{overall}</span>
          <span className={styles.statSub}>Average across all attributes</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Top Position</span>
          <span className={styles.statValue} style={{ fontSize: '1.4rem' }}>
            {overview?.top_position || '—'}
          </span>
          <span className={styles.statSub}>
            {POSITION_LABELS[overview?.top_position] || 'Run analysis first'}
          </span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Confidence</span>
          <span className={styles.statValue}>
            {overview?.predictions?.[0]?.confidence != null
              ? `${overview.predictions[0].confidence.toFixed(1)}%`
              : '—'}
          </span>
          <span className={styles.statSub}>Top position confidence</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Similar Players</span>
          <span className={styles.statValue}>{similar?.length ?? '—'}</span>
          <span className={styles.statSub}>Found in database</span>
        </div>
      </div>

      {loading && <Loader />}
      {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

      {!loading && (
        <div className={styles.grid}>
          <div className={styles.card}>
            <div className={styles.cardTitle}>Attribute Radar</div>
            <RadarChart playerAttrs={playerAttrs} />
          </div>
          <div className={styles.card}>
            <div className={styles.cardTitle}>Attribute Breakdown</div>
            <BarChart playerAttrs={playerAttrs} />
          </div>
          <div className={styles.card}>
            <div className={styles.cardTitle}>Similar Players</div>
            {similar?.length
              ? <SimilarPlayers players={similar} />
              : <p className={styles.empty}>No data yet — run an analysis.</p>}
          </div>
          <div className={styles.card} style={{
            display: 'flex', flexDirection: 'column',
            gap: '1rem', justifyContent: 'center', alignItems: 'center'
          }}>
            <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>
              Ready to get your full position analysis?
            </p>
            <Link to="/predictions"><Button>Run Prediction</Button></Link>
            <Link to="/training"><Button variant="ghost">Get Training Plan</Button></Link>
            <Link to="/sessions"><Button variant="secondary">View Past Sessions</Button></Link>
          </div>
        </div>
      )}
    </div>
  )
}
