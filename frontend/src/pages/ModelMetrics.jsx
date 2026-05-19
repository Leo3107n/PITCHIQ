import { useEffect, useState } from 'react'
import {
  MdBarChart, MdCheckCircle, MdTableChart, MdGridOn, MdInfo
} from 'react-icons/md'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, Cell
} from 'recharts'
import { useEvaluation } from '../hooks/useEvaluation'
import Loader from '../components/common/Loader'
import styles from './ModelMetrics.module.css'

/* ── Constants ────────────────────────────────────────────────────────────── */
const MODEL_NAMES = {
  knn:            'K-Nearest Neighbours',
  decision_tree:  'Decision Tree',
  random_forest:  'Random Forest',
  svm:            'Support Vector Machine',
  neural_network: 'Neural Network (MLP)',
}

const METRIC_COLORS = {
  Accuracy:  '#00e676',
  'F1 Score': '#40c4ff',
  Precision: '#ffab40',
  Recall:    '#b388ff',
}

const CARD_ACCENT = {
  knn:            '#00e676',
  decision_tree:  '#ff5252',
  random_forest:  '#ffab40',
  svm:            '#40c4ff',
  neural_network: '#b388ff',
}

/* ── Sub-components ───────────────────────────────────────────────────────── */
function MetricBar({ value, color }) {
  return (
    <div className={styles.metricBarTrack}>
      <div
        className={styles.metricBarFill}
        style={{ width: `${(value * 100).toFixed(1)}%`, background: color }}
      />
    </div>
  )
}

