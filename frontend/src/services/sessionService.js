import client from './api'

export const listSessions = (limit = 20, offset = 0) =>
  client.get(`/sessions/?limit=${limit}&offset=${offset}`)

export const getSession = (token) =>
  client.get(`/sessions/${token}`)

export const deleteSession = (token) =>
  client.delete(`/sessions/${token}`)
