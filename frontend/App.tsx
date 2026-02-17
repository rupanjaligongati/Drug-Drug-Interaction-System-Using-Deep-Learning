
import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Layout/Sidebar.tsx';
import { TopBar } from './components/Layout/TopBar.tsx';
import { StickyDisclaimer } from './components/Layout/StickyDisclaimer.tsx';
import { LandingPage } from './components/Landing/LandingPage.tsx';
import { LoginPage } from './components/Auth/LoginPage.tsx';
import { AnalysisView } from './components/Dashboard/AnalysisView.tsx';
import { ExplainableView } from './components/Dashboard/ExplainableView.tsx';
import { SafetyView } from './components/Dashboard/SafetyView.tsx';
import { RecsView } from './components/Dashboard/RecsView.tsx';
import { HistoryView } from './components/Dashboard/HistoryView.tsx';
import { AnalyticsView } from './components/Dashboard/AnalyticsView.tsx';
import { AppState, PredictionResult } from './types.ts';
import { runHybridPrediction } from './services/hybridService.ts';
import { MOCK_HISTORY } from './constants.tsx';

const App: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('ddips_theme') === 'dark';
  });

  const [state, setState] = useState<AppState>({
    view: 'landing',
    currentDashboard: 'analysis',
    isAuthenticated: false,
    isLoading: false,
    currentPrediction: null,
    history: [],
    error: null,
    userName: null,
  });

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('ddips_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('ddips_theme', 'light');
    }
  }, [isDarkMode]);

  useEffect(() => {
    const auth = localStorage.getItem('ddips_auth_ent');
    const savedHistory = localStorage.getItem('ddips_history_ent');
    const savedUser = localStorage.getItem('ddips_auth_user');
    let userName: string | null = null;
    if (savedUser) {
      try {
        const parsed = JSON.parse(savedUser);
        if (parsed && typeof parsed.name === 'string') {
          userName = parsed.name;
        }
      } catch {
        userName = null;
      }
    }
    if (auth === 'true') {
      setState(s => ({ ...s, isAuthenticated: true, view: 'dashboard', userName }));
    }
    if (savedHistory) {
      setState(s => ({ ...s, history: JSON.parse(savedHistory) }));
    } else {
      setState(s => ({ ...s, history: MOCK_HISTORY as any }));
    }
  }, []);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = typeof window !== 'undefined'
          ? window.localStorage.getItem('ddips_auth_token')
          : null;
        if (!token) {
          return;
        }
        const resp = await fetch('http://localhost:8000/history/me', {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        });
        if (!resp.ok) {
          return;
        }
        const data = await resp.json();
        const mapped = (data.history || []).map((item: any) => ({
          id: String(item.id),
          drugs: [item.drug_1, item.drug_2].filter(Boolean),
          riskLevel: (item.risk_level || 'LOW').toUpperCase(),
          severity: (item.severity || 'MILD').toUpperCase(),
          explanation: item.interaction_summary || '',
          clinicalNotes: item.interaction_summary || '',
          recommendation: item.warnings || '',
          recommendations: [],
          confidenceScore: typeof item.confidence === 'number' ? item.confidence : 0.9,
          interactionMechanism: item.interaction_summary || '',
          sideEffectOverlap: [],
          monitoringGuideline: item.warnings || '',
          timestamp: new Date(item.created_at || item.timestamp || Date.now()).getTime(),
        }));
        setState(s => ({
          ...s,
          history: mapped,
        }));
      } catch {
      }
    };
    fetchHistory();
  }, []);

  const handleAuth = (success: boolean) => {
    if (success) {
      localStorage.setItem('ddips_auth_ent', 'true');
      const savedUser = localStorage.getItem('ddips_auth_user');
      let userName: string | null = null;
      if (savedUser) {
        try {
          const parsed = JSON.parse(savedUser);
          if (parsed && typeof parsed.name === 'string') {
            userName = parsed.name;
          }
        } catch {
          userName = null;
        }
      }
      setState(s => ({ ...s, isAuthenticated: true, view: 'dashboard', userName }));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('ddips_auth_ent');
    localStorage.removeItem('ddips_auth_token');
    localStorage.removeItem('ddips_auth_user');
    setState(s => ({ ...s, isAuthenticated: false, view: 'landing', userName: null }));
  };

  const handleDeleteHistory = (id: string) => {
    setState(s => ({
      ...s,
      history: s.history.filter(h => h.id !== id)
    }));
  };

  const runAnalysis = async (drugs: string[]) => {
    setState(s => ({ ...s, isLoading: true, error: null }));
    try {
      const result = await runHybridPrediction(drugs);
      setState(s => ({
        ...s,
        isLoading: false,
        currentPrediction: result,
        history: [result, ...s.history]
      }));
    } catch (err: any) {
      setState(s => ({ ...s, isLoading: false, error: err.message }));
    }
  };

  const toggleTheme = () => setIsDarkMode(!isDarkMode);

  if (state.view === 'landing') {
    return (
      <>
        <LandingPage 
          onStart={() => setState(s => ({ ...s, view: 'auth' }))} 
          isDarkMode={isDarkMode}
          onToggleTheme={toggleTheme}
        />
        <StickyDisclaimer />
      </>
    );
  }

  if (state.view === 'auth') {
    return (
      <>
        <LoginPage 
          onBack={() => setState(s => ({ ...s, view: 'landing' }))} 
          onLogin={() => handleAuth(true)} 
        />
        <StickyDisclaimer />
      </>
    );
  }

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300 overflow-hidden relative">
      <Sidebar 
        active={state.currentDashboard} 
        onSelect={(tab) => setState(s => ({ ...s, currentDashboard: tab }))} 
      />
      
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar 
          onLogout={handleLogout} 
          isDarkMode={isDarkMode} 
          onToggleTheme={toggleTheme} 
          userName={state.userName}
        />
        
        <main className="flex-1 overflow-y-auto p-6 lg:p-10 pb-24 custom-scrollbar relative">
          <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {state.currentDashboard === 'analysis' && (
              <AnalysisView 
                onAnalyze={runAnalysis} 
                loading={state.isLoading} 
                prediction={state.currentPrediction}
                onReset={() => setState(s => ({ ...s, currentPrediction: null }))}
                onViewReasoning={() => setState(s => ({ ...s, currentDashboard: 'explain' }))}
              />
            )}

            {state.currentDashboard === 'explain' && (
              <ExplainableView prediction={state.currentPrediction} />
            )}

            {state.currentDashboard === 'safety' && (
              <SafetyView prediction={state.currentPrediction} />
            )}

            {state.currentDashboard === 'recs' && (
              <RecsView prediction={state.currentPrediction} />
            )}

            {state.currentDashboard === 'history' && (
              <HistoryView 
                history={state.history} 
                onDelete={handleDeleteHistory}
              />
            )}

            {state.currentDashboard === 'analytics' && (
              <AnalyticsView history={state.history} />
            )}

            {state.currentDashboard === 'settings' && (
              <div className="p-10 bg-white dark:bg-slate-900 rounded-[32px] border border-slate-200 dark:border-slate-800 text-center transition-colors shadow-xl">
                 <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Platform Settings</h2>
                 <p className="text-slate-500 dark:text-slate-400">Global system configuration and API management tools.</p>
                 <div className="mt-8 flex justify-center items-center gap-4">
                    <span className="text-sm font-semibold text-slate-600 dark:text-slate-300">Theme Preference:</span>
                    <button 
                      onClick={toggleTheme}
                      className="px-6 py-3 bg-slate-100 dark:bg-slate-800 rounded-xl font-bold flex items-center gap-2 hover:bg-blue-50 dark:hover:bg-slate-700 transition-all border border-slate-200 dark:border-slate-700"
                    >
                      {isDarkMode ? 'Switch to Clinical Light' : 'Switch to Midnight Labs'}
                    </button>
                 </div>
              </div>
            )}

            <div className="py-12 flex flex-col items-center">
               <p className="text-[10px] text-slate-300 dark:text-slate-700 font-black uppercase tracking-[0.3em] mb-4">
                 Clinical Decision Support Node: Alpha-Beta-9
               </p>
               <div className="w-1.5 h-1.5 rounded-full bg-slate-200 dark:bg-slate-800"></div>
            </div>
          </div>
        </main>
      </div>

      <StickyDisclaimer />
    </div>
  );
};

export default App;
