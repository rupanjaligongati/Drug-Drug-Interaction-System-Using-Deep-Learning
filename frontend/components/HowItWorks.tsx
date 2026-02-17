
import React from 'react';

export const HowItWorks: React.FC = () => {
  const steps = [
    {
      title: "Data Input & Normalization",
      description: "Users enter drug names which are normalized using pharmacological standard nomenclatures. The system handles both generic names (e.g., Atorvastatin) and brand names (e.g., Lipitor).",
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      )
    },
    {
      title: "Gemini AI Neural Analysis",
      // Fix: Updated description to reflect the use of Gemini 3 Pro for advanced reasoning over clinical data.
      description: "Our core engine utilizes Gemini 3 Pro to cross-reference the query against massive clinical databases, analyzing pharmacokinetics (what the body does to the drug) and pharmacodynamics (what the drug does to the drug).",
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      )
    },
    {
      title: "Risk Categorization",
      description: "Interactions are categorized into four distinct levels: Low (Monitor), Moderate (Precaution), High (Avoid/Modify), and Contraindicated (Fatal/Severe risk). Each level triggers specific clinical guidance.",
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      )
    },
    {
      title: "Clinical Strategy Output",
      description: "The system generates structured clinical notes and management strategies, providing healthcare professionals with immediate, actionable evidence-based recommendations for patient safety.",
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    }
  ];

  return (
    <div className="max-w-5xl mx-auto px-6 py-16 animate-in fade-in duration-700">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">How DDIPS Works</h2>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Combining deep pharmacological knowledge with state-of-the-art Generative AI to provide real-time clinical safety insights.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-12">
        {steps.map((step, idx) => (
          <div key={idx} className="glass-card p-8 rounded-[32px] border border-white hover:border-blue-100 transition-all group">
            <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600 mb-6 group-hover:bg-blue-600 group-hover:text-white transition-all shadow-sm">
              {step.icon}
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-3">{step.title}</h3>
            <p className="text-slate-600 leading-relaxed text-sm md:text-base">
              {step.description}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-20 glass-card p-10 rounded-[40px] bg-gradient-to-br from-blue-600 to-teal-500 text-white border-none shadow-2xl">
        <div className="grid md:grid-cols-2 gap-10 items-center">
          <div>
            <h3 className="text-2xl font-bold mb-4 text-white">Advanced AI Architecture</h3>
            <p className="text-blue-50 leading-relaxed mb-6">
              Our system utilizes a Retrieval-Augmented Generation (RAG) style approach where the LLM acts as a reasoning engine over verified drug interaction protocols. This ensures that the generated explanations are not only fluent but clinically sound and grounded in established medical research.
            </p>
            <ul className="space-y-3">
              <li className="flex items-center gap-3 text-sm font-medium">
                <div className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>
                </div>
                Zero-latency processing pipeline
              </li>
              <li className="flex items-center gap-3 text-sm font-medium">
                <div className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>
                </div>
                End-to-end clinical verification
              </li>
            </ul>
          </div>
          <div className="hidden md:block">
            <div className="relative">
              <div className="absolute inset-0 bg-white/10 blur-3xl rounded-full"></div>
              <div className="relative bg-white/10 backdrop-blur-md rounded-3xl p-6 border border-white/20">
                <div className="space-y-4">
                  <div className="h-4 bg-white/20 rounded-full w-3/4"></div>
                  <div className="h-4 bg-white/20 rounded-full w-full"></div>
                  <div className="h-4 bg-white/20 rounded-full w-5/6"></div>
                  <div className="grid grid-cols-3 gap-3 pt-4">
                    <div className="h-12 bg-white/30 rounded-xl"></div>
                    <div className="h-12 bg-white/30 rounded-xl"></div>
                    <div className="h-12 bg-white/30 rounded-xl"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
