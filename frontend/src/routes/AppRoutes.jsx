import { Routes, Route } from 'react-router-dom'
import Home         from '../pages/Home'
import Dashboard    from '../pages/Dashboard'
import Predictions  from '../pages/Predictions'
import Analytics    from '../pages/Analytics'
import Training     from '../pages/Training'
import Sessions     from '../pages/Sessions'
import ModelMetrics from '../pages/ModelMetrics'
import About        from '../pages/About'
import NotFound     from '../pages/NotFound'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/"              element={<Home />} />
      <Route path="/dashboard"     element={<Dashboard />} />
      <Route path="/predictions"   element={<Predictions />} />
      <Route path="/analytics"     element={<Analytics />} />
      <Route path="/training"      element={<Training />} />
      <Route path="/sessions"      element={<Sessions />} />
      <Route path="/model-metrics" element={<ModelMetrics />} />
      <Route path="/about"         element={<About />} />
      <Route path="*"              element={<NotFound />} />
    </Routes>
  )
}
