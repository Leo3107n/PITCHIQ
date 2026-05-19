import { POSITION_LABELS } from '../../utils/constants'
import ConfidenceBar from './ConfidenceBar'
import styles from './PredictionCard.module.css'

const RANK_COLORS = ['#00e676','#69f0ae','#b9f6ca','#ffab40','#ff8a65']

export default function PredictionCard({ predictions, onSelectPosition }) {
  if (!predictions?.length) return null
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Position Predictions</h3>
      <div className={styles.list}>
        {predictions.map((p, i) => (
          <div key={p.position} className={styles.row}
            onClick={() => onSelectPosition?.(p.position)}
            role="button" tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && onSelectPosition?.(p.position)}>
            <div className={styles.rank} style={{ color: RANK_COLORS[i] }}>#{i + 1}</div>
            <div className={styles.info}>
              <div className={styles.posRow}>
                <span className={styles.pos}>{p.position}</span>
                <span className={styles.posLabel}>{POSITION_LABELS[p.position] || ''}</span>
                <span className={styles.conf} style={{ color: RANK_COLORS[i] }}>
                  {p.confidence.toFixed(1)}%
                </span>
              </div>
              <ConfidenceBar value={p.confidence} color={RANK_COLORS[i]} />
            </div>
          </div>
        ))}
      </div>
      <p className={styles.hint}>Click a position to run gap analysis</p>
    </div>
  )
}
