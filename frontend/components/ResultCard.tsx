
import React from 'react';
import { PredictionResult, RiskLevel } from '../types';

interface ResultCardProps {
  result: PredictionResult;
  onReset: () => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result, onReset }) => {
  const getRiskStyles = (level: RiskLevel) => {
    switch (level) {
      case RiskLevel.CONTRAINDICATED:
      case RiskLevel.HIGH:
        return { 
            bg: 'bg-red-50', 
            text: 'text-red-700', 
            border: 'border-red-200', 
            badge: 'bg-red-600 text-white',
            pulse: 'pulse-high-risk'
        };
      case RiskLevel.MODERATE:
        return { 
            bg: 'bg-orange-50', 
            text: 'text-orange-700', 
            border: 'border-orange-200', 
            badge: 'bg-orange-500 text-white',
            pulse: ''
        };
      case RiskLevel.LOW:
      default:
        return { 
            bg: 'bg-emerald-50', 
            text: 'text-emerald-700', 
            border: 'border-emerald-200', 
            badge: 'bg-emerald-600 text-white',
            pulse: ''
        };
    }
  };

  const styles = getRiskStyles(result.riskLevel);

  return (
    <div className="max-w-3xl mx-auto px-6 py-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
      <div className="glass-card rounded-[32px] overflow-hidden shadow-2xl border border-white">
        
        {/* Risk Header */}
        <div className={`${styles.bg} ${styles.border} border-b p-8 md:p-10 flex flex-col md:flex-row items-center justify-between gap-6`}>
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${styles.badge} ${styles.pulse}`}>
                {result.riskLevel} RISK
              </span>
              <span className="text-sm font-medium text-slate-500">Confidence: {(result.confidenceScore * 100).toFixed(0)}%</span>
            </div>
            <h3 className="text-2xl md:text-3xl font-bold text-slate-900">
              {/* Fix: Changed non-existent result.drug1 and result.drug2 to use index access from result.drugs array */}
              {result.drugs[0]} <span className="text-slate-400 mx-1">+</span> {result.drugs[1]}
            </h3>
          </div>
          <button 
            onClick={onReset}
            className="px-6 py-3 bg-white text-slate-600 rounded-xl font-bold shadow-sm hover:shadow-md transition-all active:scale-95"
          >
            New Check
          </button>
        </div>

        {/* Content Body */}
        <div className="p-8 md:p-10 space-y-10">
          
          <section>
            <h4 className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4m0-4h.01"/></svg>
              AI Assessment Explanation
            </h4>
            <p className="text-slate-700 leading-relaxed text-lg">
              {result.explanation}
            </p>
          </section>

          <div className="grid md:grid-cols-2 gap-8">
            <section className="bg-slate-50/50 rounded-2xl p-6 border border-slate-100">
               <h4 className="flex items-center gap-2 text-xs font-bold text-blue-600 uppercase tracking-widest mb-3">
                Clinical Considerations
              </h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                {result.clinicalNotes}
              </p>
            </section>

            <section className="bg-emerald-50/30 rounded-2xl p-6 border border-emerald-100">
               <h4 className="flex items-center gap-2 text-xs font-bold text-emerald-600 uppercase tracking-widest mb-3">
                Management Strategy
              </h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                {result.recommendation}
              </p>
            </section>
          </div>

          <section>
            <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-400 uppercase">Analysis Precision</span>
                <span className="text-xs font-bold text-slate-800">{(result.confidenceScore * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-teal-400 transition-all duration-1000 ease-out"
                  style={{ width: `${result.confidenceScore * 100}%` }}
                ></div>
            </div>
          </section>

          <div className="pt-4 border-t border-slate-100 text-center">
            <p className="text-[10px] text-slate-400 uppercase font-semibold">
              Warning: This is an AI-generated tool for research and assistance. Always consult with a licensed healthcare professional.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
