
import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, AreaChart, Area } from 'recharts';
import { Activity, TrendingUp, AlertTriangle, Users } from 'lucide-react';
import { PredictionResult } from '../../types';

export const AnalyticsView: React.FC<{history: PredictionResult[]}> = ({ history }) => {
  const riskData = [
    { name: 'High', value: history.filter(h => h.riskLevel === 'HIGH' || h.riskLevel === 'CONTRAINDICATED').length, color: '#ef4444' },
    { name: 'Moderate', value: history.filter(h => h.riskLevel === 'MODERATE').length, color: '#f59e0b' },
    { name: 'Low', value: history.filter(h => h.riskLevel === 'LOW').length, color: '#10b981' },
  ];

  const trendData = [
    { day: 'Mon', count: 12 }, { day: 'Tue', count: 19 }, { day: 'Wed', count: 15 },
    { day: 'Thu', count: 22 }, { day: 'Fri', count: 30 }, { day: 'Sat', count: 10 },
    { day: 'Sun', count: 8 },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
           <h2 className="text-3xl font-bold text-slate-900 mb-1">Population Analytics</h2>
           <p className="text-slate-500">Global overview of polypharmacy risks and system usage metrics.</p>
        </div>
        <div className="px-4 py-2 bg-emerald-50 border border-emerald-100 rounded-xl text-emerald-600 text-xs font-bold uppercase flex items-center gap-2">
           <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
           Live Data Sync Active
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         {[
           { label: 'Total Analyses', val: history.length, icon: Activity, color: 'text-blue-600', bg: 'bg-blue-50' },
           { label: 'High Risk Detects', val: riskData[0].value, icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50' },
           { label: 'Avg Confidence', val: '92.4%', icon: TrendingUp, color: 'text-purple-600', bg: 'bg-purple-50' },
           { label: 'Managed Patients', val: '128', icon: Users, color: 'text-emerald-600', bg: 'bg-emerald-50' },
         ].map((stat, i) => (
           <div key={i} className="glass-panel p-6 rounded-[28px] border border-white shadow-lg">
              <div className={`w-12 h-12 ${stat.bg} ${stat.color} rounded-2xl flex items-center justify-center mb-4`}>
                 <stat.icon size={22} />
              </div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{stat.label}</p>
              <p className="text-3xl font-bold text-slate-900">{stat.val}</p>
           </div>
         ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
         <div className="lg:col-span-2 glass-panel p-8 rounded-[40px] border border-white shadow-xl">
            <h3 className="text-xl font-bold text-slate-900 mb-8">Weekly Utilization Trend</h3>
            <div className="h-[350px]">
               <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData}>
                     <defs>
                        <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                           <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                           <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                     </defs>
                     <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                     <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12, fontWeight: 600}} dy={10} />
                     <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12, fontWeight: 600}} />
                     <Tooltip contentStyle={{borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'}} />
                     <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={4} fillOpacity={1} fill="url(#colorCount)" />
                  </AreaChart>
               </ResponsiveContainer>
            </div>
         </div>

         <div className="glass-panel p-8 rounded-[40px] border border-white shadow-xl flex flex-col">
            <h3 className="text-xl font-bold text-slate-900 mb-8 text-center">Risk Distribution</h3>
            <div className="flex-1 min-h-[300px]">
               <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                     <Pie data={riskData} innerRadius={80} outerRadius={100} paddingAngle={10} dataKey="value">
                        {riskData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                     </Pie>
                     <Tooltip contentStyle={{borderRadius: '16px'}} />
                  </PieChart>
               </ResponsiveContainer>
            </div>
            <div className="space-y-3 mt-4">
               {riskData.map(item => (
                 <div key={item.name} className="flex items-center justify-between p-3 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="flex items-center gap-2">
                       <div className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: item.color}}></div>
                       <span className="text-xs font-bold text-slate-700">{item.name} Risk</span>
                    </div>
                    <span className="text-xs font-black text-slate-400">{item.value} Analyses</span>
                 </div>
               ))}
            </div>
         </div>
      </div>
    </div>
  );
};
