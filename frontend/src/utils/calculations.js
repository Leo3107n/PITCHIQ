import { FEATURE_COLS } from './constants'

export const overallRating = (attrs) => {
  const vals = FEATURE_COLS.map(c => Number(attrs[c]) || 0)
  return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)
}

export const normalizeToPercent = (val, min = 1, max = 99) =>
  Math.round(((val - min) / (max - min)) * 100)
