import styles from './WeeklyPlan.module.css'

export default function WeeklyPlan({ plan }) {
  if (!plan?.length) return null
  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Weekly Training Plan</h3>
      <div className={styles.grid}>
        {plan.map(({ day, drills, rest }) => (
          <div key={day} className={`${styles.day} ${rest ? styles.rest : ''}`}>
            <div className={styles.dayName}>{day}</div>
            {rest ? (
              <div className={styles.restLabel}>Rest / Recovery</div>
            ) : (
              <ul className={styles.drillList}>
                {drills.map((d, i) => <li key={i}>{d.name}</li>)}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
