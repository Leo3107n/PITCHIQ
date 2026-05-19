import client from './api'

export const predictPositions = (attrs) =>
  client.post('/predict/positions', attrs)

export const gapAnalysis = (attrs, position) =>
  client.post('/predict/gap-analysis', { ...attrs, position })

export const fullAnalysis = (attrs, playerName = '', playerAge = 0, save = true) =>
  client.post('/predict/full', { ...attrs, player_name: playerName, player_age: playerAge, save })
