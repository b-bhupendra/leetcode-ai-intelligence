import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Radio, Bot, Send, Sparkles, ChevronRight, Zap, CheckCircle2 } from 'lucide-react';

export function LiveCopilotStream() {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const [userPrompt, setUserPrompt] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const sse = new EventSource('/api/agent/stream');

    sse.onopen = () => {
      setConnected(true);
    };

    sse.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setEvents((prev) => [data, ...prev].slice(0, 30));
      } catch (err) {
        console.error('Failed to parse SSE event:', err);
      }
    };

    sse.onerror = () => {
      setConnected(false);
    };

    return () => {
      sse.close();
    };
  }, []);

  const handleSendPrompt = async (e) => {
    e.preventDefault();
    if (!userPrompt.trim()) return;

    setSubmitting(true);
    try {
      await fetch('/api/agent/submit-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query_text: userPrompt,
          query_type: 'general'
        })
      });
      setUserPrompt('');
    } catch (err) {
      console.error('Failed to submit prompt:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left 2 Cols: Live SSE Stream */}
      <div className="lg:col-span-2 space-y-4">
        {/* Stream Header */}
        <div className="glass-panel rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <span className={`w-3 h-3 rounded-full block ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
              {connected && (
                <span className="absolute inset-0 rounded-full bg-emerald-400/40 animate-ping" />
              )}
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                <span>Model Context Protocol (MCP) Copilot Bus</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950 text-indigo-300 border border-indigo-800/40">
                  SSE ACTIVE
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Live bidirectional feed broadcasting grounded MCP tool insights & 5-second queue responses.
              </p>
            </div>
          </div>

          <span className="text-xs font-mono text-slate-500">
            {events.length} Events Received
          </span>
        </div>

        {/* Animated Stream Container */}
        <div className="space-y-3 min-h-[400px]">
          <AnimatePresence initial={false}>
            {events.map((ev, index) => (
              <motion.div
                key={ev.id || index}
                layout
                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ type: 'spring', stiffness: 400, damping: 28 }}
                className="glass-panel rounded-xl p-5 border-l-4 border-l-indigo-500 relative overflow-hidden"
              >
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-lg bg-indigo-950/80 border border-indigo-800/50 flex items-center justify-center text-indigo-400">
                      <Bot className="w-3.5 h-3.5" />
                    </div>
                    <h4 className="text-sm font-semibold text-slate-100">{ev.title}</h4>
                  </div>
                  <span className="text-[11px] font-mono text-slate-500">{ev.timestamp}</span>
                </div>

                {ev.problem_slug && (
                  <div className="mb-2">
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-900 text-indigo-300 border border-slate-800">
                      Target: {ev.problem_slug}
                    </span>
                  </div>
                )}

                <div className="text-xs text-slate-300 whitespace-pre-wrap leading-relaxed bg-slate-950/40 p-3 rounded-lg border border-slate-800/50 font-mono">
                  {ev.content || ev.markdown || JSON.stringify(ev, null, 2)}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {events.length === 0 && (
            <div className="glass-panel rounded-xl p-12 text-center text-slate-500 space-y-2">
              <Radio className="w-8 h-8 mx-auto text-slate-600 animate-pulse" />
              <p className="text-sm font-medium text-slate-400">Listening to Live SSE Event Bus...</p>
              <p className="text-xs text-slate-600">Submit a problem analysis or custom prompt to see live AI agent pushes.</p>
            </div>
          )}
        </div>
      </div>

      {/* Right Col: AI Prompt & Grounded Tools Console */}
      <div className="space-y-4">
        <div className="glass-panel rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>Trigger Autonomous Agent</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Send an instruction directly to the 5-second agent worker. It will ground on the dataset and broadcast the solution live.
          </p>

          <form onSubmit={handleSendPrompt} className="space-y-3">
            <textarea
              rows={4}
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              placeholder="e.g. Find Google DP questions with sliding window or synthesize a custom hard graph problem..."
              className="w-full bg-slate-900/90 border border-slate-700/60 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono resize-none"
            />

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 px-4 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{submitting ? 'Enqueuing to SQLite...' : 'Dispatch Agent Task'}</span>
            </button>
          </form>
        </div>

        {/* MCP Active Tools List */}
        <div className="glass-panel rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Grounded MCP Tools (6 Active)</span>
          </div>

          <div className="space-y-2 text-xs">
            {[
              { name: 'query_company_radar', desc: 'Queries 200 company interview frequencies' },
              { name: 'get_problem_full_specs', desc: 'Fetches code & 5 platform links' },
              { name: 'analyze_candidate_solution', desc: 'Inspects code complexity & traps' },
              { name: 'adaptive_difficulty_stepper', desc: 'Steps up/down across 30 archetypes' },
              { name: 'suggest_custom_concept', desc: 'Synthesizes mock company prompts' },
              { name: 'push_to_web_dashboard', desc: 'Reverse MCP SSE broadcaster' },
            ].map((tool, i) => (
              <div key={i} className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-mono text-indigo-300 font-medium">{tool.name}</span>
                  <p className="text-[11px] text-slate-400">{tool.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
