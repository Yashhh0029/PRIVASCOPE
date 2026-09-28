import React from 'react';
import { User, Shield, Server, Database, Lock, AlertCircle, Info } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="flex-1 p-8 max-w-4xl mx-auto w-full space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System & Account Settings</h1>
        <p className="text-xs text-priva-muted">Manage privacy profiles and review firewall configuration</p>
      </div>

      {/* User Profile Card */}
      <div className="p-6 rounded-xl border border-priva-border bg-priva-card space-y-4">
        <div className="flex items-center gap-3 border-b border-priva-border pb-4">
          <div className="w-10 h-10 rounded-full bg-priva-primary/10 border border-priva-primary/30 flex items-center justify-center text-priva-primary font-bold">
            {user?.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h3 className="font-semibold text-white text-sm">{user?.name}</h3>
            <p className="text-xs text-priva-muted font-mono">{user?.email}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-xs font-mono">
          <div>
            <span className="text-priva-muted block text-[10px] uppercase">User Role</span>
            <span className="text-slate-200 uppercase">{user?.role}</span>
          </div>
          <div>
            <span className="text-priva-muted block text-[10px] uppercase">Account Created</span>
            <span className="text-slate-200">{user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Active'}</span>
          </div>
        </div>
      </div>

      {/* Architecture & Telemetry Card */}
      <div className="p-6 rounded-xl border border-priva-border bg-priva-card space-y-4">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Server className="w-4 h-4 text-priva-primary" />
          <span>Firewall Deployment Specifications</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-3 rounded-lg bg-priva-bg border border-priva-border space-y-1">
            <span className="text-[10px] text-priva-muted uppercase block">Core Detection Engine</span>
            <span className="text-emerald-400 font-semibold">Local Hybrid (Air-Gapped)</span>
          </div>
          <div className="p-3 rounded-lg bg-priva-bg border border-priva-border space-y-1">
            <span className="text-[10px] text-priva-muted uppercase block">External LLM Dependency</span>
            <span className="text-emerald-400 font-semibold">None (0 Cloud Calls)</span>
          </div>
          <div className="p-3 rounded-lg bg-priva-bg border border-priva-border space-y-1">
            <span className="text-[10px] text-priva-muted uppercase block">File Redaction Layer</span>
            <span className="text-slate-200">PyMuPDF / openpyxl / Pillow</span>
          </div>
          <div className="p-3 rounded-lg bg-priva-bg border border-priva-border space-y-1">
            <span className="text-[10px] text-priva-muted uppercase block">Temporary File Retention</span>
            <span className="text-slate-200">24-Hour Lifecycle Purge</span>
          </div>
        </div>
      </div>

      {/* Official Product Policy Statement */}
      <div className="p-6 rounded-xl border border-priva-primary/30 bg-priva-primary/5 space-y-3">
        <div className="flex items-center gap-2 text-priva-primary">
          <Info className="w-4 h-4 shrink-0" />
          <h4 className="font-semibold text-xs uppercase tracking-wider font-mono">Product Risk Policy Disclaimer</h4>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          PRIVASCOPE's risk score is an application-defined risk model intended to prioritize privacy protection actions. It is not an official government risk classification. Always verify legal compliance according to your institutional regulations before transmitting personal identity information.
        </p>
      </div>
    </div>
  );
};
