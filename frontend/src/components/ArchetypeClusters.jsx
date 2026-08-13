import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Layers, 
  Sparkles, 
  Code2, 
  Users, 
  ArrowUpRight, 
  X, 
  ExternalLink, 
  Compass, 
  Milestone, 
  Calendar, 
  Clock, 
  Flame, 
  CheckCircle2, 
  HelpCircle,
  Cpu,
  BookOpen
} from 'lucide-react';

const clusterVariants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: { type: 'spring', stiffness: 350, damping: 25 }
  }
};

const tierColors = {
  'Easy': 'bg-emerald-500',
  'Easy-Medium': 'bg-cyan-500',
  'Medium': 'bg-indigo-500',
  'Medium-Hard': 'bg-amber-500',
  'Hard': 'bg-rose-500'
};

const tierTextColors = {
  'Easy': 'text-emerald-400 border-emerald-800/80 bg-emerald-950/60',
  'Easy-Medium': 'text-cyan-400 border-cyan-800/80 bg-cyan-950/60',
  'Medium': 'text-indigo-400 border-indigo-800/80 bg-indigo-950/60',
  'Medium-Hard': 'text-amber-400 border-amber-800/80 bg-amber-950/60',
  'Hard': 'text-rose-400 border-rose-800/80 bg-rose-950/60'
};

const paradigmIcons = {
  'Linear Pointer Patterns': '🎯',
  'Linear Structures & Specialized Memory': '💾',
  'Tree, Graph & Search Space Traversal': '🌲',
  'Optimization & State Space Paradigms': '⚡'
};

