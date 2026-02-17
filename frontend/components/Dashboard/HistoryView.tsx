
import React, { useState } from 'react';
import { Search, Filter, MoreVertical, Eye, Trash2, Download, ShieldCheck, Clock, X, Info, AlertCircle, FileText } from 'lucide-react';
import { PredictionResult } from '../../types';

interface AuditLog {
  id: string;
  action: 'VIEW_DETAILS' | 'DELETE_ENTRY' | 'EXPORT_REPORT';
  details: string;
  timestamp: number;
  user: string;
}

interface HistoryViewProps {
  history: PredictionResult[];
  onDelete: (id: string) => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({ history, onDelete }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [selectedEntry, setSelectedEntry] = useState<PredictionResult | null>(null);

  const logAction = (action: AuditLog['action'], details: string) => {
    const newLog: AuditLog = {
      id: Math.random().toString(36).substring(2, 9),
      action,
      details,
      timestamp: Date.now(),
      user: 'Dr. Sarah Johnson'
    };
    setAuditLogs(prev => [newLog, ...prev].slice(0, 20));
  };

  const filtered = history.filter(h => 
    h.drugs.some(d => d.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleView = (item: PredictionResult) => {
    setSelectedEntry(item);
    logAction('VIEW_DETAILS', `Accessed full clinical report for ${item.drugs.join(' + ')}`);
  };

  const handleDelete = (item: PredictionResult) => {
    if (window.confirm(`Are you sure you want to permanently delete the clinical record for ${item.drugs.join(' + ')}?`)) {
      onDelete(item.id);
      logAction('DELETE_ENTRY', `Permanently removed record for ${item.drugs.join(' + ')} (ID: ${item.id})`);
    }
  };

  return (
    <div className="grid lg:grid-cols-4 gap-8 animate-in fade-in duration-500">
      <div className="lg:col-span-3 space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-1">Analysis History</h2>
            <p className="text-slate-500 dark:text-slate-400">Review and audit all past medication interaction analysis reports.</p>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={() => logAction('EXPORT_REPORT', 'Exported full system audit logs to CSV')}
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
            >
              <Download size={16} /> Export Reports
            </button>
          </div>
        </div>

        <div className="glass-panel rounded-[40px] border border-white dark:border-slate-800 overflow-hidden shadow-xl">
          <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="relative w-full max-w-md">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input 
                type="text" 
                placeholder="Search by drug name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-xl py-2 pl-10 pr-4 outline-none focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900 transition-all text-sm dark:text-slate-200"
              />
            </div>
            <div className="flex items-center gap-3">
              <button className="p-2 text-slate-400 hover:text-slate-600"><Filter size={20} /></button>
              <button className="p-2 text-slate-400 hover:text-slate-600"><MoreVertical size={20} /></button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50/50 dark:bg-slate-800/20">
                  <th className="px-8 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">Interaction Profile</th>
                  <th className="px-8 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">Risk Level</th>
                  <th className="px-8 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">Confidence</th>
                  <th className="px-8 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">Timestamp</th>
                  <th className="px-8 py-5 text-right text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filtered.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/30 dark:hover:bg-slate-800/30 transition-colors group">
                    <td className="px-8 py-6">
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-slate-900 dark:text-white leading-tight mb-1">{item.drugs.join(" + ")}</span>
                        <span className="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-widest">ID: {item.id}</span>
                      </div>
                    </td>
                    <td className="px-8 py-6">
                      <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest 
                        ${item.riskLevel === 'HIGH' ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400' : 
                          item.riskLevel === 'MODERATE' ? 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400' : 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400'}`}>
                        {item.riskLevel}
                      </span>
                    </td>
                    <td className="px-8 py-6">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-bold text-slate-700 dark:text-slate-300">{(item.confidenceScore * 100).toFixed(0)}%</span>
                        <div className="w-16 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden hidden md:block">
                          <div className="h-full bg-blue-500" style={{width: `${item.confidenceScore * 100}%`}}></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-sm text-slate-500 dark:text-slate-400 font-medium">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </td>
                    <td className="px-8 py-6 text-right">
                      <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => handleView(item)}
                          className="p-2 bg-white dark:bg-slate-900 rounded-lg border border-slate-100 dark:border-slate-800 shadow-sm text-slate-400 hover:text-blue-600 hover:border-blue-200 transition-all"
                        >
                          <Eye size={16} />
                        </button>
                        <button 
                          onClick={() => handleDelete(item)}
                          className="p-2 bg-white dark:bg-slate-900 rounded-lg border border-slate-100 dark:border-slate-800 shadow-sm text-slate-400 hover:text-red-500 hover:border-red-200 transition-all"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-8 py-20 text-center text-slate-400 dark:text-slate-600 font-medium italic">
                      No matching clinical records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Audit Trail Side Panel */}
      <div className="space-y-6">
        <div className="flex items-center gap-3 mb-2 px-2">
          <ShieldCheck className="text-blue-600" size={20} />
          <h3 className="text-lg font-bold text-slate-900 dark:text-white poppins">System Audit Trail</h3>
        </div>

        <div className="glass-panel p-6 rounded-[32px] border border-white dark:border-slate-800 shadow-lg min-h-[500px] flex flex-col">
          <div className="flex-1 space-y-6">
            {auditLogs.length > 0 ? auditLogs.map((log) => (
              <div key={log.id} className="relative pl-6 border-l border-slate-100 dark:border-slate-800 pb-1">
                <div className={`absolute -left-1.5 top-0 w-3 h-3 rounded-full border-2 border-white dark:border-slate-900 
                  ${log.action === 'DELETE_ENTRY' ? 'bg-red-500' : 'bg-blue-500'}`}></div>
                <div className="flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                      {log.action.replace('_', ' ')}
                    </span>
                    <span className="text-[9px] text-slate-400 font-bold flex items-center gap-1">
                      <Clock size={10} /> {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="text-xs font-bold text-slate-800 dark:text-slate-200 leading-tight">{log.details}</p>
                  <p className="text-[9px] text-slate-500 dark:text-slate-400 font-medium">Authored by: {log.user}</p>
                </div>
              </div>
            )) : (
              <div className="h-full flex flex-col items-center justify-center text-center p-4">
                <Clock className="text-slate-200 dark:text-slate-800 mb-4" size={48} />
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest leading-relaxed">
                  Awaiting system <br /> activity log...
                </p>
              </div>
            )}
          </div>

          <div className="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
            <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-2">Audit Compliance</p>
            <p className="text-[10px] text-slate-500 leading-relaxed font-medium">
              All user actions are logged under SOC2 Type II protocol and stored for 7 years in clinical vault.
            </p>
          </div>
        </div>
      </div>

      {/* Detail View Modal */}
      {selectedEntry && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 animate-in fade-in duration-300">
          <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={() => setSelectedEntry(null)}></div>
          <div className="glass-panel w-full max-w-2xl rounded-[40px] overflow-hidden relative z-10 animate-in zoom-in-95 duration-300 shadow-2xl border border-white dark:border-slate-800">
            <div className="p-8 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/50">
               <div className="flex items-center gap-4">
                 <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white">
                   <FileText size={24} />
                 </div>
                 <div>
                   <h3 className="text-xl font-bold text-slate-900 dark:text-white">Clinical Record Access</h3>
                   <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Transaction ID: {selectedEntry.id}</p>
                 </div>
               </div>
               <button onClick={() => setSelectedEntry(null)} className="p-2 text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                 <X size={24} />
               </button>
            </div>

            <div className="p-10 space-y-8 max-h-[70vh] overflow-y-auto custom-scrollbar">
               <div className="flex items-center gap-6">
                  <div className="flex-1 p-6 bg-slate-50 dark:bg-slate-900 rounded-3xl border border-slate-100 dark:border-slate-800">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Primary Compounds</p>
                    <p className="text-lg font-bold text-slate-900 dark:text-white">{selectedEntry.drugs.join(' + ')}</p>
                  </div>
                  <div className={`p-6 rounded-3xl border border-white dark:border-slate-800 flex flex-col items-center justify-center min-w-[120px] 
                    ${selectedEntry.riskLevel === 'HIGH' ? 'bg-red-50 dark:bg-red-900/20 text-red-600' : 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600'}`}>
                    <AlertCircle size={20} className="mb-1" />
                    <span className="text-xs font-black uppercase tracking-widest">{selectedEntry.riskLevel}</span>
                  </div>
               </div>

               <div className="space-y-4">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                    <Info size={14} className="text-blue-500" /> Assessment Logic
                  </div>
                  <p className="text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
                    {selectedEntry.explanation}
                  </p>
               </div>

               <div className="p-6 bg-blue-50/50 dark:bg-blue-900/10 rounded-3xl border border-blue-100 dark:border-blue-800">
                  <p className="text-[10px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest mb-2">Refined Management Protocol</p>
                  <p className="text-sm font-bold text-slate-800 dark:text-slate-200 leading-relaxed">
                    {selectedEntry.recommendation}
                  </p>
               </div>
            </div>

            <div className="p-8 bg-slate-50/50 dark:bg-slate-900/50 border-t border-slate-100 dark:border-slate-800 flex justify-end">
               <button 
                onClick={() => setSelectedEntry(null)}
                className="px-8 py-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl font-bold transition-all hover:opacity-90"
               >
                 Acknowledge & Close
               </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
