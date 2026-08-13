import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Compass, 
  Sparkles, 
  Radio, 
  Terminal, 
  Layers, 
  Cpu, 
  Database, 
  Zap, 
  Code2, 
  Building2 
} from 'lucide-react';

import { LayoutWrapper } from './components/LayoutWrapper';
import { ProblemExplorer } from './components/ProblemExplorer';
import { AICompanyPredictor } from './components/AICompanyPredictor';
import { LiveCopilotStream } from './components/LiveCopilotStream';
import { CrawlerConsole } from './components/CrawlerConsole';
import { ArchetypeClusters } from './components/ArchetypeClusters';
import { ProblemInspectorDrawer } from './components/ProblemInspectorDrawer';

const tabContentVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: { type: 'spring', damping: 25, stiffness: 350 }
  },
  exit: { 
    opacity: 0, 
    y: -8,
    transition: { duration: 0.15 }
  }
};

export function App() {
  const [activeTab, setActiveTab] = useState('explorer');
  const [metadata, setMetadata] = useState({
    companies: [],
    difficulties: ['Easy', 'Medium', 'Hard'],
    topics: [],
    total_problems: 2870,
    clusters: [],
    crawler_running: false
  });
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const fetchMetadata = async () => {
    try {
      const res = await fetch('/api/metadata');
      const data = await res.json();
      setMetadata(data);
    } catch (err) {
      console.error('Failed to load metadata:', err);
    }
  };

  useEffect(() => {
    fetchMetadata();
  }, []);

  const handleSelectProblem = (problem) => {
    setSelectedProblem(problem);
    setIsDrawerOpen(true);
  };

  const [filterClusterId, setFilterClusterId] = useState(null);

  const handleFilterExplorerByCluster = (clusterId) => {
    setFilterClusterId(clusterId);
    setActiveTab('explorer');
  };

  const navTabs = [
    { id: 'explorer', label: 'Problem Explorer', icon: Compass, badge: `${metadata.total_problems || 2870}` },
    { id: 'analyzer', label: 'Company Classifier', icon: Sparkles },
    { id: 'copilot', label: 'Live MCP Copilot', icon: Radio, pulse: true },
    { id: 'scraper', label: 'Crawler Daemon', icon: Terminal },
    { id: 'clusters', label: '15 Archetypes & Roadmap', icon: Layers }
  ];

  return (
    <LayoutWrapper>
      {/* Top Enterprise SaaS Navigation Bar */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-cyan-500 to-purple-600 p-0.5 shadow-lg shadow-indigo-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Cpu className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-slate-100 tracking-tight">LeetCode AI Intelligence</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-indigo-950 text-indigo-300 border border-indigo-800/50">
                  15 Unified Archetypes
                </span>
              </div>
              <span className="text-[11px] text-slate-400 font-mono hidden sm:inline">
                4 Core Paradigms • 15 Algorithmic Archetypes • 6-Phase Mastery Roadmap
              </span>
            </div>
          </div>

          {/* System Status Indicators */}
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-300">
              <Database className="w-3.5 h-3.5 text-emerald-400" />
              <span>ChromaDB HNSW</span>
            </div>

            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-300">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>SQLite Queue (5s Loop)</span>
            </div>
          </div>
        </div>

        {/* Tab Navigation Navigation Bar */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 overflow-x-auto no-scrollbar">
          {navTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  if (tab.id !== 'explorer') setFilterClusterId(null);
                  setActiveTab(tab.id);
                }}
                className={`relative py-3 px-4 text-xs font-medium flex items-center gap-2 transition-colors whitespace-nowrap ${
                  isActive ? 'text-indigo-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                <span>{tab.label}</span>

                {tab.pulse && (
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                )}

                {tab.badge && (
                  <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-slate-800 text-slate-400">
                    {tab.badge}
                  </span>
                )}

                {isActive && (
                  <motion.div
                    layoutId="activeTabIndicator"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 via-cyan-400 to-indigo-500"
                    transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                  />
                )}
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Animated View Body */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            variants={tabContentVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            {activeTab === 'explorer' && (
              <ProblemExplorer
                metadata={metadata}
                onSelectProblem={handleSelectProblem}
                initialClusterId={filterClusterId}
              />
            )}

            {activeTab === 'analyzer' && (
              <AICompanyPredictor
                onSelectProblem={handleSelectProblem}
              />
            )}

            {activeTab === 'copilot' && (
              <LiveCopilotStream />
            )}

            {activeTab === 'scraper' && (
              <CrawlerConsole
                metadata={metadata}
                onScrapeSuccess={fetchMetadata}
              />
            )}

            {activeTab === 'clusters' && (
              <ArchetypeClusters
                metadata={metadata}
                onSelectCluster={handleSelectProblem}
                onInspectProblem={handleSelectProblem}
                onFilterExplorerByCluster={handleFilterExplorerByCluster}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Slide-over Problem Inspector Drawer */}
      <ProblemInspectorDrawer
        problem={selectedProblem}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </LayoutWrapper>
  );
}

export default App;
