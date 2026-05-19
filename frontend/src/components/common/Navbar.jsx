import { useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { GiSoccerBall } from 'react-icons/gi'
import styles from './Navbar.module.css'

const NAV_LINKS = [
  { to: '/',             label: 'Home'       },
  { to: '/dashboard',    label: 'Dashboard'  },
  { to: '/predictions',  label: 'Predict'    },
  { to: '/analytics',    label: 'Analytics'  },
  { to: '/training',     label: 'Training'   },
  { to: '/sessions',     label: 'Sessions'   },
  { to: '/model-metrics',label: 'Models'     },
  { to: '/about',        label: 'About'      },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()

  const close = () => setOpen(false)

  return (
    <>
      <nav className={styles.nav}>
        <Link to="/" className={styles.brand} onClick={close}>
          <GiSoccerBall className={styles.logo} />
          <span>Pitch<strong>IQ</strong></span>
        </Link>

        {/* Desktop */}
        <ul className={styles.links}>
          {NAV_LINKS.map(({ to, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={to === '/'}
                className={({ isActive }) => isActive ? styles.active : undefined}
              >
                {label}
              </NavLink>
            </li>
          ))}
        </ul>

        {/* Hamburger */}
        <button
          className={`${styles.hamburger} ${open ? styles.open : ''}`}
          onClick={() => setOpen(o => !o)}
          aria-label="Toggle menu"
          aria-expanded={open}
        >
          <span /><span /><span />
        </button>
      </nav>

      {/* Mobile drawer */}
      <div className={`${styles.drawer} ${open ? styles.open : ''}`}>
        {NAV_LINKS.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => isActive ? styles.active : undefined}
            onClick={close}
          >
            {label}
          </NavLink>
        ))}
      </div>
    </>
  )
}