export function ArchetypeClusters({ metadata, onSelectCluster, onInspectProblem, onFilterExplorerByCluster }) {
  const clusters = metadata.clusters || [];
  const [viewMode, setViewMode] = useState('taxonomy'); // 'taxonomy' | 'roadmap'
  const [selectedParadigm, setSelectedParadigm] = useState('All');
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [activeTierTab, setActiveTierTab] = useState('Easy-Medium');

  const paradigms = ['All', 'Linear Pointer Patterns', 'Linear Structures & Specialized Memory', 'Tree, Graph & Search Space Traversal', 'Optimization & State Space Paradigms'];

  const filteredClusters = clusters.filter(c => {
    if (selectedParadigm === 'All') return true;
    return c.paradigm === selectedParadigm;
  });

  const handleOpenClusterModal = (cluster) => {
    setSelectedCluster(cluster);
    const td = cluster.tier_distribution || {};
    const firstNonEmpty = ['Easy', 'Easy-Medium', 'Medium', 'Medium-Hard', 'Hard'].find(t => (td[t] || 0) > 0) || 'Medium';
    setActiveTierTab(firstNonEmpty);
  };

  const roadmapPhases = [
    {
      phase: "Phase 1: Linear Pointer Mechanics",
      weeks: "Weeks 1–2",
      goal: "Shift from O(N²) brute force to O(N) single-pass time complexity.",
      archetypeIds: [0, 1, 2, 3],
      keyTakeaways: "Master left/right monotonic convergence, sliding window expansion/contraction, and cumulative prefix lookup."
    },
    {
      phase: "Phase 2: Core Linear Data Structures",
      weeks: "Weeks 3–4",
      goal: "Solve order-dependent and range-query problems efficiently without re-sorting.",
      archetypeIds: [4, 5, 6, 7],
      keyTakeaways: "Strict monotonic sequence maintenance, in-place cyclic swaps, and top-K binary heap properties."
    },
    {
      phase: "Phase 3: Hierarchical Structures & Search Space",
      weeks: "Weeks 5–6",
      goal: "Master divide-and-conquer logic, tree recursion, and monotonic answer spaces.",
      archetypeIds: [8, 12],
      keyTakeaways: "Bottom-up tree state propagation and binary search over continuous or discrete monotonic predicate functions."
    },
    {
      phase: "Phase 4: Graph Theory & Combinatorial Search",
      weeks: "Weeks 7–8",
      goal: "Model real-world dependency networks and state-space tree prunings.",
      archetypeIds: [9, 10, 11],
      keyTakeaways: "Level-order matrix BFS, cycle detection with DSU, topological DAG ordering, and backtracking state restoration."
    },
    {
      phase: "Phase 5: Advanced Optimization & State Transitions",
      weeks: "Weeks 9–11",
      goal: "Recognize state transition equations and convert exponential recursion to polynomial time.",
      archetypeIds: [13, 14],
      keyTakeaways: "1D/2D memoization tables, rolling array space optimization, interval partitions, and greedy sorting invariants."
    },
    {
      phase: "Phase 6: Composite Patterns & Advanced Structures",
      weeks: "Weeks 12+",
      goal: "Handle high-constraint edge cases under strict O(N log N) or O(1) limits.",
      archetypeIds: [6, 7, 13],
      keyTakeaways: "Bitmask DP, custom Trie dictionaries, and multi-paradigm combinations (Binary Search + BFS, DP + Monotonic Stack)."
    }
  ];

  return (
    <div className="space-y-6">
      {/* Top Header & Mode Switcher */}
      <div className="glass-panel rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              <span>Unified 15-Archetype Taxonomy & Mastery Roadmap</span>
            </h3>
            <span className="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 text-[11px] font-mono">
              Zero Duplication
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            2,870 LeetCode challenges partitioned into 15 algorithmic mechanics across 4 Core Paradigms with 5-tier difficulty stratification.
          </p>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-900 border border-slate-800 shrink-0 self-start md:self-auto">
          <button
            onClick={() => setViewMode('taxonomy')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
              viewMode === 'taxonomy'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>15 Archetypes</span>
          </button>

          <button
            onClick={() => setViewMode('roadmap')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
              viewMode === 'roadmap'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Milestone className="w-3.5 h-3.5" />
            <span>6-Phase Roadmap</span>
          </button>
        </div>
      </div>

      {/* Mode A: 15 Archetype Taxonomy Grid */}
      {viewMode === 'taxonomy' && (
        <div className="space-y-6">
          {/* Paradigm Filter Pills */}
          <div className="flex flex-wrap gap-2">
            {paradigms.map((p) => (
              <button
                key={p}
                onClick={() => setSelectedParadigm(p)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-colors border ${
                  selectedParadigm === p
                    ? 'bg-indigo-950/80 border-indigo-500 text-indigo-300'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <span>{p !== 'All' ? `${paradigmIcons[p]} ${p}` : '🌐 All 4 Paradigms'}</span>
              </button>
            ))}
          </div>

          {/* Grid of 15 Archetypes */}
          <motion.div
            initial="hidden"
            animate="visible"
            transition={{ staggerChildren: 0.03 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            {filteredClusters.map((c) => {
              const totalSize = c.problem_count || c.size || 1;
              const td = c.tier_distribution || { 'Easy': 0, 'Easy-Medium': 0, 'Medium': 0, 'Medium-Hard': 0, 'Hard': 0 };

              return (
                <motion.div
                  key={c.cluster_id}
                  variants={clusterVariants}
                  whileHover={{ y: -4 }}
                  onClick={() => handleOpenClusterModal(c)}
                  className="glass-panel-interactive rounded-2xl p-5 space-y-4 flex flex-col justify-between cursor-pointer group relative overflow-hidden"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900 text-indigo-400 border border-slate-800">
                        Archetype #{c.cluster_id + 1}
                      </span>
                      <span className="text-[11px] text-slate-400 font-mono">
                        {c.problem_count} Problems
                      </span>
                    </div>

                    <div>
                      <span className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider">
                        {c.paradigm}
                      </span>
                      <h4 className="text-sm font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                        {c.title}
                      </h4>
                    </div>

                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                      {c.description}
                    </p>
                  </div>

                  <div className="space-y-3">
                    {/* Invariant equation snippet */}
                    {c.invariant && (
                      <div className="p-2 rounded-lg bg-slate-950/80 border border-slate-800/80 font-mono text-[10px] text-cyan-300 truncate">
                        {c.invariant}
                      </div>
                    )}

                    {/* 5-Tier Difficulty Proportional Bar */}
                    <div className="space-y-1">
                      <div className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden flex">
                        {['Easy', 'Easy-Medium', 'Medium', 'Medium-Hard', 'Hard'].map((tier) => {
                          const count = td[tier] || 0;
                          if (count === 0) return null;
                          const pct = (count / totalSize) * 100;
                          return (
                            <div
                              key={tier}
                              style={{ width: `${pct}%` }}
                              title={`${tier}: ${count} problems`}
                              className={`${tierColors[tier]} h-full`}
                            />
                          );
                        })}
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 text-[11px] text-indigo-400 flex items-center justify-between">
                      <span className="group-hover:translate-x-0.5 transition-transform font-medium">
                        Explore {c.problem_count} Problems across 5 Tiers
                      </span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      )}

      {/* Mode B: 6-Phase Chronological Mastery Roadmap */}
      {viewMode === 'roadmap' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {roadmapPhases.map((phase, idx) => (
              <motion.div
                key={idx}
                variants={clusterVariants}
                initial="hidden"
                animate="visible"
                className="glass-panel rounded-2xl p-6 space-y-4 flex flex-col justify-between relative overflow-hidden"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800 text-[10px] font-mono">
                      {phase.weeks}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">Step 0{idx + 1}</span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-100">{phase.phase}</h4>
                  <p className="text-xs text-indigo-300 font-medium">{phase.goal}</p>
                  <p className="text-xs text-slate-400 leading-relaxed">{phase.keyTakeaways}</p>
                </div>

                <div className="space-y-2 pt-3 border-t border-slate-800">
                  <span className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider">
                    Core Archetypes Covered
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {phase.archetypeIds.map((id) => {
                      const arch = clusters.find(c => c.cluster_id === id);
                      if (!arch) return null;
                      return (
                        <button
                          key={id}
                          onClick={() => handleOpenClusterModal(arch)}
                          className="text-[11px] px-2 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 flex items-center gap-1 transition-colors"
                        >
                          <span>{arch.title}</span>
                          <ArrowUpRight className="w-3 h-3 text-slate-500" />
                        </button>
                      );
                    })}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Cluster Problems By Difficulty Tier Modal / Drawer */}
      <AnimatePresence>
        {selectedCluster && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/70 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 15 }}
              transition={{ type: 'spring', damping: 25, stiffness: 350 }}
              className="glass-panel w-full max-w-4xl max-h-[90vh] rounded-3xl p-6 sm:p-8 flex flex-col space-y-5 relative overflow-hidden"
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                      Archetype #{selectedCluster.cluster_id + 1}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      {selectedCluster.paradigm} • {selectedCluster.problem_count} Problems
                    </span>
                  </div>
                  <h2 className="text-lg sm:text-xl font-bold text-slate-100">{selectedCluster.title}</h2>
                  <p className="text-xs text-slate-300">{selectedCluster.description}</p>
                </div>

                <button
                  onClick={() => setSelectedCluster(null)}
                  className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Invariant & Complexity Callout */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1">
                  <span className="text-[10px] uppercase font-semibold text-cyan-400 tracking-wider flex items-center gap-1">
                    <Code2 className="w-3 h-3" /> Core Invariant / State Equation
                  </span>
                  <p className="text-xs font-mono text-slate-300 break-words">{selectedCluster.invariant || 'State monotonic invariant'}</p>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1">
                  <span className="text-[10px] uppercase font-semibold text-emerald-400 tracking-wider flex items-center gap-1">
                    <Clock className="w-3 h-3" /> Complexity Bounds
                  </span>
                  <p className="text-xs font-mono text-slate-300">{selectedCluster.complexity || 'Time: O(N), Space: O(1)'}</p>
                </div>
              </div>

              {/* 5 Difficulty Tier Selector Tabs */}
              <div className="flex flex-wrap items-center gap-2">
                {['Easy', 'Easy-Medium', 'Medium', 'Medium-Hard', 'Hard'].map((tier) => {
                  const count = (selectedCluster.tier_distribution && selectedCluster.tier_distribution[tier]) || 0;
                  const isActive = activeTierTab === tier;

                  return (
                    <button
                      key={tier}
                      onClick={() => setActiveTierTab(tier)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-medium flex items-center gap-2 transition-all border ${
                        isActive
                          ? 'bg-slate-800 border-indigo-500 text-slate-100 shadow-md shadow-indigo-500/10'
                          : 'bg-slate-900/80 border-slate-800 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <span className={`w-2 h-2 rounded-full ${tierColors[tier]}`} />
                      <span>{tier}</span>
                      <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono bg-slate-950 text-slate-400 border border-slate-800">
                        {count}
                      </span>
                    </button>
                  );
                })}

                {onFilterExplorerByCluster && (
                  <button
                    onClick={() => {
                      onFilterExplorerByCluster(selectedCluster.cluster_id);
                      setSelectedCluster(null);
                    }}
                    className="ml-auto px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm shadow-indigo-500/20"
                  >
                    <Compass className="w-3.5 h-3.5" />
                    <span>Filter in Problem Explorer</span>
                  </button>
                )}
              </div>

              {/* List of Problems for Selected Difficulty Tier */}
              <div className="flex-1 overflow-y-auto pr-1 space-y-2 max-h-80">
                {selectedCluster.problems_by_tier && selectedCluster.problems_by_tier[activeTierTab]?.length > 0 ? (
                  selectedCluster.problems_by_tier[activeTierTab].map((p, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between gap-3 hover:border-slate-700 transition-colors"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-xs text-slate-100">{p.title || p.task_id}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${tierTextColors[p.difficulty_tier || activeTierTab]}`}>
                            {p.difficulty_tier || activeTierTab}
                          </span>
                        </div>
                        <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-slate-400">
                          <span>{p.companies_count ? `${p.companies_count} Companies asked` : 'General Pool'}</span>
                          <span>•</span>
                          <div className="flex gap-1">
                            {p.topic_tags?.map((t, i) => (
                              <span key={i} className="text-[10px] px-1.5 py-0.2 rounded bg-slate-950 text-slate-400 border border-slate-800">
                                {t}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {onInspectProblem && (
                          <button
                            onClick={() => {
                              onInspectProblem(p);
                              setSelectedCluster(null);
                            }}
                            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 text-xs font-medium transition-colors"
                          >
                            Inspect
                          </button>
                        )}
                        <a
                          href={p.leetcode_url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
                          title="Solve on LeetCode"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 text-xs text-slate-500">
                    No problems classified in the <span className="font-semibold text-slate-400">{activeTierTab}</span> tier for this archetype.
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
