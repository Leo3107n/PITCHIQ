import { useState, useCallback } from 'react'
import { listSessions, getSession, deleteSession } from '../services/sessionService'

export function useSessions() {
  const [sessions, setSessions] = useState([])
  const [total, setTotal]       = useState(0)
  const [session, setSession]   = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  const fetchSessions = useCallback(async (limit = 20, offset = 0) => {
    setLoading(true)
    setError(null)
    try {
      const data = await listSessions(limit, offset)
      setSessions(data.sessions)
      setTotal(data.total)
    } catch (e) {
      setError(e?.error || 'Failed to load sessions.')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchSession = useCallback(async (token) => {
    setLoading(true)
    setError(null)
    try {
      const data = await getSession(token)
      setSession(data)
      return data
    } catch (e) {
      setError(e?.error || 'Session not found.')
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const removeSession = useCallback(async (token) => {
    try {
      await deleteSession(token)
      setSessions(prev => prev.filter(s => s.session_token !== token))
      setTotal(prev => prev - 1)
    } catch (e) {
      setError(e?.error || 'Failed to delete session.')
    }
  }, [])

  return { sessions, total, session, loading, error, fetchSessions, fetchSession, removeSession }
}
