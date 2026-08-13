import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Building2, Layers, CheckCircle2, ArrowRight } from 'lucide-react';

export function AICompanyPredictor({ onSelectProblem }) {
  const [description, setDescription] = useState('');
  const [title, setTitle] = useState('');
  const [difficulty, setDifficulty] = useState('Medium');
  const [predicting, setPredicting] = useState(false);
  const [results, setResults] = useState(null);

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!description.trim()) return;

    setPredicting(true);
    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          description,
          difficulty,
          top_k: 8
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setResults(data.data);
      }
    } catch (err) {
      console.error('Prediction failed:', err);
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Left: Input Form */}
      <div className="lg:col-span-6 space-y-4">
        <div className="glass-panel rounded-2xl p-6 space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>Multi-Label Company Classifier</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Paste any raw problem statement. The ML engine will predict which companies can ask it, its algorithmic archetype, and 5 alternative links.
            </p>
          </div>

          <form onSubmit={handlePredict} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Problem Title (Optional)</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Alien Dictionary"
                  className="w-full bg-slate-900/90 border border-slate-700/60 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Target Difficulty</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-700/60 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Problem Statement & Constraints</label>
              <textarea
                rows={7}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Paste full problem statement, input/output formats, and constraints here..."
                className="w-full bg-slate-900/90 border border-slate-700/60 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-sans resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={predicting || !description.trim()}
              className="w-full py-2.5 px-4 bg-gradient-to-r from-indigo-600 via-cyan-600 to-purple-600 hover:opacity-90 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-500/25 disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{predicting ? 'Classifying Vectors across 200 Companies...' : 'Predict Asking Companies & Archetype'}</span>
            </button>
          </form>
        </div>
      </div>

      {/* Right: Prediction Output */}
      <div className="lg:col-span-6 space-y-4">
        <AnimatePresence mode="wait">
          {results ? (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              {/* Archetype & Topic Match */}
              <div className="glass-panel rounded-2xl p-6 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Detected Archetype</span>
                  <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">
                    Cluster #{results.archetype_cluster?.cluster_id}
                  </span>
                </div>
                <h4 className="text-base font-bold text-slate-100">{results.archetype_cluster?.title}</h4>
                <p className="text-xs text-slate-300">{results.archetype_cluster?.description}</p>

                <div className="flex flex-wrap gap-1.5 pt-2">
                  {results.archetype_cluster?.top_tags?.map((t, i) => (
                    <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              {/* Company Probability Breakdown */}
              <div className="glass-panel rounded-2xl p-6 space-y-4">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                  <Building2 className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Company Likelihood Breakdown</span>
                </h4>

                <div className="space-y-3">
                  {results.company_predictions?.map((comp, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex items-center justify-between text-xs font-medium">
                        <span className="text-slate-200 uppercase font-mono">{comp.company}</span>
                        <span className="text-indigo-400">{comp.match_percentage}% Match</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${comp.match_percentage}%` }}
                          transition={{ duration: 0.6, delay: idx * 0.05 }}
                          className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="glass-panel rounded-2xl p-12 text-center text-slate-500 space-y-3 h-full flex flex-col items-center justify-center">
              <Layers className="w-10 h-10 text-slate-600" />
              <p className="text-sm font-medium text-slate-400">Prediction Engine Ready</p>
              <p className="text-xs text-slate-500 max-w-sm">
                Enter a problem statement and click Predict to see real-time company match probabilities, archetype assignment, and similar practice questions.
              </p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
