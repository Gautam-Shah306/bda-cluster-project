import { ReactNode } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context';
import DashboardLayout from './layout/DashboardLayout';
import LandingPage from './pages/LandingPage';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Overview from './pages/dashboard/Overview';
import HiringTrends from './pages/dashboard/HiringTrends';
import SkillsIntelligence from './pages/dashboard/SkillsIntelligence';
import AIVulnerability from './pages/dashboard/AIVulnerability';
import WorkerIntelligence from './pages/dashboard/WorkerIntelligence';
import ReskillingPath from './pages/dashboard/ReskillingPath';
import Chatbot from './pages/dashboard/Chatbot';
import NotFound from './pages/NotFound';

const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Overview />} />
        <Route path="hiring-trends" element={<HiringTrends />} />
        <Route path="skills" element={<SkillsIntelligence />} />
        <Route path="vulnerability" element={<AIVulnerability />} />
        <Route path="worker" element={<WorkerIntelligence />} />
        <Route path="reskilling" element={<ReskillingPath />} />
        <Route path="chatbot" element={<Chatbot />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}


