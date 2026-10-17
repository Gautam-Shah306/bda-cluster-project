import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import DashboardLayout from './layout/DashboardLayout';
import Overview from './pages/dashboard/Overview';
import HiringTrends from './pages/dashboard/HiringTrends';
import SkillsIntelligence from './pages/dashboard/SkillsIntelligence';
import AIVulnerability from './pages/dashboard/AIVulnerability';
import WorkerIntelligence from './pages/dashboard/WorkerIntelligence';
import ReskillingPath from './pages/dashboard/ReskillingPath';
import Chatbot from './pages/dashboard/Chatbot';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          {/* Auth routes redirect to dashboard — login/register removed */}
          <Route path="/login" element={<Navigate to="/dashboard" replace />} />
          <Route path="/register" element={<Navigate to="/dashboard" replace />} />

          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<Overview />} />
            <Route path="hiring-trends" element={<HiringTrends />} />
            <Route path="skills" element={<SkillsIntelligence />} />
            <Route path="vulnerability" element={<AIVulnerability />} />
            <Route path="worker" element={<WorkerIntelligence />} />
            <Route path="reskilling" element={<ReskillingPath />} />
            <Route path="chatbot" element={<Chatbot />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
