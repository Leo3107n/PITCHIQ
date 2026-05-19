/**
 * LineChart — shows attribute values as a connected line for quick profile scanning.
 */
import {
  LineChart as ReLine, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts'
import { FEATURE_COLS, ATTRIBUTE_COLORS } from '../../utils/constants'
import { capitalize } from '../../utils/formatters'

export default function LineChart({ playerAttrs, idealAttrs }) {
  const data = FEATURE_COLS.map(col => ({
    name:   capitalize(col),
    Player: playerAttrs?.[col] ?? 0,
    ...(idealAttrs ? { Ideal: idealAttrs[col] ?? 0 } : {}),
  }))

  return (
    <ResponsiveContainer width="100%" height={240}>
      <ReLine data={data} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e3024" vertical={false} />
        <XAxis dataKey="name" tick={{ fill: '#7a9e82', fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis domain={[0, 99]} tick={{ fill: '#7a9e82', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{ background: '#111a14', border: '1px solid #1e3024', borderRadius: 8 }}
          labelStyle={{ color: '#e8f5e9' }}
        />
        <ReferenceLine y={50} stroke="#1e3024" strokeDasharray="4 2" />
        <Line type="monotone" dataKey="Player"
          stroke="#00e676" strokeWidth={2} dot={{ fill: '#00e676', r: 4 }} />
        {idealAttrs && (
          <Line type="monotone" dataKey="Ideal"
            stroke="#ffab40" strokeWidth={2} strokeDasharray="5 3"
            dot={{ fill: '#ffab40', r: 3 }} />
        )}
      </ReLine>
    </ResponsiveContainer>
  )
}
