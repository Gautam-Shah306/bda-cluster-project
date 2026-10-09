
import { Link } from 'react-router-dom';
import { useAuth } from '../context';
import { Activity, ShieldAlert, Map } from 'lucide-react';

export default function LandingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="h-16 flex items-center justify-between px-8 bg-secondary border-b border-gray-800">
        <h1 className="text-xl font-bold text-accent">Skills Mirage</h1>
        <nav className="flex items-center gap-4">
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn-primary">
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="btn-secondary">
                Login
              </Link>
              <Link to="/register" className="btn-primary">
                Sign Up
              </Link>
            </>
          )}
        </nav>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-5xl font-extrabold mb-6 tracking-tight">
            Future-Proof Your Workforce
          </h2>
          <p className="text-xl text-textSecondary mb-8">
            Navigate the shifting landscape of tech hiring. Discover real-time market trends, assess AI vulnerability, and empower your team with tailored reskilling pathways.
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/register" className="btn-primary px-8 py-3 text-lg">
              Get Started
            </Link>
            <Link to="/login" className="btn-secondary px-8 py-3 text-lg">
              Explore Demo
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full">
          <div className="card-glow">
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4">
              <Activity className="w-6 h-6 text-accent" />
            </div>
            <h3 className="text-xl font-bold mb-2">Market Signals</h3>
            <p className="text-textSecondary">
              Track surging skills and declining roles in real-time. Make data-driven hiring decisions with confidence.
            </p>
          </div>
          
          <div className="card-glow">
            <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center mb-4">
              <ShieldAlert className="w-6 h-6 text-red-400" />
            </div>
            <h3 className="text-xl font-bold mb-2">AI Vulnerability Index</h3>
            <p className="text-textSecondary">
              Identify which roles are most exposed to automation and prioritize workforce transformation effectively.
            </p>
          </div>
          
          <div className="card-glow">
            <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
              <Map className="w-6 h-6 text-green-400" />
            </div>
            <h3 className="text-xl font-bold mb-2">Reskilling Paths</h3>
            <p className="text-textSecondary">
              Generate personalized learning journeys to transition at-risk workers into high-demand engineering roles.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
