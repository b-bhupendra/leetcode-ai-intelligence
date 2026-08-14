import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  GraduationCap, 
  Play, 
  RefreshCw, 
  Eye, 
  Brain, 
  CheckCircle2, 
  ArrowRight, 
  AlertTriangle, 
  Zap, 
  GitFork, 
  Sparkles,
  Layers,
  ChevronRight,
  BookmarkCheck
} from 'lucide-react';

export function CurriculumStudio({ onSelectProblem }) {
  const [startProblem, setStartProblem] = useState('meeting-rooms');
  const [targetLength, setTargetLength] = useState(8);
  const [beamWidth] = useState(10); // Hidden implementation detail
  
  const [signatures, setSignatures] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pathSteps, setPathSteps] = useState([]);
  const [metrics, setMetrics] = useState(null);
  
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [bridgeLoading, setBridgeLoading] = useState(false);

  useEffect(() => {
    fetch('/api/curriculum/gold-standard')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') setSignatures(data.signatures || []);
      })
      .catch(console.error);
    
    // Initial compile
    handleCompile();
  }, []);

  const handleCompile = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/curriculum/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_problem_id: startProblem, target_length: Number(targetLength), beam_width: Number(beamWidth) })
      });
      const data = await res.json();
      setPathSteps(data.steps || []);
      setMetrics(data.metrics);
      setActiveStepIndex(0);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleSimulateStruggleAndInsertBridge = async (currentIndex) => {
    if (currentIndex === 0) return;
    setBridgeLoading(true);
    const targetId = pathSteps[currentIndex].problem_id;
    const sourceId = pathSteps[currentIndex - 1].problem_id;

    try {
      const res = await fetch('/api/curriculum/bridge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_id: sourceId, target_id: targetId, cognitive_jump_threshold: 1 })
      });
      const data = await res.json();
      
      if (data.status === 'success' && data.data.bridge_needed) {
        const bridgeData = data.data.bridge_problem;
        const bridgeStep = {
          isBridge: true,
          sequence_step: `${currentIndex}.5`,
          problem_id: bridgeData.problem_id,
          title: bridgeData.title,
          canonical_pattern: bridgeData.canonical_pattern,
          difficulty_matrix: bridgeData.difficulty_matrix,
          introduced_concepts: bridgeData.introduced_concepts,
          prerequisite_concepts: [],
          operations: bridgeData.operations || ['greedy_selection'],
          pedagogical_reason: data.data.pedagogical_rationale,
          transition_delta: data.data.source_to_bridge_delta
        };
        const updatedPath = [...pathSteps];
        updatedPath.splice(currentIndex, 0, bridgeStep);
        setPathSteps(updatedPath);
        setActiveStepIndex(currentIndex); // Shift focus to newly inserted bridge
      }
    } catch (err) {
      console.error(err);
    }
    setBridgeLoading(false);
  };

  const currentStep = pathSteps[activeStepIndex] || pathSteps[0];
  const delta = currentStep?.transition_delta;
  const diff = currentStep?.difficulty_matrix;

  return (
    <div className="flex flex-col h-full space-y-6">
      
      {/* TOP LEARNING PATH CONFIGURATION & STATUS */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-wrap lg:flex-nowrap items-center justify-between gap-4 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs mb-1 uppercase tracking-wider">
            <GraduationCap className="w-4 h-4 text-cyan-400" />
            <span>Target Pattern Progression</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-3">
            Greedy &amp; Interval Scheduling Sequence
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono font-normal">
              {pathSteps.length} Step Path
            </span>
          </h2>
        </div>

        {/* Path Selector Controls */}
        <div className="flex items-center gap-3 bg-slate-950/80 p-2 rounded-xl border border-slate-800 shrink-0">
          <div>
            <label className="block text-[9px] font-mono text-slate-500 uppercase mb-0.5">Start Baseline</label>
            <select 
              value={startProblem} 
              onChange={(e) => setStartProblem(e.target.value)} 
              className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 outline-none font-sans"
            >
              {signatures.map(s => (
                <option key={s.problem_id} value={s.problem_id}>{s.title}</option>
              ))}
            </select>
          </div>

          <button 
            onClick={handleCompile} 
            disabled={loading} 
            className="py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-indigo-500/20 disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-white" />}
            <span>Regenerate Path</span>
          </button>
        </div>
      </div>

      {/* MAIN LEARNER WORKSPACE: TIMELINE RAIL ON LEFT, PEDAGOGICAL DEEP DIVE ON RIGHT */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
        
        {/* LEFT COLUMN: VISUAL PROGRESSION RAIL (5 COLS) */}
        <div className="lg:col-span-5 bg-slate-900/50 border border-slate-800/90 rounded-2xl p-5 flex flex-col overflow-hidden backdrop-blur-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Learning Sequence</span>
            </span>
            <span className="text-[11px] font-mono text-slate-500">
              Step {activeStepIndex + 1} of {pathSteps.length}
            </span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 relative">
            {loading && (
              <div className="flex items-center justify-center py-16">
                <RefreshCw className="w-6 h-6 text-indigo-400 animate-spin" />
              </div>
            )}
            {pathSteps.map((step, idx) => {
              const isCurrent = activeStepIndex === idx;
              const isPast = idx < activeStepIndex;
              const isBridge = step.isBridge;

              return (
                <motion.div
                  key={`${step.problem_id}-${idx}`}
                  onClick={() => setActiveStepIndex(idx)}
                  whileHover={{ x: 2 }}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer relative overflow-hidden flex items-center justify-between gap-3 ${
                    isCurrent
                      ? (isBridge ? 'bg-amber-950/30 border-amber-500 shadow-md shadow-amber-500/10' : 'bg-indigo-950/40 border-indigo-500 shadow-md shadow-indigo-500/10 ring-1 ring-indigo-500')
                      : isPast
                        ? 'bg-slate-950/40 border-slate-800/60 text-slate-400'
                        : 'bg-slate-950/80 border-slate-800 hover:border-slate-700 text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    {/* Step Node Marker */}
                    <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-mono font-bold shrink-0 ${
                      isCurrent
                        ? (isBridge ? 'bg-amber-500 text-slate-950' : 'bg-indigo-600 text-white')
                        : isPast
                          ? 'bg-slate-800 text-slate-400'
                          : 'bg-slate-900 text-slate-500 border border-slate-800'
                    }`}>
                      {isBridge ? 'B' : idx + 1}
                    </div>

                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className={`text-xs font-bold truncate ${isCurrent ? 'text-indigo-200' : 'text-slate-200'}`}>
                          {step.title}
                        </span>
                        {isBridge && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-amber-950 text-amber-300 border border-amber-800/80">
                            Bridge
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] font-mono text-slate-500 block truncate">
                        {step.canonical_pattern}
                      </span>
                    </div>
                  </div>

                  <ChevronRight className={`w-4 h-4 shrink-0 transition-transform ${isCurrent ? 'text-indigo-400 translate-x-0.5' : 'text-slate-600'}`} />
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* RIGHT COLUMN: PEDAGOGICAL EXPLAINABILITY & INSIGHTS (7 COLS) */}
        {currentStep && (
          <div className="lg:col-span-7 space-y-5 flex flex-col justify-between">
            
            {/* CURRENT PROBLEM FOCUS CARD */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 backdrop-blur-md space-y-4">
              <div className="flex items-start justify-between gap-4 pb-3 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/60">
                      {currentStep.isBridge ? 'Scaffolding Bridge Step' : `Target Step #${activeStepIndex + 1}`}
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      Algorithmic Difficulty: {diff?.algorithmic || 2}/5
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-slate-100">{currentStep.title}</h3>
                </div>

                <button
                  onClick={() => onSelectProblem && onSelectProblem({ task_id: currentStep.problem_id, title: currentStep.title })}
                  className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm shadow-indigo-500/20 shrink-0"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Solve Problem</span>
                </button>
              </div>

              {/* WHY THIS IS NEXT (PEDAGOGICAL BREAKDOWN) */}
              <div className="bg-slate-950/80 rounded-xl p-5 border border-slate-800/80 space-y-4">
                <div className="flex items-center gap-2 text-xs font-bold text-indigo-300 uppercase tracking-wider">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <span>Why This Problem Is Next</span>
                </div>

                {/* 3 PEDAGOGICAL METRIC TILES */}
                <div className="grid grid-cols-3 gap-3">
                  
                  {/* RETAINS */}
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800/80 text-center">
                    <span className="text-[10px] font-mono text-slate-400 block mb-0.5">RETAINS</span>
                    <span className="text-lg font-bold text-emerald-400 font-mono">
                      {delta ? Math.round(delta.retention_ratio * 100) : 100}%
                    </span>
                    <span className="text-[9px] text-slate-500 block truncate mt-0.5">Prior Knowledge</span>
                  </div>

                  {/* INTRODUCES */}
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800/80 text-center">
                    <span className="text-[10px] font-mono text-slate-400 block mb-0.5">INTRODUCES</span>
                    <span className="text-lg font-bold text-cyan-400 font-mono">
                      {delta ? Math.round(delta.new_concept_ratio * 100) : 0}%
                    </span>
                    <span className="text-[9px] text-slate-500 block truncate mt-0.5">New Mechanics</span>
                  </div>

                  {/* COGNITIVE JUMP */}
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800/80 text-center">
                    <span className="text-[10px] font-mono text-slate-400 block mb-0.5">COGNITIVE JUMP</span>
                    <span className="text-lg font-bold text-amber-400 font-mono">
                      +{delta ? Object.values(delta.cognitive_jumps || {}).reduce((a, b) => a + b, 0) : 0}
                    </span>
                    <span className="text-[9px] text-slate-500 block truncate mt-0.5">Complexity Delta</span>
                  </div>
                </div>

                {/* CONCEPT BADGES */}
                <div className="space-y-2 pt-2 border-t border-slate-800/80">
                  {delta?.retained_concepts?.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 text-xs">
                      <span className="text-[10px] font-mono text-slate-500 shrink-0">Retained:</span>
                      {delta.retained_concepts.map(c => (
                        <span key={c} className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 font-mono">
                          {c.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  )}

                  {currentStep.introduced_concepts?.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 text-xs">
                      <span className="text-[10px] font-mono text-slate-500 shrink-0">Introduced:</span>
                      {currentStep.introduced_concepts.map(c => (
                        <span key={c} className="text-[10px] px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/60 font-mono">
                          {c.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* NARRATIVE RATIONALE */}
                <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-900/60 p-3 rounded-lg border border-slate-800/60">
                  <span className="font-semibold text-cyan-400">Pedagogical Rationale: </span>
                  {currentStep.pedagogical_reason}
                </p>
              </div>

              {/* INLINE SCAFFOLDING BRIDGE TRIGGER */}
              {activeStepIndex > 0 && !currentStep.isBridge && (
                <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-900/40 flex items-center justify-between gap-4">
                  <div className="space-y-0.5">
                    <span className="text-xs font-semibold text-amber-300 flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                      Feeling stuck on this step?
                    </span>
                    <p className="text-[11px] text-slate-400">
                      If the cognitive jump is too large, the engine will insert an intermediate bridge problem into your timeline.
                    </p>
                  </div>

                  <button
                    onClick={() => handleSimulateStruggleAndInsertBridge(activeStepIndex)}
                    disabled={bridgeLoading}
                    className="px-3.5 py-1.5 rounded-lg bg-amber-950 hover:bg-amber-900 text-amber-300 border border-amber-800 text-xs font-semibold flex items-center gap-1.5 transition-colors shrink-0 disabled:opacity-50"
                  >
                    {bridgeLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <GitFork className="w-3.5 h-3.5" />}
                    <span>Insert Bridge</span>
                  </button>
                </div>
              )}
            </div>

            {/* METRICS FOOTER (small, unobtrusive) */}
            {metrics && (
              <div className="flex items-center gap-4 text-[10px] font-mono text-slate-600 px-1">
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                  {metrics.concept_coverage_count} concepts covered
                </span>
                <span>·</span>
                <span>{Math.round((metrics.average_retention_ratio || 0) * 100)}% avg retention</span>
                <span>·</span>
                <span className={metrics.prerequisite_violations_count === 0 ? 'text-emerald-600' : 'text-red-500'}>
                  {metrics.prerequisite_violations_count} prerequisite violations
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
