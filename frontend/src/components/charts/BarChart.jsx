import {
  BarChart as ReBar, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { FEATURE_COLS, ATTRIBUTE_COLORS } from '../../utils/constants'
import { capitalize } from '../../utils/formatters'

export default function BarChart({ playerAttrs }) {
  const data = FEATURE_COLS.map(col => ({
    name: capitalize(col),
    value: playerAttrs?.[col] ?? 0,
    fill: ATTRIBUTE_COLORS[col],
  }))

  return (
    <ResponsiveContainer width="100%" height={260}>
      <ReBar data={data} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e3024" vertical={false} />
        <XAxis dataKey="name" tick={{ fill: '#7a9e82', fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis domain={[0, 99]} tick={{ fill: '#7a9e82', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{ background: '#111a14', border: '1px solid #1e3024', borderRadius: 8 }}
          cursor={{ fill: 'rgba(255,255,255,0.04)' }}
        />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {data.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
        </Bar>
      </ReBar>
    </ResponsiveContainer>
  )
}
