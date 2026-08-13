import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Map,
  CheckCircle2,
  Circle,
  ExternalLink,
  PlayCircle,
  BookOpen,
  ArrowRight,
  Sparkles,
  Search,
  Filter,
  Layers,
  ChevronRight,
  TrendingUp,
  Award,
  CheckSquare,
  Square,
  Eye,
  Info
} from 'lucide-react';

export function NeetCodeVisualRoadmap({ onSelectProblem, onFilterCluster }) {
  const [roadmapData, setRoadmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTrackId, setSelectedTrackId] = useState('arrays-hashing');
  const [curatedListFilter, setCuratedListFilter] = useState('all'); // 'all', 'nc75', 'nc150'
  const [searchQuery, setSearchQuery] = useState('');
  const [completedProblems, setCompletedProblems] = useState(() => {
    try {
      const saved = localStorage.getItem('neetcode_completed_problems');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  useEffect(() => {
    fetch('/api/roadmap/neetcode')
      .then(res => res.json())
      .then(json => {
        if (json.status === 'success') {
          setRoadmapData(json.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load NeetCode roadmap:', err);
        setLoading(false);
      });
  }, []);

  const toggleProblemCompletion = (taskId) => {
    setCompletedProblems(prev => {
      const updated = { ...prev, [taskId]: !prev[taskId] };
      try {
        localStorage.setItem('neetcode_completed_problems', JSON.stringify(updated));
      } catch (e) {
        console.error(e);
      }
      return updated;
    });
  };

  const selectedTrack = useMemo(() => {
    if (!roadmapData || !roadmapData.nodes) return null;
    return roadmapData.nodes.find(n => n.id === selectedTrackId) || roadmapData.nodes[0];
  }, [roadmapData, selectedTrackId]);

  const filteredTrackProblems = useMemo(() => {
    if (!selectedTrack) return [];
    let list = selectedTrack.problems || [];
    if (curatedListFilter === 'nc75') {
      list = list.filter(p => p.in_nc75);
    } else if (curatedListFilter === 'nc150') {
      list = list.filter(p => p.in_nc150);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(p => 
        p.title.toLowerCase().includes(q) || 
        p.task_id.toLowerCase().includes(q)
      );
    }
    return list;
  }, [selectedTrack, curatedListFilter, searchQuery]);

  // Total progression stats
  const totalStats = useMemo(() => {
    if (!roadmapData || !roadmapData.all_problems) return { total: 0, completed: 0, pct: 0 };
    let list = roadmapData.all_problems;
    if (curatedListFilter === 'nc75') {
      list = list.filter(p => p.in_nc75);
    } else if (curatedListFilter === 'nc150') {
      list = list.filter(p => p.in_nc150);
    }
    const total = list.length;
    const completed = list.filter(p => completedProblems[p.task_id]).length;
    const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
    return { total, completed, pct };
  }, [roadmapData, curatedListFilter, completedProblems]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[450px] text-slate-400 gap-3">
        <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-medium">Constructing Interactive NeetCode Roadmap Tree...</p>
      </div>
    );
  }

  if (!roadmapData) {
    return (
      <div className="p-8 text-center text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
        <p>Failed to load NeetCode Roadmap data.</p>
      </div>
    );
  }

  // Group nodes by level for organized visual layout
  const levelGroups = {};
  roadmapData.nodes.forEach(node => {
    const lvl = node.level || 1;
    if (!levelGroups[lvl]) levelGroups[lvl] = [];
    levelGroups[lvl].push(node);
  });

  return (
    <div className="space-y-6">
      {/* Header Banner & Stats */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs mb-1.5 uppercase tracking-wider">
              <Map className="w-4 h-4 text-cyan-400" />
              <span>Topological Skill Tree & Study Tracks</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-3">
              NeetCode Roadmap & Curated Problem Tracks
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800/60 font-mono font-normal">
                18 Topological Tracks
              </span>
            </h2>
            <p className="text-sm text-slate-400 max-w-2xl mt-1">
              Master Data Structures & Algorithms following the optimal topological dependency path. Track progress across NeetCode 75, NeetCode 150, and NeetCode 250+.
            </p>
          </div>

          {/* Curated List Filter & Overall Progress */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80">
            <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-800">
              <button
                onClick={() => setCuratedListFilter('all')}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  curatedListFilter === 'all'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                NeetCode 250+
              </button>
              <button
                onClick={() => setCuratedListFilter('nc150')}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  curatedListFilter === 'nc150'
                    ? 'bg-cyan-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                NeetCode 150
              </button>
              <button
                onClick={() => setCuratedListFilter('nc75')}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  curatedListFilter === 'nc75'
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                NeetCode 75
              </button>
            </div>

            <div className="border-t sm:border-t-0 sm:border-l border-slate-800 pt-2 sm:pt-0 sm:pl-4 flex flex-col justify-center min-w-[140px]">
              <div className="flex items-center justify-between text-xs text-slate-300 font-mono mb-1">
                <span className="flex items-center gap-1">
                  <Award className="w-3.5 h-3.5 text-amber-400" />
                  Progress
                </span>
                <span className="font-bold text-indigo-400">{totalStats.completed} / {totalStats.total}</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <motion.div
                  className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${totalStats.pct}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <div className="text-right text-[10px] font-mono text-slate-500 mt-0.5">
                {totalStats.pct}% Solved
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Interactive Roadmap Tree on Left, Track Details & Problem Checklist on Right */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* Left Column: Visual Roadmap Progression Graph (7 Cols) */}
        <div className="xl:col-span-7 space-y-4">
          <div className="bg-slate-900/60 border border-slate-800/90 rounded-2xl p-5 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-semibold text-slate-200">Topological Roadmap Tree</h3>
              </div>
              <span className="text-xs font-mono text-slate-400">Click any track to view problems & study guide</span>
            </div>

            {/* Tree Level Hierarchy */}
            <div className="space-y-4 relative">
              {Object.keys(levelGroups).map((lvl) => {
                const nodes = levelGroups[lvl];
                return (
                  <div key={lvl} className="flex flex-col sm:flex-row items-center justify-center gap-3 relative">
                    {nodes.map(node => {
                      const isSelected = selectedTrackId === node.id;
                      const trackProblems = node.problems || [];
                      let activeCount = trackProblems.length;
                      if (curatedListFilter === 'nc75') {
                        activeCount = trackProblems.filter(p => p.in_nc75).length;
                      } else if (curatedListFilter === 'nc150') {
                        activeCount = trackProblems.filter(p => p.in_nc150).length;
                      }
                      const completedCount = trackProblems.filter(p => completedProblems[p.task_id]).length;
                      const isComplete = activeCount > 0 && completedCount === activeCount;

                      return (
                        <motion.button
                          key={node.id}
                          onClick={() => setSelectedTrackId(node.id)}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className={`flex-1 min-w-[160px] max-w-[240px] text-left p-3.5 rounded-xl border transition-all relative overflow-hidden ${
                            isSelected
                              ? 'bg-slate-800/90 border-indigo-500 shadow-lg shadow-indigo-500/20 ring-1 ring-indigo-500'
                              : 'bg-slate-950/70 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/60'
                          }`}
                        >
                          {/* Active Indicator bar */}
                          <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${node.color || 'from-indigo-500 to-cyan-500'}`} />

                          <div className="flex items-start justify-between gap-2 mb-1.5">
                            <span className="text-xs font-bold text-slate-100 leading-snug">{node.title}</span>
                            {isComplete ? (
                              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                            ) : (
                              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60">
                                {completedCount}/{activeCount}
                              </span>
                            )}
                          </div>

                          <div className="flex items-center justify-between text-[10px] text-slate-400">
                            <span className="truncate max-w-[100px] text-slate-500">{node.category}</span>
                            <span className="text-indigo-400 font-mono flex items-center gap-0.5">
                              Level {node.level}
                            </span>
                          </div>

                          {/* Prerequisites badge */}
                          {node.prerequisites && node.prerequisites.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500 flex items-center gap-1 truncate">
                              <span className="text-slate-600">Requires:</span>
                              <span className="font-mono text-cyan-400/80 truncate">
                                {node.prerequisites.map(p => p.replace('-', ' ')).join(', ')}
                              </span>
                            </div>
                          )}
                        </motion.button>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Selected Track Problem List & Study Notes (5 Cols) */}
        <div className="xl:col-span-5 space-y-4">
          {selectedTrack && (
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 sticky top-20 backdrop-blur-md">
              {/* Track Title & External Links */}
              <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/60">
                      Level {selectedTrack.level} Track
                    </span>
                    <span className="text-xs text-slate-400">{selectedTrack.category}</span>
                  </div>
                  <h3 className="text-xl font-bold text-slate-100">{selectedTrack.title}</h3>
                </div>

                {selectedTrack.gfg_url && (
                  <a
                    href={selectedTrack.gfg_url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 text-xs font-medium hover:bg-emerald-900 transition-colors shrink-0"
                  >
                    <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
                    <span>GFG Theory</span>
                    <ExternalLink className="w-3 h-3 ml-0.5 opacity-70" />
                  </a>
                )}
              </div>

              {/* Track Concept Invariant */}
              <p className="text-xs text-slate-300 my-3 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 leading-relaxed">
                <Info className="w-3.5 h-3.5 text-cyan-400 inline mr-1.5 -mt-0.5" />
                {selectedTrack.description}
              </p>

              {/* Search & Track Filter Controls */}
              <div className="flex items-center gap-2 mb-3">
                <div className="relative flex-1">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search in this track..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <span className="text-xs font-mono text-slate-400 px-2 py-1 bg-slate-950 rounded-lg border border-slate-800 shrink-0">
                  {filteredTrackProblems.length} Problems
                </span>
              </div>

              {/* Problem Rows Checklist */}
              <div className="space-y-2 max-h-[480px] overflow-y-auto pr-1">
                {filteredTrackProblems.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-500 bg-slate-950/40 rounded-xl border border-slate-800">
                    No problems match your current filters in this track.
                  </div>
                ) : (
                  filteredTrackProblems.map((problem) => {
                    const isDone = !!completedProblems[problem.task_id];
                    const diffColors = {
                      Easy: 'text-emerald-400 bg-emerald-950/60 border-emerald-800/50',
                      Medium: 'text-amber-400 bg-amber-950/60 border-amber-800/50',
                      Hard: 'text-rose-400 bg-rose-950/60 border-rose-800/50'
                    };

                    return (
                      <div
                        key={problem.task_id}
                        className={`p-2.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${
                          isDone
                            ? 'bg-slate-950/50 border-emerald-900/40 text-slate-400'
                            : 'bg-slate-950/80 border-slate-800/80 hover:border-slate-700 text-slate-200'
                        }`}
                      >
                        {/* Checkbox + Title */}
                        <div className="flex items-center gap-2.5 flex-1 min-w-0">
                          <button
                            onClick={() => toggleProblemCompletion(problem.task_id)}
                            className="text-slate-500 hover:text-emerald-400 transition-colors shrink-0"
                            title={isDone ? "Mark as incomplete" : "Mark as solved"}
                          >
                            {isDone ? (
                              <CheckSquare className="w-4 h-4 text-emerald-400" />
                            ) : (
                              <Square className="w-4 h-4 text-slate-600 hover:text-slate-400" />
                            )}
                          </button>

                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <a
                                href={`https://leetcode.com/problems/${problem.task_id}/`}
                                target="_blank"
                                rel="noreferrer"
                                className={`text-xs font-semibold hover:text-indigo-400 transition-colors truncate ${
                                  isDone ? 'line-through text-slate-500' : 'text-slate-200'
                                }`}
                              >
                                {problem.title}
                              </a>
                            </div>

                            <div className="flex items-center gap-2 mt-0.5">
                              <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded border ${diffColors[problem.difficulty] || diffColors.Medium}`}>
                                {problem.difficulty}
                              </span>
                              {problem.in_nc75 && (
                                <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/50">
                                  NC75
                                </span>
                              )}
                              {problem.in_nc150 && (
                                <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/50">
                                  NC150
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Action buttons: Video + Inspect */}
                        <div className="flex items-center gap-1.5 shrink-0">
                          {problem.video_url && (
                            <a
                              href={problem.video_url}
                              target="_blank"
                              rel="noreferrer"
                              className="p-1.5 rounded-lg bg-rose-950/40 text-rose-400 border border-rose-900/50 hover:bg-rose-900/60 transition-colors"
                              title="Watch Video Solution"
                            >
                              <PlayCircle className="w-3.5 h-3.5" />
                            </a>
                          )}

                          <button
                            onClick={() => onSelectProblem && onSelectProblem({ task_id: problem.task_id, title: problem.title, difficulty: problem.difficulty })}
                            className="p-1.5 rounded-lg bg-indigo-950/40 text-indigo-300 border border-indigo-800/50 hover:bg-indigo-900/60 transition-colors"
                            title="Inspect Cross-Platform Alternatives & AI Predictions"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
