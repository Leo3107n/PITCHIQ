import client from './api'

export const getTrainingPlan = (attrs, position = null) =>
  client.post('/training/plan', position ? { ...attrs, position } : attrs)
