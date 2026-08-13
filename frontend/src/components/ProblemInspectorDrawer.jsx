import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ExternalLink, Code2, Sparkles, Building2, Layers, Check, Copy, Send, Play } from 'lucide-react';

export function ProblemInspectorDrawer({ problem, isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('specs'); // 'specs' | 'code' | 'review'
  const [candidateCode, setCandidateCode] = useState('');
  const [rating, setRating] = useState('moderate');
  const [copied, setCopied] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  if (!problem) return null;

  const alternatives = problem.platform_alternatives || [
    { platform: 'LeetCode', name: 'LeetCode Direct', url: `https://leetcode.com/problems/${problem.task_id}/`, badge: 'Official' },
    { platform: 'GeeksforGeeks', name: 'GeeksforGeeks', url: `https://www.geeksforgeeks.org/?s=${encodeURIComponent(problem.title || problem.task_id)}`, badge: 'GFG' },
    { platform: 'LintCode', name: 'LintCode', url: `https://www.lintcode.com/search?key=${encodeURIComponent(problem.title || problem.task_id)}`, badge: 'LintCode' },
    { platform: 'HackerRank', name: 'HackerRank', url: `https://www.hackerrank.com/search?keyword=${encodeURIComponent(problem.title || problem.task_id)}`, badge: 'HackerRank' },
    { platform: 'CodeStudio', name: 'CodeStudio', url: `https://www.naukri.com/code360/problems?search=${encodeURIComponent(problem.title || problem.task_id)}`, badge: 'Studio' }
  ];

  const handleCopyCode = () => {
    navigator.clipboard.writeText(problem.completion || problem.starter_code || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleAnalyzeSolution = async () => {
    if (!candidateCode.trim()) return;
    setAnalyzing(true);
    try {
      const res = await fetch('/api/agent/analyze-solution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_slug: problem.task_id,
          candidate_code: candidateCode,
          performance_rating: rating
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setAnalysisResult(data.data);
      }
    } catch (err) {
      console.error('Analysis failed:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden flex justify-end">
          {/* Backdrop Blur Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm"
          />

          {/* Slide-over Drawer Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="relative w-full max-w-2xl bg-slate-900/95 border-l border-slate-800 shadow-2xl z-10 flex flex-col h-full overflow-hidden"
          >
            {/* Drawer Header */}
            <div className="p-6 border-b border-slate-800 flex items-start justify-between gap-4 bg-slate-950/40">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                    problem.difficulty === 'Easy' ? 'text-emerald-400 bg-emerald-950/50 border-emerald-800/50' :
                    problem.difficulty === 'Medium' ? 'text-amber-400 bg-amber-950/50 border-amber-800/50' :
                    'text-rose-400 bg-rose-950/50 border-rose-800/50'
                  }`}>
                    {problem.difficulty}
                  </span>
                  <span className="text-xs font-mono text-slate-400">#{problem.question_id || problem.task_id}</span>
                </div>
                <h2 className="text-lg font-bold text-slate-100">{problem.title || problem.task_id}</h2>
              </div>

              <button
                onClick={onClose}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 5 Cross-Platform Online Judge Alternatives Bar */}
            <div className="px-6 py-3 bg-slate-950/70 border-b border-slate-800/80">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                5 Cross-Platform Alternatives
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {alternatives.map((alt, idx) => (
                  <motion.a
                    key={idx}
                    href={alt.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.95 }}
                    className="p-2 rounded-lg bg-slate-800/70 hover:bg-indigo-950/50 border border-slate-700/60 hover:border-indigo-500/50 flex flex-col items-center justify-center text-center transition-all group"
                  >
                    <span className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 truncate w-full">
                      {alt.platform}
                    </span>
                    <span className="text-[10px] text-slate-500 flex items-center gap-0.5 mt-0.5">
                      Open <ExternalLink className="w-2.5 h-2.5" />
                    </span>
                  </motion.a>
                ))}
              </div>
            </div>

            {/* Nav Tabs */}
            <div className="flex border-b border-slate-800 bg-slate-950/30 px-6">
              {[
                { id: 'specs', label: 'Problem & Companies' },
                { id: 'code', label: 'Reference Code' },
                { id: 'review', label: 'AI Review & Stepper' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-3 px-4 text-xs font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-400'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content Container */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {activeTab === 'specs' && (
                <div className="space-y-6">
                  {/* Archetype Cluster */}
                  {problem.cluster_title && (
                    <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                      <div className="flex items-center gap-2 text-xs font-semibold text-indigo-400">
                        <Layers className="w-4 h-4" />
                        <span>Algorithmic Archetype (Cluster #{problem.cluster_id})</span>
                      </div>
                      <p className="text-sm font-medium text-slate-200">{problem.cluster_title}</p>
                    </div>
                  )}

                  {/* Description */}
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Problem Description</h4>
                    <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/80 text-xs text-slate-300 leading-relaxed whitespace-pre-wrap font-sans">
                      {problem.problem_description || 'No description recorded.'}
                    </div>
                  </div>

                  {/* Companies Asking */}
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                      <Building2 className="w-3.5 h-3.5 text-slate-500" />
                      <span>Asking Companies ({problem.companies?.length || 0})</span>
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {problem.companies?.map((c, i) => (
                        <span key={i} className="text-xs px-2.5 py-1 rounded-md bg-slate-800/70 border border-slate-700/50 text-slate-300 font-mono">
                          {c.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'code' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Python Canonical Solution</span>
                    <button
                      onClick={handleCopyCode}
                      className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied!' : 'Copy Code'}</span>
                    </button>
                  </div>

                  <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-indigo-200 overflow-x-auto leading-relaxed">
                    {problem.completion || problem.starter_code || '# No code snippet recorded.'}
                  </pre>
                </div>
              )}

              {activeTab === 'review' && (
                <div className="space-y-6">
                  {/* Candidate Code Input */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <Code2 className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Paste Your Candidate Solution (Python)</span>
                    </label>
                    <textarea
                      rows={6}
                      value={candidateCode}
                      onChange={(e) => setCandidateCode(e.target.value)}
                      placeholder="def twoSum(nums, target):&#10;    # Write your candidate solution here..."
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 resize-none"
                    />
                  </div>

                  {/* Performance Stepper Radios */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-300">How did you perform on this problem?</label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: 'struggled', label: 'Struggled (Step Down)', color: 'hover:border-rose-500' },
                        { id: 'moderate', label: 'Moderate (Reinforce)', color: 'hover:border-amber-500' },
                        { id: 'mastered', label: 'Mastered (Step Up)', color: 'hover:border-emerald-500' }
                      ].map((btn) => (
                        <button
                          key={btn.id}
                          type="button"
                          onClick={() => setRating(btn.id)}
                          className={`p-2.5 rounded-xl border text-xs font-medium transition-all ${btn.color} ${
                            rating === btn.id
                              ? 'bg-indigo-950/80 border-indigo-500 text-indigo-200'
                              : 'bg-slate-950/50 border-slate-800 text-slate-400'
                          }`}
                        >
                          {btn.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Analyze Button */}
                  <motion.button
                    whileTap={{ scale: 0.98 }}
                    onClick={handleAnalyzeSolution}
                    disabled={analyzing || !candidateCode.trim()}
                    className="w-full py-2.5 px-4 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>{analyzing ? 'Analyzing with MCP Tools...' : 'Run Autonomous Code Review'}</span>
                  </motion.button>

                  {/* Analysis Results Display */}
                  {analysisResult && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-4 rounded-xl bg-slate-950/80 border border-indigo-900/40 space-y-3"
                    >
                      <h4 className="text-xs font-semibold text-indigo-300">Analysis & Recommendation</h4>
                      <p className="text-xs text-slate-300">
                        {analysisResult.recommendation?.stepping_intent}
                      </p>

                      <div className="space-y-1.5 pt-2 border-t border-slate-800">
                        <span className="text-[11px] font-semibold text-slate-400 uppercase">Recommended Next Challenges:</span>
                        {analysisResult.recommendation?.recommended_stepped_problems?.map((p, idx) => (
                          <div key={idx} className="flex items-center justify-between text-xs p-2 rounded bg-slate-900 border border-slate-800">
                            <span className="font-mono text-slate-200 font-medium">{p.task_id}</span>
                            <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400">{p.difficulty}</span>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
