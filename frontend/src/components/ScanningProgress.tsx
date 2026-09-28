import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Loader2, Circle, AlertCircle, Scan, Eye } from 'lucide-react';
import { ScanStage } from '../types';

interface ScanningProgressProps {
  stages: ScanStage[];
  filename?: string;
  ocrStatus?: string;
}

export const ScanningProgress: React.FC<ScanningProgressProps> = ({ stages, filename, ocrStatus }) => {
  return (
    <div className="w-full max-w-2xl mx-auto p-6 rounded-xl border border-priva-border bg-priva-card shadow-2xl space-y-6">
      {/* Header Viewport with Laser Animation */}
      <div className="relative h-24 rounded-lg bg-priva-bg border border-priva-border/80 overflow-hidden flex flex-col justify-center px-6">
        {/* Animated Laser Scanline */}
        <div className="absolute left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-priva-primary to-transparent animate-scanline shadow-[0_0_8px_#3B82F6]" />
        
        <div className="flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-priva-primary/10 border border-priva-primary/30 text-priva-primary">
              <Scan className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <p className="text-xs font-mono uppercase text-priva-muted">Active Pipeline Analysis</p>
              <h4 className="text-sm font-semibold text-white truncate max-w-xs">
                {filename || "Processing document stream"}
              </h4>
            </div>
          </div>
          {ocrStatus && (
            <div className="text-right">
              <span className="text-[10px] font-mono text-priva-muted block">OCR LAYER</span>
              <span className="text-xs font-mono text-priva-accent font-medium">{ocrStatus}</span>
            </div>
          )}
        </div>
      </div>

      {/* Progressive Real Stages */}
      <div className="space-y-3">
        {stages.map((stage, idx) => {
          const isCompleted = stage.status === 'completed';
          const isProcessing = stage.status === 'processing';
          const isFailed = stage.status === 'failed';
          const isSkipped = stage.status === 'skipped';

          return (
            <motion.div
              key={stage.name}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className={`flex items-center justify-between p-3 rounded-lg border text-sm transition-all ${
                isProcessing
                  ? 'border-priva-primary/50 bg-priva-primary/5'
                  : isCompleted
                  ? 'border-priva-border bg-priva-bg/40 text-slate-300'
                  : isFailed
                  ? 'border-priva-critical/50 bg-priva-critical/5 text-priva-critical'
                  : 'border-transparent text-priva-muted'
              }`}
            >
              <div className="flex items-center gap-3">
                {isCompleted && <CheckCircle2 className="w-4 h-4 text-priva-low shrink-0" />}
                {isProcessing && <Loader2 className="w-4 h-4 text-priva-primary animate-spin shrink-0" />}
                {isFailed && <AlertCircle className="w-4 h-4 text-priva-critical shrink-0" />}
                {isSkipped && <Eye className="w-4 h-4 text-priva-muted shrink-0" />}
                {stage.status === 'pending' && <Circle className="w-4 h-4 text-slate-600 shrink-0" />}

                <div>
                  <span className={`font-medium ${isProcessing ? 'text-white' : ''}`}>
                    {stage.label}
                  </span>
                  {stage.detail && (
                    <p className="text-[11px] font-mono text-priva-muted">{stage.detail}</p>
                  )}
                </div>
              </div>

              <span className="text-[11px] font-mono uppercase tracking-wider text-priva-muted">
                {stage.status}
              </span>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
