import { MdTrendingDown } from 'react-icons/md'
import { capitalize } from '../../utils/formatters'
import styles from './WeaknessCard.module.css'

export default function WeaknessCard({ weaknesses }) {
  if (!weaknesses?.length) return null
  return (
    <div className={styles.card}>
      <h3 className={styles.title}><MdTrendingDown /> Areas to Improve</h3>
      <div className={styles.list}>
        {weaknesses.map(w => (
          <div key={w.attribute} className={styles.row}>
            <span className={styles.attr}>{capitalize(w.attribute)}</span>
            <span className={styles.val}>{w.value}</span>
            <span className={styles.deficit}>-{w.deficit} below ideal</span>
          </div>
        ))}
      </div>
    </div>
  )
}
