import { BrowserRouter } from 'react-router-dom'
import { PlayerProvider } from './context/PlayerContext'
import { ThemeProvider }  from './context/ThemeContext'
import Navbar    from './components/common/Navbar'
import Footer    from './components/common/Footer'
import AppRoutes from './routes/AppRoutes'

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <PlayerProvider>
          <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <Navbar />
            <main style={{ flex: 1 }}>
              <AppRoutes />
            </main>
            <Footer />
          </div>
        </PlayerProvider>
      </ThemeProvider>
    </BrowserRouter>
  )
}
