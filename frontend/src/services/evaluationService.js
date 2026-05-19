import client from './api'

export const getAllModelMetrics = () =>
  client.get('/evaluate/models')

export const getModelMetrics = (name) =>
  client.get(`/evaluate/models/${name}`)

export const getConfusionMatrix = (name = 'best') =>
  client.get(`/evaluate/confusion-matrix/${name}`)
