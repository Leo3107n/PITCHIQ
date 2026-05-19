import styles from './Button.module.css'

export default function Button({ children, variant = 'primary', onClick, disabled, type = 'button', fullWidth }) {
  return (
    <button
      type={type}
      className={`${styles.btn} ${styles[variant]} ${fullWidth ? styles.full : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}
