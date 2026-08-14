import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  GraduationCap,
  Sparkles,
  GitCommit,
  ArrowRight,
  TrendingUp,
  Brain,
  Layers,
  CheckCircle2,
  AlertTriangle,
  Play,
  Zap,
  BookOpen,
  Eye,
  Sliders,
  Award,
  RefreshCw,
  GitFork,
  Link
} from 'lucide-react';

export function CurriculumStudio({ onSelectProblem }) {
  const [startProblem, setStartProblem] = useState('meeting-rooms');
  const [targetLength, setTargetLength] = useState(8);
  const [beamWidth, setBeamWidth] = useState(10);
  const [compiledResult, setCompiledResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('compiler'); // 'compiler', 'bridge_tester', 'signatures'

  // Bridge simulator state
  const [bridgeSource, setBridgeSource] = useState('meeting-rooms');
  const [bridgeTarget, setBridgeTarget] = useState('minimum-number-of-arrows-to-burst-balloons');
  const [bridgeResult, setBridgeResult] = useState(null);
  const [bridgeLoading, setBridgeLoading] = useState(false);

  // Signatures list
  const [signatures, setSignatures] = useState([]);

  useEffect(() => {
    fetch('/api/curriculum/gold-standard')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setSignatures(data.signatures || []);
        }
      })
      .catch(err => console.error(err));

    // Auto compile on initial load
    handleCompile();
  }, []);

  const handleCompile = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/curriculum/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_problem_id: startProblem,
          target_length: Number(targetLength),
          beam_width: Number(beamWidth)
        })
      });
      const data = await res.json();
      setCompiledResult(data);
    } catch (err) {
      console.error('Failed to compile curriculum:', err);
    }
    setLoading(false);
  };

  const handleTestBridge = async () => {
    setBridgeLoading(true);
    try {
      const res = await fetch('/api/curriculum/bridge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_id: bridgeSource,
          target_id: bridgeTarget,
          cognitive_jump_threshold: 2
        })
      });
      const data = await res.json();
      setBridgeResult(data.data);
    } catch (err) {
      console.error('Failed to test bridge:', err);
    }
    setBridgeLoading(false);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs mb-1.5 uppercase tracking-wider">
              <GraduationCap className="w-4 h-4 text-cyan-400" />
              <span>Pedagogy-Driven Curriculum Compiler V2</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-3">
              Intelligent Tutoring Engine & Beam Search Path Compiler
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800/60 font-mono font-normal">
                Beam Width K={beamWidth}
              </span>
            </h2>
            <p className="text-sm text-slate-400 max-w-2xl mt-1">
              Compiles problem sequences by maximizing expected learning gain, concept continuity, and prerequisite retention while bounding multi-dimensional cognitive jumps.
            </p>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center gap-1.5 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800/80">
            <button
              onClick={() => setActiveView('compiler')}
              className={`px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                activeView === 'compiler'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Path Compiler
            </button>
            <button
              onClick={() => setActiveView('bridge_tester')}
              className={`px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                activeView === 'bridge_tester'
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Bridge Insertion
            </button>
            <button
              onClick={() => setActiveView('signatures')}
              className={`px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                activeView === 'signatures'
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Skill Signatures
            </button>
          </div>
        </div>
      </div>

      {/* VIEW 1: PATH COMPILER */}
      {activeView === 'compiler' && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-sm grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1.5">Start Baseline Problem</label>
              <select
                value={startProblem}
                onChange={(e) => setStartProblem(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {signatures.map(s => (
                  <option key={s.problem_id} value={s.problem_id}>
                    {s.title || s.problem_id} (Diff: {s.difficulty_matrix.algorithmic}/5)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1.5">Sequence Steps ({targetLength})</label>
              <input
                type="range"
                min="4"
                max="12"
                value={targetLength}
                onChange={(e) => setTargetLength(Number(e.target.value))}
                className="w-full accent-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1.5">Beam Width K ({beamWidth})</label>
              <input
                type="range"
                min="5"
                max="20"
                value={beamWidth}
                onChange={(e) => setBeamWidth(Number(e.target.value))}
                className="w-full accent-cyan-500"
              />
            </div>

            <div>
              <button
                onClick={handleCompile}
                disabled={loading}
                className="w-full py-2 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 text-white font-medium text-xs flex items-center justify-center gap-2 hover:opacity-90 transition-opacity shadow-lg shadow-indigo-500/20 disabled:opacity-50"
              >
                {loading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 fill-white" />
                )}
                <span>Compile Curriculum</span>
              </button>
            </div>
          </div>

          {/* Path Compilation Output */}
          {compiledResult && (
            <div className="space-y-6">
              {/* Metrics Summary Banner */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-0.5">Concept Coverage</div>
                  <div className="text-xl font-bold text-slate-100 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-cyan-400" />
                    {compiledResult.metrics?.concept_coverage_count} Concepts
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-0.5">Knowledge Retention</div>
                  <div className="text-xl font-bold text-emerald-400 flex items-center gap-2">
                    <Brain className="w-4 h-4" />
                    {Math.round((compiledResult.metrics?.average_retention_ratio || 0) * 100)}%
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-0.5">Prerequisite Violations</div>
                  <div className="text-xl font-bold text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    {compiledResult.metrics?.prerequisite_violations_count} (Zero)
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[11px] font-mono text-slate-400 mb-0.5">Pedagogical Score</div>
                  <div className="text-xl font-bold text-indigo-400 flex items-center gap-2">
                    <Award className="w-4 h-4" />
                    {compiledResult.global_pedagogical_score}
                  </div>
                </div>
              </div>

              {/* Step-by-Step Pedagogical Timeline */}
              <div className="space-y-4 relative before:absolute before:left-6 before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-800">
                {compiledResult.steps?.map((step, idx) => {
                  const delta = step.transition_delta;
                  const diff = step.difficulty_matrix;

                  return (
                    <motion.div
                      key={step.problem_id}
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="relative flex items-start gap-4 pl-1"
                    >
                      {/* Step Indicator Node */}
                      <div className="w-10 h-10 rounded-xl bg-slate-900 border-2 border-indigo-500/80 flex items-center justify-center text-xs font-mono font-bold text-indigo-300 shadow-lg shadow-indigo-500/20 shrink-0 z-10">
                        {step.sequence_step}
                      </div>

                      {/* Problem Card Details */}
                      <div className="flex-1 bg-slate-900/70 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all backdrop-blur-md">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800/80">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/50">
                                {step.canonical_pattern}
                              </span>
                              <span className="text-xs text-slate-400 font-mono">
                                Ops: {step.operations?.join(', ')}
                              </span>
                            </div>
                            <h4 className="text-base font-bold text-slate-100">{step.title}</h4>
                          </div>

                          <div className="flex items-center gap-2 shrink-0">
                            <button
                              onClick={() => onSelectProblem && onSelectProblem({ task_id: step.problem_id, title: step.title })}
                              className="px-3 py-1.5 rounded-lg bg-indigo-950/60 text-indigo-300 border border-indigo-800/60 text-xs font-medium hover:bg-indigo-900 transition-colors flex items-center gap-1.5"
                            >
                              <Eye className="w-3.5 h-3.5" />
                              <span>Inspect</span>
                            </button>
                          </div>
                        </div>

                        {/* Explainability Rationale */}
                        <div className="my-3 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs text-slate-300 leading-relaxed font-sans">
                          <span className="font-mono text-cyan-400 font-semibold mr-1.5">Pedagogical Rationale:</span>
                          {step.pedagogical_reason}
                        </div>

                        {/* 6-Dimensional Difficulty Matrix Pill Bar */}
                        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/60 text-[11px] font-mono text-slate-400">
                          <span className="text-slate-500">Cognitive Load:</span>
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                            Alg: {diff.algorithmic}/5
                          </span>
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                            Reasoning: {diff.reasoning}/5
                          </span>
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                            Impl: {diff.implementation}/5
                          </span>
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                            State: {diff.state_complexity}/5
                          </span>

                          {delta && (
                            <div className="ml-auto flex items-center gap-2">
                              <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/50">
                                Retained: {Math.round(delta.retention_ratio * 100)}%
                              </span>
                              <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/50">
                                Novelty: {Math.round(delta.new_concept_ratio * 100)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* VIEW 2: DYNAMIC BRIDGE INSERTION TESTER */}
      {activeView === 'bridge_tester' && (
        <div className="space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
            <h3 className="text-base font-bold text-slate-100 mb-2 flex items-center gap-2">
              <GitFork className="w-5 h-5 text-cyan-400" />
              Dynamic Bridge Problem Generator
            </h3>
            <p className="text-xs text-slate-400 mb-6 max-w-2xl">
              Simulate cognitive difficulty overload or prerequisite gaps. The compiler evaluates the vector delta and dynamically inserts intermediate scaffolding problems (Source &rarr; Bridge &rarr; Target).
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1.5">Source Problem (Learned)</label>
                <select
                  value={bridgeSource}
                  onChange={(e) => setBridgeSource(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  {signatures.map(s => (
                    <option key={s.problem_id} value={s.problem_id}>
                      {s.title || s.problem_id} (Diff: {s.difficulty_matrix.algorithmic}/5)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1.5">Target Problem (Challenging)</label>
                <select
                  value={bridgeTarget}
                  onChange={(e) => setBridgeTarget(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  {signatures.map(s => (
                    <option key={s.problem_id} value={s.problem_id}>
                      {s.title || s.problem_id} (Diff: {s.difficulty_matrix.algorithmic}/5)
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={handleTestBridge}
              disabled={bridgeLoading}
              className="py-2.5 px-5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              {bridgeLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              <span>Evaluate Transition & Generate Bridge</span>
            </button>
          </div>

          {/* Bridge Output Result */}
          {bridgeResult && (
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 backdrop-blur-md">
              {bridgeResult.bridge_needed ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-amber-400 text-sm font-semibold">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Bridge Problem Inserted Dynamically!</span>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300">
                    <div className="font-mono text-slate-400 mb-1">Scaffolded Progression Path:</div>
                    <div className="text-base font-bold text-cyan-400 flex items-center gap-2">
                      <span>{bridgeResult.progression_path?.[0]}</span>
                      <ArrowRight className="w-4 h-4 text-slate-600" />
                      <span className="px-2.5 py-1 rounded-lg bg-cyan-950 text-cyan-300 border border-cyan-800">
                        {bridgeResult.progression_path?.[1]} (Bridge)
                      </span>
                      <ArrowRight className="w-4 h-4 text-slate-600" />
                      <span>{bridgeResult.progression_path?.[2]}</span>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
                    <div className="font-mono text-indigo-400 font-semibold mb-1">Pedagogical Justification:</div>
                    {bridgeResult.pedagogical_rationale}
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3 text-emerald-400">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="text-sm font-semibold">{bridgeResult.reason}</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* VIEW 3: SKILL SIGNATURES REGISTRY */}
      {activeView === 'signatures' && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {signatures.map((sig) => (
            <div key={sig.problem_id} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/50">
                    {sig.canonical_pattern}
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    Diff: {sig.difficulty_matrix.algorithmic}/5
                  </span>
                </div>
                <h4 className="text-sm font-bold text-slate-100 mb-2">{sig.title}</h4>

                <div className="space-y-2 text-xs text-slate-300 mb-4">
                  <div>
                    <span className="text-slate-500 font-mono">Introduced: </span>
                    <span className="text-emerald-400">{sig.introduced_concepts?.join(', ')}</span>
                  </div>
                  {sig.prerequisite_concepts?.length > 0 && (
                    <div>
                      <span className="text-slate-500 font-mono">Prerequisites: </span>
                      <span className="text-amber-400">{sig.prerequisite_concepts?.join(', ')}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-slate-500 font-mono">Operations: </span>
                    <span className="text-cyan-400">{sig.operations?.join(', ')}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => onSelectProblem && onSelectProblem({ task_id: sig.problem_id, title: sig.title })}
                className="w-full py-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-medium transition-colors"
              >
                Inspect Problem Details
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
