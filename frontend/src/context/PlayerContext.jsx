import { createContext, useContext, useState } from 'react'
import { FEATURE_COLS } from '../utils/constants'

const PlayerContext = createContext(null)

const defaultAttrs = Object.fromEntries(FEATURE_COLS.map(c => [c, 60]))

export function PlayerProvider({ children }) {
  const [playerAttrs, setPlayerAttrs] = useState(defaultAttrs)
  const [playerName, setPlayerName]   = useState('')
  const [playerAge, setPlayerAge]     = useState(20)
  const [results, setResults]         = useState(null)   // last API results
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState(null)

  const updateAttr = (key, val) =>
    setPlayerAttrs(prev => ({ ...prev, [key]: Number(val) }))

  const resetAttrs = () => setPlayerAttrs(defaultAttrs)

  return (
    <PlayerContext.Provider value={{
      playerAttrs, setPlayerAttrs, updateAttr, resetAttrs,
      playerName, setPlayerName,
      playerAge, setPlayerAge,
      results, setResults,
      loading, setLoading,
      error, setError,
    }}>
      {children}
    </PlayerContext.Provider>
  )
}

export const usePlayer = () => useContext(PlayerContext)
