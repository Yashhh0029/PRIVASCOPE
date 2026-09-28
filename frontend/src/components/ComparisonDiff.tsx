import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { ArrowRight, ShieldCheck, FileCheck, Binary } from 'lucide-react';
import { DetectedEntity } from '../types';

interface ComparisonDiffProps {
  entities: DetectedEntity[];
  mode: 'MASK' | 'REDACT';
}

export const ComparisonDiff: React.FC<ComparisonDiffProps> = ({ entities, mode }) => {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div className="border border-slate-800 rounded-2xl bg-slate-900/80 backdrop-blur-md p-6 space-y-4 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Binary className="w-5 h-5 text-cyan-400" />
          <h3 className="font-semibold text-white text-sm">Original vs Protected Preview</h3>
        </div>
        <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/30">
          Transformation: {mode}
        </span>
      </div>

      <div className="space-y-3">
        {entities.slice(0, 5).map((e, idx) => {
          const protectedVal = mode === 'REDACT' ? '[REDACTED]' : e.masked_preview;
          return (
            <motion.div
              key={e.id}
              initial={shouldReduceMotion ? {} : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05, duration: 0.25 }}
              className="p-3.5 rounded-xl border border-slate-800/80 bg-slate-950/70 flex items-center justify-between gap-4 text-xs font-mono"
            >
              <div className="space-y-0.5">
                <span className="text-[10px] text-slate-500 block uppercase tracking-wider">
                  {e.entity_type} ({e.sheet_name || `Page ${e.page_number}`})
                </span>
                <span className="text-rose-400/90 line-through text-[11px]">
                  {e.masked_preview.replace(/X/g, '•')}
                </span>
              </div>

              <div className="flex items-center gap-2 text-slate-600">
                <span className="text-[10px] tracking-widest text-slate-500 hidden sm:inline">██████</span>
                <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />
              </div>

              <div className="space-y-0.5 text-right">
                <span className="text-[10px] text-emerald-400 block uppercase tracking-wider">
                  Sanitized ({mode})
                </span>
                <span className={mode === 'REDACT' ? 'text-rose-400 font-bold text-[11px]' : 'text-emerald-400 font-bold text-[11px]'}>
                  {protectedVal}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
