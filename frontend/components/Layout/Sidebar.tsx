
import React from 'react';
import { Activity, Zap, ShieldAlert, HeartPulse, History, BarChart3, Settings, ShieldCheck } from 'lucide-react';

interface SidebarProps {
  active: string;
  onSelect: (tab: any) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ active, onSelect }) => {
  const menu = [
    { id: 'analysis', label: 'Analysis', icon: Activity },
    { id: 'explain', label: 'Explainable AI', icon: Zap },
    { id: 'safety', label: 'Risk & Safety', icon: ShieldAlert },
    { id: 'recs', label: 'Recommendations', icon: HeartPulse },
    { id: 'history', label: 'Patient History', icon: History },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 flex-shrink-0 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 transition-colors duration-300 flex flex-col h-full z-20">
      <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-blue-200 dark:shadow-blue-900/20">
          <ShieldCheck size={22} />
        </div>
        <div>
          <h1 className="text-lg font-bold text-slate-900 dark:text-white poppins leading-tight">DDIPS</h1>
          <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-widest">Enterprise AI</p>
        </div>
      </div>

      <nav className="flex-1 py-8 px-3 space-y-1">
        {menu.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelect(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl text-sm font-semibold transition-all group
              ${active === item.id 
                ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-800' 
                : 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white border border-transparent'}`}
          >
            <item.icon size={18} className={active === item.id ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300'} />
            {item.label}
          </button>
        ))}
      </nav>

      <div className="p-6 bg-slate-50/50 dark:bg-slate-800/50 m-4 rounded-2xl border border-slate-100 dark:border-slate-800">
        <p className="text-xs font-bold text-slate-900 dark:text-slate-200 mb-2">Beta Access</p>
        <p className="text-[10px] text-slate-500 dark:text-slate-400 mb-4 leading-relaxed">You are currently using the polypharmacy-enabled engine v3.0.</p>
        <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <div className="h-full bg-blue-600 w-3/4"></div>
        </div>
      </div>
    </aside>
  );
};
