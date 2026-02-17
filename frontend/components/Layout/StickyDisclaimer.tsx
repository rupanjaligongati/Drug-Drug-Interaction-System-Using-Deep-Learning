
import React, { useState } from 'react';
import { ShieldAlert, ChevronUp, ChevronDown, ExternalLink, Scale } from 'lucide-react';

export const StickyDisclaimer: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`fixed bottom-0 left-0 right-0 z-[200] transition-all duration-500 ease-in-out border-t border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-950/90 backdrop-blur-xl shadow-[0_-10px_30px_rgba(0,0,0,0.05)] dark:shadow-[0_-10px_30px_rgba(0,0,0,0.3)] ${isExpanded ? 'h-auto py-8' : 'h-10 py-0'}`}>
      <div className="max-w-7xl mx-auto px-6 h-full flex flex-col justify-center">
        <div className="flex items-center justify-between gap-4 h-full">
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 transition-colors ${isExpanded ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 dark:text-slate-500'}`}>
              <ShieldAlert size={isExpanded ? 18 : 14} />
              <span className="text-[10px] font-black uppercase tracking-[0.2em] whitespace-nowrap">Clinical Ethics & Safety Protocol</span>
            </div>
            {!isExpanded && (
              <p className="text-[9px] text-slate-400 dark:text-slate-600 font-medium truncate hidden md:block max-w-xl">
                DDIPS is a decision support tool. It does not replace clinical judgment or official pharmaceutical manuals.
              </p>
            )}
          </div>

          <div className="flex items-center gap-4">
            {!isExpanded && (
              <div className="hidden sm:flex gap-4 text-[9px] font-bold text-slate-300 dark:text-slate-700 uppercase tracking-widest border-r border-slate-100 dark:border-slate-800 pr-4">
                <span>V3.4 PRO</span>
                <span>HIPAA READY</span>
                <span>SOC2 TYPE II</span>
              </div>
            )}
            <button 
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-2 text-[10px] font-bold text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-300 transition-colors uppercase tracking-widest px-2 py-1 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-900"
            >
              {isExpanded ? (
                <>Minimize <ChevronDown size={14} /></>
              ) : (
                <>View Disclaimer <ChevronUp size={14} /></>
              )}
            </button>
          </div>
        </div>

        {isExpanded && (
          <div className="mt-6 grid md:grid-cols-3 gap-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-sm">
                <Scale size={16} className="text-blue-600" />
                Legal Framework
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                This platform is provided for research and professional decision support. By using this service, you acknowledge that all AI-generated predictions are probabilistic and must be verified against current medical literature and local clinical protocols.
              </p>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-sm">
                <ShieldAlert size={16} className="text-emerald-600" />
                Clinical Sovereignty
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                The attending physician maintains full clinical sovereignty over patient care. DDIPS recommendations are supplementary and do not constitute a prescription or medical order. Always consult official pharmaceutical compendiums for final confirmation.
              </p>
            </div>
            <div className="space-y-4">
               <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-2">Ethics Resources</p>
                  <div className="flex flex-col gap-2">
                    <a href="#" className="text-xs font-bold text-blue-600 dark:text-blue-400 flex items-center justify-between group hover:underline">
                      AI Transparency Report <ExternalLink size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                    <a href="#" className="text-xs font-bold text-blue-600 dark:text-blue-400 flex items-center justify-between group hover:underline">
                      Bias Mitigation Protocol <ExternalLink size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                    <a href="#" className="text-xs font-bold text-blue-600 dark:text-blue-400 flex items-center justify-between group hover:underline">
                      Enterprise SLA & Privacy <ExternalLink size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                    </a>
                  </div>
               </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
