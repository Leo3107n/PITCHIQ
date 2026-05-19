import styles from './ConfidenceBar.module.css'

export default function ConfidenceBar({ value, color = 'var(--green)' }) {
  return (
    <div className={styles.track}>
      <div className={styles.fill} style={{ width: `${value}%`, background: color }} />
    </div>
  )
}
