import React from 'react';

export function LayoutWrapper({ children }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 relative overflow-hidden flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Ambient Mesh Radial Glows */}
      <div className="fixed -top-40 -left-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none ambient-glow-1 z-0" />
      <div className="fixed top-1/3 -right-40 w-[30rem] h-[30rem] bg-cyan-600/15 rounded-full blur-3xl pointer-events-none ambient-glow-2 z-0" />
      <div className="fixed -bottom-40 left-1/3 w-[32rem] h-[32rem] bg-purple-600/15 rounded-full blur-3xl pointer-events-none ambient-glow-1 z-0" />

      {/* Grid Pattern Texture Overlay */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-20 z-0"
        style={{
          backgroundImage: `radial-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px)`,
          backgroundSize: '24px 24px'
        }}
      />

      {/* Main Content Container */}
      <div className="relative z-10 flex-1 flex flex-col">
        {children}
      </div>
    </div>
  );
}
