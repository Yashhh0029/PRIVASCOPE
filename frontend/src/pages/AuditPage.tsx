import React, { useEffect, useState } from 'react';
import { ScrollText, ShieldCheck, CheckCircle2, AlertTriangle, FileText, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { AuditLogItem } from '../types';

export const AuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await api.getAuditLogs(1, 50);
        setLogs(data);
      } catch (err) {
        console.error("Failed to load audit logs:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  return (
    <div className="flex-1 p-8 max-w-7xl mx-auto w-full space-y-6">
      <div className="flex items-center justify-between border-b border-priva-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <ScrollText className="w-5 h-5 text-priva-primary" />
            <h1 className="text-xl font-bold text-white tracking-tight">Security Audit Log</h1>
          </div>
          <p className="text-xs text-priva-muted">
            Immutable log of all firewall lifecycle actions. Zero raw personal data stored.
          </p>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-priva-border bg-priva-card text-xs font-mono text-priva-muted">
          <ShieldCheck className="w-4 h-4 text-priva-low" />
          <span>Zero-PII Compliance Enforced</span>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-12">
          <Loader2 className="w-8 h-8 text-priva-primary animate-spin" />
        </div>
      ) : logs.length === 0 ? (
        <div className="p-12 rounded-xl border border-dashed border-priva-border bg-priva-card text-center space-y-3">
          <ScrollText className="w-8 h-8 text-priva-muted mx-auto" />
          <h3 className="text-sm font-semibold text-white">No audit events recorded</h3>
          <p className="text-xs text-priva-muted max-w-xs mx-auto">
            Operations like upload, scan, protection, and downloads will be tracked here.
          </p>
        </div>
      ) : (
        <div className="border border-priva-border rounded-xl bg-priva-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-priva-bg/80 border-b border-priva-border text-[11px] font-mono uppercase text-priva-muted">
                <tr>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Document</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Operational Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-priva-border/60 font-mono">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-priva-bg/40 transition-colors">
                    <td className="py-3 px-4 font-bold text-white">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 border border-slate-700">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-priva-muted">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      {log.filename || "—"}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        log.status === 'SUCCESS' ? 'text-emerald-400 bg-emerald-400/10' :
                        log.status === 'WARNING' ? 'text-amber-400 bg-amber-400/10' :
                        'text-red-400 bg-red-400/10'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-priva-muted text-[11px] truncate max-w-md font-sans">
                      {log.details || "Operation recorded."}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
