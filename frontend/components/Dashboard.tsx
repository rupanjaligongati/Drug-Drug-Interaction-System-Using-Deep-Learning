
import React from 'react';
import { PredictionResult, RiskLevel } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface DashboardProps {
  history: PredictionResult[];
}

export const Dashboard: React.FC<DashboardProps> = ({ history }) => {
  const analytics = history.reduce((acc, curr) => {
    acc[curr.riskLevel] = (acc[curr.riskLevel] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const chartData = [
    { name: 'Low', count: analytics[RiskLevel.LOW] || 0, color: '#10b981' },
    { name: 'Moderate', count: analytics[RiskLevel.MODERATE] || 0, color: '#f59e0b' },
    { name: 'High', count: (analytics[RiskLevel.HIGH] || 0) + (analytics[RiskLevel.CONTRAINDICATED] || 0), color: '#ef4444' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <h2 className="text-3xl font-bold text-slate-900 mb-8">System Analytics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <div className="glass-card p-6 rounded-2xl">
          <p className="text-xs font-bold text-slate-400 uppercase mb-1">Total Requests</p>
          <p className="text-3xl font-bold text-slate-900">{history.length}</p>
        </div>
        <div className="glass-card p-6 rounded-2xl border-l-4 border-red-500">
          <p className="text-xs font-bold text-slate-400 uppercase mb-1">High Risk Detected</p>
          <p className="text-3xl font-bold text-slate-900">{(analytics[RiskLevel.HIGH] || 0) + (analytics[RiskLevel.CONTRAINDICATED] || 0)}</p>
        </div>
        <div className="glass-card p-6 rounded-2xl border-l-4 border-orange-400">
          <p className="text-xs font-bold text-slate-400 uppercase mb-1">Moderate Risk</p>
          <p className="text-3xl font-bold text-slate-900">{analytics[RiskLevel.MODERATE] || 0}</p>
        </div>
        <div className="glass-card p-6 rounded-2xl border-l-4 border-emerald-500">
          <p className="text-xs font-bold text-slate-400 uppercase mb-1">Average Confidence</p>
          <p className="text-3xl font-bold text-slate-900">
            {history.length ? (history.reduce((a, b) => a + b.confidenceScore, 0) / history.length * 100).toFixed(0) : 0}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card p-8 rounded-[32px]">
          <h3 className="text-xl font-bold text-slate-800 mb-6">Interaction Risk Distribution</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                <Tooltip 
                    cursor={{fill: '#f8fafc'}}
                    contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'}}
                />
                <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-8 rounded-[32px] overflow-hidden">
          <h3 className="text-xl font-bold text-slate-800 mb-6">Recent Activity</h3>
          <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
            {history.slice(0, 10).map((item) => (
              <div key={item.id} className="flex items-center gap-4 p-4 rounded-xl bg-slate-50/50 hover:bg-white border border-transparent hover:border-slate-100 transition-all group">
                <div className={`w-3 h-3 rounded-full ${
                  item.riskLevel === RiskLevel.HIGH ? 'bg-red-500' : 
                  item.riskLevel === RiskLevel.MODERATE ? 'bg-orange-400' : 'bg-emerald-500'
                }`}></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-slate-800 truncate">
                    {/* Fix: Changed non-existent item.drug1 and item.drug2 to use index access from item.drugs array */}
                    {item.drugs[0]} + {item.drugs[1]}
                  </p>
                  <p className="text-[10px] text-slate-400 uppercase font-bold">
                    {new Date(item.timestamp).toLocaleDateString()} • {item.riskLevel}
                  </p>
                </div>
              </div>
            ))}
            {history.length === 0 && (
                <div className="text-center py-10">
                    <p className="text-slate-400 text-sm">No recent activity found.</p>
                </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
