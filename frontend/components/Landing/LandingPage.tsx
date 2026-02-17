
import React, { useState, useMemo } from 'react';
import { ShieldCheck, ArrowRight, BrainCircuit, Activity, LineChart, Stethoscope, Moon, Sun, Calendar as CalendarIcon, Mail, User, X, CheckCircle, PlayCircle, Loader2, ChevronLeft, ChevronRight, Globe, Lock } from 'lucide-react';

interface LandingPageProps {
  onStart: () => void;
  isDarkMode: boolean;
  onToggleTheme: () => void;
}

// Custom Calendar Picker Component
const CustomCalendarPicker: React.FC<{ 
  selectedDate: string; 
  onSelect: (date: string) => void;
  minDate: string;
}> = ({ selectedDate, onSelect, minDate }) => {
  const [viewDate, setViewDate] = useState(new Date(selectedDate || new Date()));
  const [isYearPickerOpen, setIsYearPickerOpen] = useState(false);

  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const currentMonth = viewDate.getMonth();
  const currentYear = viewDate.getFullYear();

  const daysInMonth = useMemo(() => {
    const days = [];
    const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay();
    const lastDateOfMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    const prevMonthLastDate = new Date(currentYear, currentMonth, 0).getDate();
    for (let i = firstDayOfMonth - 1; i >= 0; i--) {
      days.push({ day: prevMonthLastDate - i, month: currentMonth - 1, year: currentYear, current: false });
    }

    for (let i = 1; i <= lastDateOfMonth; i++) {
      days.push({ day: i, month: currentMonth, year: currentYear, current: true });
    }

    const totalCells = 42; 
    const nextDaysNeeded = totalCells - days.length;
    for (let i = 1; i <= nextDaysNeeded; i++) {
      days.push({ day: i, month: currentMonth + 1, year: currentYear, current: false });
    }

    return days;
  }, [currentMonth, currentYear]);

  const changeMonth = (offset: number) => {
    setViewDate(new Date(currentYear, currentMonth + offset, 1));
  };

  const handleDateClick = (d: { day: number, month: number, year: number }) => {
    const date = new Date(d.year, d.month, d.day);
    const dateStr = date.toISOString().split('T')[0];
    if (dateStr >= minDate) {
      onSelect(dateStr);
    }
  };

  const years = Array.from({ length: 12 }, (_, i) => currentYear - 5 + i);

  return (
    <div className="bg-white/50 dark:bg-slate-900/50 backdrop-blur-md border border-slate-200/60 dark:border-slate-800/60 rounded-[28px] p-6 shadow-xl animate-in fade-in zoom-in-95 duration-300">
      <div className="flex items-center justify-between mb-6">
        <button 
          type="button"
          onClick={() => setIsYearPickerOpen(!isYearPickerOpen)}
          className="text-sm font-bold text-slate-900 dark:text-white hover:bg-slate-100 dark:hover:bg-slate-800/80 px-3 py-1.5 rounded-xl transition-all flex items-center gap-2 group"
        >
          <span className="group-hover:text-blue-600 transition-colors">{months[currentMonth]} {currentYear}</span>
          <ChevronRight size={14} className={`text-slate-400 transition-transform ${isYearPickerOpen ? 'rotate-90' : ''}`} />
        </button>
        <div className="flex gap-2">
          <button type="button" onClick={() => changeMonth(-1)} className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800/80 rounded-xl text-slate-500 hover:text-blue-600 transition-all border border-transparent hover:border-slate-200 dark:hover:border-slate-700">
            <ChevronLeft size={18} />
          </button>
          <button type="button" onClick={() => changeMonth(1)} className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800/80 rounded-xl text-slate-500 hover:text-blue-600 transition-all border border-transparent hover:border-slate-200 dark:hover:border-slate-700">
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      {isYearPickerOpen ? (
        <div className="grid grid-cols-3 gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
          {years.map(y => (
            <button
              key={y}
              type="button"
              onClick={() => {
                setViewDate(new Date(y, currentMonth, 1));
                setIsYearPickerOpen(false);
              }}
              className={`py-3 rounded-2xl text-xs font-bold transition-all border ${y === currentYear ? 'bg-blue-600 text-white border-blue-500 shadow-lg shadow-blue-500/20' : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 border-transparent hover:border-slate-200 dark:hover:border-slate-700'}`}
            >
              {y}
            </button>
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-7 mb-3">
            {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(d => (
              <div key={d} className="text-[10px] font-black text-slate-400 dark:text-slate-600 text-center uppercase tracking-[0.2em]">{d}</div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1.5">
            {daysInMonth.map((d, i) => {
              const dateObj = new Date(d.year, d.month, d.day);
              const dateStr = dateObj.toISOString().split('T')[0];
              const isSelected = selectedDate === dateStr;
              const isToday = new Date().toISOString().split('T')[0] === dateStr;
              const isPast = dateStr < minDate;

              return (
                <button
                  key={i}
                  type="button"
                  disabled={isPast}
                  onClick={() => handleDateClick(d)}
                  className={`
                    relative h-10 w-full rounded-xl text-xs font-bold transition-all flex items-center justify-center border
                    ${!d.current ? 'opacity-30 text-slate-400' : 'text-slate-700 dark:text-slate-300'}
                    ${isSelected 
                      ? 'bg-blue-600 text-white border-blue-500 shadow-xl shadow-blue-500/30 scale-105 z-10' 
                      : 'hover:bg-blue-50 dark:hover:bg-blue-900/20 border-transparent hover:border-blue-200 dark:hover:border-blue-800/50'}
                    ${isPast ? 'cursor-not-allowed opacity-10 bg-slate-50 dark:bg-slate-900/20' : ''}
                  `}
                >
                  {d.day}
                  {isToday && !isSelected && (
                    <div className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-blue-500 rounded-full ring-2 ring-white dark:ring-slate-900"></div>
                  )}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export const LandingPage: React.FC<LandingPageProps> = ({ onStart, isDarkMode, onToggleTheme }) => {
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);
  const [demoStep, setDemoStep] = useState<'form' | 'loading' | 'success'>('form');
  const [formData, setFormData] = useState({ name: '', email: '', date: '' });
  const [showCalendar, setShowCalendar] = useState(false);

  const handleDemoSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.date) return;
    setDemoStep('loading');
    setTimeout(() => {
      setDemoStep('success');
    }, 2400);
  };

  const closeModal = () => {
    setIsDemoModalOpen(false);
    setTimeout(() => {
      setDemoStep('form');
      setFormData({ name: '', email: '', date: '' });
      setShowCalendar(false);
    }, 300);
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 transition-colors duration-300 selection:bg-blue-100 selection:text-blue-900 dark:selection:bg-blue-900 dark:selection:text-blue-100 pb-20">
      {/* Header */}
      <nav className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg">
            <ShieldCheck size={22} />
          </div>
          <span className="text-xl font-bold text-slate-900 dark:text-white poppins">DDIPS</span>
        </div>
        <div className="flex items-center gap-6">
          <button 
            onClick={onToggleTheme}
            className="p-2 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
          >
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <button onClick={onStart} className="font-bold text-slate-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Sign In</button>
          <button 
            onClick={onStart} 
            className="bg-slate-900 dark:bg-blue-600 text-white px-6 py-3 rounded-2xl font-bold hover:bg-blue-700 dark:hover:bg-blue-500 transition-all shadow-xl shadow-slate-200 dark:shadow-blue-900/20"
          >
            Start Analysis
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 pt-20 pb-40 text-center relative overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-50 dark:bg-blue-900 opacity-50 dark:opacity-10 blur-[120px] rounded-full pointer-events-none -z-10"></div>
        
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full text-xs font-bold uppercase tracking-wider mb-8 animate-bounce">
          <BrainCircuit size={14} />
          Next-Gen Pharmacology Engine
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold text-slate-900 dark:text-white poppins leading-[1.1] mb-8">
          Clinical Intelligence for <br />
          <span className="bg-gradient-to-r from-blue-600 to-teal-500 bg-clip-text text-transparent">Drug Interactions</span>
        </h1>
        
        <p className="text-lg md:text-xl text-slate-500 dark:text-slate-400 max-w-3xl mx-auto mb-12 leading-relaxed">
          The ultimate polypharmacy analysis platform powered by proprietary Gemini AI reasoning. 
          Analyze complex patient profiles, mitigate toxic risks, and optimize medication safety instantly.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button 
            onClick={onStart}
            className="w-full sm:w-auto px-10 py-5 bg-blue-600 text-white rounded-2xl font-bold text-lg shadow-2xl shadow-blue-200 dark:shadow-blue-900/40 hover:shadow-blue-300 dark:hover:shadow-blue-500 hover:-translate-y-1 transition-all flex items-center justify-center gap-3 group"
          >
            Deploy Dashboard
            <ArrowRight className="group-hover:translate-x-1 transition-transform" />
          </button>
          <button 
            onClick={() => setIsDemoModalOpen(true)}
            className="w-full sm:w-auto px-10 py-5 bg-white dark:bg-slate-900 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-800 rounded-2xl font-bold text-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-all shadow-sm"
          >
            Schedule Demo
          </button>
        </div>

        <div className="mt-32 grid md:grid-cols-3 gap-12 text-left">
          <div className="space-y-4">
            <div className="w-12 h-12 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-2xl flex items-center justify-center transition-colors">
              <Activity />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Explainable AI</h3>
            <p className="text-slate-500 dark:text-slate-400">Beyond risk levels—understand the pharmacokinetic mechanisms driving every predicted interaction.</p>
          </div>
          <div className="space-y-4">
            <div className="w-12 h-12 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 rounded-2xl flex items-center justify-center transition-colors">
              <Stethoscope />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Clinical Protocol</h3>
            <p className="text-slate-500 dark:text-slate-400">Verified against FDA and global medical standards to ensure professional grade accuracy in every report.</p>
          </div>
          <div className="space-y-4">
            <div className="w-12 h-12 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded-2xl flex items-center justify-center transition-colors">
              <LineChart />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Health Analytics</h3>
            <p className="text-slate-500 dark:text-slate-400">Monitor population health trends and identify high-risk medication patterns across your network.</p>
          </div>
        </div>
      </section>

      {/* Demo Modal */}
      {isDemoModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 animate-in fade-in duration-500">
          <div 
            className="absolute inset-0 bg-slate-900/70 backdrop-blur-xl"
            onClick={closeModal}
          ></div>
          
          <div className="glass-panel w-full max-w-xl rounded-[40px] overflow-hidden relative z-10 animate-in zoom-in-95 slide-in-from-bottom-4 duration-500 shadow-[0_48px_80px_-16px_rgba(0,0,0,0.4)] border border-white/20 dark:border-slate-800 transition-all">
            {demoStep === 'form' && (
              <div className="p-12">
                <div className="flex justify-between items-start mb-10">
                  <div>
                    <h3 className="text-3xl font-bold text-slate-900 dark:text-white poppins tracking-tight">Schedule a Live Demo</h3>
                    <p className="text-slate-500 dark:text-slate-400 text-sm mt-2 font-medium">Experience the DDIPS enterprise engine in a 1-on-1 walkthrough.</p>
                  </div>
                  <button onClick={closeModal} className="p-2.5 bg-slate-100 dark:bg-slate-800 text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-full transition-all hover:rotate-90">
                    <X size={20} />
                  </button>
                </div>

                <form onSubmit={handleDemoSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Full Name</label>
                      <div className="relative group">
                        <User className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors z-10" size={18} />
                        <input 
                          required
                          type="text"
                          placeholder="Dr. John Doe"
                          value={formData.name}
                          onChange={(e) => setFormData({...formData, name: e.target.value})}
                          className="w-full bg-slate-50/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl pl-12 pr-6 py-4 outline-none focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30 focus:border-blue-400 transition-all font-semibold text-slate-700 dark:text-slate-200 placeholder:text-slate-400"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Work Email</label>
                      <div className="relative group">
                        <Mail className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors z-10" size={18} />
                        <input 
                          required
                          type="email"
                          placeholder="john.doe@hospital.org"
                          value={formData.email}
                          onChange={(e) => setFormData({...formData, email: e.target.value})}
                          className="w-full bg-slate-50/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl pl-12 pr-6 py-4 outline-none focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30 focus:border-blue-400 transition-all font-semibold text-slate-700 dark:text-slate-200 placeholder:text-slate-400"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Deployment Date</label>
                    <div className="relative">
                      <button
                        type="button"
                        onClick={() => setShowCalendar(!showCalendar)}
                        className={`w-full bg-slate-50/50 dark:bg-slate-900/50 border transition-all text-left flex items-center justify-between group rounded-2xl pl-12 pr-6 py-4 
                          ${showCalendar ? 'border-blue-400 ring-4 ring-blue-100 dark:ring-blue-900/30 shadow-lg shadow-blue-500/10' : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'}`}
                      >
                        <CalendarIcon className={`absolute left-5 top-1/2 -translate-y-1/2 transition-colors ${showCalendar ? 'text-blue-500' : 'text-slate-400'}`} size={18} />
                        <span className={`font-semibold ${formData.date ? 'text-slate-800 dark:text-slate-100' : 'text-slate-400'}`}>
                          {formData.date ? new Date(formData.date).toLocaleDateString('en-US', { dateStyle: 'long' }) : 'Choose your preferred slot'}
                        </span>
                        <ChevronRight size={16} className={`text-slate-300 transition-transform ${showCalendar ? 'rotate-90 text-blue-500' : ''}`} />
                      </button>

                      {showCalendar && (
                        <div className="mt-4">
                          <CustomCalendarPicker 
                            minDate={today}
                            selectedDate={formData.date}
                            onSelect={(date) => {
                              setFormData({ ...formData, date });
                              setShowCalendar(false);
                            }}
                          />
                        </div>
                      )}
                    </div>
                  </div>

                  <button 
                    type="submit"
                    disabled={!formData.date || !formData.name || !formData.email}
                    className={`w-full py-5 rounded-[20px] font-black text-lg shadow-2xl transition-all flex items-center justify-center gap-3 mt-6 active:scale-[0.98]
                      ${(!formData.date || !formData.name || !formData.email) 
                        ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed' 
                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-1'}`}
                  >
                    Lock In Demo Slot <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                  </button>
                </form>

                <div className="mt-8 flex items-center justify-center gap-6 pt-8 border-t border-slate-100 dark:border-slate-800/50">
                  <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest grayscale opacity-60">
                    <Globe size={12} /> Global Support
                  </div>
                  <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest grayscale opacity-60">
                    <Lock size={12} /> Privacy First
                  </div>
                </div>
              </div>
            )}

            {demoStep === 'loading' && (
              <div className="p-24 text-center flex flex-col items-center gap-8 bg-white dark:bg-slate-950">
                <div className="relative">
                   <div className="w-24 h-24 border-4 border-blue-500/10 rounded-full animate-ping absolute inset-0"></div>
                   <div className="w-24 h-24 border-t-4 border-blue-600 rounded-full animate-spin relative flex items-center justify-center">
                      <BrainCircuit size={32} className="text-blue-600 animate-pulse" />
                   </div>
                </div>
                <div className="space-y-3">
                  <h3 className="text-2xl font-bold text-slate-900 dark:text-white poppins">Provisioning Environment</h3>
                  <p className="text-slate-500 dark:text-slate-400 font-medium max-w-xs mx-auto">Allocating clinical demo resources and syncing scheduling protocols...</p>
                </div>
              </div>
            )}

            {demoStep === 'success' && (
              <div className="p-14 text-center bg-white dark:bg-slate-950">
                <div className="w-24 h-24 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 rounded-[32px] flex items-center justify-center mx-auto mb-10 shadow-xl shadow-emerald-500/10 border border-emerald-100 dark:border-emerald-800/50 animate-in zoom-in-50 duration-500">
                  <CheckCircle size={48} strokeWidth={2.5} />
                </div>
                <h3 className="text-3xl font-bold text-slate-900 dark:text-white mb-4 poppins tracking-tight">Deployment Successful!</h3>
                <p className="text-slate-500 dark:text-slate-400 leading-relaxed mb-10 font-medium">
                  Dr. <span className="text-slate-900 dark:text-white font-black">{formData.name}</span>, your clinical walkthrough is locked for <span className="text-blue-600 dark:text-blue-400 font-black">{new Date(formData.date).toLocaleDateString(undefined, { dateStyle: 'long' })}</span>.
                </p>
                
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-8 rounded-[32px] border border-blue-100/50 dark:border-blue-800/30 text-left flex items-start gap-6 mb-10 shadow-lg shadow-blue-500/5">
                  <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center text-white flex-shrink-0 shadow-lg shadow-blue-600/20">
                    <PlayCircle size={28} />
                  </div>
                  <div>
                    <p className="text-[10px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-[0.2em] mb-2">Pre-Demo Briefing</p>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-100 leading-relaxed italic">"Check your inbox at <span className="underline decoration-blue-400 underline-offset-4">{formData.email}</span> for an exclusive early-access platform briefing."</p>
                  </div>
                </div>

                <button 
                  onClick={closeModal}
                  className="w-full py-5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl font-black text-lg hover:opacity-90 transition-all shadow-xl active:scale-95"
                >
                  Return to Control Portal
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
