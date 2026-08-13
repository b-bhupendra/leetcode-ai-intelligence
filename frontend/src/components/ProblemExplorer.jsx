import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, Sparkles, Building2, Layers, RefreshCw } from 'lucide-react';
import { ProblemCard } from './ProblemCard';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.04,
      delayChildren: 0.05
    }
  }
};

export function ProblemExplorer({ metadata, onSelectProblem }) {
  const [selectedCompany, setSelectedCompany] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({ direct_problems: [], similar_problems: [] });

  const fetchFilteredProblems = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/problems/filter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: selectedCompany || null,
          difficulty: selectedDifficulty || null,
          topic: selectedTopic || null,
          timeframe: selectedTimeframe || null,
          search_query: searchQuery || null,
          max_direct: 30,
          max_similar: 15
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setResults(data.data);
      }
    } catch (err) {
      console.error('Failed to filter problems:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFilteredProblems();
  }, [selectedCompany, selectedDifficulty, selectedTopic, selectedTimeframe]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchFilteredProblems();
  };

  const totalCount = (results.direct_problems?.length || 0) + (results.similar_problems?.length || 0);

  return (
    <div className="space-y-6">
      {/* Search & Filter Bar */}
      <div className="glass-panel rounded-2xl p-4 sm:p-6 space-y-4">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search problems by name, slug, archetype, or keyword..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/80 border border-slate-700/60 rounded-xl pl-10 pr-24 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors"
          >
            Search
          </button>
        </form>

        {/* Dropdown Filters */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {/* Company */}
          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Company</label>
            <select
              value={selectedCompany}
              onChange={(e) => setSelectedCompany(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All 200 Companies</option>
              {metadata.companies?.map((c) => (
                <option key={c} value={c}>{c.toUpperCase()}</option>
              ))}
            </select>
          </div>

          {/* Difficulty */}
          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Difficulty</label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Difficulties</option>
              {metadata.difficulties?.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          {/* Topic */}
          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Topic Tag</label>
            <select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Topics</option>
              {metadata.topics?.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          {/* Timeframe */}
          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Recency</label>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Time</option>
              <option value="6months">Last 6 Months</option>
              <option value="1year">Last 1 Year</option>
              <option value="2year">Last 2 Years</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-200">
            {selectedCompany ? `${selectedCompany.toUpperCase()} Question Radar` : 'Algorithmic Problem Bank'}
          </span>
          <span className="px-2 py-0.5 rounded-full bg-indigo-950/70 border border-indigo-800/40 text-xs font-mono text-indigo-300">
            {totalCount} problems
          </span>
        </div>

        {loading && (
          <div className="flex items-center gap-2 text-xs text-indigo-400">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>Scanning Vector Index...</span>
          </div>
        )}
      </div>

      {/* Staggered Grid Container */}
      <AnimatePresence mode="wait">
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="glass-panel rounded-xl p-5 h-44 animate-pulse bg-slate-900/40" />
            ))}
          </div>
        ) : (
          <div className="space-y-8">
            {/* Direct Questions Grid */}
            {results.direct_problems?.length > 0 && (
              <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
              >
                {results.direct_problems.map((p) => (
                  <ProblemCard key={p.task_id} problem={p} onSelect={onSelectProblem} />
                ))}
              </motion.div>
            )}

            {/* Similar Unasked Counterparts */}
            {results.similar_problems?.length > 0 && (
              <div className="space-y-3 pt-4 border-t border-slate-800/80">
                <div className="flex items-center gap-2 text-sm font-semibold text-purple-300">
                  <Sparkles className="w-4 h-4 text-purple-400" />
                  <span>Unasked Similar Counterparts (High Interview Probability)</span>
                </div>
                <p className="text-xs text-slate-400">
                  These problems share identical algorithmic archetypes and constraint patterns with verified interview questions.
                </p>

                <motion.div
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                  className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
                >
                  {results.similar_problems.map((p) => (
                    <ProblemCard key={p.task_id} problem={p} onSelect={onSelectProblem} />
                  ))}
                </motion.div>
              </div>
            )}

            {totalCount === 0 && !loading && (
              <div className="glass-panel rounded-2xl p-12 text-center text-slate-400 space-y-3">
                <Layers className="w-10 h-10 mx-auto text-slate-600" />
                <h4 className="text-base font-medium text-slate-300">No matching problems found</h4>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Try adjusting your search query, difficulty filters, or selecting a broader company tag.
                </p>
              </div>
            )}
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
