import {
  RadarChart as ReRadar, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend
} from 'recharts'
import { FEATURE_COLS, ATTRIBUTE_COLORS } from '../../utils/constants'
import { capitalize } from '../../utils/formatters'

export default function RadarChart({ playerAttrs, idealAttrs, position }) {
  const data = FEATURE_COLS.map(col => ({
    attribute: capitalize(col),
    Player: playerAttrs?.[col] ?? 0,
    ...(idealAttrs ? { Ideal: idealAttrs[col] ?? 0 } : {}),
  }))

  return (
    <ResponsiveContainer width="100%" height={320}>
      <ReRadar data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
        <PolarGrid stroke="#1e3024" />
        <PolarAngleAxis dataKey="attribute" tick={{ fill: '#7a9e82', fontSize: 12 }} />
        <PolarRadiusAxis domain={[0, 99]} tick={false} axisLine={false} />
        <Radar name="Player" dataKey="Player" stroke="#00e676" fill="#00e676" fillOpacity={0.25} />
        {idealAttrs && (
          <Radar name={`Ideal ${position || ''}`} dataKey="Ideal"
            stroke="#ffab40" fill="#ffab40" fillOpacity={0.1} strokeDasharray="4 2" />
        )}
        <Tooltip
          contentStyle={{ background: '#111a14', border: '1px solid #1e3024', borderRadius: 8 }}
          labelStyle={{ color: '#e8f5e9' }}
        />
        {idealAttrs && <Legend wrapperStyle={{ color: '#7a9e82', fontSize: 12 }} />}
      </ReRadar>
    </ResponsiveContainer>
  )
}
