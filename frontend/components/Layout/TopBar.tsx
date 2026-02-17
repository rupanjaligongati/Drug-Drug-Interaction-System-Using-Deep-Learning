
import React from 'react';
import { Bell, Search, LogOut, UserCircle, Sun, Moon } from 'lucide-react';

interface TopBarProps {
  onLogout: () => void;
  isDarkMode: boolean;
  onToggleTheme: () => void;
  userName?: string | null;
}

export const TopBar: React.FC<TopBarProps> = ({ onLogout, isDarkMode, onToggleTheme, userName }) => {
  return (
    <header className="h-20 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 transition-colors duration-300 flex items-center justify-between px-8 z-10">
      <div className="flex-1 flex items-center max-w-xl">
        <div className="relative w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500" size={18} />
          <input
            type="text"
            placeholder="Search clinical protocols, drug IDs..."
            className="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl py-2.5 pl-12 pr-4 outline-none focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900 focus:border-blue-400 transition-all text-sm font-medium text-slate-900 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-6">
        <button
          onClick={onToggleTheme}
          className="p-2.5 bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 rounded-xl border border-slate-200 dark:border-slate-700 transition-all"
          title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        <button className="relative p-2.5 bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 rounded-xl border border-slate-200 dark:border-slate-700 transition-all">
          <Bell size={20} />
          <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-red-500 border-2 border-white dark:border-slate-900 rounded-full"></span>
        </button>

        <div className="h-10 w-[1px] bg-slate-200 dark:bg-slate-800 mx-2"></div>

        <div className="flex items-center gap-4">
          <div className="flex flex-col items-end hidden sm:flex">
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              {userName || 'Dr. Sarah Johnson'}
            </span>
            <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase">User</span>
          </div>
          <button className="group relative">
            <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-xl border-2 border-white dark:border-slate-800 shadow-sm flex items-center justify-center text-slate-400 dark:text-slate-500 overflow-hidden group-hover:border-blue-400 transition-all">
              <UserCircle size={32} />
            </div>
          </button>
          <button
            onClick={onLogout}
            className="p-2.5 text-slate-400 dark:text-slate-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
            title="Logout"
          >
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </header>
  );
};
