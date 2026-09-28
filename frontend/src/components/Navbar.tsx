import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Shield,
  LogOut,
  User as UserIcon,
  Menu,
  X,
  LayoutDashboard,
  ShieldAlert,
  ScanLine,
  History,
  ScrollText,
  Settings
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

const MOBILE_NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/ai-firewall', label: 'AI Privacy Firewall', icon: Shield, badge: 'GATEWAY' },
  { to: '/scan', label: 'Document Firewall', icon: ScanLine },
  { to: '/history', label: 'Scan History', icon: History },
  { to: '/audit', label: 'Audit Trail', icon: ScrollText },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [backendHealth, setBackendHealth] = useState<'checking' | 'online' | 'offline'>('checking');
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  // Close mobile drawer on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Prevent background scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [mobileMenuOpen]);

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
    <header className="h-16 border-b border-priva-border bg-priva-card/80 backdrop-blur-md sticky top-0 z-40 px-3.5 sm:px-6 flex items-center justify-between">
      {/* Brand & Mobile Hamburger */}
      <div className="flex items-center gap-2.5 sm:gap-3">
        {user && (
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors focus:outline-none focus:ring-1 focus:ring-cyan-500/30"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5 text-cyan-400" /> : <Menu className="w-5 h-5" />}
          </button>
        )}

        <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-2.5 sm:gap-3 group">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-priva-primary/10 border border-priva-primary/30 flex items-center justify-center text-priva-primary group-hover:border-priva-primary transition-colors shrink-0">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 sm:gap-2">
              <span className="font-bold text-base sm:text-lg tracking-wider text-white">PRIVASCOPE</span>
              <span className="text-[9px] sm:text-[10px] px-1.5 py-0.5 rounded bg-priva-primary/20 text-priva-accent border border-priva-primary/30 font-mono font-semibold">
                FIREWALL
              </span>
            </div>
            <p className="text-[10px] sm:text-[11px] text-priva-muted hidden sm:block">Indian Personal Data Privacy Guard</p>
          </div>
        </Link>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2 sm:gap-4">
        {/* Backend Health Telemetry */}
        <div className="flex items-center gap-1.5 text-xs px-2 sm:px-2.5 py-1 rounded-full border border-priva-border bg-priva-bg/80 shrink-0">
          <span
            className={`w-2 h-2 rounded-full ${
              backendHealth === 'online'
                ? 'bg-priva-low animate-pulse'
                : backendHealth === 'checking'
                ? 'bg-priva-medium'
                : 'bg-priva-critical'
            }`}
          />
          <span className="text-priva-muted text-[10px] sm:text-[11px] font-mono uppercase">
            <span className="hidden sm:inline">API </span>{backendHealth}
          </span>
        </div>

        {user ? (
          <div className="flex items-center gap-2 sm:gap-3">
            {/* User display */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-priva-border bg-priva-bg text-sm">
              <UserIcon className="w-3.5 h-3.5 text-priva-primary shrink-0" />
              <span className="text-slate-200 text-xs font-medium truncate max-w-[120px]">{user.name}</span>
            </div>

            {/* Logout button */}
            <button
              onClick={logout}
              title="Logout"
              className="p-2 rounded-lg border border-priva-border hover:border-priva-critical/50 hover:text-priva-critical text-priva-muted transition-colors focus:outline-none"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 sm:gap-3">
            <Link
              to="/login"
              className="text-xs font-medium text-slate-300 hover:text-white px-2.5 sm:px-3 py-1.5 rounded-lg border border-transparent hover:border-priva-border transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="text-xs font-medium text-white bg-priva-primary hover:bg-priva-primaryHover px-3 sm:px-3.5 py-1.5 rounded-lg shadow-sm transition-colors"
            >
              Get Started
            </Link>
          </div>
        )}
      </div>

      {/* Mobile Slide-Over Navigation Drawer */}
      {user && mobileMenuOpen && (
        <div className="fixed inset-0 top-16 z-50 lg:hidden">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => setMobileMenuOpen(false)}
          />

          {/* Drawer Content */}
          <div className="relative w-72 max-w-[85vw] h-full bg-slate-900 border-r border-slate-800 p-5 flex flex-col justify-between overflow-y-auto shadow-2xl">
            <div className="space-y-6">
              {/* User Identity Pill in Drawer */}
              <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                <div className="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-cyan-400 font-bold text-sm shrink-0">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="overflow-hidden">
                  <p className="text-xs font-semibold text-white truncate">{user.name}</p>
                  <p className="text-[10px] text-slate-400 font-mono truncate">{user.email}</p>
                </div>
              </div>

              {/* Navigation Links */}
              <div>
                <p className="text-[10px] font-mono uppercase tracking-wider text-slate-400 px-2 mb-2 flex items-center justify-between">
                  <span>Navigation</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                </p>
                <nav className="space-y-1">
                  {MOBILE_NAV_ITEMS.map((item) => {
                    const Icon = item.icon;
                    const isActive =
                      location.pathname === item.to ||
                      (item.to !== '/' && location.pathname.startsWith(`${item.to}/`));

                    return (
                      <Link
                        key={item.to}
                        to={item.to}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-colors ${
                          isActive
                            ? 'bg-indigo-500/15 border border-indigo-500/40 text-cyan-300 shadow-sm'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                        }`}
                      >
                        <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                        <span className="flex-1 tracking-tight">{item.label}</span>
                        {item.badge && (
                          <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    );
                  })}
                </nav>
              </div>
            </div>

            {/* Mobile Footer Area with Logout & Engine Disclaimer */}
            <div className="space-y-3 pt-6 border-t border-slate-800/80">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  logout();
                }}
                className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 text-xs font-medium transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out of Firewall</span>
              </button>

              <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/60 text-[10px] text-slate-400 space-y-1">
                <div className="flex items-center gap-1.5 text-cyan-400 font-semibold">
                  <ShieldAlert className="w-3 h-3" />
                  <span>Air-Gapped Privacy Engine</span>
                </div>
                <p className="leading-relaxed">Zero external LLM dependence. Local context fusion active.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
