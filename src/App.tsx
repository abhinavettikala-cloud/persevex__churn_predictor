import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { Sidebar } from "@/src/components/layout/Sidebar"
import { Header } from "@/src/components/layout/Header"
import Dashboard from "@/src/pages/Dashboard"
import MakePrediction from "@/src/pages/MakePrediction"
import PredictionHistory from "@/src/pages/PredictionHistory"
import Analytics from "@/src/pages/Analytics"
import ModelPerformance from "@/src/pages/ModelPerformance"
import SystemStatus from "@/src/pages/SystemStatus"
import Settings from "@/src/pages/Settings"
import About from "@/src/pages/About"
import Reports from "@/src/pages/Reports"

export default function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-white text-slate-800 font-sans">
        <Sidebar />
        <div className="flex flex-1 flex-col md:pl-64">
          <Header />
          <main className="flex-1 overflow-y-auto bg-white flex flex-col min-w-0">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/predict" element={<MakePrediction />} />
              <Route path="/history" element={<PredictionHistory />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/performance" element={<ModelPerformance />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/status" element={<SystemStatus />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}
