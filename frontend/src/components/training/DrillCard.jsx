import { MdFitnessCenter, MdTimer } from 'react-icons/md'
import { capitalize } from '../../utils/formatters'
import styles from './DrillCard.module.css'

export default function DrillCard({ drill }) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <MdFitnessCenter className={styles.icon} />
        <div>
          <div className={styles.name}>{drill.name}</div>
          <div className={styles.focus}>{capitalize(drill.focus_attribute)}</div>
        </div>
        <div className={styles.duration}><MdTimer />{drill.duration}</div>
      </div>
      <p className={styles.desc}>{drill.description}</p>
    </div>
  )
}
