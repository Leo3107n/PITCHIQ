import { GiSoccerBall } from 'react-icons/gi'
import { MdAnalytics, MdSportsScore, MdFitnessCenter, MdGroup } from 'react-icons/md'
import styles from './About.module.css'

const TECH = [
  { label: 'Frontend', items: ['React 18', 'Vite', 'Recharts', 'CSS Modules'] },
  { label: 'Backend',  items: ['Flask', 'Flask-CORS', 'Python 3.11'] },
  { label: 'ML',       items: ['scikit-learn', 'Random Forest', 'KNN', 'SVM', 'K-Means'] },
  { label: 'Data',     items: ['51,878 real FIFA player profiles', 'male_players.csv dataset', 'StandardScaler', 'LabelEncoder'] },
]

export default function About() {
  return (
    <div className={styles.page}>
      <div className={styles.hero}>
        <GiSoccerBall className={styles.icon} />
        <h1>About PitchIQ</h1>
        <p>
          PitchIQ is an AI-powered football player analysis system designed for amateur
          and developing players who don't have access to professional performance profiling.
        </p>
      </div>

      <div className={styles.section}>
        <h2>How It Works</h2>
        <div className={styles.steps}>
          {[
            { icon: <MdSportsScore />, title: '1. Enter Attributes', desc: 'Input your pace, shooting, passing, dribbling, defending, physical, stamina, strength, agility, and vision ratings.' },
            { icon: <MdAnalytics />,   title: '2. ML Analysis',      desc: 'Our ensemble of Random Forest, KNN, and SVM classifiers predict your top 5 positions with confidence scores.' },
            { icon: <MdGroup />,       title: '3. Gap Analysis',     desc: 'Your stats are compared against ideal position profiles to identify strengths and weaknesses.' },
            { icon: <MdFitnessCenter />, title: '4. Training Plan',  desc: 'K-Means clustering and gap data generate a personalized weekly training plan with specific drills.' },
          ].map(s => (
            <div key={s.title} className={styles.step}>
              <div className={styles.stepIcon}>{s.icon}</div>
              <h3>{s.title}</h3>
              <p>{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.section}>
        <h2>Technology Stack</h2>
        <div className={styles.techGrid}>
          {TECH.map(t => (
            <div key={t.label} className={styles.techCard}>
              <h3>{t.label}</h3>
              <ul>{t.items.map(i => <li key={i}>{i}</li>)}</ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
