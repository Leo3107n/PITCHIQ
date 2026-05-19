import { MdArrowUpward } from 'react-icons/md'
import { capitalize } from '../../utils/formatters'
import styles from './ImprovementArea.module.css'

/**
 * ImprovementArea — shows the top N attributes to improve with a progress bar
 * showing current vs ideal value.
 */
export default function ImprovementArea({ weaknesses, maxShow = 4 }) {
  if (!weaknesses?.length) return null
  const items = weaknesses.slice(0, maxShow)

  return (
    <div className={styles.card}>
      <h3 className={styles.title}><MdArrowUpward /> Priority Improvements</h3>
      <div className={styles.list}>
        {items.map(w => {
          const playerPct = (w.value / 99) * 100
          const idealPct  = (w.ideal  / 99) * 100
          return (
            <div key={w.attribute} className={styles.item}>
              <div className={styles.row}>
                <span className={styles.attr}>{capitalize(w.attribute)}</span>
                <span className={styles.vals}>
                  <span className={styles.current}>{w.value}</span>
                  <span className={styles.arrow}>→</span>
                  <span className={styles.ideal}>{w.ideal}</span>
                  <span className={styles.deficit}>−{w.deficit}</span>
                </span>
              </div>
              <div className={styles.track}>
                <div className={styles.fill}
                  style={{ width: `${playerPct}%`, background: 'var(--danger)' }} />
                <div className={styles.idealMark}
                  style={{ left: `${idealPct}%` }} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
