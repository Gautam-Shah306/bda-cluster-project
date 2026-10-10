
import { Link, Outlet, useLocation } from 'react-router-dom';
import ErrorBoundary from '../components/ErrorBoundary';
import { 
  LayoutDashboard, 
  TrendingUp, 
  Brain, 
  ShieldAlert, 
  UserSquare2, 
  Map, 
  MessageSquare, 
  LogOut,
  Activity
} from 'lucide-react';
import { useAuth } from '../context';

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <div className="flex h-screen bg-background text-textPrimary">
      {/* Sidebar */}
      <aside className="w-64 bg-secondary border-r border-gray-800 flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold text-accent">Skills Mirage</h1>
        </div>
        
        <nav className="flex-1 overflow-y-auto py-4">
          <div className="px-6 mb-2">
            <h2 className="text-xs font-semibold text-textSecondary uppercase tracking-wider">
              Core Intelligence
            </h2>
          </div>
          <div className="space-y-1 mb-6">
            <Link to="/dashboard" className="flex items-center px-6 py-2 hover:bg-gray-800 transition-colors">
              <LayoutDashboard className="w-5 h-5 mr-3 text-gray-400" />
              <span>Dashboard</span>
            </Link>
            <Link to="/dashboard/hiring-trends" className="flex items-center px-6 py-2 hover:bg-gray-800 transition-colors">
              <TrendingUp className="w-5 h-5 mr-3 text-gray-400" />
              <span>Hiring Trends</span>
            </Link>
            <Link to="/dashboard/skills" className="flex items-center px-6 py-2 hover:bg-gray-800 transition-colors">
              <Brain className="w-5 h-5 mr-3 text-gray-400" />
              <span>Skills Intelligence</span>
            </Link>
            <Link to="/dashboard/vulnerability" className="flex items-center px-6 py-2 hover:bg-gray-800 transition-colors">
              <ShieldAlert className="w-5 h-5 mr-3 text-gray-400" />
              <span>AI Vulnerability Index</span>
            </Link>
          </div>

          <div className="px-6 mb-2">
            <h2 className="text-xs font-semibold text-textSecondary uppercase tracking-wider">
              Worker Action
            </h2>
          </div>
          <div className="space-y-1">
            <Link to="/dashboard/worker" className="flex items-center px-6 py-2 hover:bg-gray-800 transition-colors">
              <UserSquare2 className="w-5 h-5 mr-3 text-gray-400" />
              <span>Worker Analysis</span>
            </Link>
            <Link to="/dashboard/reskilling" className="flex items-center px-6 py-2 hover:bg-gray-800 transition-colors">
              <Map className="w-5 h-5 mr-3 text-gray-400" />
              <span>Reskilling Paths</span>
            </Link>
            <Link to="/dashboard/chatbot" className="flex items-center px-6 py-2 hover:bg-gray-800 transition-colors">
              <MessageSquare className="w-5 h-5 mr-3 text-gray-400" />
              <span>AI Chatbot</span>
            </Link>
          </div>
        </nav>
        
        <div className="p-4 border-t border-gray-800">
          <button 
            onClick={logout}
            className="flex items-center w-full px-2 py-2 text-textSecondary hover:text-white transition-colors"
          >
            <LogOut className="w-5 h-5 mr-3" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* TopBar */}
        <header className="h-16 bg-secondary border-b border-gray-800 flex items-center justify-between px-8 shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
              <Activity className="w-4 h-4 text-green-400" />
              <span className="text-sm font-medium text-green-400">System Live</span>
            </div>
            <span className="text-sm text-textSecondary font-medium px-3 py-1 bg-gray-800 rounded-full border border-gray-700">
              Hackathon Demo
            </span>
          </div>
          
          <div className="flex items-center">
            <span className="text-sm font-medium text-textPrimary">
              {user?.name || "Administrator"}
            </span>
            <div className="w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center ml-3 font-bold">
              {(user?.name || "A").charAt(0).toUpperCase()}
            </div>
          </div>
        </header>
        
        {/* Scrollable Page Area */}
        <div className="flex-1 overflow-auto p-8">
          <div className="max-w-7xl mx-auto">
            <ErrorBoundary resetKey={location.pathname}>
              <Outlet />
            </ErrorBoundary>
          </div>
        </div>
      </main>
    </div>
  );
}


