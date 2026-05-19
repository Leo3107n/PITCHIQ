export const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1)

export const formatConfidence = (val) => `${val.toFixed(1)}%`

export const ratingColor = (val) => {
  if (val >= 75) return '#00e676'
  if (val >= 55) return '#ffab40'
  return '#ff5252'
}

export const gapColor = (gap) => {
  if (gap >= 0) return '#00e676'
  if (gap >= -15) return '#ffab40'
  return '#ff5252'
}
