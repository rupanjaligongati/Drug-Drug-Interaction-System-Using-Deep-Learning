
import React, { useState } from 'react';
// Fix: Import ShieldCheck from lucide-react instead of non-existent UI_ICONS
import { ShieldCheck } from 'lucide-react';

interface LoginPageProps {
  onLogin: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  // Pre-filling with default demo credentials
  const [email, setEmail] = useState('demo@ddips.ai');
  const [password, setPassword] = useState('Admin@12345');

  const hasMinLength = password.length >= 10;
  const hasCapital = /[A-Z]/.test(password);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  const isValid = !isSignUp || (hasMinLength && hasCapital && hasSpecial);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isValid) {
      onLogin();
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-6 py-12">
      <div className="absolute top-20 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-400 opacity-10 rounded-full blur-[100px] pointer-events-none"></div>
      
      <div className="glass-card w-full max-w-md rounded-[32px] p-8 md:p-10 relative z-10 border border-white/50 shadow-2xl">
        <div className="text-center mb-10">
          <div className="flex justify-center mb-4 text-blue-600">
            {/* Fix: Replaced UI_ICONS.Logo with ShieldCheck for visual consistency */}
            <ShieldCheck size={40} />
          </div>
          <h2 className="text-3xl font-bold text-slate-900 mb-2">
            {isSignUp ? 'Create Account' : 'Welcome Back'}
          </h2>
          <p className="text-slate-500 text-sm">
            {isSignUp 
              ? 'Join the DDIPS network for clinical insights' 
              : 'Sign in to access your dashboard'}
          </p>
        </div>

        <div className="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-2xl">
          <p className="text-[10px] font-bold text-blue-600 uppercase tracking-widest mb-1">Demo Credentials</p>
          <div className="flex flex-col gap-1">
            <p className="text-xs text-slate-600"><span className="font-bold">Email:</span> demo@ddips.ai</p>
            <p className="text-xs text-slate-600"><span className="font-bold">Pass:</span> Admin@12345</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Email Address</label>
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@hospital.org"
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-400 transition-all font-medium text-slate-700"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Password</label>
            <input 
              type="password" 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-400 transition-all font-medium text-slate-700"
            />
          </div>

          {isSignUp && (
            <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100 space-y-3">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Security Requirements</p>
              <ul className="space-y-2">
                <li className={`flex items-center gap-2 text-xs font-medium transition-colors ${hasMinLength ? 'text-emerald-600' : 'text-slate-400'}`}>
                  <div className={`w-4 h-4 rounded-full flex items-center justify-center border ${hasMinLength ? 'bg-emerald-100 border-emerald-200' : 'border-slate-300'}`}>
                    {hasMinLength && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4"><path d="M20 6L9 17l-5-5"/></svg>}
                  </div>
                  At least 10 characters
                </li>
                <li className={`flex items-center gap-2 text-xs font-medium transition-colors ${hasCapital ? 'text-emerald-600' : 'text-slate-400'}`}>
                  <div className={`w-4 h-4 rounded-full flex items-center justify-center border ${hasCapital ? 'bg-emerald-100 border-emerald-200' : 'border-slate-300'}`}>
                    {hasCapital && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4"><path d="M20 6L9 17l-5-5"/></svg>}
                  </div>
                  Includes Capital Letter
                </li>
                <li className={`flex items-center gap-2 text-xs font-medium transition-colors ${hasSpecial ? 'text-emerald-600' : 'text-slate-400'}`}>
                  <div className={`w-4 h-4 rounded-full flex items-center justify-center border ${hasSpecial ? 'bg-emerald-100 border-emerald-200' : 'border-slate-300'}`}>
                    {hasSpecial && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4"><path d="M20 6L9 17l-5-5"/></svg>}
                  </div>
                  Includes Special Character (@, #, !, etc.)
                </li>
              </ul>
            </div>
          )}

          <button 
            type="submit"
            disabled={!isValid || !email || !password}
            className={`w-full py-4 rounded-2xl font-bold text-lg transition-all shadow-xl active:scale-95 
              ${(!isValid || !email || !password) 
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed shadow-none' 
                : 'bg-gradient-to-r from-blue-600 to-teal-500 text-white shadow-blue-200 hover:shadow-blue-300'}`}
          >
            {isSignUp ? 'Create Account' : 'Sign In'}
          </button>
        </form>

        <div className="mt-8 text-center">
          <button 
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors"
          >
            {isSignUp ? 'Already have an account? Sign In' : "Don't have an account? Create one"}
          </button>
        </div>
      </div>
    </div>
  );
};
