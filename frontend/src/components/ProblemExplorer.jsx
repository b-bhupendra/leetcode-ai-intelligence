import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, Compass, Sparkles, Building2, Layers, RotateCcw } from 'lucide-react';
import { ProblemCard } from './ProblemCard';

const gridContainerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.03,
      delayChildren: 0.05
    }
  }
};

const cardItemVariants = {
  hidden: { opacity: 0, y: 15, scale: 0.97 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 350, damping: 25 }
  }
};

export function ProblemExplorer({ metadata, onSelectProblem, initialClusterId = null }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCompany, setSelectedCompany] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [selectedTier, setSelectedTier] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [selectedClusterId, setSelectedClusterId] = useState(initialClusterId !== null ? String(initialClusterId) : '');
  const [timeframe, setTimeframe] = useState('alltime');

  const [loading, setLoading] = useState(false);
  const [directProblems, setDirectProblems] = useState([]);
  const [similarProblems, setSimilarProblems] = useState([]);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const PAGE_SIZE = 50;

  useEffect(() => {
    if (initialClusterId !== null) {
      setSelectedClusterId(String(initialClusterId));
    }
  }, [initialClusterId]);

  const fetchProblems = async (pageNum = 1) => {
    setLoading(true);
    try {
      const res = await fetch('/api/problems/filter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: selectedCompany || null,
          difficulty: selectedDifficulty || null,
          difficulty_tier: selectedTier || null,
          topic: selectedTopic || null,
          cluster_id: selectedClusterId !== '' ? parseInt(selectedClusterId) : null,
          timeframe,
          search_query: searchQuery || null,
          page: pageNum,
          page_size: PAGE_SIZE,
          max_similar: 12
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setDirectProblems(data.data.direct_problems || []);
        setSimilarProblems(data.data.similar_unasked_problems || []);
        setTotalCount(data.data.total_count ?? data.data.direct_count ?? 0);
        setTotalPages(data.data.total_pages ?? 1);
        setPage(pageNum);
      }
    } catch (err) {
      console.error('Failed to fetch problems:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProblems(1);
  }, [selectedCompany, selectedDifficulty, selectedTier, selectedTopic, selectedClusterId, timeframe]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchProblems(1);
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedCompany('');
    setSelectedDifficulty('');
    setSelectedTier('');
    setSelectedTopic('');
    setSelectedClusterId('');
    setTimeframe('alltime');
  };


  return (
    <div className="space-y-6">
      {/* Search & Filter Header Control Center */}
      <div className="glass-panel rounded-2xl p-5 space-y-4">
        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search 2,870 problems by title, keywords, or algorithmic tags..."
            className="w-full bg-slate-900/80 border border-slate-700/60 rounded-xl pl-11 pr-28 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors font-sans"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors"
          >
            Search
          </button>
        </form>

        {/* Filter Dropdowns Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
          {/* Company Filter */}
          <select
            value={selectedCompany}
            onChange={(e) => setSelectedCompany(e.target.value)}
            className="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All 200 Companies</option>
            {metadata.companies?.map((c) => (
              <option key={c} value={c}>
                {c.toUpperCase()}
              </option>
            ))}
          </select>

          {/* 5-Tier Granular Difficulty */}
          <select
            value={selectedTier}
            onChange={(e) => setSelectedTier(e.target.value)}
            className="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Difficulty Tiers</option>
            <option value="Easy">Easy</option>
            <option value="Easy-Medium">Easy-Medium</option>
            <option value="Medium">Medium</option>
            <option value="Medium-Hard">Medium-Hard</option>
            <option value="Hard">Hard</option>
          </select>

          {/* 30 Algorithmic Archetype Clusters */}
          <select
            value={selectedClusterId}
            onChange={(e) => setSelectedClusterId(e.target.value)}
            className="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All 30 Archetypes</option>
            {metadata.clusters?.map((cl) => (
              <option key={cl.cluster_id} value={cl.cluster_id}>
                #{cl.cluster_id}: {cl.title}
              </option>
            ))}
          </select>

          {/* Topic Tags */}
          <select
            value={selectedTopic}
            onChange={(e) => setSelectedTopic(e.target.value)}
            className="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All 70+ Topics</option>
            {metadata.topics?.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>

          {/* Timeframe */}
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="alltime">All-Time Radar</option>
            <option value="6months">Recent 6 Months</option>
            <option value="1year">Recent 1 Year</option>
            <option value="2year">Recent 2 Years</option>
          </select>

          {/* Reset Filters */}
          <button
            onClick={handleResetFilters}
            className="bg-slate-900/80 hover:bg-slate-800 border border-slate-700/60 rounded-xl px-3 py-2 text-xs text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1.5 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Main Results Grid */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Compass className="w-4 h-4 text-indigo-400" />
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              {selectedCompany ? `${selectedCompany.toUpperCase()} Radar Questions` : 'Verified Problems'}
            </h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">
              {totalCount > 0 ? `${totalCount} total` : `${directProblems.length} found`}
            </span>
            {totalPages > 1 && (
              <span className="text-[10px] font-mono text-slate-500">
                Page {page} of {totalPages}
              </span>
            )}
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="glass-panel h-48 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : directProblems.length > 0 ? (
          <motion.div
            variants={gridContainerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            {directProblems.map((problem) => (
              <motion.div key={problem.task_id} variants={cardItemVariants}>
                <ProblemCard problem={problem} onSelect={onSelectProblem} />
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <div className="glass-panel rounded-2xl p-12 text-center text-slate-500 space-y-2">
            <p className="text-sm">No problems found matching these criteria.</p>
            <p className="text-xs text-slate-600">Try broadening your search or resetting active filters.</p>
          </div>
        )}

        {/* Pagination controls */}
        {totalPages > 1 && !loading && (
          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              onClick={() => fetchProblems(page - 1)}
              disabled={page <= 1}
              className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-xs font-medium hover:border-slate-600 hover:text-slate-200 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            >
              ← Previous
            </button>
            <span className="text-xs font-mono text-slate-500">
              {page} / {totalPages} · {totalCount} problems
            </span>
            <button
              onClick={() => fetchProblems(page + 1)}
              disabled={page >= totalPages}
              className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-xs font-medium hover:border-slate-600 hover:text-slate-200 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
