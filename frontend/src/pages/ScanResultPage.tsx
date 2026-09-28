import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldAlert,
  ShieldCheck,
  FileText,
  AlertTriangle,
  ArrowLeft,
  Loader2,
  Calendar,
  Layers,
  FileCheck
} from 'lucide-react';
import { api } from '../services/api';
import { Scan, DetectedEntity, ProtectionAction } from '../types';
import { RiskGauge } from '../components/RiskGauge';
import { EntityTable } from '../components/EntityTable';
import { DocumentViewer } from '../components/DocumentViewer';
import { ProtectionControls } from '../components/ProtectionControls';
import { ComparisonDiff } from '../components/ComparisonDiff';
import { ScrollReveal, HoverCard } from '../components/motion/MotionSystem';

export const ScanResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [scan, setScan] = useState<Scan | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [protectionMode, setProtectionMode] = useState<'MASK' | 'REDACT'>('MASK');

  useEffect(() => {
    const fetchScan = async () => {
      if (!id) return;
      try {
        const data = await api.getScan(id);
        setScan(data);
      } catch (err: any) {
        setErrorMsg(err.response?.data?.detail || "Could not retrieve scan result.");
      } finally {
        setLoading(false);
      }
    };
    fetchScan();
  }, [id]);

  const handleProtectionSuccess = (action: ProtectionAction) => {
    if (scan) {
      setScan({
        ...scan,
        has_protected_file: true,
        protected_action_id: action.id,
      });
      setProtectionMode(action.mode);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <Loader2 className="w-8 h-8 text-priva-primary animate-spin" />
      </div>
    );
  }

  if (errorMsg || !scan) {
    return (
      <div className="flex-1 p-8 max-w-4xl mx-auto space-y-4">
        <div className="p-4 rounded-xl border border-priva-critical/30 bg-priva-critical/10 text-priva-critical text-sm">
          {errorMsg || "Scan not found."}
        </div>
        <Link to="/scan" className="inline-flex items-center gap-2 text-xs font-mono text-priva-accent hover:underline">
          <ArrowLeft className="w-4 h-4" /> Back to Scanner
        </Link>
      </div>
    );
  }

  return (
    <div className="flex-1 px-3.5 py-6 sm:px-6 sm:py-8 max-w-7xl mx-auto w-full space-y-6 sm:space-y-8">
      {/* Top Breadcrumb & Metadata Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-priva-border pb-4">
        <div className="space-y-1">
          <Link to="/history" className="inline-flex items-center gap-1.5 text-xs text-priva-muted hover:text-white font-mono">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Audit History
          </Link>
          <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
            <h1 className="text-lg sm:text-xl font-bold text-white font-mono break-all">{scan.original_filename}</h1>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-priva-card border border-priva-border text-priva-muted">
              {scan.file_type}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 sm:gap-4 text-xs font-mono text-priva-muted">
          <div className="flex items-center gap-1.5">
            <Calendar className="w-4 h-4 shrink-0" />
            <span>{new Date(scan.started_at).toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Layers className="w-4 h-4 shrink-0" />
            <span>{scan.entity_count} Personal Identifiers</span>
          </div>
        </div>
      </div>

      {/* Primary Privacy Exposure Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center p-4 sm:p-6 rounded-2xl border border-priva-border bg-priva-card">
        {/* Animated Gauge */}
        <div className="flex justify-center md:border-r border-priva-border md:pr-6">
          <RiskGauge score={scan.risk_score} level={scan.risk_level} size={190} />
        </div>

        {/* Explainable Risk Details */}
        <div className="md:col-span-2 space-y-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono uppercase text-priva-muted">Privacy Risk Evaluation</span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-priva-primary/20 text-priva-accent border border-priva-primary/30">
              Deterministic Fusion Model
            </span>
          </div>

          <h2 className="text-base sm:text-lg font-bold text-white">
            {scan.risk_level === 'CRITICAL' && 'Critical Privacy Exposure Detected'}
            {scan.risk_level === 'HIGH' && 'High Privacy Risk Identified'}
            {scan.risk_level === 'MEDIUM' && 'Moderate Privacy Impact Detected'}
            {scan.risk_level === 'LOW' && 'Low Privacy Exposure'}
          </h2>

          <p className="text-xs text-slate-300 leading-relaxed bg-priva-bg/60 p-3 sm:p-4 rounded-xl border border-priva-border font-sans break-words">
            {scan.risk_explanation}
          </p>

          <div className="flex flex-wrap items-center gap-x-4 sm:gap-x-6 gap-y-1.5 text-[10px] sm:text-[11px] font-mono text-priva-muted pt-1">
            <span>OCR Status: <strong className="text-white">{scan.ocr_status}</strong></span>
            <span>Ground Pipeline: <strong className="text-white">Active</strong></span>
            <span>External LLMs: <strong className="text-white">None (Air-Gapped)</strong></span>
          </div>
        </div>
      </div>

      {/* Purpose-Aware Sharing Recommendations (Mode A Enhancement) */}
      <div className="p-4 sm:p-6 rounded-2xl border border-indigo-500/20 bg-slate-900 space-y-4 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400">
              <ShieldCheck className="w-4 h-4 shrink-0" />
              <span>Contextual Purpose-Aware Sharing Policy</span>
            </div>
            <h3 className="text-sm sm:text-base font-bold text-white">
              Action Plan for: <span className="text-cyan-400">{scan.sharing_purpose || 'General Sharing'}</span>
            </h3>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center gap-2 w-full sm:w-auto">
            <label className="text-xs text-slate-400 shrink-0">Evaluate for another purpose:</label>
            <select
              value={scan.sharing_purpose || 'General Sharing'}
              onChange={async (e) => {
                const newPurpose = e.target.value;
                if (!id) return;
                try {
                  const updated = await api.getScan(id, newPurpose);
                  setScan(updated);
                } catch (err) {
                  console.error("Failed to re-evaluate purpose:", err);
                }
              }}
              className="w-full sm:w-auto bg-slate-800 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-indigo-500"
            >
              <option value="General Sharing">General Sharing (Protect All)</option>
              <option value="Job Application">Job Application</option>
              <option value="College Admission">College Admission</option>
              <option value="Scholarship">Scholarship</option>
              <option value="Bank Verification">Bank Verification</option>
              <option value="Medical Document">Medical Document</option>
              <option value="Government Form">Government Form</option>
              <option value="Custom">Custom</option>
            </select>
          </div>
        </div>

        {scan.purpose_recommendations && scan.purpose_recommendations.length > 0 ? (
          <motion.div layout className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
            <AnimatePresence mode="popLayout">
              {scan.purpose_recommendations.map((rec, idx) => (
                <motion.div
                  layout
                  key={`${scan.sharing_purpose}-${rec.what}-${idx}`}
                  initial={{ opacity: 0, scale: 0.95, y: 8 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
                  className={`p-3.5 sm:p-4 rounded-xl border transition-all overflow-hidden break-words ${
                    rec.recommended_action === 'KEEP'
                      ? 'bg-emerald-950/20 border-emerald-500/30'
                      : 'bg-cyan-950/20 border-cyan-500/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2 gap-2">
                    <span className="font-mono text-xs font-bold text-white uppercase truncate">
                      {rec.what} {rec.count ? `(${rec.count})` : ''}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded border shrink-0 ${
                        rec.recommended_action === 'KEEP'
                          ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                          : 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300'
                      }`}
                    >
                      ACTION: {rec.recommended_action}
                    </span>
                  </div>
                  <div className="space-y-1.5 text-xs">
                    <div>
                      <span className="text-slate-400 font-medium">Why Keep/Protect: </span>
                      <span className="text-slate-300">{rec.why}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 font-medium">Evidence: </span>
                      <span className="text-slate-400 font-mono text-[11px] break-all">{rec.evidence}</span>
                    </div>
                    <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-800 break-words">
                      {rec.reason}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>
        ) : (
          <div className="text-xs text-slate-400 p-3 bg-slate-950 rounded-lg">
            No sensitive personal coordinates detected in this document.
          </div>
        )}
      </div>

      {/* Main Split View: Document Viewer / Heatmap & Protection Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* Left: Document Viewport */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Document Viewport & Coordinate Heatmap</h3>
            <span className="text-xs font-mono text-priva-muted">Click row below to locate</span>
          </div>
          <DocumentViewer
            documentId={scan.document_id}
            fileType={scan.file_type}
            filename={scan.original_filename}
            entities={scan.entities}
            selectedEntityId={selectedEntityId}
          />
        </div>

        {/* Right: Protection Controls & Diff */}
        <div className="space-y-6">
          <ProtectionControls
            scanId={scan.id}
            documentId={scan.document_id}
            filename={scan.original_filename}
            entityCount={scan.entity_count}
            initialActionId={scan.protected_action_id}
            hasProtectedFile={scan.has_protected_file}
            onProtectedSuccess={handleProtectionSuccess}
          />

          {scan.entities.length > 0 && (
            <ComparisonDiff entities={scan.entities} mode={protectionMode} />
          )}
        </div>
      </div>

      {/* Findings Table */}
      <div className="space-y-3 pt-4 border-t border-priva-border">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Granular Personal Data Findings</h3>
          <span className="text-xs font-mono text-priva-muted">Verified algorithmic signals</span>
        </div>
        <EntityTable
          entities={scan.entities}
          onSelectEntity={(e) => setSelectedEntityId(e.id)}
          selectedEntityId={selectedEntityId}
        />
      </div>
    </div>
  );
};
