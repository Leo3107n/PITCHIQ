import { usePlayer } from '../../context/PlayerContext'
import { FEATURE_COLS } from '../../utils/constants'
import { overallRating } from '../../utils/calculations'
import InputSlider from './InputSlider'
import Button from '../common/Button'
import { MdPerson } from 'react-icons/md'
import styles from './PlayerForm.module.css'

export default function PlayerForm({ onSubmit, submitLabel = 'Analyze', loading }) {
  const { playerAttrs, updateAttr, resetAttrs, playerName, setPlayerName, playerAge, setPlayerAge } = usePlayer()
  const overall = overallRating(playerAttrs)

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit?.(playerAttrs)
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.title}><MdPerson /> Player Attributes</div>

      <div className={styles.meta}>
        <div className={styles.field}>
          <label htmlFor="pname">Player Name</label>
          <input id="pname" type="text" placeholder="e.g. Carlos Silva"
            value={playerName} onChange={e => setPlayerName(e.target.value)} />
        </div>
        <div className={styles.field}>
          <label htmlFor="page">Age</label>
          <input id="page" type="number" min={14} max={45} placeholder="20"
            value={playerAge} onChange={e => setPlayerAge(Number(e.target.value))} />
        </div>
      </div>

      <div className={styles.overall}>
        Overall Rating: <strong>{overall}</strong>
      </div>

      <div className={styles.grid}>
        {FEATURE_COLS.map(col => (
          <InputSlider key={col} name={col} value={playerAttrs[col]} onChange={updateAttr} />
        ))}
      </div>

      <div className={styles.actions}>
        <Button type="submit" disabled={loading} fullWidth>
          {loading ? 'Analyzing...' : submitLabel}
        </Button>
        <Button type="button" variant="secondary" onClick={resetAttrs}>Reset</Button>
      </div>
    </form>
  )
}
