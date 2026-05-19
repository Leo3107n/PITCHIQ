import { Link } from 'react-router-dom'
import Button from '../components/common/Button'
import styles from './NotFound.module.css'

export default function NotFound() {
  return (
    <div className={styles.page}>
      <div className={styles.code}>404</div>
      <h1>Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <Link to="/"><Button>Back to Home</Button></Link>
    </div>
  )
}
