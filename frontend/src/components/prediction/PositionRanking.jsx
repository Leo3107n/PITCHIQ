import { POSITION_LABELS } from '../../utils/constants'
import ConfidenceBar from './ConfidenceBar'
import styles from './PositionRanking.module.css'

const MEDAL_COLORS = ['#FFD700', '#C0C0C0', '#CD7F32', '#69f0ae', '#b9f6ca']

/**
 * PositionRanking — compact ranked list of predicted positions.
 * Designed for embedding in dashboards or sidebars.
 */
export default function PositionRanking({ predictions, onSelect }) {
  if (!predictions?.length) return null

  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Position Ranking</h3>
      <div className={styles.list}>
        {predictions.map((p, i) => (
          <div
            key={p.position}
            className={styles.row}
            onClick={() => onSelect?.(p.position)}
            role="button"
            tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && onSelect?.(p.position)}
          >
            <div className={styles.medal} style={{ color: MEDAL_COLORS[i] }}>
              {i + 1}
            </div>
            <div className={styles.info}>
              <div className={styles.posRow}>
                <span className={styles.pos}>{p.position}</span>
                <span className={styles.label}>{POSITION_LABELS[p.position] || ''}</span>
                <span className={styles.conf} style={{ color: MEDAL_COLORS[i] }}>
                  {p.confidence.toFixed(1)}%
                </span>
              </div>
              <ConfidenceBar value={p.confidence} color={MEDAL_COLORS[i]} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
