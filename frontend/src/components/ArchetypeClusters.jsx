import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Layers, Sparkles, Code2, Users, ArrowUpRight } from 'lucide-react';

const clusterVariants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: { type: 'spring', stiffness: 350, damping: 25 }
  }
};

export function ArchetypeClusters({ metadata, onSelectCluster }) {
  const clusters = metadata.clusters || [];

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-2xl p-6 flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            <span>30 Algorithmic Archetype Clusters</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Unsupervised K-Means clustering partitions all 2,870 problems into 30 core patterns across Dynamic Programming, Graphs, Two Pointers, and Greedy strategies.
          </p>
        </div>
        <span className="px-3 py-1 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800 text-xs font-mono">
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
        {clusters.map((c) => (
          <motion.div
            key={c.cluster_id}
            variants={clusterVariants}
            whileHover={{ y: -3 }}
            className="glass-panel-interactive rounded-xl p-5 space-y-3 flex flex-col justify-between"
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

              <h4 className="text-sm font-semibold text-slate-100 line-clamp-1 mb-1">
                {c.title}
              </h4>
              <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                {c.description}
              </p>
            </div>

            <div>
              <div className="flex flex-wrap gap-1 mb-3">
                {c.top_tags?.slice(0, 3).map((tag, i) => (
                  <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-850 text-slate-300 border border-slate-800">
                    {tag}
                  </span>
                ))}
              </div>

              {c.sample_problems?.length > 0 && (
                <div className="pt-2 border-t border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between">
                  <span className="truncate">Sample: {c.sample_problems[0]}</span>
                  <ArrowUpRight className="w-3 h-3 text-slate-500 shrink-0" />
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
