/**
 * ClusterChart — visualises cluster membership as a scatter-like bar chart.
 * Shows the average attribute profile of the player's cluster vs the player.
 */
import {
  RadarChart as ReRadar, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend
} from 'recharts'
import { FEATURE_COLS } from '../../utils/constants'
import { capitalize } from '../../utils/formatters'

export default function ClusterChart({ playerAttrs, clusterAvg, clusterId }) {
  if (!playerAttrs || !clusterAvg) return null

  const data = FEATURE_COLS.map(col => ({
    attribute: capitalize(col),
    Player:  playerAttrs[col] ?? 0,
    Cluster: Math.round(clusterAvg[col] ?? 0),
  }))

  return (
    <div>
      {clusterId != null && (
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
          Cluster #{clusterId} average profile
        </p>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <ReRadar data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
          <PolarGrid stroke="#1e3024" />
          <PolarAngleAxis dataKey="attribute" tick={{ fill: '#7a9e82', fontSize: 11 }} />
          <PolarRadiusAxis domain={[0, 99]} tick={false} axisLine={false} />
          <Radar name="You" dataKey="Player"
            stroke="#00e676" fill="#00e676" fillOpacity={0.25} />
          <Radar name="Cluster Avg" dataKey="Cluster"
            stroke="#ffab40" fill="#ffab40" fillOpacity={0.1} strokeDasharray="4 2" />
          <Tooltip
            contentStyle={{ background: '#111a14', border: '1px solid #1e3024', borderRadius: 8 }}
          />
          <Legend wrapperStyle={{ color: '#7a9e82', fontSize: 12 }} />
        </ReRadar>
      </ResponsiveContainer>
    </div>
  )
}
