import client from './api'

export const getOverview = (attrs) =>
  client.post('/analytics/overview', attrs)

export const getPositionProfiles = () =>
  client.get('/analytics/position-profiles')

export const getSimilarPlayers = (attrs, top_n = 5) =>
  client.post('/cluster/similar', { ...attrs, top_n })

export const getClusterInfo = (attrs) =>
  client.post('/cluster/info', attrs)
