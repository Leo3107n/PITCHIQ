import { GiSoccerBall } from 'react-icons/gi'
import styles from './Footer.module.css'

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <GiSoccerBall className={styles.icon} />
      <span>PitchIQ &copy; {new Date().getFullYear()} — AI Football Intelligence Platform</span>
    </footer>
  )
}
