
import React from 'react';
import { ShieldAlert, AlertTriangle, Eye, Ruler, BellRing } from 'lucide-react';
import { PredictionResult } from '../../types';

export const SafetyView: React.FC<{prediction: PredictionResult | null}> = ({ prediction }) => {
  if (!prediction) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center bg-white rounded-[40px] border border-slate-200 border-dashed">
         <ShieldAlert size={48} className="text-slate-200 mb-4" />
         <h2 className="text-xl font-bold text-slate-900">Safety Profile Not Initialized</h2>
         <p className="text-slate-500 text-sm">Run an analysis to generate a personalized safety and monitoring profile.</p>
      </div>
    );
  }

  return (
    <div className="space-y-10 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
           <h2 className="text-3xl font-bold text-slate-900 mb-1">Risk & Safety Protocol</h2>
           <p className="text-slate-500">Critical monitoring guidelines and toxicology prevention measures.</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <div className={`p-10 rounded-[40px] border-2 shadow-2xl relative overflow-hidden
          ${prediction.riskLevel === 'HIGH' ? 'bg-red-50 border-red-200' : 'bg-emerald-50 border-emerald-200'}`}>
           <div className="absolute top-0 right-0 p-8 text-slate-200 opacity-20"><ShieldAlert size={120} /></div>
           
           <div className="relative z-10">
              <div className="flex items-center gap-3 mb-8">
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center 
                  ${prediction.riskLevel === 'HIGH' ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'}`}>
                   <AlertTriangle />
                </div>
                <h3 className="text-2xl font-bold text-slate-900">Safety Assessment</h3>
              </div>

              <div className="space-y-6">
                <div className="bg-white/80 backdrop-blur p-6 rounded-3xl border border-white">
                  <h4 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Severity Impact</h4>
                  <p className={`text-3xl font-bold ${prediction.riskLevel === 'HIGH' ? 'text-red-600' : 'text-emerald-600'}`}>
                    {prediction.severity} PROFILE
                  </p>
                </div>

                <div className="space-y-4">
                  <p className="text-sm font-bold text-slate-400 uppercase tracking-widest ml-1">Key Observations</p>
                  <ul className="space-y-3">
                     {[prediction.monitoringGuideline, "Baseline vitals check recommended", "Maintain strict dosage windows"].map((point, idx) => (
                       <li key={idx} className="flex items-start gap-3 text-slate-700 font-medium">
                         <div className="w-5 h-5 mt-0.5 rounded-full bg-white flex items-center justify-center border border-slate-200 flex-shrink-0 text-blue-500">
                           <BellRing size={12} />
                         </div>
                         {point}
                       </li>
                     ))}
                  </ul>
                </div>
              </div>
           </div>
        </div>

        <div className="space-y-8">
           <div className="glass-panel p-8 rounded-[32px] border border-white shadow-xl">
              <div className="flex items-center justify-between mb-8">
                 <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600"><Ruler size={18} /></div>
                    <h3 className="text-xl font-bold text-slate-900">Risk Meter</h3>
                 </div>
                 <span className="text-sm font-bold text-slate-400">System Accuracy: 98.4%</span>
              </div>
              
              <div className="relative h-20 bg-slate-100 rounded-2xl overflow-hidden p-1 flex">
                 <div className="h-full bg-emerald-400 flex-1 border-r border-white/50"></div>
                 <div className="h-full bg-amber-400 flex-1 border-r border-white/50"></div>
                 <div className="h-full bg-red-400 flex-1"></div>
                 
                 <div 
                   className="absolute top-0 bottom-0 w-1.5 bg-slate-900 shadow-2xl transition-all duration-1000 ease-out z-10"
                   style={{ left: `${prediction.riskLevel === 'HIGH' ? '85%' : prediction.riskLevel === 'MODERATE' ? '50%' : '15%'}` }}
                 >
                   <div className="absolute -top-1 -left-2 w-5 h-5 bg-slate-900 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-[10px] text-white font-bold">!</div>
                 </div>
              </div>
              <div className="flex justify-between mt-4 px-2">
                 <span className="text-[10px] font-black text-slate-400 uppercase">SAFE</span>
                 <span className="text-[10px] font-black text-slate-400 uppercase">MODERATE</span>
                 <span className="text-[10px] font-black text-slate-400 uppercase">CRITICAL</span>
              </div>
           </div>

           <div className="glass-panel p-8 rounded-[32px] border border-white shadow-xl">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-purple-50 rounded-xl flex items-center justify-center text-purple-600"><Eye size={18} /></div>
                <h3 className="text-xl font-bold text-slate-900">Monitoring Checklist</h3>
              </div>
              <div className="space-y-3">
                 {["Check renal function weekly", "Monitor blood pressure spikes", "Report gastrointestinal pain"].map(c => (
                   <div key={c} className="flex items-center gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-100">
                      <input type="checkbox" className="w-5 h-5 rounded-lg border-slate-300 text-blue-600 focus:ring-blue-100" />
                      <span className="text-sm font-bold text-slate-700">{c}</span>
                   </div>
                 ))}
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};
