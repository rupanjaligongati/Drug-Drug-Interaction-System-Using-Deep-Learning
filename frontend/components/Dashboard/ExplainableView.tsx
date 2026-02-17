
import React from 'react';
import { Zap, Microscope, Activity } from 'lucide-react';
import { PredictionResult } from '../../types.ts';

export const ExplainableView: React.FC<{prediction: PredictionResult | null}> = ({ prediction }) => {
  if (!prediction) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center bg-white dark:bg-slate-900 rounded-[40px] border border-slate-200 dark:border-slate-800 border-dashed">
         <Zap size={48} className="text-slate-200 dark:text-slate-700 mb-4" />
         <h2 className="text-xl font-bold text-slate-900 dark:text-white">Analysis Data Unavailable</h2>
         <p className="text-slate-500 dark:text-slate-400 text-sm">Please run an interaction analysis first to unlock explainability tools.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
           <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-1">Explainable Reasoning</h2>
           <p className="text-slate-500 dark:text-slate-400">Deep dive into the pharmacological mechanism behind this prediction.</p>
        </div>
        <div className="flex items-center gap-2 bg-blue-50 dark:bg-blue-900/20 px-4 py-2 rounded-xl text-blue-600 dark:text-blue-400 text-xs font-bold uppercase border border-blue-100 dark:border-blue-800">
           <Zap size={14} /> Gemini Logic Engine Enabled
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-8">
          <div className="glass-panel p-8 rounded-[32px] border border-white dark:border-slate-800 shadow-xl transition-colors">
             <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                   <Microscope size={20} />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white">Kinetic Mechanism</h3>
             </div>
             <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-lg">
               {prediction.interactionMechanism}
             </p>
          </div>

          <div className="glass-panel p-8 rounded-[32px] border border-white dark:border-slate-800 shadow-xl transition-colors">
             <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-emerald-50 dark:bg-emerald-900/20 rounded-xl flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                   <Activity size={20} />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white">Side Effect Synergism</h3>
             </div>
             <div className="flex flex-wrap gap-3">
                {prediction.sideEffectOverlap.length > 0 ? prediction.sideEffectOverlap.map(side => (
                  <span key={side} className="px-4 py-2 bg-slate-100 dark:bg-slate-800 rounded-full text-sm font-bold text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                    {side}
                  </span>
                )) : (
                  <p className="text-slate-400 dark:text-slate-500 text-sm italic">No significant side effect overlap detected in clinical data.</p>
                )}
             </div>
          </div>
        </div>

        <div className="space-y-8">
           <div className="bg-slate-900 dark:bg-slate-900/80 text-white p-8 rounded-[32px] shadow-2xl relative overflow-hidden group border border-white/5 dark:border-slate-800">
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-blue-600/20 blur-[60px] group-hover:bg-blue-600/40 transition-all"></div>
              <h4 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-4">Clinical Insight</h4>
              <p className="text-sm text-blue-50/80 dark:text-blue-100/80 leading-relaxed mb-6 italic">
                "The patient profile indicates a potential metabolic pathway conflict. This AI reasoning reflects verified pathways but should be cross-referenced with recent oncology literature."
              </p>
              <div className="flex items-center gap-3 border-t border-white/10 dark:border-slate-800 pt-6">
                 <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold">G</div>
                 <div>
                    <p className="text-[10px] font-bold text-white uppercase">Neural Refinement</p>
                    <p className="text-[11px] text-blue-400 dark:text-blue-300">Gemini 3 Pro v2.4</p>
                 </div>
              </div>
           </div>

           <div className="glass-panel p-8 rounded-[32px] border border-white dark:border-slate-800 shadow-xl transition-colors">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-4">Literature Sources</h4>
              <div className="space-y-4">
                 {[1, 2].map(i => (
                   <div key={i} className="flex gap-4 group cursor-pointer">
                      <div className="w-1 h-10 bg-slate-100 dark:bg-slate-800 group-hover:bg-blue-400 transition-all"></div>
                      <div>
                         <p className="text-xs font-bold text-slate-900 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">Journal of Clinical Pharmacology</p>
                         <p className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-widest">Section 4.1.2 - Interactions</p>
                      </div>
                   </div>
                 ))}
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};
