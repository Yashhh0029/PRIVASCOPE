import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { History, Search, Download, ExternalLink, Loader2, FileText, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { RecentScanItem } from '../types';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<RecentScanItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await api.getHistory(1, 50);
        setHistory(data);
      } catch (err) {
        console.error("Failed to load scan history:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const filteredHistory = history.filter((item) =>
    item.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.risk_level.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex-1 p-3.5 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Firewall Audit History</h1>
          <p className="text-xs text-priva-muted">Historical log of document scans and generated protection policies</p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-priva-muted absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by filename or risk..."
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-priva-card border border-priva-border text-xs text-white placeholder-priva-muted focus:outline-none focus:border-priva-primary"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-12">
          <Loader2 className="w-8 h-8 text-priva-primary animate-spin" />
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="p-12 rounded-xl border border-dashed border-priva-border bg-priva-card text-center space-y-3">
          <History className="w-8 h-8 text-priva-muted mx-auto" />
          <h3 className="text-sm font-semibold text-white">No historical scans recorded</h3>
          <p className="text-xs text-priva-muted max-w-xs mx-auto">
            Uploaded and analyzed documents will appear here with complete audit trails.
          </p>
        </div>
      ) : (
        <div className="border border-priva-border rounded-xl bg-priva-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-xs">
              <thead className="bg-priva-bg/80 border-b border-priva-border text-[11px] font-mono uppercase text-priva-muted">
                <tr>
                  <th className="py-3 px-4">Document / File</th>
                  <th className="py-3 px-4">Scan Date</th>
                  <th className="py-3 px-4">Risk Evaluation</th>
                  <th className="py-3 px-4">Entities</th>
                  <th className="py-3 px-4">Firewall Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-priva-border/60">
                {filteredHistory.map((scan) => (
                  <tr key={scan.id} className="hover:bg-priva-bg/40 transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-priva-primary shrink-0" />
                        <span className="font-medium text-white truncate max-w-xs font-mono">{scan.filename}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono text-priva-muted">
                      {new Date(scan.scan_date).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                        scan.risk_level === 'CRITICAL' ? 'text-red-400 bg-red-400/10'
                        : scan.risk_level === 'HIGH' ? 'text-orange-400 bg-orange-400/10'
                        : scan.risk_level === 'MEDIUM' ? 'text-amber-400 bg-amber-400/10'
                        : 'text-emerald-400 bg-emerald-400/10'
                      }`}>
                        {scan.risk_level} ({scan.risk_score})
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300 font-medium">
                      {scan.entity_count} items
                    </td>
                    <td className="py-3 px-4">
                      {scan.has_protected_file ? (
                        <div className="flex items-center gap-1.5 text-priva-low font-mono text-[11px]">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          <span>Protected</span>
                        </div>
                      ) : (
                        <span className="text-priva-muted font-mono text-[11px]">Unprotected</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <Link
                        to={`/scan/${scan.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-priva-bg hover:bg-priva-border text-priva-accent text-[11px] font-mono transition-colors"
                      >
                        <span>Inspect</span>
                        <ExternalLink className="w-3 h-3" />
                      </Link>
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