function SummaryTable({ models, bestModel, selected, onSelect }) {
  const rows = Object.entries(models)
  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Model</th>
            <th>Accuracy</th>
            <th>F1 Score</th>
            <th>Precision</th>
            <th>Recall</th>
          </tr>
        </thead>
        <tbody>
          {rows
            .sort((a, b) => b[1].f1 - a[1].f1)
            .map(([key, m]) => (
              <tr
                key={key}
                className={`
                  ${key === bestModel ? styles.bestRow : ''}
                  ${key === selected  ? styles.selectedRow : ''}
                `}
                onClick={() => onSelect(key)}
              >
                <td>
                  <div className={styles.modelNameCell}>
                    <span className={styles.modelFullName}>
                      {MODEL_NAMES[key] || key}
                      {key === bestModel && (
                        <span className={styles.bestTag}>
                          <MdCheckCircle /> Best
                        </span>
                      )}
                    </span>
                    <span className={styles.modelKeyName}>{key}</span>
                  </div>
                </td>
                <td style={{ color: '#00e676' }}>{(m.accuracy * 100).toFixed(2)}%</td>
                <td style={{ color: '#40c4ff' }}>{(m.f1       * 100).toFixed(2)}%</td>
                <td style={{ color: '#ffab40' }}>{(m.precision * 100).toFixed(2)}%</td>
                <td style={{ color: '#b388ff' }}>{(m.recall   * 100).toFixed(2)}%</td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  )
}

function ComparisonChart({ models }) {
  const data = Object.entries(models)
    .sort((a, b) => b[1].f1 - a[1].f1)
    .map(([key, m]) => ({
      name:      MODEL_NAMES[key]?.split(' ').slice(-1)[0] || key,  // short label
      fullName:  MODEL_NAMES[key] || key,
      Accuracy:  parseFloat((m.accuracy  * 100).toFixed(1)),
      'F1 Score': parseFloat((m.f1       * 100).toFixed(1)),
      Precision: parseFloat((m.precision * 100).toFixed(1)),
      Recall:    parseFloat((m.recall    * 100).toFixed(1)),
    }))

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    const full = data.find(d => d.name === label)?.fullName || label
    return (
      <div style={{
        background: 'var(--bg-card)', border: '1px solid var(--border)',
        borderRadius: 8, padding: '0.75rem 1rem', fontSize: '0.82rem'
      }}>
        <p style={{ fontWeight: 700, marginBottom: '0.4rem' }}>{full}</p>
        {payload.map(p => (
          <p key={p.name} style={{ color: p.fill }}>
            {p.name}: {p.value}%
          </p>
        ))}
      </div>
    )
  }

  return (
    <div className={styles.chartCard}>
      <div className={styles.chartTitle}>All Classifiers — Metric Comparison (%)</div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }} barGap={2}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e3024" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: '#7a9e82', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 100]} tick={{ fill: '#7a9e82', fontSize: 11 }} axisLine={false} tickLine={false} unit="%" />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: '#7a9e82', fontSize: 12 }} />
          {Object.entries(METRIC_COLORS).map(([metric, color]) => (
            <Bar key={metric} dataKey={metric} fill={color} radius={[3, 3, 0, 0]} maxBarSize={18} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function ModelCards({ models, bestModel, selected, onSelect }) {
  return (
    <div className={styles.modelGrid}>
      {Object.entries(models)
        .sort((a, b) => b[1].f1 - a[1].f1)
        .map(([key, m]) => {
          const accent = CARD_ACCENT[key] || 'var(--green)'
          const isBest = key === bestModel
          const isSel  = key === selected
          return (
            <div
              key={key}
              className={`${styles.modelCard} ${isBest ? styles.best : ''} ${isSel ? styles.selected : ''}`}
              onClick={() => onSelect(key)}
              role="button"
              tabIndex={0}
              onKeyDown={e => e.key === 'Enter' && onSelect(key)}
              aria-pressed={isSel}
            >
              {isBest && (
                <div className={styles.bestBadge}>
                  <MdCheckCircle /> Best
                </div>
              )}
              <div className={styles.modelName}>{MODEL_NAMES[key] || key}</div>
              <div className={styles.modelKey}>{key}</div>

              <div className={styles.metricsBlock}>
                {[
                  { label: 'Accuracy',  val: m.accuracy,  color: '#00e676' },
                  { label: 'F1 Score',  val: m.f1,        color: '#40c4ff' },
                  { label: 'Precision', val: m.precision, color: '#ffab40' },
                  { label: 'Recall',    val: m.recall,    color: '#b388ff' },
                ].map(({ label, val, color }) => (
                  <div key={label} className={styles.metricRow}>
                    <div className={styles.metricHeader}>
                      <span className={styles.metricLabel}>{label}</span>
                      <span className={styles.metricValue} style={{ color }}>
                        {(val * 100).toFixed(1)}%
                      </span>
                    </div>
                    <MetricBar value={val} color={color} />
                  </div>
                ))}
              </div>
            </div>
          )
        })}
    </div>
  )
}

function ConfusionMatrixPanel({ matrix, modelName }) {
  if (!matrix?.matrix || !matrix?.labels) return null
  const { matrix: cm, labels } = matrix
  const maxVal = Math.max(...cm.flat())
  const cols   = labels.length

  return (
    <div className={styles.cmCard}>
      <div className={styles.cmHeader}>
        <span className={styles.cmTitle}>
          Confusion Matrix — {MODEL_NAMES[modelName] || modelName}
        </span>
        <div className={styles.cmLegend}>
          <div className={styles.cmLegendItem}>
            <div className={styles.cmLegendDot} style={{ background: 'rgba(0,200,83,0.7)' }} />
            Correct
          </div>
          <div className={styles.cmLegendItem}>
            <div className={styles.cmLegendDot} style={{ background: 'rgba(255,82,82,0.5)' }} />
            Incorrect
          </div>
        </div>
      </div>
      <p className={styles.cmSubtitle}>
        Rows = actual position · Columns = predicted · Diagonal = correct predictions
      </p>

      <div className={styles.cmWrapper}>
        <div
          className={styles.cmGrid}
          style={{ gridTemplateColumns: `64px repeat(${cols}, 1fr)` }}
        >
          {/* Corner */}
          <div className={styles.cmCorner}>Actual ↓<br />Pred →</div>
          {/* Column headers */}
          {labels.map(l => (
            <div key={l} className={styles.cmColHeader}>{l}</div>
          ))}
          {/* Rows */}
          {cm.map((row, i) => (
            <>
              <div key={`lbl-${i}`} className={styles.cmRowLabel}>{labels[i]}</div>
              {row.map((val, j) => {
                const intensity = maxVal > 0 ? val / maxVal : 0
                const isDiag    = i === j
                return (
                  <div
                    key={`${i}-${j}`}
                    className={styles.cmCell}
                    title={`Actual: ${labels[i]} → Predicted: ${labels[j]}  (${val})`}
                    style={{
                      background: isDiag
                        ? `rgba(0,200,83,${0.12 + intensity * 0.75})`
                        : `rgba(255,82,82,${intensity * 0.55})`,
                      color: intensity > 0.45 ? '#fff' : 'var(--text-muted)',
                    }}
                  >
                    {val}
                  </div>
                )
              })}
            </>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ── Main page ────────────────────────────────────────────────────────────── */
export default function ModelMetrics() {
  const { metrics, matrix, loading, error, fetchMetrics, fetchMatrix } = useEvaluation()
  const [selected, setSelected] = useState(null)

  // Load all metrics on mount, then load confusion matrix for best model
  useEffect(() => {
    fetchMetrics().then(data => {
      const best = data?.best_model || 'best'
      setSelected(best)
      fetchMatrix(best)
    })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // When user clicks a card/row, load that model's confusion matrix
  const handleSelect = (key) => {
    setSelected(key)
    fetchMatrix(key)
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1>Model Performance</h1>
        <p>
          Accuracy, F1, Precision and Recall for all 5 classifiers trained on
          51,878 real FIFA player profiles. Click any model to view its confusion matrix.
        </p>
      </div>

      {loading && <Loader text="Loading model metrics..." />}
      {error   && <p style={{ color: 'var(--danger)' }}>{error}</p>}

      {metrics && !loading && (
        <>
          {/* ── 1. Summary table ─────────────────────────────────────── */}
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>
              <MdTableChart /> Performance Summary
            </h2>
            <SummaryTable
              models={metrics.models}
              bestModel={metrics.best_model}
              selected={selected}
              onSelect={handleSelect}
            />
          </div>

          {/* ── 2. Bar chart ──────────────────────────────────────────── */}
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>
              <MdBarChart /> Classifier Comparison
            </h2>
            <ComparisonChart models={metrics.models} />
          </div>

          {/* ── 3. Model cards ────────────────────────────────────────── */}
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>
              <MdGridOn /> Detailed Metrics
            </h2>
            <ModelCards
              models={metrics.models}
              bestModel={metrics.best_model}
              selected={selected}
              onSelect={handleSelect}
            />
          </div>

          {/* ── 4. Confusion matrix ───────────────────────────────────── */}
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>
              <MdInfo /> Confusion Matrix
              {selected && (
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400 }}>
                  — {MODEL_NAMES[selected] || selected}
                </span>
              )}
            </h2>
            {matrix
              ? <ConfusionMatrixPanel matrix={matrix} modelName={selected} />
              : <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  Select a model above to view its confusion matrix.
                </p>
            }
          </div>
        </>
      )}
    </div>
  )
}
