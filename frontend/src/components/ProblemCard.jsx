import React from 'react';
import { motion } from 'framer-motion';
import { Building2, Layers, ExternalLink, Sparkles } from 'lucide-react';

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { type: 'spring', stiffness: 300, damping: 24 }
  }
};

export function ProblemCard({ problem, onSelect }) {
  const diffColor = 
    problem.difficulty === 'Easy' ? 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40' :
    problem.difficulty === 'Medium' ? 'text-amber-400 bg-amber-950/40 border-amber-800/40' :
    'text-rose-400 bg-rose-950/40 border-rose-800/40';

  const companies = problem.companies || [];
  const topics = problem.topic_tags || [];

  return (
    <motion.div
      variants={cardVariants}
      whileHover={{ 
        y: -4, 
        transition: { type: 'spring', stiffness: 400, damping: 25 } 
      }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(problem)}
      className="glass-panel-interactive rounded-xl p-5 cursor-pointer flex flex-col justify-between group relative overflow-hidden"
    >
      {/* Subtle top card glow line on hover */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-indigo-500/0 to-transparent group-hover:via-indigo-500/70 transition-all duration-500" />

      <div>
        {/* Header Badges */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${diffColor}`}>
            {problem.difficulty || 'Medium'}
          </span>

          <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            #{problem.question_id || problem.task_id}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-base font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors line-clamp-1 mb-2">
          {problem.title || problem.task_id}
        </h3>

        {/* Archetype Cluster Badge */}
        {problem.cluster_title && (
          <div className="flex items-center gap-1.5 text-xs text-slate-300 bg-slate-900/60 border border-slate-800/80 px-2 py-1 rounded-md mb-3">
            <Layers className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span className="truncate">{problem.cluster_title}</span>
          </div>
        )}

        {/* Topics Pills */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {topics.slice(0, 3).map((tag, idx) => (
            <span key={idx} className="text-[11px] px-2 py-0.5 rounded bg-slate-800/50 text-slate-400 border border-slate-700/40">
              {tag}
            </span>
          ))}
          {topics.length > 3 && (
            <span className="text-[11px] px-1.5 py-0.5 rounded text-slate-500 font-mono">
              +{topics.length - 3}
            </span>
          )}
        </div>
      </div>

      {/* Footer: Companies Asking & Action Button */}
      <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5 text-slate-400">
          <Building2 className="w-3.5 h-3.5 text-slate-500" />
          <span>
            {companies.length > 0 ? (
              <span className="text-slate-300 font-medium">{companies.length} Companies</span>
            ) : (
              <span>General DSA</span>
            )}
          </span>
        </div>

        <div className="flex items-center gap-1 text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity font-medium">
          <span>Inspect</span>
          <ExternalLink className="w-3 h-3" />
        </div>
      </div>
    </motion.div>
  );
}
