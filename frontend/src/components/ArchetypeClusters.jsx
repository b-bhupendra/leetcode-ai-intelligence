import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, Sparkles, Code2, Users, ArrowUpRight, X, ExternalLink, Compass } from 'lucide-react';

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

export function ArchetypeClusters({ metadata, onSelectCluster, onInspectProblem, onFilterExplorerByCluster }) {
  const clusters = metadata.clusters || [];
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [activeTierTab, setActiveTierTab] = useState('Easy-Medium');

  const handleOpenClusterModal = (cluster) => {
    setSelectedCluster(cluster);
    // Default to first non-empty tier
    const td = cluster.tier_distribution || {};
    const firstNonEmpty = ['Easy', 'Easy-Medium', 'Medium', 'Medium-Hard', 'Hard'].find(t => (td[t] || 0) > 0) || 'Medium';
    setActiveTierTab(firstNonEmpty);
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-2xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            <span>30 Algorithmic Archetype Clusters & 5-Tier Stratification</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Unsupervised K-Means clustering partitions 2,870 problems into 30 core patterns with 5 granular difficulty bands (Easy, Easy-Medium, Medium, Medium-Hard, Hard).
          </p>
        </div>
        <span className="px-3 py-1 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800 text-xs font-mono self-start sm:self-auto">
          {clusters.length} Archetypes
        </span>
      </div>

      {/* Grid of 30 Clusters */}
      <motion.div
        initial="hidden"
        animate="visible"
        transition={{ staggerChildren: 0.03 }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        {clusters.map((c) => {
          const totalSize = c.problem_count || c.size || 1;
          const td = c.tier_distribution || { 'Easy': 0, 'Easy-Medium': 0, 'Medium': 0, 'Medium-Hard': 0, 'Hard': 0 };

          return (
            <motion.div
              key={c.cluster_id}
              variants={clusterVariants}
              whileHover={{ y: -4 }}
              onClick={() => handleOpenClusterModal(c)}
              className="glass-panel-interactive rounded-xl p-5 space-y-3 flex flex-col justify-between cursor-pointer group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900 text-indigo-400 border border-slate-800">
                    Cluster #{c.cluster_id}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">
                    {c.problem_count} Problems
                  </span>
                </div>

                <h4 className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors line-clamp-1 mb-1">
                  {c.title}
                </h4>
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                  {c.description}
                </p>
              </div>

              <div>
                {/* 5-Tier Difficulty Proportional Bar */}
                <div className="space-y-1 mb-3">
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                    <span>Difficulty Stratification</span>
                    <span>5 Bands</span>
                  </div>
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

                <div className="flex flex-wrap gap-1 mb-3">
                  {c.top_tags?.slice(0, 3).map((tag, i) => (
                    <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-850 text-slate-300 border border-slate-800">
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="pt-2 border-t border-slate-800/80 text-[11px] text-indigo-400 flex items-center justify-between">
                  <span className="group-hover:translate-x-0.5 transition-transform">Explore {c.problem_count} Problems by Tier</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Cluster Problems By Difficulty Tier Modal / Drawer */}
      <AnimatePresence>
        {selectedCluster && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/70 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 15 }}
              transition={{ type: 'spring', damping: 25, stiffness: 350 }}
              className="glass-panel w-full max-w-4xl max-h-[85vh] rounded-3xl p-6 sm:p-8 flex flex-col space-y-5 relative overflow-hidden"
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                      Cluster #{selectedCluster.cluster_id}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      {selectedCluster.problem_count} Problems
                    </span>
                  </div>
                  <h2 className="text-lg sm:text-xl font-bold text-slate-100">{selectedCluster.title}</h2>
                  <p className="text-xs text-slate-400 mt-1">{selectedCluster.description}</p>
                </div>

                <button
                  onClick={() => setSelectedCluster(null)}
                  className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
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
                    <span>Open in Problem Explorer</span>
                  </button>
                )}
              </div>

              {/* List of Problems for the Selected Difficulty Tier */}
              <div className="flex-1 overflow-y-auto pr-1 space-y-2 max-h-96">
                {selectedCluster.problems_by_tier && selectedCluster.problems_by_tier[activeTierTab]?.length > 0 ? (
                  selectedCluster.problems_by_tier[activeTierTab].map((p, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between gap-3 hover:border-slate-700 transition-colors"
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
                    No problems classified in the <span className="font-semibold text-slate-400">{activeTierTab}</span> tier for this cluster.
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
