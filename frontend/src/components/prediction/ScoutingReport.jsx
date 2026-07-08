import { MdAutoAwesome, MdRefresh, MdErrorOutline } from 'react-icons/md'
import { GiSoccerBall } from 'react-icons/gi'
import styles from './ScoutingReport.module.css'

/**
 * ScoutingReport
 * Renders the AI-generated scouting report card on the Predictions page.
 * Fully isolated — errors here never affect the ML predictions above it.
 *
 * Props:
 *   report    {string|null}  — the report text if already generated
 *   loading   {bool}
 *   error     {string|null}
 *   canRetry  {bool}        — whether the error allows retrying
 *   onGenerate {fn}         — called when user clicks "Generate Report"
 *   onRegenerate {fn}       — called when user clicks "Regenerate"
 *   hasAnalysis {bool}      — whether ML results exist (guards the button)
 */
export default function ScoutingReport({
  report, loading, error, canRetry = true,
  onGenerate, onRegenerate, hasAnalysis,
}) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.titleRow}>
          <MdAutoAwesome className={styles.icon} />
          <span className={styles.title}>AI Scouting Report</span>
          <span className={styles.badge}>Powered by AI</span>
        </div>

        {/* Actions row */}
        <div className={styles.actions}>
          {!report && !loading && (
            <button
              className={styles.generateBtn}
              onClick={onGenerate}
              disabled={!hasAnalysis || loading}
            >
              <MdAutoAwesome />
              Generate Report
            </button>
          )}
          {report && !loading && (
            <button className={styles.regenBtn} onClick={onRegenerate}>
              <MdRefresh style={{ verticalAlign: 'middle', marginRight: 4 }} />
              Regenerate
            </button>
          )}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className={styles.loadingBox}>
          <div className={styles.spinner} />
          <span>Writing your scouting report…</span>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className={styles.errorBox}>
          <MdErrorOutline className={styles.errorIcon} />
          <span className={styles.errorText}>{error}</span>
          {canRetry && (
            <button className={styles.retryBtn} onClick={onGenerate}>
              Try again
            </button>
          )}
        </div>
      )}

      {/* Report text — split on double-newlines into paragraphs */}
      {report && !loading && (
        <div className={styles.reportText}>
          {report.split(/\n\n+/).map((para, i) => (
            <p key={i}>{para.trim()}</p>
          ))}
        </div>
      )}

      {/* Prompt state — no report yet, no error, not loading */}
      {!report && !error && !loading && (
        <div className={styles.prompt}>
          <div className={styles.promptIcon}><GiSoccerBall /></div>
          {hasAnalysis
            ? 'Click "Generate Report" to get an AI-written scouting assessment of your player profile.'
            : 'Run a position analysis first, then generate your scouting report.'}
        </div>
      )}
    </div>
  )
}
