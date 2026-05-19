import { MdTrendingUp } from 'react-icons/md'
import { capitalize } from '../../utils/formatters'
import styles from './StrengthCard.module.css'

export default function StrengthCard({ strengths }) {
  if (!strengths?.length) return null
  return (
    <div className={styles.card}>
      <h3 className={styles.title}><MdTrendingUp /> Strengths</h3>
      <div className={styles.list}>
        {strengths.map(s => (
          <div key={s.attribute} className={styles.row}>
            <span className={styles.attr}>{capitalize(s.attribute)}</span>
            <span className={styles.val}>{s.value}</span>
            <span className={styles.surplus}>+{s.surplus} above ideal</span>
          </div>
        ))}
      </div>
    </div>
  )
}
