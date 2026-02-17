
import React from 'react';

interface HeroProps {
  onStart: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onStart }) => {
  return (
    <div className="relative overflow-hidden pt-20 pb-24 md:pt-32 md:pb-40">
      {/* Decorative blobs */}
      <div className="absolute top-0 -left-20 w-72 h-72 bg-blue-400 opacity-10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-0 -right-20 w-96 h-96 bg-teal-400 opacity-10 rounded-full blur-3xl animate-pulse delay-700"></div>

      <div className="max-w-5xl mx-auto px-6 text-center relative z-10">
        {/* Fix: Updated the model designation to Gemini 3 Pro to match the engine upgrade. */}
        <div className="inline-block px-4 py-1.5 mb-6 rounded-full bg-blue-50 border border-blue-100 text-blue-600 text-xs font-bold uppercase tracking-wider animate-bounce">
          Powered by Gemini 3 Pro
        </div>
        
        <h2 className="text-4xl md:text-6xl font-bold text-slate-900 leading-tight mb-6">
          Predict Drug Interactions <br />
          <span className="bg-gradient-to-r from-blue-600 via-blue-500 to-teal-500 bg-clip-text text-transparent">
            Instantly Using AI
          </span>
        </h2>
        
        <p className="text-lg md:text-xl text-slate-600 max-w-2xl mx-auto mb-10 leading-relaxed">
          The professional clinical platform for analyzing synergistic and antagonistic effects between medications. 
          Reduce clinical risks with evidence-based AI insights.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button 
            onClick={onStart}
            className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-2xl font-bold text-lg shadow-xl shadow-blue-200 hover:shadow-2xl hover:shadow-blue-300 hover:-translate-y-1 transition-all active:scale-95"
          >
            Start Prediction Now
          </button>
          <button className="w-full sm:w-auto px-8 py-4 bg-white text-slate-700 border border-slate-200 rounded-2xl font-bold text-lg hover:bg-slate-50 transition-all">
            View Sample Report
          </button>
        </div>

        <div className="mt-16 pt-10 border-t border-slate-200/60 flex flex-wrap justify-center gap-8 md:gap-16 opacity-60">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-800">99.9%</span>
            <span className="text-sm text-slate-500">Uptime</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-800">10k+</span>
            <span className="text-sm text-slate-500">Compounds</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-800">200ms</span>
            <span className="text-sm text-slate-500">Response</span>
          </div>
        </div>
      </div>
    </div>
  );
};
