
import React, { useState } from 'react';
import { ShieldCheck, ChevronLeft, Eye, EyeOff, CheckCircle2, Lock, Mail, UserPlus, LogIn, Info } from 'lucide-react';
import { registerAccount, loginAccount } from '../../services/authService.ts';
import { OTPVerification } from './OTPVerification.tsx';

interface LoginPageProps {
  onBack: () => void;
  onLogin: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onBack, onLogin }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('Dr. Sarah Johnson');
  const [email, setEmail] = useState('Sarah.Johnson@clinical.org');
  const [pass, setPass] = useState('Admin@Secure123');
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // OTP verification state
  const [showOTPVerification, setShowOTPVerification] = useState(false);
  const [pendingEmail, setPendingEmail] = useState('');

  // Password Validation Logic
  const requirements = {
    length: pass.length >= 10,
    capital: /[A-Z]/.test(pass),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(pass),
  };

  const isPasswordValid = requirements.length && requirements.capital && requirements.special;
  const canSubmit = isSignUp ? (isPasswordValid && email.includes('@') && !!name.trim()) : (email && pass);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit || loading) return;

    setError(null);
    setLoading(true);

    try {
      if (isSignUp) {
        // Registration - send OTP
        const response = await fetch('http://localhost:8000/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: name.trim(),
            email: email.trim(),
            password: pass
          })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Registration failed');
        }

        // Show OTP verification screen
        setPendingEmail(email.trim());
        setShowOTPVerification(true);
      } else {
        // Login
        const authResult = await loginAccount(email.trim(), pass);

        localStorage.setItem('ddips_auth_ent', 'true');
        localStorage.setItem('ddips_auth_token', authResult.access_token);
        localStorage.setItem('ddips_auth_user', JSON.stringify(authResult.user));

        onLogin();
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOTPVerified = (token: string, user: any) => {
    // Save auth data and login
    localStorage.setItem('ddips_auth_ent', 'true');
    localStorage.setItem('ddips_auth_token', token);
    localStorage.setItem('ddips_auth_user', JSON.stringify(user));
    onLogin();
  };

  const handleResendOTP = async () => {
    const response = await fetch('http://localhost:8000/auth/resend-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: pendingEmail })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to resend OTP');
    }
  };

  // Show OTP verification screen
  if (showOTPVerification) {
    return (
      <OTPVerification
        email={pendingEmail}
        onVerified={handleOTPVerified}
        onBack={() => {
          setShowOTPVerification(false);
          setPendingEmail('');
        }}
        onResendOTP={handleResendOTP}
      />
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden bg-slate-50 dark:bg-slate-950 transition-colors duration-500">
      {/* Background Orbs */}
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_-20%,#e0f2fe_0%,rgba(255,255,255,0)_60%)] dark:bg-[radial-gradient(circle_at_50%_-20%,#1e3a8a_0%,rgba(15,23,42,0)_60%)] opacity-50"></div>

      <button
        onClick={onBack}
        className="absolute top-10 left-10 flex items-center gap-2 text-slate-400 hover:text-slate-900 dark:hover:text-white font-bold text-sm transition-all z-20"
      >
        <ChevronLeft size={18} />
        Back to Portal
      </button>

      <div className="w-full max-w-lg relative z-10">
        <div className="text-center mb-10 animate-in fade-in slide-in-from-top-4 duration-700">
          <div className="w-16 h-16 bg-blue-600 rounded-[24px] flex items-center justify-center text-white shadow-2xl mx-auto mb-6">
            <ShieldCheck size={32} />
          </div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2 poppins">
            {isSignUp ? 'Create Clinical Account' : 'Enterprise Access'}
          </h2>
          <p className="text-slate-500 dark:text-slate-400 font-medium">
            {isSignUp
              ? 'Join the secure DDIPS network for AI-powered pharmacology.'
              : 'Verify your clinical credentials to access the dashboard.'}
          </p>
        </div>

        <div className="glass-panel p-10 rounded-[40px] border border-white dark:border-slate-800 shadow-2xl space-y-6 transition-all duration-500">

          {!isSignUp && (
            <div className="p-5 bg-blue-50/50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-3xl animate-in fade-in slide-in-from-bottom-2 duration-500">
              <div className="flex items-center gap-2 mb-3">
                <Info size={14} className="text-blue-600 dark:text-blue-400" />
                <span className="text-[10px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest">Demo Credentials</span>
              </div>
              <div className="grid grid-cols-1 gap-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500 dark:text-slate-400 font-bold">Email:</span>
                  <code className="bg-white dark:bg-slate-800 px-2 py-1 rounded-lg border border-blue-100 dark:border-blue-900 text-blue-700 dark:text-blue-300 font-bold">Sarah.Johnson@clinical.org</code>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500 dark:text-slate-400 font-bold">Password:</span>
                  <code className="bg-white dark:bg-slate-800 px-2 py-1 rounded-lg border border-blue-100 dark:border-blue-900 text-blue-700 dark:text-blue-300 font-bold">Admin@Secure123</code>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {isSignUp && (
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">Full Name</label>
                <div className="relative">
                  <Mail className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                  <input
                    required
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Dr. Jane Smith"
                    className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl pl-12 pr-6 py-4 outline-none focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30 focus:border-blue-400 transition-all font-bold text-slate-700 dark:text-slate-200"
                  />
                </div>
              </div>
            )}
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">Work Email</label>
              <div className="relative">
                <Mail className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  required
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="physician@hospital.org"
                  className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl pl-12 pr-6 py-4 outline-none focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30 focus:border-blue-400 transition-all font-bold text-slate-700 dark:text-slate-200"
                />
              </div>
            </div>

            <div className="space-y-2 relative">
              <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">Security PIN / Password</label>
              <div className="relative">
                <Lock className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  required
                  type={showPass ? "text" : "password"}
                  value={pass}
                  onChange={(e) => setPass(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl pl-12 pr-14 py-4 outline-none focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30 focus:border-blue-400 transition-all font-bold text-slate-700 dark:text-slate-200"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-6 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-blue-600 transition-colors"
                >
                  {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Password Requirements Checklist (Only shown during Sign Up) */}
            {isSignUp && (
              <div className="p-5 bg-slate-100 dark:bg-slate-900 rounded-3xl space-y-3 animate-in fade-in zoom-in-95 duration-300">
                <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">Security Requirements</p>
                <div className="grid gap-2">
                  <div className={`flex items-center gap-3 text-xs font-bold transition-colors ${requirements.length ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-600'}`}>
                    <CheckCircle2 size={14} className={requirements.length ? 'opacity-100' : 'opacity-20'} />
                    Minimum 10 Characters
                  </div>
                  <div className={`flex items-center gap-3 text-xs font-bold transition-colors ${requirements.capital ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-600'}`}>
                    <CheckCircle2 size={14} className={requirements.capital ? 'opacity-100' : 'opacity-20'} />
                    One Capital Letter (A-Z)
                  </div>
                  <div className={`flex items-center gap-3 text-xs font-bold transition-colors ${requirements.special ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-600'}`}>
                    <CheckCircle2 size={14} className={requirements.special ? 'opacity-100' : 'opacity-20'} />
                    One Special Character (@, #, !, etc.)
                  </div>
                </div>
              </div>
            )}

            {!isSignUp && (
              <div className="flex items-center justify-between py-2">
                <div className="flex items-center gap-2 text-xs font-bold text-slate-400 dark:text-slate-500 cursor-pointer">
                  <input type="checkbox" className="rounded dark:bg-slate-800 dark:border-slate-700" id="remember" />
                  <label htmlFor="remember">Remember Session</label>
                </div>
                <a href="#" className="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline">Reset Access</a>
              </div>
            )}

            <button
              type="submit"
              disabled={!canSubmit || loading}
              className={`w-full py-5 rounded-2xl font-black text-lg shadow-2xl transition-all active:scale-95 flex items-center justify-center gap-3
                  ${canSubmit && !loading
                  ? 'bg-slate-900 dark:bg-blue-600 text-white hover:bg-blue-700 shadow-blue-200 dark:shadow-blue-900/30'
                  : 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed shadow-none'}`}
            >
              {isSignUp ? (
                <>
                  <UserPlus size={20} />
                  {loading ? 'Registering...' : 'Register Account'}
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  {loading ? 'Verifying...' : 'Initialize Dashboard'}
                </>
              )}
            </button>

            {error && (
              <p className="text-xs font-bold text-red-500 text-center">
                {error}
              </p>
            )}
          </form>

          <div className="pt-6 border-t border-slate-100 dark:border-slate-800 text-center">
            <button
              onClick={() => {
                setIsSignUp(!isSignUp);
                setPass('');
                setError(null);
              }}
              className="text-sm font-bold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
            >
              {isSignUp ? 'Already have an account? Sign In' : "New to the platform? Create an account"}
            </button>
          </div>
        </div>

        <div className="mt-12 text-center flex items-center justify-center gap-6">
          <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 dark:text-slate-600 grayscale opacity-60">
            <CheckCircle2 size={12} /> SOC2 Compliant
          </div>
          <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 dark:text-slate-600 grayscale opacity-60">
            <CheckCircle2 size={12} /> HIPAA Ready
          </div>
          <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 dark:text-slate-600 grayscale opacity-60">
            <CheckCircle2 size={12} /> End-to-End Encryption
          </div>
        </div>
      </div>
    </div>
  );
};
