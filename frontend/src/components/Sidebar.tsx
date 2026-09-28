import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, useReducedMotion } from 'framer-motion';
import {
  LayoutDashboard,
  ScanLine,
  History,
  ScrollText,
  Settings,
  ShieldAlert,
  Shield
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/ai-firewall', label: 'AI Privacy Firewall', icon: Shield, badge: 'GATEWAY' },
  { to: '/scan', label: 'Document Firewall', icon: ScanLine },
  { to: '/history', label: 'Scan History', icon: History },
  { to: '/audit', label: 'Audit Trail', icon: ScrollText },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const shouldReduceMotion = useReducedMotion();

  return (
    <aside className="hidden lg:flex w-64 border-r border-priva-border/80 bg-priva-card/60 backdrop-blur-md flex-col justify-between py-6 px-4 shrink-0 min-h-[calc(100vh-4rem)] relative z-20">
      <div className="space-y-6">
        <div>
          <p className="text-[10px] font-mono uppercase tracking-wider text-slate-400 px-3 mb-2 flex items-center justify-between">
            <span>Navigation</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          </p>
          <nav className="space-y-1 relative">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.to || (item.to !== '/' && location.pathname.startsWith(`${item.to}/`));

              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={`group relative flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? 'text-white'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  {/* Moving Active Background & Indicator */}
                  {isActive && (
                    <>
                      <motion.div
                        layoutId={shouldReduceMotion ? undefined : "active-sidebar-pill"}
                        className="absolute inset-0 rounded-lg bg-indigo-500/10 border border-indigo-500/30 shadow-sm"
                        transition={{ type: "spring", stiffness: 350, damping: 32 }}
                      />
                      <motion.div
                        layoutId={shouldReduceMotion ? undefined : "active-sidebar-bar"}
                        className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.7)]"
                        transition={{ type: "spring", stiffness: 350, damping: 32 }}
                      />
                    </>
                  )}

                  <Icon className={`w-4 h-4 relative z-10 transition-transform duration-200 group-hover:translate-x-0.5 ${
                    isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'
                  }`} />
                  <span className="flex-1 relative z-10 tracking-tight">{item.label}</span>
                  {item.badge && (
                    <span className="relative z-10 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-xs">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Security Engine Disclaimer */}
      <div className="p-3.5 rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md text-[11px] text-slate-400 space-y-1.5 shadow-sm">
        <div className="flex items-center gap-1.5 text-cyan-400 font-semibold text-xs">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>Local Engine Active</span>
        </div>
        <p className="leading-relaxed text-[11px] text-slate-400">
          Zero external LLM dependence. Verhoeff, regex, and context fusion run on local backend.
        </p>
      </div>
    </aside>
  );
};
