/**
 * LearningJourney.jsx
 *
 * The learner's primary interface. The engine (beam search, bridge insertion,
 * concept graph) is entirely behind this experience — the learner sees:
 *
 *   Your path  →  Current problem  →  Why next  →  Solve  →  Continue
 *
 * No "compiler", no "beam width K=10", no "signatures tab". Those details
 * live in the backend. The learner sees learning.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  Circle,
  ArrowRight,
  Brain,
  Sparkles,
  Zap,
  AlertTriangle,
  RefreshCw,
  ExternalLink,
  BookMarked,
  Target,
  TrendingUp,
  Lock,
  Unlock
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────────────
// Difficulty color helper
const diffColor = (d) => {
  if (d <= 1) return 'text-emerald-400';
  if (d <= 2) return 'text-cyan-400';
  if (d <= 3) return 'text-amber-400';
  if (d <= 4) return 'text-orange-400';
  return 'text-red-400';
};

const diffBg = (d) => {
  if (d <= 1) return 'bg-emerald-950/60 border-emerald-800/50';
  if (d <= 2) return 'bg-cyan-950/60 border-cyan-800/50';
  if (d <= 3) return 'bg-amber-950/60 border-amber-800/50';
  return 'bg-red-950/60 border-red-800/50';
};

// ─────────────────────────────────────────────────────────────────────────────
// Path Rail — horizontal progress strip
function PathRail({ steps, currentIdx, onJump, solvedIds }) {
  return (
    <div className="relative">
      <div className="flex items-center gap-1 overflow-x-auto no-scrollbar pb-1">
        {steps.map((step, i) => {
          const solved = solvedIds.has(step.problem_id);
          const isCurrent = i === currentIdx;
          const isPast = i < currentIdx;
          const isFuture = i > currentIdx;

          return (
            <React.Fragment key={step.problem_id}>
              <button
                onClick={() => onJump(i)}
                className={`relative flex-shrink-0 flex flex-col items-center gap-1 group`}
                title={step.title}
              >
                {/* Node */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all duration-200 ${
                  isCurrent
                    ? 'bg-indigo-600 border-indigo-400 text-white shadow-lg shadow-indigo-500/40 scale-110'
                    : solved
                    ? 'bg-emerald-900/60 border-emerald-600 text-emerald-300'
                    : isPast
                    ? 'bg-slate-800 border-slate-600 text-slate-400'
                    : 'bg-slate-900 border-slate-700 text-slate-500 hover:border-slate-500'
                }`}>
                  {solved ? <CheckCircle2 className="w-4 h-4" /> : i + 1}
                </div>

                {/* Label (current only) */}
                {isCurrent && (
                  <motion.div
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] font-medium text-indigo-300"
                  >
                    YOU ARE HERE
                  </motion.div>
                )}
              </button>

              {/* Connector */}
              {i < steps.length - 1 && (
                <div className={`w-6 h-0.5 flex-shrink-0 transition-colors ${
                  i < currentIdx ? 'bg-emerald-700' : 'bg-slate-800'
                }`} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// "Why this problem?" explanation panel
function WhyThisNext({ delta, step }) {
  if (!delta) return null;
  const retainPct = Math.round((delta.retention_ratio || 0) * 100);
  const novelPct = Math.round((delta.new_concept_ratio || 0) * 100);

  // Dominant cognitive jump dimension
  const jumps = delta.cognitive_jumps || {};
  const maxJumpDim = Object.entries(jumps).reduce((best, [k, v]) =>
    v > (best[1] || 0) ? [k, v] : best, ['', 0]);
  const jumpLabel = maxJumpDim[0]?.replace(/_/g, ' ') || '';
  const jumpVal = maxJumpDim[1] || 0;

  const retainedConcepts = delta.retained_concepts || [];
  const newConcepts = delta.new_concepts || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5"
    >
      <h3 className="text-xs font-mono uppercase tracking-wider text-slate-500 mb-4">
        Why this is next
      </h3>

      <div className="grid grid-cols-3 gap-3">
        {/* Retention */}
        <div className="bg-slate-950/70 rounded-xl p-3 border border-slate-800/80">
          <div className="text-[10px] font-mono text-slate-500 uppercase mb-1">Retains</div>
          <div className="text-2xl font-bold text-emerald-400 mb-2">{retainPct}%</div>
          {retainedConcepts.length > 0 ? (
            <div className="space-y-0.5">
              {retainedConcepts.slice(0, 3).map(c => (
                <div key={c} className="text-[11px] text-emerald-300/80 font-mono leading-snug">
                  {c.replace(/_/g, ' ')}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-[11px] text-slate-600 font-mono">starting fresh</div>
          )}
        </div>

        {/* Novelty */}
        <div className="bg-slate-950/70 rounded-xl p-3 border border-slate-800/80">
          <div className="text-[10px] font-mono text-slate-500 uppercase mb-1">Introduces</div>
          <div className="text-2xl font-bold text-cyan-400 mb-2">{novelPct}%</div>
          {newConcepts.length > 0 ? (
            <div className="space-y-0.5">
              {newConcepts.slice(0, 3).map(c => (
                <div key={c} className="text-[11px] text-cyan-300/80 font-mono leading-snug">
                  {c.replace(/_/g, ' ')}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-[11px] text-slate-600 font-mono">no new concepts</div>
          )}
        </div>

        {/* Cognitive jump */}
        <div className="bg-slate-950/70 rounded-xl p-3 border border-slate-800/80">
          <div className="text-[10px] font-mono text-slate-500 uppercase mb-1">Cognitive jump</div>
          <div className={`text-2xl font-bold mb-2 ${jumpVal === 0 ? 'text-emerald-400' : jumpVal <= 2 ? 'text-amber-400' : 'text-orange-400'}`}>
            {jumpVal === 0 ? '~0' : `+${jumpVal}`}
          </div>
          <div className="text-[11px] text-slate-400 font-mono leading-snug capitalize">
            {jumpVal === 0
              ? 'Smooth continuation'
              : `${jumpLabel} increases`}
          </div>
        </div>
      </div>

      {/* Pedagogical rationale */}
      {delta.mechanism_change_summary && (
        <div className="mt-3 px-3 py-2 rounded-xl bg-slate-950/50 border border-slate-800/50 text-[11px] text-slate-400 leading-relaxed font-mono">
          <span className="text-indigo-400 mr-1">mechanism:</span>
          {delta.mechanism_change_summary}
        </div>
      )}
    </motion.div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Bridge card — shown automatically, not a separate tool
function BridgeCard({ bridge }) {
  if (!bridge?.bridge_needed) return null;
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-amber-950/30 border border-amber-800/50 rounded-2xl p-5"
    >
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg bg-amber-900/50 border border-amber-800/60 flex items-center justify-center flex-shrink-0">
          <Zap className="w-4 h-4 text-amber-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-semibold text-amber-300 mb-1">Adding an intermediate step</div>
          <div className="text-xs text-amber-200/70 leading-relaxed mb-3">
            {bridge.reason || 'The concept gap to the next problem is too large to jump directly. We have inserted one intermediate problem to scaffold your understanding.'}
          </div>
          {bridge.progression_path && (
            <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
              <span className="text-slate-500">{bridge.progression_path[0]}</span>
              <ArrowRight className="w-3 h-3 text-amber-500" />
              <span className="px-2 py-0.5 rounded-md bg-amber-900/50 text-amber-300 border border-amber-800/60">
                {bridge.progression_path[1]}
              </span>
              <ArrowRight className="w-3 h-3 text-slate-600" />
              <span className="text-slate-500">{bridge.progression_path[2]}</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Current problem card
function ProblemCard({ step, stepIdx, totalSteps, isSolved, onSolve, onUnsolved, onSelectProblem }) {
  const diff = step.difficulty_matrix || {};
  const alg = diff.algorithmic || 1;

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-sm">
      {/* Problem header */}
      <div className={`px-6 py-4 border-b border-slate-800 flex items-start justify-between gap-4`}>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${diffBg(alg)} ${diffColor(alg)}`}>
              Difficulty {alg}/5
            </span>
            {step.canonical_pattern && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                {step.canonical_pattern}
              </span>
            )}
            <span className="text-[10px] font-mono text-slate-600">
              Step {stepIdx + 1} of {totalSteps}
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight">{step.title || step.problem_id}</h2>
          {step.operations?.length > 0 && (
            <div className="mt-1.5 flex flex-wrap gap-1">
              {step.operations.map(op => (
                <span key={op} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800/70 text-indigo-300/80 border border-slate-700/60">
                  {op}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={() => onSelectProblem && onSelectProblem({ task_id: step.problem_id, title: step.title })}
            className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors border border-slate-700"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Details</span>
          </button>
        </div>
      </div>

      {/* Concepts this problem builds */}
      <div className="px-6 py-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
        {step.introduced_concepts?.length > 0 && (
          <div>
            <div className="text-[10px] font-mono uppercase text-slate-500 mb-2">Concepts you will practice</div>
            <div className="flex flex-wrap gap-1.5">
              {step.introduced_concepts.map(c => (
                <span key={c} className="text-[11px] px-2 py-0.5 rounded-md bg-indigo-950/60 text-indigo-300 border border-indigo-800/50 font-mono">
                  {c.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        )}

        {step.prerequisite_concepts?.length > 0 && (
          <div>
            <div className="text-[10px] font-mono uppercase text-slate-500 mb-2">Prerequisites unlocked</div>
            <div className="flex flex-wrap gap-1.5">
              {step.prerequisite_concepts.map(c => (
                <span key={c} className="text-[11px] px-2 py-0.5 rounded-md bg-emerald-950/60 text-emerald-300 border border-emerald-800/50 font-mono">
                  <CheckCircle2 className="inline w-2.5 h-2.5 mr-0.5 mb-0.5" />
                  {c.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Solve CTA */}
      <div className="px-6 py-4 border-t border-slate-800/60 flex items-center justify-between gap-4">
        {isSolved ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-emerald-400 font-medium">
              <CheckCircle2 className="w-5 h-5" />
              Solved
            </div>
            <button
              onClick={onUnsolved}
              className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
            >
              Mark unsolved
            </button>
          </div>
        ) : (
          <button
            onClick={onSolve}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 text-white text-sm font-semibold flex items-center gap-2 hover:opacity-90 transition-opacity shadow-lg shadow-indigo-500/20"
          >
            <CheckCircle2 className="w-4 h-4" />
            Mark as Solved &amp; Continue
          </button>
        )}

        {/* 6D difficulty sparkbar */}
        <div className="hidden sm:flex items-center gap-2">
          <span className="text-[10px] font-mono text-slate-600 uppercase">cognitive load</span>
          <div className="flex items-end gap-0.5 h-5">
            {['algorithmic', 'implementation', 'reasoning', 'state_complexity', 'edge_cases', 'cognitive_load'].map((dim, i) => {
              const val = diff[dim] || 1;
              return (
                <div
                  key={dim}
                  title={`${dim.replace(/_/g, ' ')}: ${val}/5`}
                  className={`w-2 rounded-sm ${diffColor(val).replace('text-', 'bg-')}`}
                  style={{ height: `${(val / 5) * 100}%`, minHeight: 4, opacity: 0.75 }}
                />
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Compiler health status — small, tucked away
function CompilerHealth({ metrics }) {
  if (!metrics) return null;
  return (
    <div className="flex items-center gap-3 text-[10px] font-mono text-slate-600">
      <span className="flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        {metrics.concept_coverage_count} concepts covered
      </span>
      <span>·</span>
      <span>{Math.round((metrics.average_retention_ratio || 0) * 100)}% avg retention</span>
      <span>·</span>
      <span className={metrics.prerequisite_violations_count === 0 ? 'text-emerald-600' : 'text-red-500'}>
        {metrics.prerequisite_violations_count} prerequisite violations
      </span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Start selector
function StartSelector({ signatures, onStart, loading }) {
  const [selected, setSelected] = useState('meeting-rooms');
  const [length, setLength] = useState(8);

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center gap-8 py-16">
      {/* Hero */}
      <div className="text-center max-w-lg">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600/30 via-cyan-500/20 to-purple-600/20 border border-indigo-600/30 flex items-center justify-center mx-auto mb-5">
          <Brain className="w-8 h-8 text-indigo-400" />
        </div>
        <h1 className="text-2xl font-bold text-slate-100 mb-3 tracking-tight">Your learning path</h1>
        <p className="text-sm text-slate-400 leading-relaxed">
          The engine will compile a personalized sequence of problems, ordering them so each step retains what you know and introduces only as much as you can absorb.
        </p>
      </div>

      {/* Config */}
      <div className="w-full max-w-sm space-y-4">
        <div>
          <label className="block text-xs font-mono text-slate-400 mb-2">Start from</label>
          <select
            value={selected}
            onChange={e => setSelected(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
          >
            {signatures.map(s => (
              <option key={s.problem_id} value={s.problem_id}>
                {s.title || s.problem_id} — difficulty {s.difficulty_matrix?.algorithmic}/5
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-mono text-slate-400 mb-2">
            Path length — {length} problems
          </label>
          <input
            type="range" min={4} max={12} value={length}
            onChange={e => setLength(Number(e.target.value))}
            className="w-full accent-indigo-500"
          />
        </div>

        <button
          onClick={() => onStart(selected, length)}
          disabled={loading}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 text-white font-semibold text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50 shadow-lg shadow-indigo-500/20"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          Build my learning path
        </button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main export
export function LearningJourney({ onSelectProblem }) {
  const [signatures, setSignatures] = useState([]);
  const [compiledPath, setCompiledPath] = useState(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [solvedIds, setSolvedIds] = useState(() => {
    try { return new Set(JSON.parse(localStorage.getItem('lc_solved') || '[]')); }
    catch { return new Set(); }
  });
  const [bridge, setBridge] = useState(null);
  const [loading, setLoading] = useState(false);
  const [bridgeLoading, setBridgeLoading] = useState(false);

  // Persist solved
  useEffect(() => {
    localStorage.setItem('lc_solved', JSON.stringify([...solvedIds]));
  }, [solvedIds]);

  // Load gold-standard signatures for the start selector
  useEffect(() => {
    fetch('/api/curriculum/gold-standard')
      .then(r => r.json())
      .then(d => d.status === 'success' && setSignatures(d.signatures || []))
      .catch(console.error);
  }, []);

  const compilePath = useCallback(async (startId, length) => {
    setLoading(true);
    setBridge(null);
    try {
      const res = await fetch('/api/curriculum/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_problem_id: startId, target_length: length, beam_width: 10 })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setCompiledPath(data);
        setCurrentIdx(0);
      }
    } catch (err) { console.error(err); }
    setLoading(false);
  }, []);

  // Auto-check for bridge whenever we advance to a new step
  const checkBridge = useCallback(async (steps, fromIdx) => {
    const src = steps[fromIdx];
    const tgt = steps[fromIdx + 1];
    if (!src || !tgt) { setBridge(null); return; }
    setBridgeLoading(true);
    try {
      const res = await fetch('/api/curriculum/bridge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_id: src.problem_id,
          target_id: tgt.problem_id,
          cognitive_jump_threshold: 2
        })
      });
      const data = await res.json();
      setBridge(data.data || null);
    } catch (err) { console.error(err); }
    setBridgeLoading(false);
  }, []);

  const handleSolve = () => {
    const step = compiledPath?.steps?.[currentIdx];
    if (!step) return;
    setSolvedIds(prev => new Set([...prev, step.problem_id]));
    const nextIdx = currentIdx + 1;
    if (nextIdx < (compiledPath?.steps?.length || 0)) {
      setCurrentIdx(nextIdx);
      checkBridge(compiledPath.steps, nextIdx);
    }
  };

  const handleUnsolved = () => {
    const step = compiledPath?.steps?.[currentIdx];
    if (!step) return;
    setSolvedIds(prev => { const s = new Set(prev); s.delete(step.problem_id); return s; });
  };

  const handleJump = (idx) => {
    setCurrentIdx(idx);
    if (compiledPath?.steps) checkBridge(compiledPath.steps, idx);
  };

  // ── Render ──────────────────────────────────────────────────────────────

  if (!compiledPath) {
    return (
      <StartSelector
        signatures={signatures}
        onStart={compilePath}
        loading={loading}
      />
    );
  }

  const steps = compiledPath.steps || [];
  const currentStep = steps[currentIdx];
  const prevStep = steps[currentIdx - 1];
  const delta = currentStep?.transition_delta;
  const isFirstStep = currentIdx === 0;
  const isLastStep = currentIdx === steps.length - 1;
  const isSolved = solvedIds.has(currentStep?.problem_id);
  const allSolved = steps.every(s => solvedIds.has(s.problem_id));

  return (
    <div className="space-y-6">
      {/* ── Path rail ── */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl px-6 pt-5 pb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-200">Your learning path</h2>
            <div className="text-xs text-slate-500 mt-0.5">
              {solvedIds.size} of {steps.length} solved
            </div>
          </div>
          <button
            onClick={() => { setCompiledPath(null); setBridge(null); }}
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" />
            Rebuild path
          </button>
        </div>

        <PathRail
          steps={steps}
          currentIdx={currentIdx}
          onJump={handleJump}
          solvedIds={solvedIds}
        />
      </div>

      {/* ── All-solved celebration ── */}
      <AnimatePresence>
        {allSolved && (
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-r from-emerald-950/60 to-cyan-950/40 border border-emerald-800/60 rounded-2xl p-6 text-center"
          >
            <div className="text-3xl mb-3">🎉</div>
            <div className="text-lg font-bold text-emerald-300 mb-1">Path complete!</div>
            <div className="text-sm text-slate-400 mb-4">You have solved every problem in this path. Build a new one to continue progressing.</div>
            <button
              onClick={() => { setCompiledPath(null); setBridge(null); setSolvedIds(new Set()); }}
              className="px-5 py-2 rounded-xl bg-emerald-700 text-white text-sm font-medium hover:bg-emerald-600 transition-colors"
            >
              Start next path
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Bridge card (automatic — no user action required) ── */}
      <AnimatePresence>
        {bridge?.bridge_needed && !bridgeLoading && <BridgeCard bridge={bridge} />}
      </AnimatePresence>

      {/* ── Current problem card ── */}
      {currentStep && (
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep.problem_id}
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -16 }}
            transition={{ duration: 0.18 }}
          >
            <ProblemCard
              step={currentStep}
              stepIdx={currentIdx}
              totalSteps={steps.length}
              isSolved={isSolved}
              onSolve={handleSolve}
              onUnsolved={handleUnsolved}
              onSelectProblem={onSelectProblem}
            />
          </motion.div>
        </AnimatePresence>
      )}

      {/* ── Why this is next (hidden for first step) ── */}
      <AnimatePresence>
        {!isFirstStep && delta && (
          <WhyThisNext delta={delta} step={currentStep} />
        )}
      </AnimatePresence>

      {/* ── Navigation ── */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => handleJump(Math.max(0, currentIdx - 1))}
          disabled={isFirstStep}
          className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-sm flex items-center gap-2 hover:border-slate-600 hover:text-slate-200 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-4 h-4" />
          Previous
        </button>

        {/* Compiler health — small, unobtrusive */}
        <CompilerHealth metrics={compiledPath.metrics} />

        <button
          onClick={() => handleJump(Math.min(steps.length - 1, currentIdx + 1))}
          disabled={isLastStep}
          className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-sm flex items-center gap-2 hover:border-slate-600 hover:text-slate-200 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Next
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

export default LearningJourney;
