import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Shield,
  FileCheck,
  Lock,
  ArrowRight,
  Database,
  FileSpreadsheet,
  FileCode,
  Image,
  CheckCircle2,
  Cpu
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const supportedFormats = [
    { ext: 'PDF', label: 'PyMuPDF Native & Scanned', icon: FileCheck },
    { ext: 'XLSX', label: 'Excel Spreadsheets', icon: FileSpreadsheet },
    { ext: 'DOCX', label: 'Word Documents', icon: FileCode },
    { ext: 'CSV', label: 'Data Feeds & Records', icon: Database },
    { ext: 'TXT', label: 'Unstructured Text', icon: FileCode },
    { ext: 'PNG / JPG', label: 'ID Cards & Scans', icon: Image },
  ];

  const piiCategories = [
    { name: 'Aadhaar (UID)', detail: 'Verhoeff Algorithm Check' },
    { name: 'PAN Card', detail: 'Entity-Type & 4th-Char Verification' },
    { name: 'Bank Accounts', detail: 'Conservative Banking Context Engine' },
    { name: 'UPI / VPA Handles', detail: 'NPCI & Major PSP Registry' },
    { name: 'IFSC Codes', detail: 'RBI Bank Branch Code Validation' },
    { name: 'Mobile Numbers', detail: 'Indian +91 Telecom Patterns' },
    { name: 'Email Addresses', detail: 'RFC Validation & TLD Verification' },
    { name: 'Academic PRN / Roll', detail: 'Indian University Roll Patterns' },
  ];

  return (
    <div className="min-h-screen bg-priva-bg text-priva-text overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative pt-12 sm:pt-20 pb-12 sm:pb-20 px-4 sm:px-6 max-w-6xl mx-auto text-center space-y-6 sm:space-y-8 overflow-hidden">
        {/* Ambient Glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[320px] sm:w-[550px] h-[250px] sm:h-[350px] bg-priva-primary/10 blur-[100px] sm:blur-[130px] rounded-full pointer-events-none" />

        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-3.5 py-1.5 rounded-full border border-priva-primary/30 bg-priva-primary/10 text-priva-accent text-[10px] sm:text-xs font-mono max-w-full truncate"
        >
          <Cpu className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">PRODUCTION-GRADE AI PRIVACY FIREWALL</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight"
        >
          Protect Before You Share.
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-xs sm:text-base md:text-lg text-priva-muted max-w-2xl mx-auto leading-relaxed"
        >
          PRIVASCOPE scans documents and unstructured text for sensitive Indian personal information, evaluates privacy exposure through an explainable risk engine, and generates verifiable sanitized files.
        </motion.p>

        {/* Call to Actions */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3 sm:gap-4 max-w-md sm:max-w-none mx-auto pt-2"
        >
          <Link
            to="/scan"
            className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-priva-primary hover:bg-priva-primaryHover text-white font-semibold text-sm transition-all shadow-lg shadow-priva-primary/25 group"
          >
            <span>Scan a Document</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            to="/login"
            className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl border border-priva-border bg-priva-card hover:bg-priva-cardHover text-slate-200 font-medium text-sm transition-colors"
          >
            <span>Access Firewall Console</span>
          </Link>
        </motion.div>

        {/* Real Data Flow Diagram Animation */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-8 sm:mt-12 p-4 sm:p-6 rounded-2xl border border-priva-border bg-priva-card/60 backdrop-blur-md shadow-2xl max-w-4xl mx-auto"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 items-center">
            {/* Step 1 */}
            <div className="p-3.5 sm:p-4 rounded-xl border border-priva-border bg-priva-bg/80 text-left space-y-1">
              <span className="text-[10px] font-mono text-priva-accent font-bold uppercase">01. INGEST</span>
              <p className="text-sm font-semibold text-white">Upload Document</p>
              <p className="text-xs text-priva-muted">PDF, XLSX, DOCX, CSV, TXT, Images</p>
            </div>

            {/* Step 2 */}
            <div className="p-3.5 sm:p-4 rounded-xl border border-priva-primary/40 bg-priva-primary/5 text-left space-y-1">
              <span className="text-[10px] font-mono text-priva-primary font-bold uppercase">02. ANALYZE</span>
              <p className="text-sm font-semibold text-white">Context & Checksum</p>
              <p className="text-xs text-priva-muted">Verhoeff, RBI codes, cell headers</p>
            </div>

            {/* Step 3 */}
            <div className="p-3.5 sm:p-4 rounded-xl border border-amber-500/40 bg-amber-500/5 text-left space-y-1">
              <span className="text-[10px] font-mono text-priva-medium font-bold uppercase">03. SCORE</span>
              <p className="text-sm font-semibold text-white">Risk Evaluation</p>
              <p className="text-xs text-priva-muted">Multi-factor compounding engine</p>
            </div>

            {/* Step 4 */}
            <div className="p-3.5 sm:p-4 rounded-xl border border-emerald-500/40 bg-emerald-500/5 text-left space-y-1">
              <span className="text-[10px] font-mono text-priva-low font-bold uppercase">04. SANITIZE</span>
              <p className="text-sm font-semibold text-white">Verified Redaction</p>
              <p className="text-xs text-priva-muted">Post-protection check & download</p>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Capabilities Section */}
      <section className="py-12 sm:py-16 border-t border-priva-border/80 bg-priva-card/20 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto space-y-8 sm:space-y-12">
          <div className="text-center space-y-2">
            <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-white">Multi-Format Verification Pipeline</h2>
            <p className="text-xs sm:text-sm text-priva-muted">Physical format extractors and pixel/text layer modifiers.</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
            {supportedFormats.map((f) => {
              const Icon = f.icon;
              return (
                <div
                  key={f.ext}
                  className="p-3 sm:p-4 rounded-xl border border-priva-border bg-priva-card flex flex-col items-center text-center space-y-2 hover:border-priva-primary/40 transition-colors"
                >
                  <div className="p-2.5 rounded-lg bg-priva-primary/10 text-priva-primary">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="font-mono font-bold text-xs sm:text-sm text-white">{f.ext}</span>
                  <span className="text-[10px] sm:text-[11px] text-priva-muted">{f.label}</span>
                </div>
              );
            })}
          </div>

          {/* Indian PII Entities */}
          <div className="pt-6 sm:pt-8 border-t border-priva-border/60">
            <h3 className="text-base sm:text-lg font-semibold text-white text-center mb-4 sm:mb-6">
              Specialized Indian Personal Identifiers
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              {piiCategories.map((pii) => (
                <div
                  key={pii.name}
                  className="p-3 sm:p-3.5 rounded-lg border border-priva-border bg-priva-bg/60 flex items-start gap-3"
                >
                  <CheckCircle2 className="w-4 h-4 text-priva-low shrink-0 mt-0.5" />
                  <div>
                    <p className="text-xs font-semibold text-white font-mono">{pii.name}</p>
                    <p className="text-[10px] sm:text-[11px] text-priva-muted">{pii.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-6 sm:py-8 border-t border-priva-border text-center text-[10px] sm:text-xs text-priva-muted font-mono px-4">
        <p>PRIVASCOPE AI Privacy Firewall • Local Execution Architecture • Zero Cloud Leakage</p>
      </footer>
    </div>
  );
};
