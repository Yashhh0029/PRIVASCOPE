import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { 
  Shield, 
  Send, 
  Lock, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Cpu, 
  Eye, 
  EyeOff, 
  Zap, 
  Server, 
  RotateCcw,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Activity,
  Layers,
  Check,
  Terminal,
  Binary
} from 'lucide-react';
import { api } from '../services/api';
import { GatewayProvider, GatewayAnalyzeResponse, GatewayStats } from '../types';
import { AnimatedNumber, HoverCard, ScrollReveal } from '../components/motion/MotionSystem';

const DEMO_SCENARIOS = [
  {
    id: 'safe',
    title: '1. Safe Algorithmic Prompt',
    badge: 'ALLOW',
    badgeColor: 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10',
    prompt: 'Explain the difference between Dijkstra algorithm and A* pathfinding with Python examples.'
  },
  {
    id: 'warn',
    title: '2. Advisory Warning (Email)',
    badge: 'WARN',
    badgeColor: 'border-amber-500/40 text-amber-400 bg-amber-500/10',
    prompt: 'Please draft a polite follow-up email regarding my project report. You can mention my email developer.contact@example.org.'
  },
  {
    id: 'protect',
    title: '3. Identity Protection (Aadhaar & Mobile)',
    badge: 'PROTECT',
    badgeColor: 'border-cyan-500/40 text-cyan-400 bg-cyan-500/10',
    prompt: 'Please draft a formal scholarship appeal letter for citizen with Aadhaar number 4512 7896 3218 and WhatsApp mobile 9876543210.'
  },
  {
    id: 'block',
    title: '4. Critical Compound Breach',
    badge: 'BLOCK',
    badgeColor: 'border-rose-500/40 text-rose-400 bg-rose-500/10',
    prompt: 'Urgent: verify citizen Rajesh with Aadhaar 4512 7896 3218, PAN ABCDE1234F, Bank Account 123456789012, and phone 9876543210 for income tax refund processing.'
  }
];

