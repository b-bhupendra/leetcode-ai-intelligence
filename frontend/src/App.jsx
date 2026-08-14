import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen,
  Compass,
  Radio,
  Terminal,
  Layers,
  Cpu,
  Settings,
  Map,
  X,
  ChevronDown,
  Activity
} from 'lucide-react';

import { LayoutWrapper } from './components/LayoutWrapper';
import { LearningJourney } from './components/LearningJourney';
import { ProblemExplorer } from './components/ProblemExplorer';
import { AICompanyPredictor } from './components/AICompanyPredictor';
import { LiveCopilotStream } from './components/LiveCopilotStream';
import { CrawlerConsole } from './components/CrawlerConsole';
import { ArchetypeClusters } from './components/ArchetypeClusters';
import { NeetCodeVisualRoadmap } from './components/NeetCodeVisualRoadmap';
import { ProblemInspectorDrawer } from './components/ProblemInspectorDrawer';

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { type: 'spring', damping: 28, stiffness: 380 } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.13 } }
};

// Primary nav — what the learner cares about
const PRIMARY_TABS = [
  { id: 'learn', label: 'Learn', icon: BookOpen },
  { id: 'explore', label: 'Explore Problems', icon: Compass },
  { id: 'assistant', label: 'AI Assistant', icon: Radio, pulse: true }
];

// System nav — infrastructure the learner doesn't need to see
const SYSTEM_TABS = [
  { id: 'roadmap', label: 'NeetCode Roadmap', icon: Map },
  { id: 'clusters', label: '15 Archetypes', icon: Layers },
  { id: 'scraper', label: 'Crawler Daemon', icon: Terminal }
];

export function App() {
  const [activeTab, setActiveTab] = useState('learn');
  const [systemMenuOpen, setSystemMenuOpen] = useState(false);
  const [metadata, setMetadata] = useState({
    companies: [], difficulties: ['Easy', 'Medium', 'Hard'],
    topics: [], total_problems: 2870, clusters: [], crawler_running: false
  });
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [filterClusterId, setFilterClusterId] = useState(null);
  const systemMenuRef = useRef(null);

  useEffect(() => {
    fetch('/api/metadata').then(r => r.json()).then(setMetadata).catch(console.error);
  }, []);

  // Close system menu on outside click
  useEffect(() => {
    function handleClick(e) {
      if (systemMenuRef.current && !systemMenuRef.current.contains(e.target)) {
        setSystemMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSelectProblem = (problem) => {
    setSelectedProblem(problem);
    setIsDrawerOpen(true);
  };

  const handleNav = (tabId) => {
    if (tabId !== 'explore') setFilterClusterId(null);
    setActiveTab(tabId);
    setSystemMenuOpen(false);
  };

  const isSystemTab = SYSTEM_TABS.some(t => t.id === activeTab);

  return (
    <LayoutWrapper>
      {/* ─── Header ─── */}
      <header className="border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 via-cyan-500 to-purple-600 p-0.5 shadow-lg shadow-indigo-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Cpu className="w-4 h-4 text-cyan-400" />
              </div>
            </div>
            <div>
              <span className="font-bold text-sm text-slate-100 tracking-tight">Algorithmic Learning Engine</span>
              <div className="hidden sm:flex items-center gap-1.5 mt-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-[10px] text-slate-500 font-mono">
                  {metadata.total_problems?.toLocaleString()} problems indexed
                </span>
              </div>
            </div>
          </div>

          {/* Primary navigation — 3 items only */}
          <nav className="flex items-center gap-1">
            {PRIMARY_TABS.map(tab => {
              const Icon = tab.icon;
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => handleNav(tab.id)}
                  className={`relative px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${
                    active
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-600/40'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">{tab.label}</span>
                  {tab.pulse && (
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  )}
                </button>
              );
            })}

            {/* System / Infrastructure dropdown */}
            <div className="relative ml-1" ref={systemMenuRef}>
              <button
                onClick={() => setSystemMenuOpen(v => !v)}
                className={`px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-1.5 transition-all ${
                  isSystemTab
                    ? 'bg-slate-700/40 text-slate-300 border border-slate-700'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/60'
                }`}
                title="System tools"
              >
                <Settings className="w-3.5 h-3.5" />
                <ChevronDown className={`w-3 h-3 transition-transform ${systemMenuOpen ? 'rotate-180' : ''}`} />
              </button>

              <AnimatePresence>
                {systemMenuOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -6, scale: 0.96 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -6, scale: 0.96 }}
                    transition={{ duration: 0.12 }}
                    className="absolute right-0 top-full mt-2 w-48 bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden z-50"
                  >
                    <div className="px-3 py-2 border-b border-slate-800">
                      <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">System</span>
                    </div>
                    {SYSTEM_TABS.map(tab => {
                      const Icon = tab.icon;
                      return (
                        <button
                          key={tab.id}
                          onClick={() => handleNav(tab.id)}
                          className={`w-full px-3 py-2.5 flex items-center gap-2.5 text-sm transition-colors ${
                            activeTab === tab.id
                              ? 'bg-slate-800 text-slate-200'
                              : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                          }`}
                        >
                          <Icon className="w-3.5 h-3.5 text-slate-500" />
                          {tab.label}
                        </button>
                      );
                    })}
                    {/* Company Classifier — power-user feature */}
                    <button
                      onClick={() => handleNav('analyzer')}
                      className={`w-full px-3 py-2.5 flex items-center gap-2.5 text-sm transition-colors ${
                        activeTab === 'analyzer'
                          ? 'bg-slate-800 text-slate-200'
                          : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                      }`}
                    >
                      <Activity className="w-3.5 h-3.5 text-slate-500" />
                      Company Classifier
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </nav>
        </div>
      </header>

      {/* ─── Content ─── */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        <AnimatePresence mode="wait">
          <motion.div key={activeTab} variants={pageVariants} initial="initial" animate="animate" exit="exit">

            {activeTab === 'learn' && (
              <LearningJourney onSelectProblem={handleSelectProblem} />
            )}

            {activeTab === 'explore' && (
              <ProblemExplorer
                metadata={metadata}
                onSelectProblem={handleSelectProblem}
                initialClusterId={filterClusterId}
              />
            )}

            {activeTab === 'assistant' && (
              <LiveCopilotStream />
            )}

            {activeTab === 'roadmap' && (
              <NeetCodeVisualRoadmap
                onSelectProblem={handleSelectProblem}
                onFilterCluster={(id) => { setFilterClusterId(id); setActiveTab('explore'); }}
              />
            )}

            {activeTab === 'clusters' && (
              <ArchetypeClusters
                metadata={metadata}
                onSelectCluster={handleSelectProblem}
                onInspectProblem={handleSelectProblem}
                onFilterExplorerByCluster={(id) => { setFilterClusterId(id); setActiveTab('explore'); }}
              />
            )}

            {activeTab === 'scraper' && (
              <CrawlerConsole metadata={metadata} onScrapeSuccess={() =>
                fetch('/api/metadata').then(r => r.json()).then(setMetadata).catch(console.error)
              } />
            )}

            {activeTab === 'analyzer' && (
              <AICompanyPredictor onSelectProblem={handleSelectProblem} />
            )}

          </motion.div>
        </AnimatePresence>
      </main>

      <ProblemInspectorDrawer
        problem={selectedProblem}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </LayoutWrapper>
  );
}

export default App;
