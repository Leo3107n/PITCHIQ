import { ratingColor, capitalize } from '../../utils/formatters'
import styles from './InputSlider.module.css'

export default function InputSlider({ name, value, onChange }) {
  const color = ratingColor(value)
  // Compute fill % in JS — avoids CSS calc() cross-browser issues
  const pct = `${((value - 1) / 98) * 100}%`
  const bg  = `linear-gradient(to right, ${color} 0%, ${color} ${pct}, var(--border) ${pct})`

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <span className={styles.label}>{capitalize(name)}</span>
        <span className={styles.value} style={{ color }}>{value}</span>
      </div>
      <input
        type="range"
        min={1}
        max={99}
        value={value}
        onChange={(e) => onChange(name, Number(e.target.value))}
        className={styles.slider}
        style={{ '--fill': color, background: bg }}
        aria-label={capitalize(name)}
        aria-valuemin={1}
        aria-valuemax={99}
        aria-valuenow={value}
      />
      <div className={styles.ticks}>
        <span>1</span><span>25</span><span>50</span><span>75</span><span>99</span>
      </div>
    </div>
  )
}
