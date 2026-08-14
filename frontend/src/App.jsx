import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  GraduationCap, 
  Compass, 
  Radio, 
  Terminal, 
  Sparkles, 
  Layers, 
  Cpu, 
  Database, 
  Zap, 
  Settings, 
  X,
  MessageSquare
} from 'lucide-react';
import { LayoutWrapper } from './components/LayoutWrapper';
import { CurriculumStudio } from './components/CurriculumStudio';
import { ProblemExplorer } from './components/ProblemExplorer';
import { LiveCopilotStream } from './components/LiveCopilotStream';
import { ArchetypeClusters } from './components/ArchetypeClusters';
import { AICompanyPredictor } from './components/AICompanyPredictor';
import { CrawlerConsole } from './components/CrawlerConsole';
import { ProblemInspectorDrawer } from './components/ProblemInspectorDrawer';

export function App() {
  const [activeTab, setActiveTab] = useState('learn'); // 'learn' | 'explore' | 'assistant'
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isSystemMenuOpen, setIsSystemMenuOpen] = useState(false);
  const [systemTool, setSystemTool] = useState(null); // 'clusters' | 'classifier' | 'crawler'

  const [metadata, setMetadata] = useState({
    companies: [], difficulties: ['Easy', 'Medium', 'Hard'], topics: [], total_problems: 2870, clusters: [], crawler_running: false
  });
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  useEffect(() => {
    fetch('/api/metadata')
      .then(res => res.json())
      .then(data => setMetadata(data))
      .catch(console.error);
  }, []);

  const handleSelectProblem = (problem) => {
    setSelectedProblem(problem);
    setIsDrawerOpen(true);
  };

  return (
    <LayoutWrapper>
      <div className="flex h-screen overflow-hidden bg-slate-950 font-sans">
        
        {/* MAIN APPLICATION CONTAINER */}
        <div className="flex-1 flex flex-col min-w-0">
          
          {/* PRIMARY UNIFIED HEADER */}
          <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between shrink-0 z-20">
            
            {/* Brand Logo & Tagline */}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 via-cyan-500 to-purple-600 p-0.5 shadow-lg shadow-indigo-500/20">
                <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                  <Cpu className="w-4 h-4 text-cyan-400" />
                </div>
              </div>
              <div>
                <span className="font-bold text-sm text-slate-100 tracking-tight">Algorithmic Learning Engine</span>
                <span className="text-[10px] text-indigo-400 font-mono block -mt-0.5">Pedagogical Curriculum Compiler</span>
              </div>
            </div>

            {/* CORE PRIMARY NAVIGATION (Learn / Explore / Assistant) */}
            <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setActiveTab('learn')}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'learn'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <GraduationCap className="w-4 h-4" />
                <span>Your Learning Path</span>
              </button>

              <button
                onClick={() => setActiveTab('explore')}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'explore'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Compass className="w-4 h-4" />
                <span>Explore Problems</span>
                <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-slate-800 text-slate-400">
                  {metadata.total_problems}
                </span>
              </button>

              <button
                onClick={() => setActiveTab('assistant')}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'assistant'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
                <span>AI Copilot</span>
              </button>
            </div>

            {/* RIGHT UTILITIES & SYSTEM CONSOLE TRIGGER */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsSystemMenuOpen(!isSystemMenuOpen)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 text-xs font-medium transition-colors"
                title="System Utilities & Admin Tools"
              >
                <Settings className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">System Utilities</span>
              </button>
            </div>
          </header>

          {/* SECONDARY OVERLAY: SYSTEM UTILITIES MENU */}
          <AnimatePresence>
            {isSystemMenuOpen && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="bg-slate-900/90 border-b border-slate-800 px-6 py-3 flex items-center justify-between text-xs backdrop-blur-md z-10"
              >
                <div className="flex items-center gap-4 text-slate-400 font-mono">
                  <span className="text-slate-500 uppercase font-semibold text-[10px]">Infrastructure Tools:</span>
                  <button onClick={() => { setSystemTool('clusters'); setIsSystemMenuOpen(false); }} className="hover:text-indigo-300 flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5 text-indigo-400" /> Archetype Ontology
                  </button>
                  <button onClick={() => { setSystemTool('classifier'); setIsSystemMenuOpen(false); }} className="hover:text-cyan-300 flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Company Predictor
                  </button>
                  <button onClick={() => { setSystemTool('crawler'); setIsSystemMenuOpen(false); }} className="hover:text-amber-300 flex items-center gap-1">
                    <Terminal className="w-3.5 h-3.5 text-amber-400" /> Crawler Daemon
                  </button>
                </div>
                <div className="flex items-center gap-4 text-[11px] font-mono text-slate-500">
                  <span className="flex items-center gap-1"><Database className="w-3 h-3 text-emerald-400" /> ChromaDB HNSW</span>
                  <span className="flex items-center gap-1"><Zap className="w-3 h-3 text-amber-400" /> SQLite ACID Queue</span>
                  <button onClick={() => setIsSystemMenuOpen(false)} className="text-slate-400 hover:text-white"><X className="w-4 h-4" /></button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* CORE VIEW BODY */}
          <main className="flex-1 overflow-y-auto p-6 relative">
            
            {/* Render Modal for Secondary System Tools if selected */}
            <AnimatePresence>
              {systemTool && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/70 backdrop-blur-md">
                  <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl max-h-[85vh] overflow-y-auto p-6 relative shadow-2xl">
                    <div className="flex justify-between items-center pb-4 border-b border-slate-800 mb-4">
                      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">System Administration Console</h3>
                      <button onClick={() => setSystemTool(null)} className="p-1 rounded-lg text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
                    </div>
                    {systemTool === 'clusters' && <ArchetypeClusters metadata={metadata} onSelectCluster={handleSelectProblem} onInspectProblem={handleSelectProblem} />}
                    {systemTool === 'classifier' && <AICompanyPredictor onSelectProblem={handleSelectProblem} />}
                    {systemTool === 'crawler' && <CrawlerConsole metadata={metadata} onScrapeSuccess={() => {}} />}
                  </motion.div>
                </div>
              )}
            </AnimatePresence>

            {/* Primary Product Views */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.15 }}
                className="h-full"
              >
                {activeTab === 'learn' && <CurriculumStudio onSelectProblem={handleSelectProblem} />}
                {activeTab === 'explore' && <ProblemExplorer metadata={metadata} onSelectProblem={handleSelectProblem} />}
                {activeTab === 'assistant' && <LiveCopilotStream />}
              </motion.div>
            </AnimatePresence>
          </main>
        </div>

      </div>

      {/* Slide-over Problem Inspector */}
      <ProblemInspectorDrawer problem={selectedProblem} isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)} />
    </LayoutWrapper>
  );
}

export default App;
