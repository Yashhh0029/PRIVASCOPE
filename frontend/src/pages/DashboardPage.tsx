import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, useReducedMotion } from 'framer-motion';
import {
  FileText,
  ShieldCheck,
  AlertTriangle,
  Fingerprint,
  ArrowRight,
  Download,
  Loader2,
  ScanLine,
  Activity,
  Layers,
  Shield
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { api } from '../services/api';
import { DashboardStats } from '../types';
import { 
  StaggerContainer, 
  StaggerItem, 
  HoverCard, 
  AnimatedNumber, 
  ScrollReveal 
} from '../components/motion/MotionSystem';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await api.getDashboardStats();
        setStats(data);
      } catch (err) {
        console.error("Failed to load dashboard statistics:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 min-h-[60vh] space-y-3">
        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-xs font-mono text-slate-400 uppercase tracking-wider">Synchronizing Telemetry...</p>
      </div>
    );
  }

  const piiChartData = stats
    ? Object.entries(stats.pii_distribution).map(([type, count]) => ({
        name: type.replace('_', ' '),
        count,
      }))
    : [];

  const riskChartData = stats
    ? [
        { name: 'Low', value: stats.risk_distribution['LOW'] || 0, color: '#10B981' },
        { name: 'Medium', value: stats.risk_distribution['MEDIUM'] || 0, color: '#F59E0B' },
        { name: 'High', value: stats.risk_distribution['HIGH'] || 0, color: '#F97316' },
        { name: 'Critical', value: stats.risk_distribution['CRITICAL'] || 0, color: '#EF4444' },
      ].filter(item => item.value > 0)
    : [];

  const isEmpty = !stats || stats.total_scans === 0;

  return (
    <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto w-full relative z-10">
      {/* Command Center Header */}
      <motion.div 
        initial={shouldReduceMotion ? {} : { opacity: 0, y: -12, filter: 'blur(4px)' }}
        animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
        transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-5"
      >
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-mono font-semibold uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            PRIVASCOPE Command Center
          </div>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white tracking-tight font-sans">
            Personal Data Firewall Telemetry
          </h1>
          <p className="text-xs text-slate-400">
            Authoritative telemetry and cryptographic audit state retrieved from local engine database
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 sm:gap-3 w-full sm:w-auto">
          <Link
            to="/ai-firewall"
            className="flex items-center justify-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-indigo-500/30 hover:border-indigo-500/60 text-indigo-300 font-medium text-xs transition-colors"
          >
            <Shield className="w-4 h-4 text-cyan-400" />
            <span>AI Gateway (Mode B)</span>
          </Link>
          <Link
            to="/scan"
            className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-medium text-xs shadow-md shadow-indigo-600/20 transition-all"
          >
            <ScanLine className="w-4 h-4" />
            <span>New Document Scan</span>
          </Link>
        </div>
      </motion.div>

      {/* Sequential KPI Cards (Command Center Stagger) */}
      <StaggerContainer className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Documents Scanned */}
        <StaggerItem>
          <HoverCard className="p-5 rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-md space-y-2 hover:border-indigo-500/40 hover:bg-slate-900/90 transition-all shadow-sm">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Documents Scanned</span>
              <FileText className="w-4 h-4 text-cyan-400" />
            </div>
            <p className="text-3xl font-extrabold text-white font-mono tracking-tight">
              <AnimatedNumber value={stats?.total_scans || 0} />
            </p>
            <span className="text-[10px] text-slate-500 font-mono block">Authentic database count</span>
          </HoverCard>
        </StaggerItem>

        {/* Card 2: Protected Documents */}
        <StaggerItem>
          <HoverCard className="p-5 rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-md space-y-2 hover:border-emerald-500/40 hover:bg-slate-900/90 transition-all shadow-sm">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Protected Documents</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <p className="text-3xl font-extrabold text-emerald-400 font-mono tracking-tight">
              <AnimatedNumber value={stats?.protected_documents || 0} />
            </p>
            <span className="text-[10px] text-slate-500 font-mono block">Masked or redacted artifacts</span>
          </HoverCard>
        </StaggerItem>

        {/* Card 3: High-Risk Exposure */}
        <StaggerItem>
          <HoverCard className="p-5 rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-md space-y-2 hover:border-rose-500/40 hover:bg-slate-900/90 transition-all shadow-sm">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">High-Risk Exposure</span>
              <AlertTriangle className="w-4 h-4 text-rose-400" />
            </div>
            <p className="text-3xl font-extrabold text-rose-400 font-mono tracking-tight">
              <AnimatedNumber value={stats?.high_risk_documents || 0} />
            </p>
            <span className="text-[10px] text-slate-500 font-mono block">Exposure Score &ge; 61.0</span>
          </HoverCard>
        </StaggerItem>

        {/* Card 4: Entities Detected */}
        <StaggerItem>
          <HoverCard className="p-5 rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-md space-y-2 hover:border-cyan-500/40 hover:bg-slate-900/90 transition-all shadow-sm">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Entities Detected</span>
              <Fingerprint className="w-4 h-4 text-cyan-400" />
            </div>
            <p className="text-3xl font-extrabold text-white font-mono tracking-tight">
              <AnimatedNumber value={stats?.total_entities_detected || 0} />
            </p>
            <span className="text-[10px] text-slate-500 font-mono block">Indian personal identifiers</span>
          </HoverCard>
        </StaggerItem>
      </StaggerContainer>

      {/* Empty State */}
      {isEmpty ? (
        <ScrollReveal>
          <div className="p-12 rounded-2xl border border-dashed border-slate-800 bg-slate-900/40 text-center space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-cyan-400 mx-auto">
              <ScanLine className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">No scans recorded yet</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
                Upload your first document or test the AI Privacy Gateway to begin privacy monitoring.
              </p>
            </div>
            <div className="flex items-center justify-center gap-3 pt-2">
              <Link
                to="/scan"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-all"
              >
                <span>Start Document Scan</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </ScrollReveal>
      ) : (
        <>
          {/* Charts Row with ScrollReveal */}
          <ScrollReveal>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* PII Distribution */}
              <div className="lg:col-span-2 p-5 rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-md space-y-4 shadow-sm">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-white">Personal Data Entity Distribution</h3>
                  <span className="text-[10px] font-mono text-slate-500 uppercase">Histogram</span>
                </div>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={piiChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                      <XAxis dataKey="name" stroke="#64748B" fontSize={10} angle={-25} textAnchor="end" />
                      <YAxis stroke="#64748B" fontSize={11} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0F172A', borderColor: '#1E293B', borderRadius: '8px', fontSize: '12px' }}
                        itemStyle={{ color: '#F8FAFC' }}
                      />
                      <Bar dataKey="count" fill="#6366F1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Risk Distribution */}
              <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/70 backdrop-blur-md space-y-4 shadow-sm">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-white">Privacy Risk Classification</h3>
                  <span className="text-[10px] font-mono text-slate-500 uppercase">Spectrum</span>
                </div>
                <div className="h-64 w-full flex items-center justify-center">
                  {riskChartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={riskChartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={75}
                          paddingAngle={4}
                          dataKey="value"
                        >
                          {riskChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ backgroundColor: '#0F172A', borderColor: '#1E293B', borderRadius: '8px', fontSize: '12px' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-xs text-slate-500">No risk evaluations recorded</p>
                  )}
                </div>
              </div>
            </div>
          </ScrollReveal>

          {/* Recent Scans Table */}
          <ScrollReveal delay={0.08}>
            <div className="border border-slate-800 rounded-2xl bg-slate-900/70 backdrop-blur-md overflow-hidden space-y-2 p-3.5 sm:p-5 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-semibold text-white">Recent Firewall Audits</h3>
                </div>
                <Link to="/history" className="text-xs text-cyan-400 hover:text-cyan-300 font-mono transition-colors">
                  View All History &rarr;
                </Link>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full min-w-[540px] text-left text-xs">
                  <thead className="text-[10px] font-mono uppercase text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5">Document</th>
                      <th className="py-2.5">Scan Date</th>
                      <th className="py-2.5">Risk Level</th>
                      <th className="py-2.5">Entities</th>
                      <th className="py-2.5">Protection</th>
                      <th className="py-2.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {stats.recent_scans.map((scan) => (
                      <tr key={scan.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3 font-medium text-white truncate max-w-xs">{scan.filename}</td>
                        <td className="py-3 text-slate-400 font-mono text-[11px]">{new Date(scan.scan_date).toLocaleDateString()}</td>
                        <td className="py-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                            scan.risk_level === 'CRITICAL' ? 'text-rose-400 bg-rose-500/10 border border-rose-500/30'
                            : scan.risk_level === 'HIGH' ? 'text-amber-400 bg-amber-500/10 border border-amber-500/30'
                            : scan.risk_level === 'MEDIUM' ? 'text-blue-400 bg-blue-500/10 border border-blue-500/30'
                            : 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/30'
                          }`}>
                            {scan.risk_level} ({scan.risk_score})
                          </span>
                        </td>
                        <td className="py-3 font-mono text-slate-400">{scan.entity_count}</td>
                        <td className="py-3">
                          {scan.has_protected_file ? (
                            <span className="text-emerald-400 text-[11px] font-mono flex items-center gap-1">
                              <ShieldCheck className="w-3.5 h-3.5" /> Protected
                            </span>
                          ) : (
                            <span className="text-slate-500 text-[11px] font-mono">Unprotected</span>
                          )}
                        </td>
                        <td className="py-3 text-right">
                          <Link
                            to={`/scan/${scan.id}`}
                            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-[11px] font-mono transition-colors"
                          >
                            View Results
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </ScrollReveal>
        </>
      )}
    </div>
  );
};
