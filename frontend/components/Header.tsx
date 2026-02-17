
import React from 'react';
// Fix: Import ShieldCheck from lucide-react instead of non-existent UI_ICONS
import { ShieldCheck } from 'lucide-react';

interface HeaderProps {
  onNav: (view: 'home' | 'predict' | 'dashboard' | 'how-it-works') => void;
  currentView: string;
  isAuthenticated: boolean;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onNav, currentView, isAuthenticated, onLogout }) => {
  return (
    <header className="sticky top-0 z-50 w-full glass-card border-b border-blue-100 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div 
          className="flex items-center gap-3 cursor-pointer group"
          onClick={() => onNav('home')}
        >
          {/* Fix: Replaced UI_ICONS.Logo with a standard icon container using ShieldCheck */}
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
            <ShieldCheck size={18} />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-teal-500 bg-clip-text text-transparent">
              DDIPS
            </h1>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold">
              Interaction AI
            </p>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600">
          <button 
            onClick={() => onNav('home')}
            className={`hover:text-blue-600 transition-colors ${currentView === 'home' ? 'text-blue-600' : ''}`}
          >
            Home
          </button>
          <button 
            onClick={() => onNav('dashboard')}
            className={`hover:text-blue-600 transition-colors ${currentView === 'dashboard' ? 'text-blue-600' : ''}`}
          >
            Analytics
          </button>
          <button 
            onClick={() => onNav('how-it-works')}
            className={`hover:text-blue-600 transition-colors ${currentView === 'how-it-works' ? 'text-blue-600' : ''}`}
          >
            How It Works
          </button>
          <button className="hover:text-blue-600 transition-colors">Docs</button>
        </nav>

        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <>
              <button 
                onClick={onLogout}
                className="text-slate-500 hover:text-red-600 font-bold text-sm transition-colors"
              >
                Logout
              </button>
              <button 
                onClick={() => onNav('predict')}
                className="bg-gradient-to-r from-blue-600 to-teal-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm shadow-lg shadow-blue-200 hover:shadow-blue-300 hover:-translate-y-0.5 transition-all active:scale-95"
              >
                New Analysis
              </button>
            </>
          ) : (
            <button 
              onClick={() => onNav('predict')}
              className="bg-gradient-to-r from-blue-600 to-teal-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm shadow-lg shadow-blue-200 hover:shadow-blue-300 hover:-translate-y-0.5 transition-all active:scale-95"
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