export const AiFirewallPage: React.FC = () => {
  const [prompt, setPrompt] = useState<string>(DEMO_SCENARIOS[2].prompt);
  const [providers, setProviders] = useState<GatewayProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('local_demo');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<GatewayAnalyzeResponse | null>(null);
  const [stats, setStats] = useState<GatewayStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRehydrated, setShowRehydrated] = useState<boolean>(true);
  const [isRehydrating, setIsRehydrating] = useState<boolean>(false);
  const [customRehydratedText, setCustomRehydratedText] = useState<string | null>(null);
  const [activePipelineStep, setActivePipelineStep] = useState<number>(0);

  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    loadProviders();
    loadStats();
  }, []);

  const loadProviders = async () => {
    try {
      const data = await api.getGatewayProviders();
      setProviders(data);
      if (data.length > 0 && !data.some(p => p.id === selectedProvider)) {
        setSelectedProvider(data[0].id);
      }
    } catch (err: any) {
      console.error('Failed to load providers:', err);
    }
  };

  const loadStats = async () => {
    try {
      const s = await api.getGatewayStats();
      setStats(s);
    } catch (err) {
      console.error('Failed to load gateway stats:', err);
    }
  };

  const handleSendPrompt = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setCustomRehydratedText(null);
    setActivePipelineStep(1); // User -> Detect

    try {
      const stepTimer1 = setTimeout(() => setActivePipelineStep(2), 150);
      const stepTimer2 = setTimeout(() => setActivePipelineStep(3), 300);

      const res = await api.analyzePrompt({
        prompt,
        provider: selectedProvider
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setActivePipelineStep(4);
      setResult(res);
      await loadStats();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Gateway transmission failed.');
      setActivePipelineStep(0);
    } finally {
      setLoading(false);
    }
  };

  const handleManualRehydration = async () => {
    if (!result || !result.provider_raw_response || !result.session_id) return;
    setIsRehydrating(true);
    try {
      const res = await api.rehydrateGatewayTokens(result.provider_raw_response, result.session_id);
      setCustomRehydratedText(res.rehydrated_text);
      setShowRehydrated(true);
    } catch (err: any) {
      console.error('Manual rehydration failed:', err);
    } finally {
      setIsRehydrating(false);
    }
  };

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'ALLOW':
        return (
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 glow-emerald"
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="font-mono font-bold text-xs">ALLOW &middot; CLEAN TRANSMISSION</span>
          </motion.div>
        );
      case 'WARN':
        return (
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/40 text-amber-400"
          >
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span className="font-mono font-bold text-xs">WARN &middot; ADVISORY ISSUED</span>
          </motion.div>
        );
      case 'PROTECT':
        return (
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/40 text-cyan-400 glow-cyan"
          >
            <Lock className="w-4 h-4 text-cyan-400" />
            <span className="font-mono font-bold text-xs">PROTECT &middot; LOCAL PSEUDONYMIZATION ACTIVE</span>
          </motion.div>
        );
      case 'BLOCK':
        return (
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/40 text-rose-400 glow-rose"
          >
            <XCircle className="w-4 h-4 text-rose-400" />
            <span className="font-mono font-bold text-xs">BLOCK &middot; TRANSMISSION TERMINATED</span>
          </motion.div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6 sm:space-y-8 p-3.5 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full relative z-10">
      {/* Hero Header with Animated Pipeline Visualization */}
      <div className="rounded-2xl sm:rounded-3xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl p-4 sm:p-6 lg:p-8 shadow-2xl relative overflow-hidden">
        {/* Ambient Top Glow */}
        <div className="absolute top-0 right-1/4 w-96 h-40 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
              <Shield className="w-3.5 h-3.5 text-cyan-400" />
              AI Privacy Firewall & Gateway (Mode B)
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white tracking-tight leading-tight">
              Protect Before Your Data Leaves Your Device.
            </h1>
            <p className="text-slate-400 text-xs lg:text-sm leading-relaxed">
              Outbound prompt interception, context-aware PII detection, and reversible local pseudonymization.
              Guarantees that third-party AI models never receive your real Indian personal coordinates.
            </p>
          </div>

          {/* Real-time Telemetry Stats Pill */}
          {stats && (
            <div className="flex items-center justify-between sm:justify-start gap-4 bg-slate-950/70 p-3.5 sm:p-4 rounded-2xl border border-slate-800 backdrop-blur-md shrink-0">
              <div className="text-right">
                <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Shielded Entities</div>
                <div className="text-2xl font-bold font-mono text-cyan-400">
                  <AnimatedNumber value={stats.total_entities_shielded} />
                </div>
              </div>
              <div className="h-9 w-[1px] bg-slate-800" />
              <div className="text-right">
                <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Firewall Status</div>
                <div className="flex items-center justify-end gap-1.5 text-xs font-mono font-bold text-emerald-400 mt-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  0 LEAKS (AIR-GAPPED)
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Animated Network Pipeline Visualization */}
        <div className="mt-8 pt-6 border-t border-slate-800/80">
          <div className="text-[10px] font-mono uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
            <span>Hardware Boundary Pipeline Flow</span>
            <span className="h-px flex-1 bg-slate-800" />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 sm:gap-3 items-center">
            {/* Stage 1: User Device */}
            <div className={`p-3 rounded-xl border text-center transition-all ${
              activePipelineStep >= 1 ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-300' : 'border-slate-800 bg-slate-950/60 text-slate-400'
            }`}>
              <div className="text-[10px] font-mono uppercase font-bold">1. User Client</div>
              <div className="text-[11px] text-slate-300 mt-0.5 truncate">Raw Outbound Text</div>
            </div>

            {/* Stage 2: Detection */}
            <div className={`p-3 rounded-xl border text-center transition-all ${
              activePipelineStep >= 2 ? 'border-indigo-500/50 bg-indigo-500/10 text-indigo-300' : 'border-slate-800 bg-slate-950/60 text-slate-400'
            }`}>
              <div className="text-[10px] font-mono uppercase font-bold">2. Local Detect</div>
              <div className="text-[11px] text-slate-300 mt-0.5">Checksum & Verhoeff</div>
            </div>

            {/* Stage 3: Policy Engine */}
            <div className={`p-3 rounded-xl border text-center transition-all ${
              activePipelineStep >= 3 ? 'border-indigo-500/50 bg-indigo-500/10 text-indigo-300' : 'border-slate-800 bg-slate-950/60 text-slate-400'
            }`}>
              <div className="text-[10px] font-mono uppercase font-bold">3. Policy Engine</div>
              <div className="text-[11px] text-slate-300 mt-0.5">ALLOW / WARN / BLOCK</div>
            </div>

            {/* Stage 4: Pseudonymize */}
            <div className={`p-3 rounded-xl border text-center transition-all ${
              activePipelineStep >= 4 ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-300' : 'border-slate-800 bg-slate-950/60 text-slate-400'
            }`}>
              <div className="text-[10px] font-mono uppercase font-bold">4. Pseudonymize</div>
              <div className="text-[11px] text-slate-300 mt-0.5">Token Substitution</div>
            </div>

            {/* Stage 5: Wire Transfer */}
            <div className={`p-3 rounded-xl border text-center transition-all ${
              result && result.policy_decision !== 'BLOCK' ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300' : 'border-slate-800 bg-slate-950/60 text-slate-400'
            }`}>
              <div className="text-[10px] font-mono uppercase font-bold">5. Network Wire</div>
              <div className="text-[11px] text-slate-300 mt-0.5">Tokenized Payload</div>
            </div>

            {/* Stage 6: External AI */}
            <div className={`p-3 rounded-xl border text-center transition-all ${
              result && result.policy_decision !== 'BLOCK' ? 'border-indigo-500/50 bg-indigo-500/10 text-indigo-300' : 'border-slate-800 bg-slate-950/60 text-slate-400'
            }`}>
              <div className="text-[10px] font-mono uppercase font-bold">6. External AI</div>
              <div className="text-[11px] text-slate-300 mt-0.5">Zero PII Received</div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick-Fill Scenario Selector */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
            Simulate Live Outbound Prompts
          </span>
          <span className="text-xs text-slate-500">Click a scenario to load into firewall interceptor</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {DEMO_SCENARIOS.map((sc) => (
            <HoverCard
              key={sc.id}
              onClick={() => {
                setPrompt(sc.prompt);
                setResult(null);
                setError(null);
                setActivePipelineStep(0);
              }}
              className="text-left p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/50 hover:bg-slate-900/90 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-300 group-hover:text-white transition-colors">
                  {sc.title}
                </span>
                <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border ${sc.badgeColor}`}>
                  {sc.badge}
                </span>
              </div>
              <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">{sc.prompt}</p>
            </HoverCard>
          ))}
        </div>
      </div>

      {/* Main Firewall Studio Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Outbound Prompt & Controls */}
        <div className="lg:col-span-6 space-y-5">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 sm:p-5 space-y-4 shadow-lg backdrop-blur-md">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-white font-semibold text-sm">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>Outbound Prompt Interceptor</span>
              </div>

              {/* Provider Selection */}
              <div className="flex items-center gap-2">
                <label className="text-[11px] text-slate-400 font-mono shrink-0">Target Provider:</label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-cyan-500 font-mono w-full sm:w-auto"
                >
                  {providers.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.display_name} {p.is_demo ? '(Local Engine)' : p.is_available ? '(Connected)' : '(Mock/Disabled)'}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Prompt Input */}
            <div className="relative">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={7}
                placeholder="Type or paste any query or sensitive prompt you intend to send to an external AI..."
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 sm:p-4 text-slate-200 text-xs font-mono focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/20 leading-relaxed transition-all resize-none"
              />
              <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-1 text-[11px] text-slate-500 mt-2 px-1 font-mono">
                <span>{prompt.length} characters</span>
                <span className="flex items-center gap-1 text-cyan-400">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Active Privacy Policy Guard
                </span>
              </div>
            </div>

            {/* Action Bar */}
            <div className="flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  setPrompt('');
                  setResult(null);
                  setActivePipelineStep(0);
                }}
                className="text-xs text-slate-500 hover:text-slate-300 transition-colors font-mono py-1 text-center"
              >
                Clear input
              </button>
              <motion.button
                onClick={handleSendPrompt}
                disabled={loading || !prompt.trim()}
                whileHover={shouldReduceMotion ? {} : { y: -1 }}
                whileTap={shouldReduceMotion ? {} : { scale: 0.97 }}
                className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all w-full sm:w-auto"
              >
                {loading ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin text-cyan-300" />
                    <span>Firewall Intercepting...</span>
                  </>
                ) : (
                  <>
                    <span>Transmit via Privacy Firewall</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                  </>
                )}
              </motion.button>
            </div>
          </div>

          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-3"
            >
              <XCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </motion.div>
          )}

          {/* Policy Decision Summary Card */}
          {result && (
            <motion.div
              initial={shouldReduceMotion ? {} : { opacity: 0, y: 16, filter: 'blur(4px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
              className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-lg backdrop-blur-md"
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider">
                  Firewall Enforcement Verdict
                </span>
                {getDecisionBadge(result.policy_decision)}
              </div>

              {/* Policy Reasoning */}
              <div className="bg-slate-950/70 rounded-xl p-3.5 border border-slate-800 space-y-1.5">
                <div className="text-xs font-semibold text-slate-300">Policy Evaluation Logic:</div>
                <ul className="text-xs text-slate-400 space-y-1 list-disc list-inside leading-relaxed font-sans">
                  {result.policy_reasons.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>

              {/* Sub-Millisecond Latency Breakdown */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center font-mono">
                <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Detection</div>
                  <div className="text-xs font-semibold text-slate-300 mt-0.5">{result.latencies_ms.detection_ms} ms</div>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Policy Check</div>
                  <div className="text-xs font-semibold text-slate-300 mt-0.5">{result.latencies_ms.policy_ms} ms</div>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Pseudonymize</div>
                  <div className="text-xs font-semibold text-slate-300 mt-0.5">{result.latencies_ms.tokenization_ms} ms</div>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                  <div className="text-[10px] text-slate-500 uppercase">Total Latency</div>
                  <div className="text-xs font-semibold text-cyan-400 mt-0.5">{result.latencies_ms.total_ms} ms</div>
                </div>
              </div>

              {/* Zero Leak Invariant Guarantee */}
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Lock className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-medium text-emerald-300">
                    External Network PII Leakage:
                  </span>
                </div>
                <span className="text-xs font-bold font-mono text-emerald-400 flex items-center gap-1.5">
                  <Check className="w-4 h-4" />
                  {result.exposure_summary.sensitive_values_transmitted_externally} RAW BYTES EXPOSED
                </span>
              </div>
            </motion.div>
          )}
        </div>

        {/* Right Column: Wire Inspection & Signature Morphing Animation */}
        <div className="lg:col-span-6 space-y-5">
          {/* Wire Inspection Panel */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-lg backdrop-blur-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-white font-semibold text-sm">
                <Server className="w-4 h-4 text-cyan-400" />
                <span>Network Wire Inspection (Payload Received by AI Provider)</span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                HTTP OUTBOUND
              </span>
            </div>

            {result ? (
              result.policy_decision === 'BLOCK' ? (
                <motion.div
                  initial={shouldReduceMotion ? {} : { scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="bg-rose-950/20 border border-rose-800/40 rounded-xl p-6 text-center space-y-3"
                >
                  <div className="w-12 h-12 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 mx-auto">
                    <XCircle className="w-6 h-6" />
                  </div>
                  <h4 className="text-sm font-bold text-rose-300 font-mono tracking-tight">OUTBOUND WIRE TRANSMISSION TERMINATED</h4>
                  <p className="text-xs text-rose-400/80 max-w-md mx-auto leading-relaxed">
                    Critical compound risk detected. The firewall halted this request prior to opening any socket connection. 
                    Zero network packets were sent to {result.provider_display_name}.
                  </p>
                </motion.div>
              ) : (
                <div className="space-y-3">
                  <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto relative group">
                    <pre className="whitespace-pre-wrap">{result.provider_received_prompt}</pre>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span>
                      Target: <strong className="text-slate-200">{result.provider_display_name}</strong>
                    </span>
                    <span className="text-cyan-400 flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      All sensitive entities replaced with typed tokens
                    </span>
                  </div>
                </div>
              )
            ) : (
              <div className="bg-slate-950/50 rounded-xl p-8 border border-slate-800/50 text-center space-y-2">
                <Terminal className="w-7 h-7 text-slate-600 mx-auto" />
                <div className="text-xs text-slate-400 font-medium">Awaiting Outbound Interception</div>
                <div className="text-[11px] text-slate-600">Transmit a prompt on the left to inspect outbound wire contents.</div>
              </div>
            )}
          </div>

          {/* Signature Live Privacy Transformation Showcase */}
          {result && result.entities_detected.length > 0 && result.policy_decision !== 'BLOCK' && (
            <motion.div
              initial={shouldReduceMotion ? {} : { opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-slate-900/80 border border-indigo-500/30 rounded-2xl p-5 space-y-3 shadow-lg backdrop-blur-md"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-cyan-400 flex items-center gap-1.5 uppercase tracking-wider">
                  <Binary className="w-3.5 h-3.5" />
                  Live Privacy Morphing Sequence
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                  ACTIVE TOKENS: {result.exposure_summary.tokens_mapped_count}
                </span>
              </div>

              <div className="space-y-2 pt-1">
                {result.entities_detected.map((ent, idx) => (
                  <div 
                    key={idx}
                    className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between gap-4 font-mono text-xs"
                  >
                    <div className="space-y-0.5">
                      <div className="text-[10px] text-slate-500 uppercase">{ent.entity_type} IDENTIFIED</div>
                      <div className="text-rose-400 line-through text-[11px]">{ent.masked_preview}</div>
                    </div>

                    <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />

                    <div className="space-y-0.5 text-center">
                      <div className="text-[10px] text-slate-500 uppercase">SCRUBBED</div>
                      <div className="text-slate-400 text-[11px] tracking-widest">████████</div>
                    </div>

                    <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0" />

                    <div className="space-y-0.5 text-right">
                      <div className="text-[10px] text-cyan-400 uppercase">TOKEN ON WIRE</div>
                      <div className="text-cyan-300 font-bold text-[11px]">{`<${ent.entity_type}_01>`}</div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* AI Response & Local Rehydration Terminal */}
          {result && result.policy_decision !== 'BLOCK' && (
            <motion.div
              initial={shouldReduceMotion ? {} : { opacity: 0, y: 16, filter: 'blur(4px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
              className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-lg backdrop-blur-md"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-white font-semibold text-sm">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  <span>Provider Response & Local Rehydration</span>
                </div>

                {/* Hydration Toggle */}
                {result.policy_decision === 'PROTECT' && (
                  <button
                    onClick={() => setShowRehydrated(!showRehydrated)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs hover:bg-indigo-500/20 transition-colors font-mono"
                  >
                    {showRehydrated ? (
                      <>
                        <EyeOff className="w-3.5 h-3.5 text-cyan-400" />
                        <span>View Raw Wire Tokens</span>
                      </>
                    ) : (
                      <>
                        <Eye className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Hydrate for User Session</span>
                      </>
                    )}
                  </button>
                )}
              </div>

              {/* Terminal Output */}
              <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto whitespace-pre-wrap">
                {showRehydrated
                  ? (customRehydratedText || result.rehydrated_response)
                  : result.provider_raw_response}
              </div>

              {/* Rehydration Explainer */}
              {result.policy_decision === 'PROTECT' && (
                <div className="flex items-center justify-between pt-1 font-mono text-[11px]">
                  <span className="text-slate-500">
                    {showRehydrated
                      ? "✓ Tokens restored locally in browser session. Remote provider never saw these values."
                      : "Viewing raw tokens as returned by the AI provider (<AADHAAR_01>, <PHONE_01>)."}
                  </span>
                  <button
                    onClick={handleManualRehydration}
                    disabled={isRehydrating}
                    className="text-cyan-400 hover:text-cyan-300 inline-flex items-center gap-1 transition-colors"
                  >
                    <RotateCcw className={`w-3 h-3 ${isRehydrating ? 'animate-spin' : ''}`} />
                    <span>Re-verify Rehydration</span>
                  </button>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};
