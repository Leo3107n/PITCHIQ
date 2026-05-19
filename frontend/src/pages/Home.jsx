import { Link } from 'react-router-dom'
import { GiSoccerBall } from 'react-icons/gi'
import { MdAnalytics, MdSportsScore, MdFitnessCenter } from 'react-icons/md'
import Button from '../components/common/Button'
import styles from './Home.module.css'

const FEATURES = [
  { icon: <MdSportsScore />, title: 'Position Prediction', desc: 'ML models analyze your attributes and predict your top 5 suitable positions with confidence scores.' },
  { icon: <MdAnalytics />,   title: 'Gap Analysis',        desc: 'Compare your stats against ideal position profiles to pinpoint exactly where you need to improve.' },
  { icon: <GiSoccerBall />,  title: 'Player Clustering',   desc: 'K-Means clustering finds players with similar playing styles from a database of 51,878 real FIFA player profiles.' },
  { icon: <MdFitnessCenter />, title: 'Training Plans',    desc: 'Personalized weekly training plans generated from your data — no hardcoded rules.' },
]

export default function Home() {
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <div className={styles.badge}><GiSoccerBall /> AI Football Intelligence</div>
          <h1 className={styles.headline}>
            Discover Your <span>True Position</span><br />with Machine Learning
          </h1>
          <p className={styles.sub}>
            PitchIQ analyzes your football attributes to predict suitable positions,
            identify weaknesses, and generate personalized training plans — built for
            amateur and developing players.
          </p>
          <div className={styles.cta}>
            <Link to="/predictions"><Button>Get Your Analysis</Button></Link>
            <Link to="/about"><Button variant="ghost">Learn More</Button></Link>
          </div>
        </div>
        <div className={styles.heroVisual}>
          <div className={styles.pitch}>
            {['GK','CB','LB','RB','CDM','CM','CAM','LW','RW','ST'].map(p => (
              <div key={p} className={styles.posPin}>{p}</div>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.features}>
        <h2 className={styles.sectionTitle}>What PitchIQ Does</h2>
        <div className={styles.featureGrid}>
          {FEATURES.map(f => (
            <div key={f.title} className={styles.featureCard}>
              <div className={styles.featureIcon}>{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.cta2}>
        <h2>Ready to find your position?</h2>
        <p>Enter your attributes and let the AI do the rest.</p>
        <Link to="/predictions"><Button>Start Analysis</Button></Link>
      </section>
    </div>
  )
}
