import { POSITION_LABELS } from '../../utils/constants'
import styles from './SimilarPlayers.module.css'

export default function SimilarPlayers({ players }) {
  if (!players?.length) return null
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Similar Players</h3>
      <div className={styles.list}>
        {players.map((p, i) => (
          <div key={i} className={styles.row}>
            <div className={styles.avatar}>{p.name.charAt(0)}</div>
            <div className={styles.info}>
              <div className={styles.name}>{p.name}</div>
              <div className={styles.pos}>{p.position} · {POSITION_LABELS[p.position] || ''}</div>
            </div>
            <div className={styles.sim}>{p.similarity}%</div>
          </div>
        ))}
      </div>
    </div>
  )
}
