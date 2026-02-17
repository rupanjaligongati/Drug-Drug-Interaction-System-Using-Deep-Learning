import React, { useState, useRef, useEffect } from 'react';
import { ShieldCheck, Mail, RefreshCw, CheckCircle2, AlertCircle, ArrowLeft } from 'lucide-react';

interface OTPVerificationProps {
    email: string;
    onVerified: (token: string, user: any) => void;
    onBack: () => void;
    onResendOTP: () => Promise<void>;
}

export const OTPVerification: React.FC<OTPVerificationProps> = ({
    email,
    onVerified,
    onBack,
    onResendOTP
}) => {
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);
    const [resending, setResending] = useState(false);
    const [countdown, setCountdown] = useState(0);

    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    // Countdown timer for resend
    useEffect(() => {
        if (countdown > 0) {
            const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
            return () => clearTimeout(timer);
        }
    }, [countdown]);

    const handleChange = (index: number, value: string) => {
        if (value.length > 1) {
            value = value[0];
        }

        if (!/^\d*$/.test(value)) return;

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);
        setError(null);

        // Auto-focus next input
        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }

        // Auto-submit when all fields are filled
        if (newOtp.every(digit => digit !== '') && newOtp.join('').length === 6) {
            handleVerify(newOtp.join(''));
        }
    };

    const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        }
    };

    const handlePaste = (e: React.ClipboardEvent) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text').slice(0, 6);

        if (!/^\d+$/.test(pastedData)) return;

        const newOtp = [...otp];
        for (let i = 0; i < pastedData.length && i < 6; i++) {
            newOtp[i] = pastedData[i];
        }
        setOtp(newOtp);

        // Focus last filled input
        const lastIndex = Math.min(pastedData.length, 5);
        inputRefs.current[lastIndex]?.focus();

        // Auto-submit if complete
        if (pastedData.length === 6) {
            handleVerify(pastedData);
        }
    };

    const handleVerify = async (otpCode: string) => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/auth/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: email,
                    otp: otpCode
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'OTP verification failed');
            }

            setSuccess(true);
            setTimeout(() => {
                onVerified(data.access_token, data.user);
            }, 1000);

        } catch (err: any) {
            setError(err.message || 'Verification failed. Please try again.');
            setOtp(['', '', '', '', '', '']);
            inputRefs.current[0]?.focus();
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        if (countdown > 0 || resending) return;

        setResending(true);
        setError(null);

        try {
            await onResendOTP();
            setCountdown(60); // 60 second cooldown
            setOtp(['', '', '', '', '', '']);
            inputRefs.current[0]?.focus();
        } catch (err: any) {
            setError(err.message || 'Failed to resend OTP');
        } finally {
            setResending(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const otpCode = otp.join('');
        if (otpCode.length === 6) {
            handleVerify(otpCode);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden bg-slate-50 dark:bg-slate-950 transition-colors duration-500">
            {/* Background Orbs */}
            <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_-20%,#e0f2fe_0%,rgba(255,255,255,0)_60%)] dark:bg-[radial-gradient(circle_at_50%_-20%,#1e3a8a_0%,rgba(15,23,42,0)_60%)] opacity-50"></div>

            <button
                onClick={onBack}
                className="absolute top-10 left-10 flex items-center gap-2 text-slate-400 hover:text-slate-900 dark:hover:text-white font-bold text-sm transition-all z-20"
            >
                <ArrowLeft size={18} />
                Back to Registration
            </button>

            <div className="w-full max-w-lg relative z-10">
                <div className="text-center mb-10 animate-in fade-in slide-in-from-top-4 duration-700">
                    <div className={`w-16 h-16 ${success ? 'bg-emerald-600' : 'bg-blue-600'} rounded-[24px] flex items-center justify-center text-white shadow-2xl mx-auto mb-6 transition-all duration-500`}>
                        {success ? <CheckCircle2 size={32} /> : <ShieldCheck size={32} />}
                    </div>
                    <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2 poppins">
                        {success ? 'Verification Successful!' : 'Verify Your Email'}
                    </h2>
                    <p className="text-slate-500 dark:text-slate-400 font-medium">
                        {success
                            ? 'Your account has been created successfully.'
                            : `We've sent a 6-digit code to`}
                    </p>
                    {!success && (
                        <p className="text-blue-600 dark:text-blue-400 font-bold mt-1">{email}</p>
                    )}
                </div>

                <div className="glass-panel p-10 rounded-[40px] border border-white dark:border-slate-800 shadow-2xl space-y-6 transition-all duration-500">

                    {!success && (
                        <div className="p-5 bg-blue-50/50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-3xl">
                            <div className="flex items-center gap-2 mb-2">
                                <Mail size={14} className="text-blue-600 dark:text-blue-400" />
                                <span className="text-[10px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest">Check Your Inbox</span>
                            </div>
                            <p className="text-xs text-slate-600 dark:text-slate-400 font-medium">
                                Enter the 6-digit code we sent to your email. The code expires in 10 minutes.
                            </p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-4">
                            <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">
                                Verification Code
                            </label>

                            <div className="flex gap-3 justify-center">
                                {otp.map((digit, index) => (
                                    <input
                                        key={index}
                                        ref={(el) => (inputRefs.current[index] = el)}
                                        type="text"
                                        inputMode="numeric"
                                        maxLength={1}
                                        value={digit}
                                        onChange={(e) => handleChange(index, e.target.value)}
                                        onKeyDown={(e) => handleKeyDown(index, e)}
                                        onPaste={index === 0 ? handlePaste : undefined}
                                        disabled={loading || success}
                                        className={`w-14 h-16 text-center text-2xl font-bold rounded-2xl border-2 outline-none transition-all
                      ${success
                                                ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-400 dark:border-emerald-600 text-emerald-600 dark:text-emerald-400'
                                                : digit
                                                    ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-400 dark:border-blue-600 text-blue-600 dark:text-blue-400'
                                                    : 'bg-slate-50 dark:bg-slate-900/50 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200'
                                            }
                      ${!loading && !success && 'focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30 focus:border-blue-400'}
                      ${loading && 'opacity-50 cursor-not-allowed'}
                    `}
                                    />
                                ))}
                            </div>
                        </div>

                        {error && (
                            <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl flex items-center gap-3">
                                <AlertCircle size={18} className="text-red-600 dark:text-red-400 flex-shrink-0" />
                                <p className="text-sm font-bold text-red-600 dark:text-red-400">{error}</p>
                            </div>
                        )}

                        {success && (
                            <div className="p-4 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-2xl flex items-center gap-3">
                                <CheckCircle2 size={18} className="text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
                                <p className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                                    Account created! Redirecting to dashboard...
                                </p>
                            </div>
                        )}

                        {!success && (
                            <button
                                type="submit"
                                disabled={otp.join('').length !== 6 || loading}
                                className={`w-full py-5 rounded-2xl font-black text-lg shadow-2xl transition-all active:scale-95 flex items-center justify-center gap-3
                  ${otp.join('').length === 6 && !loading
                                        ? 'bg-slate-900 dark:bg-blue-600 text-white hover:bg-blue-700 shadow-blue-200 dark:shadow-blue-900/30'
                                        : 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed shadow-none'}`}
                            >
                                <ShieldCheck size={20} />
                                {loading ? 'Verifying...' : 'Verify & Create Account'}
                            </button>
                        )}
                    </form>

                    {!success && (
                        <div className="pt-6 border-t border-slate-100 dark:border-slate-800 text-center space-y-3">
                            <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
                                Didn't receive the code?
                            </p>
                            <button
                                onClick={handleResend}
                                disabled={countdown > 0 || resending}
                                className={`inline-flex items-center gap-2 text-sm font-bold transition-all
                  ${countdown > 0 || resending
                                        ? 'text-slate-400 dark:text-slate-600 cursor-not-allowed'
                                        : 'text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300'
                                    }`}
                            >
                                <RefreshCw size={16} className={resending ? 'animate-spin' : ''} />
                                {countdown > 0
                                    ? `Resend in ${countdown}s`
                                    : resending
                                        ? 'Sending...'
                                        : 'Resend Code'
                                }
                            </button>
                        </div>
                    )}
                </div>

                <div className="mt-12 text-center flex items-center justify-center gap-6">
                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 dark:text-slate-600 grayscale opacity-60">
                        <CheckCircle2 size={12} /> Secure Verification
                    </div>
                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 dark:text-slate-600 grayscale opacity-60">
                        <CheckCircle2 size={12} /> 10-Minute Validity
                    </div>
                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 dark:text-slate-600 grayscale opacity-60">
                        <CheckCircle2 size={12} /> Email Protected
                    </div>
                </div>
            </div>
        </div>
    );
};
