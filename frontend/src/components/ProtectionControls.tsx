import React, { useState } from 'react';
import { ShieldCheck, Lock, Download, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { ProtectionAction } from '../types';

interface ProtectionControlsProps {
  scanId: string;
  documentId?: string;
  filename?: string;
  entityCount: number;
  initialActionId?: string;
  hasProtectedFile: boolean;
  onProtectedSuccess: (action: ProtectionAction) => void;
}

export const ProtectionControls: React.FC<ProtectionControlsProps> = ({
  scanId,
  documentId,
  filename,
  entityCount,
  initialActionId,
  hasProtectedFile,
  onProtectedSuccess,
}) => {
  const [mode, setMode] = useState<'MASK' | 'REDACT'>('MASK');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(initialActionId || null);

  const handleApplyProtection = async () => {
    if (!documentId) {
      setErrorMsg("Direct text scans cannot produce a downloadable file artifact.");
      return;
    }

    setIsProcessing(true);
    setErrorMsg(null);

    try {
      const action = await api.applyProtection(scanId, mode);
      setActionId(action.id);
      onProtectedSuccess(action);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Failed to execute protection. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    if (!actionId) return;
    try {
      const targetFilename = filename
        ? `${filename.substring(0, filename.lastIndexOf('.'))}_PROTECTED${filename.substring(filename.lastIndexOf('.'))}`
        : 'protected_document.pdf';
      await api.downloadProtectedFile(actionId, targetFilename);
    } catch (err: any) {
      setErrorMsg("Download failed: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="border border-priva-border rounded-xl bg-priva-card p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-priva-border pb-4">
        <div>
          <h3 className="font-semibold text-white text-base">Privacy Firewall Policy</h3>
          <p className="text-xs text-priva-muted">
            Configure sanitization action for {entityCount} detected personal identifiers.
          </p>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-priva-primary/10 border border-priva-primary/30 text-priva-primary text-xs font-mono">
          <ShieldCheck className="w-4 h-4" />
          <span>Server-Side Guard</span>
        </div>
      </div>

      {/* Mode Selector */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <label
          className={`flex items-start gap-3 p-4 rounded-xl border cursor-pointer transition-all ${
            mode === 'MASK'
              ? 'border-priva-primary bg-priva-primary/10 shadow-lg shadow-priva-primary/5'
              : 'border-priva-border bg-priva-bg/50 hover:border-priva-borderLight'
          }`}
        >
          <input
            type="radio"
            name="protection-mode"
            checked={mode === 'MASK'}
            onChange={() => setMode('MASK')}
            className="mt-1 text-priva-primary focus:ring-0"
          />
          <div>
            <p className="font-semibold text-white text-sm">Mask Sensitive Values</p>
            <p className="text-xs text-priva-muted mt-1 leading-relaxed">
              Replaces sensitive content with privacy tokens (e.g. <code className="text-priva-accent">XXXX XXXX 3210</code>, <code className="text-priva-accent">r****@gmail.com</code>). Retains document layout and contextual usability.
            </p>
          </div>
        </label>

        <label
          className={`flex items-start gap-3 p-4 rounded-xl border cursor-pointer transition-all ${
            mode === 'REDACT'
              ? 'border-priva-critical bg-priva-critical/10 shadow-lg shadow-priva-critical/5'
              : 'border-priva-border bg-priva-bg/50 hover:border-priva-borderLight'
          }`}
        >
          <input
            type="radio"
            name="protection-mode"
            checked={mode === 'REDACT'}
            onChange={() => setMode('REDACT')}
            className="mt-1 text-priva-critical focus:ring-0"
          />
          <div>
            <p className="font-semibold text-white text-sm">Fully Redact Content</p>
            <p className="text-xs text-priva-muted mt-1 leading-relaxed">
              Physically removes sensitive characters from the PDF content stream or draws solid black pixel blocks. Replaces text with <code className="text-priva-critical">[REDACTED]</code>.
            </p>
          </div>
        </label>
      </div>

      {errorMsg && (
        <div className="p-3 rounded-lg border border-priva-critical/40 bg-priva-critical/10 text-priva-critical text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Action Trigger Buttons */}
      <div className="flex items-center justify-between flex-wrap gap-4 pt-2">
        <button
          onClick={handleApplyProtection}
          disabled={isProcessing || !documentId}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-priva-primary hover:bg-priva-primaryHover disabled:opacity-50 text-white font-medium text-sm transition-all shadow-md shadow-priva-primary/20"
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Sanitizing & Verifying...</span>
            </>
          ) : (
            <>
              <Lock className="w-4 h-4" />
              <span>Apply {mode === 'MASK' ? 'Masking' : 'Full Redaction'}</span>
            </>
          )}
        </button>

        {(actionId || hasProtectedFile) && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs text-priva-low font-mono bg-priva-low/10 px-3 py-1.5 rounded-lg border border-priva-low/30">
              <CheckCircle className="w-4 h-4" />
              <span>Verification Passed</span>
            </div>

            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm transition-colors shadow-md shadow-emerald-900/30"
            >
              <Download className="w-4 h-4" />
              <span>Download Protected File</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
