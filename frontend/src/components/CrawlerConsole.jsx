import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Play, Square, DownloadCloud, Activity, CheckCircle2 } from 'lucide-react';

export function CrawlerConsole({ metadata, onScrapeSuccess }) {
  const [slugInput, setSlugInput] = useState('');
  const [scraping, setScraping] = useState(false);
  const [crawlerRunning, setCrawlerRunning] = useState(metadata.crawler_running || false);
  const [crawlerStatus, setCrawlerStatus] = useState({ queue_size: 0, total_ingested_count: 0, recent_activity: [] });
  const [message, setMessage] = useState(null);

  const fetchCrawlerStatus = async () => {
    try {
      const res = await fetch('/api/crawler/status');
      const data = await res.json();
      if (data.status === 'success') {
        setCrawlerStatus(data.data);
        setCrawlerRunning(data.data.is_running);
      }
    } catch (err) {
      console.error('Failed to fetch crawler status:', err);
    }
  };

  useEffect(() => {
    fetchCrawlerStatus();
    const interval = setInterval(fetchCrawlerStatus, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleCrawler = async () => {
    try {
      const res = await fetch('/api/crawler/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enable: !crawlerRunning })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setCrawlerRunning(data.crawler_running);
      }
    } catch (err) {
      console.error('Toggle failed:', err);
    }
  };

  const handleScrapeSlug = async (e) => {
    e.preventDefault();
    if (!slugInput.trim()) return;

    setScraping(true);
    setMessage(null);
    try {
      const res = await fetch('/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug_or_url: slugInput.trim() })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setMessage({ type: 'success', text: `Successfully scraped & enriched '${data.data.task_id}' into live database!` });
        setSlugInput('');
        if (onScrapeSuccess) onScrapeSuccess();
      } else {
        setMessage({ type: 'error', text: data.message || 'Scrape failed.' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: `Network error: ${err}` });
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Left: Crawler Controls & Single Scraper */}
      <div className="lg:col-span-5 space-y-4">
        {/* Continuous Ingestion Card */}
        <div className="glass-panel rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-400" />
              <span>Continuous Crawler Daemon</span>
            </h3>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono border ${
              crawlerRunning
                ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300 animate-pulse'
                : 'bg-slate-900 border-slate-800 text-slate-500'
            }`}>
              {crawlerRunning ? 'RUNNING' : 'STOPPED'}
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Crawls LeetCode GraphQL public endpoints in the background, extracts specifications, autocalibrates 30 archetypes, and dynamically indexes vectors.
          </p>

          <button
            onClick={handleToggleCrawler}
            className={`w-full py-2.5 px-4 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
              crawlerRunning
                ? 'bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-300'
                : 'bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-800 text-emerald-300'
            }`}
          >
            {crawlerRunning ? <Square className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{crawlerRunning ? 'Pause Continuous Crawler' : 'Start Continuous Crawler'}</span>
          </button>
        </div>

        {/* Single Problem Scraper Card */}
        <div className="glass-panel rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <DownloadCloud className="w-4 h-4 text-cyan-400" />
            <span>On-Demand Single Problem Ingestion</span>
          </h3>

          <form onSubmit={handleScrapeSlug} className="space-y-3">
            <input
              type="text"
              value={slugInput}
              onChange={(e) => setSlugInput(e.target.value)}
              placeholder="e.g. median-of-two-sorted-arrays or URL..."
              className="w-full bg-slate-900/90 border border-slate-700/60 rounded-xl p-3 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500"
            />

            <button
              type="submit"
              disabled={scraping || !slugInput.trim()}
              className="w-full py-2.5 px-4 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:opacity-90 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
            >
              <DownloadCloud className="w-3.5 h-3.5" />
              <span>{scraping ? 'Extracting & Auto-Classifying...' : 'Fetch & Enrich to Live DB'}</span>
            </button>
          </form>

          {message && (
            <div className={`p-3 rounded-xl text-xs font-mono ${
              message.type === 'success' ? 'bg-emerald-950/70 border border-emerald-800 text-emerald-300' : 'bg-rose-950/70 border border-rose-800 text-rose-300'
            }`}>
              {message.text}
            </div>
          )}
        </div>
      </div>

      {/* Right: Real-time Ingestion Stream Console */}
      <div className="lg:col-span-7 space-y-4">
        <div className="glass-panel rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Terminal className="w-4 h-4 text-emerald-400" />
              <span>Live Ingestion Activity Log</span>
            </h4>
            <span className="text-xs font-mono text-slate-500">
              Total Ingested: {crawlerStatus.total_ingested_count || 0}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 h-80 overflow-y-auto space-y-2">
            {crawlerStatus.recent_activity?.length > 0 ? (
              crawlerStatus.recent_activity.map((log, idx) => (
                <div key={idx} className="flex items-start gap-2 border-b border-slate-900 pb-1.5">
                  <span className="text-slate-500 text-[11px] shrink-0">[{log.time}]</span>
                  <span className={log.status === 'success' ? 'text-emerald-400' : 'text-slate-300'}>
                    {log.message || JSON.stringify(log)}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-slate-600 text-center py-24">
                No crawler activity recorded yet. Start the crawler or fetch a problem to view logs.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
