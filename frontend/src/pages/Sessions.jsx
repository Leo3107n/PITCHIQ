import { useEffect, useState } from 'react'
import { MdHistory, MdDelete, MdVisibility, MdClose } from 'react-icons/md'
import { useSessions } from '../hooks/useSessions'
import { FEATURE_COLS, POSITION_LABELS } from '../utils/constants'
import Loader from '../components/common/Loader'
import styles from './Sessions.module.css'

function SessionModal({ session, onClose }) {
  if (!session) return null
  const overall = Math.round(
    FEATURE_COLS.reduce((s, c) => s + (session[c] ?? 0), 0) / FEATURE_COLS.length
  )
  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <div className={styles.modalTitle}>
            {session.player_name || 'Anonymous'}
            {session.player_age ? ` · Age ${session.player_age}` : ''}
          </div>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
            <MdClose />
          </button>
        </div>

        <div className={styles.detailGrid}>
          {/* Attributes */}
          <div className={styles.detailCard} style={{ gridColumn: '1 / -1' }}>
            <div className={styles.detailLabel}>Attributes</div>
            <div className={styles.attrGrid}>
              {FEATURE_COLS.map(c => (
                <div key={c} className={styles.attrItem}>
                  <div className={styles.attrVal}>{session[c]}</div>
                  <div className={styles.attrName}>{c}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Predictions */}
          {session.predictions?.length > 0 && (
            <div className={styles.detailCard}>
              <div className={styles.detailLabel}>Position Predictions</div>
              <div className={styles.predList}>
                {session.predictions.slice(0, 5).map(p => (
                  <div key={p.position} className={styles.predRow}>
                    <span className={styles.predPos}>{p.position} · {POSITION_LABELS[p.position]}</span>
                    <span className={styles.predConf}>{p.confidence.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Cluster */}
          {session.cluster_info && (
            <div className={styles.detailCard}>
              <div className={styles.detailLabel}>Cluster Info</div>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                Cluster #{session.cluster_info.cluster_id} · {session.cluster_info.cluster_size} players
              </p>
              <p style={{ fontSize: '0.88rem', marginTop: '0.5rem' }}>
                Style: {Object.keys(session.cluster_info.dominant_positions || {}).join(', ')}
              </p>
            </div>
          )}
        </div>

        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Session: {session.session_token} · {new Date(session.created_at).toLocaleString()}
        </p>
      </div>
    </div>
  )
}

export default function Sessions() {
  const { sessions, total, loading, error, fetchSessions, fetchSession, removeSession } = useSessions()
  const [activeSession, setActiveSession] = useState(null)

  useEffect(() => { fetchSessions() }, [fetchSessions])

  const handleView = async (token) => {
    const data = await fetchSession(token)
    if (data) setActiveSession(data)
  }

  const handleDelete = async (token) => {
    if (window.confirm('Delete this session?')) {
      await removeSession(token)
      if (activeSession?.session_token === token) setActiveSession(null)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Past Sessions</h1>
        <p>{total} saved analysis session{total !== 1 ? 's' : ''}</p>
      </div>

      {loading && <Loader />}
      {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

      {!loading && sessions.length === 0 && (
        <div className={styles.empty}>
          <div className={styles.emptyIcon}><MdHistory /></div>
          <p>No sessions yet. Run a full analysis to save your first session.</p>
        </div>
      )}

      {sessions.length > 0 && (
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Player</th>
              <th>Age</th>
              <th>Overall</th>
              <th>Top Position</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map(s => {
              const overall = Math.round(
                FEATURE_COLS.reduce((acc, c) => acc + (s[c] ?? 0), 0) / FEATURE_COLS.length
              )
              return (
                <tr key={s.session_token}>
                  <td>
                    <div style={{ fontWeight: 600 }}>{s.player_name || 'Anonymous'}</div>
                    <div className={styles.token}>{s.session_token.slice(0, 8)}…</div>
                  </td>
                  <td>{s.player_age || '—'}</td>
                  <td><span className={styles.rating}>{overall}</span></td>
                  <td>
                    {s.predictions?.[0]?.position
                      ? <span className={styles.pos}>{s.predictions[0].position}</span>
                      : '—'}
                  </td>
                  <td>
                    <span className={styles.date}>
                      {new Date(s.created_at).toLocaleDateString()}
                    </span>
                  </td>
                  <td>
                    <div className={styles.actions}>
                      <button className={styles.viewBtn} onClick={() => handleView(s.session_token)}>
                        <MdVisibility style={{ verticalAlign: 'middle', marginRight: 4 }} />
                        View
                      </button>
                      <button className={styles.delBtn} onClick={() => handleDelete(s.session_token)}
                        aria-label="Delete session">
                        <MdDelete />
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}

      {activeSession && (
        <SessionModal session={activeSession} onClose={() => setActiveSession(null)} />
      )}
    </div>
  )
}
