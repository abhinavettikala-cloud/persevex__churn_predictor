import React, { useEffect, useState } from 'react';
import { Activity, LayoutDashboard, Settings, Info, Server, Cpu } from 'lucide-react';

export default function Sidebar() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          setApiStatus('online');
        } else {
          setApiStatus('offline');
        }
      } catch {
        setApiStatus('offline');
      }
    };
    checkApi();
    const interval = setInterval(checkApi, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="w-64 bg-slate-900 flex-shrink-0 flex flex-col text-slate-400 border-r border-slate-800 h-screen fixed top-0 left-0 z-10">
      <div className="p-6 flex items-center space-x-3 mt-2">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">C</div>
        <span className="text-white font-bold text-lg tracking-tight">CHURN_AI</span>
      </div>
      <nav className="flex-1 px-4 space-y-1 mt-4">
        <a href="#" className="flex items-center space-x-3 bg-slate-800 text-white px-3 py-2 rounded-md">
          <LayoutDashboard className="w-5 h-5" />
          <span className="text-sm font-medium">Deployment Home</span>
        </a>
        <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-md hover:bg-slate-800 transition-colors">
          <Cpu className="w-5 h-5" />
          <span className="text-sm font-medium">Predictive Analytics</span>
        </a>
        <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-md hover:bg-slate-800 transition-colors">
          <Settings className="w-5 h-5" />
          <span className="text-sm font-medium">Model History</span>
        </a>
      </nav>
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center justify-between mb-2 px-2">
          <span className="text-xs uppercase tracking-wider font-semibold">API Status</span>
          <span className={`flex h-2 w-2 rounded-full ${apiStatus === 'online' ? 'bg-emerald-500' : apiStatus === 'offline' ? 'bg-rose-500' : 'bg-amber-400'}`}></span>
        </div>
        <div className="bg-slate-800 rounded-lg p-3">
          <p className="text-[10px] leading-relaxed mb-1">Endpoint: <span className="text-blue-400">v2.churn-api.prod</span></p>
          <p className="text-[10px] leading-relaxed">Latency: <span className="text-emerald-400">12ms</span></p>
        </div>
      </div>
    </aside>
  );
}
