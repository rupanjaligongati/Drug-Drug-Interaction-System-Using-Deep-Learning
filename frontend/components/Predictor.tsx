
import React, { useState } from 'react';
import { DRUG_SUGGESTIONS } from '../constants';

interface PredictorProps {
  onPredict: (d1: string, d2: string) => void;
  isLoading: boolean;
  error: string | null;
}

export const Predictor: React.FC<PredictorProps> = ({ onPredict, isLoading, error }) => {
  const [drug1, setDrug1] = useState('');
  const [drug2, setDrug2] = useState('');
  const [showSug1, setShowSug1] = useState(false);
  const [showSug2, setShowSug2] = useState(false);

  const handleSwap = () => {
    setDrug1(drug2);
    setDrug2(drug1);
  };

  const filteredSug1 = DRUG_SUGGESTIONS.filter(s => s.toLowerCase().includes(drug1.toLowerCase()));
  const filteredSug2 = DRUG_SUGGESTIONS.filter(s => s.toLowerCase().includes(drug2.toLowerCase()));

  return (
    <div id="predictor-module" className="max-w-2xl mx-auto px-6 py-12">
      <div className="glass-card rounded-[28px] p-8 md:p-10 relative">
        <div className="mb-8 text-center">
          <h3 className="text-2xl font-bold text-slate-800 mb-2">Check Interaction</h3>
          <p className="text-slate-500 text-sm">Enter two generic or brand drug names to analyze risk.</p>
        </div>

        <div className="space-y-6">
          <div className="relative">
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 ml-1">Drug One</label>
            <input 
              type="text"
              value={drug1}
              onChange={(e) => setDrug1(e.target.value)}
              onFocus={() => setShowSug1(true)}
              onBlur={() => setTimeout(() => setShowSug1(false), 200)}
              placeholder="e.g. Aspirin"
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-400 transition-all font-medium text-slate-700"
            />
            {showSug1 && drug1 && filteredSug1.length > 0 && (
              <div className="absolute z-20 w-full mt-2 bg-white border border-slate-100 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                {filteredSug1.map(s => (
                  <button key={s} onMouseDown={() => setDrug1(s)} className="w-full text-left px-6 py-3 hover:bg-blue-50 transition-colors text-sm text-slate-600 border-b border-slate-50 last:border-0">
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-center -my-3 relative z-10">
            <button 
              onClick={handleSwap}
              className="bg-white border border-slate-200 rounded-full p-2.5 shadow-md hover:bg-slate-50 transition-all hover:rotate-180"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400">
                <path d="m7 16-4-4 4-4M10 12h11M17 8l4 4-4 4M14 12H3" />
              </svg>
            </button>
          </div>

          <div className="relative">
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 ml-1">Drug Two</label>
            <input 
              type="text"
              value={drug2}
              onChange={(e) => setDrug2(e.target.value)}
              onFocus={() => setShowSug2(true)}
              onBlur={() => setTimeout(() => setShowSug2(false), 200)}
              placeholder="e.g. Warfarin"
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-400 transition-all font-medium text-slate-700"
            />
             {showSug2 && drug2 && filteredSug2.length > 0 && (
              <div className="absolute z-20 w-full mt-2 bg-white border border-slate-100 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                {filteredSug2.map(s => (
                  <button key={s} onMouseDown={() => setDrug2(s)} className="w-full text-left px-6 py-3 hover:bg-blue-50 transition-colors text-sm text-slate-600 border-b border-slate-50 last:border-0">
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          {error && <p className="text-red-500 text-sm text-center font-medium">{error}</p>}

          <button 
            disabled={!drug1 || !drug2 || isLoading}
            onClick={() => onPredict(drug1, drug2)}
            className={`w-full py-5 rounded-2xl font-bold text-lg transition-all flex items-center justify-center gap-3 
              ${(!drug1 || !drug2 || isLoading) 
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                : 'bg-gradient-to-r from-blue-600 to-teal-500 text-white shadow-xl shadow-blue-200 hover:shadow-2xl hover:shadow-blue-300 active:scale-95'}`}
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Analyzing Profile...
              </>
            ) : 'Analyze Interaction'}
          </button>
        </div>
      </div>
    </div>
  );
};
