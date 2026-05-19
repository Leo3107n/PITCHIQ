import DrillCard from './DrillCard'
import WeeklyPlan from './WeeklyPlan'
import styles from './TrainingSuggestions.module.css'

export default function TrainingSuggestions({ plan }) {
  if (!plan) return null
  const { training_plan } = plan
  return (
    <div className={styles.wrapper}>
      <div className={styles.section}>
        <h3 className={styles.title}>Recommended Drills</h3>
        <div className={styles.drills}>
          {training_plan.drills.map((d, i) => <DrillCard key={i} drill={d} />)}
        </div>
      </div>
      <WeeklyPlan plan={training_plan.weekly_plan} />
    </div>
  )
}
