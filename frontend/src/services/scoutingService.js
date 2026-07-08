import client from './api'

export const generateScoutingReport = (payload) =>
  client.post('/scouting/report', payload)

export const getSavedReport = (sessionToken) =>
  client.get(`/scouting/${sessionToken}`)
