import {
  PieChart as RePie, Pie, Cell, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

const COLORS = ['#00e676','#69f0ae','#b9f6ca','#ffab40','#ff8a65']

export default function PieChart({ predictions }) {
  if (!predictions?.length) return null
  const data = predictions.slice(0, 5).map(p => ({
    name: p.position,
    value: parseFloat(p.confidence.toFixed(1)),
  }))

  return (
    <ResponsiveContainer width="100%" height={260}>
      <RePie>
        <Pie data={data} cx="50%" cy="50%" outerRadius={90}
          dataKey="value" nameKey="name" label={({ name, value }) => `${name} ${value}%`}
          labelLine={{ stroke: '#1e3024' }}>
          {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#111a14', border: '1px solid #1e3024', borderRadius: 8 }}
        />
        <Legend wrapperStyle={{ color: '#7a9e82', fontSize: 12 }} />
      </RePie>
    </ResponsiveContainer>
  )
}
