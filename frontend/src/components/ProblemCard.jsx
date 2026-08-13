import React from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Building2, Layers, Flame, ArrowUpRight } from 'lucide-react';

const tierBadgeStyles = {
  'Easy': 'bg-emerald-950/60 text-emerald-300 border-emerald-800/80',
  'Easy-Medium': 'bg-cyan-950/60 text-cyan-300 border-cyan-800/80',
  'Medium': 'bg-indigo-950/60 text-indigo-300 border-indigo-800/80',
  'Medium-Hard': 'bg-amber-950/60 text-amber-300 border-amber-800/80',
  'Hard': 'bg-rose-950/60 text-rose-300 border-rose-800/80'
};

export function ProblemCard({ problem, onSelect }) {
  const diffTier = problem.difficulty_tier || problem.difficulty || 'Medium';
  const badgeClass = tierBadgeStyles[diffTier] || tierBadgeStyles['Medium'];
  const formattedTitle = problem.title || (problem.task_id ? problem.task_id.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Algorithm Challenge');

  return (
    <motion.div
      layout
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(problem)}
      className="glass-panel-interactive rounded-2xl p-5 cursor-pointer flex flex-col justify-between h-full relative overflow-hidden group"
    >
      {/* Top subtle glow on hover */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      <div>
        {/* Top Badges & Meta */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold border ${badgeClass}`}>
              {diffTier}
            </span>
            {problem.cluster_id !== undefined && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-900 text-slate-400 border border-slate-800">
                #{problem.cluster_id}
              </span>
            )}
          </div>

          <span className="text-[11px] font-mono text-slate-500">
            ID #{problem.question_id || '—'}
          </span>
        </div>

        {/* Problem Title */}
        <h3 className="font-semibold text-slate-100 text-sm mb-2 group-hover:text-indigo-300 transition-colors line-clamp-2">
          {formattedTitle}
        </h3>

        {/* Archetype cluster title */}
        {problem.cluster_title && (
          <div className="flex items-center gap-1 text-[11px] text-slate-400 mb-3 line-clamp-1">
            <Layers className="w-3 h-3 text-indigo-400 shrink-0" />
            <span className="truncate">{problem.cluster_title}</span>
          </div>
        )}
      </div>

      <div>
        {/* Topic Tags */}
        <div className="flex flex-wrap gap-1 mb-3">
          {problem.topic_tags?.slice(0, 3).map((tag, idx) => (
            <span
              key={idx}
              className="text-[10px] px-2 py-0.5 rounded bg-slate-900/80 text-slate-400 border border-slate-800"
            >
              {tag}
            </span>
          ))}
          {problem.topic_tags?.length > 3 && (
            <span className="text-[10px] text-slate-500 self-center">
              +{problem.topic_tags.length - 3}
            </span>
          )}
        </div>

        {/* Company interview frequency */}
        <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5">
            <Building2 className="w-3 h-3 text-slate-500" />
            <span className="font-mono">
              {problem.companies_count ? `${problem.companies_count} companies` : 'General Pool'}
            </span>
          </div>

          <span className="text-indigo-400 flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
            Inspect <ArrowUpRight className="w-3 h-3" />
          </span>
        </div>
      </div>
    </motion.div>
  );
}
