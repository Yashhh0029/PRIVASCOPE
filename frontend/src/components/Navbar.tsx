import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, ShieldAlert, ShieldCheck, LogOut, User as UserIcon, Activity } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [backendHealth, setBackendHealth] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const check = async () => {
      try {
        await api.checkHealth();
        setBackendHealth('online');
      } catch {
        setBackendHealth('offline');
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 border-b border-priva-border bg-priva-card/70 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
      {/* Brand */}
      <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-3 group">
        <div className="w-10 h-10 rounded-lg bg-priva-primary/10 border border-priva-primary/30 flex items-center justify-center text-priva-primary group-hover:border-priva-primary transition-colors">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg tracking-wider text-white">PRIVASCOPE</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-priva-primary/20 text-priva-accent border border-priva-primary/30 font-mono">
              FIREWALL
            </span>
          </div>
          <p className="text-[11px] text-priva-muted hidden sm:block">Indian Personal Data Privacy Guard</p>
        </div>
      </Link>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Backend Health Telemetry */}
        <div className="flex items-center gap-2 text-xs px-2.5 py-1 rounded-full border border-priva-border bg-priva-bg/80">
          <span
            className={`w-2 h-2 rounded-full ${
              backendHealth === 'online'
                ? 'bg-priva-low animate-pulse'
                : backendHealth === 'checking'
                ? 'bg-priva-medium'
                : 'bg-priva-critical'
            }`}
          />
          <span className="text-priva-muted text-[11px] font-mono uppercase">
            API {backendHealth}
          </span>
        </div>

        {user ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-priva-border bg-priva-bg text-sm">
              <UserIcon className="w-4 h-4 text-priva-primary" />
              <span className="text-slate-200 text-xs font-medium">{user.name}</span>
            </div>
            <button
              onClick={logout}
              title="Logout"
              className="p-2 rounded-lg border border-priva-border hover:border-priva-critical/50 hover:text-priva-critical text-priva-muted transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-transparent hover:border-priva-border transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="text-xs font-medium text-white bg-priva-primary hover:bg-priva-primaryHover px-3.5 py-1.5 rounded-lg shadow-sm transition-colors"
            >
              Get Started
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
