import { gapColor } from '../../utils/formatters'
import { POSITION_LABELS } from '../../utils/constants'
import styles from './GapAnalysis.module.css'

export default function GapAnalysis({ data }) {
  if (!data) return null
  const { position, gaps } = data
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.title}>Gap Analysis</h3>
        <span className={styles.pos}>{position} · {POSITION_LABELS[position] || ''}</span>
      </div>
      <div className={styles.grid}>
        {Object.entries(gaps).map(([attr, { player, ideal, gap }]) => {
          const color = gapColor(gap)
          const playerPct = (player / 99) * 100
          const idealPct  = (ideal  / 99) * 100
          return (
            <div key={attr} className={styles.row}>
              <div className={styles.rowHeader}>
                <span className={styles.attr}>{attr}</span>
                <div className={styles.vals}>
                  <span className={styles.player} style={{ color }}>{player}</span>
                  <span className={styles.ideal}>/ {ideal}</span>
                  <span className={styles.gap} style={{ color }}>
                    {gap >= 0 ? `+${gap}` : gap}
                  </span>
                </div>
              </div>
              <div className={styles.track}>
                <div className={styles.fill} style={{ width: `${playerPct}%`, background: color }} />
                <div className={styles['ideal-marker']} style={{ left: `${idealPct}%` }} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
