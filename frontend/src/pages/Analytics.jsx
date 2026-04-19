import React, { useState, useEffect } from 'react';
import { BarChart3, PieChart as PieChartIcon } from 'lucide-react';
import { apiUrl } from '../config/api';

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch(apiUrl('/analytics'));
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <div className="max-w-6xl mx-auto space-y-4">
          <div className="h-10 w-72 rounded-lg animated-shimmer" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="h-32 rounded-2xl animated-shimmer" />
            <div className="h-32 rounded-2xl animated-shimmer" />
            <div className="h-32 rounded-2xl animated-shimmer" />
          </div>
          <div className="h-72 rounded-2xl animated-shimmer" />
        </div>
      </div>
    );
  }

  if (!stats) return <div className="p-8 text-slate-700">Failed to load analytics</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto page-enter">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Analytics Dashboard</h1>
      <p className="text-slate-600 mb-8">System-wide statistics and insights</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-panel rounded-2xl p-6 shadow-sm border-l-4 border-emerald-500 border border-slate-200 kpi-card hover-lift section-enter">
          <p className="text-slate-600 text-sm font-medium mb-2">Total Analyzed</p>
          <p className="text-4xl font-bold text-slate-900">{stats.total.toLocaleString()}</p>
          <p className="text-xs text-slate-500 mt-2">Claims in dataset</p>
        </div>
        <div className="glass-panel rounded-2xl p-6 shadow-sm border-l-4 border-indigo-500 border border-slate-200 kpi-card hover-lift section-enter" style={{ animationDelay: '70ms' }}>
          <p className="text-slate-600 text-sm font-medium mb-2">System Accuracy</p>
          <p className="text-4xl font-bold text-indigo-600">{stats.accuracy}%</p>
          <p className="text-xs text-slate-500 mt-2">Overall verification accuracy</p>
        </div>
        <div className="glass-panel rounded-2xl p-6 shadow-sm border-l-4 border-cyan-500 border border-slate-200 kpi-card hover-lift section-enter" style={{ animationDelay: '120ms' }}>
          <p className="text-slate-600 text-sm font-medium mb-2">Avg Confidence</p>
          <p className="text-4xl font-bold text-cyan-600">{stats.avg_confidence}%</p>
          <p className="text-xs text-slate-500 mt-2">Average confidence score</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel rounded-2xl p-6 shadow-sm border border-slate-200 hover-lift section-enter">
          <h3 className="text-lg font-semibold text-slate-900 mb-6 flex items-center gap-2">
            <PieChartIcon className="w-5 h-5 text-indigo-600" />
            Verdict Distribution
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-700">Verified (True)</span>
                <span className="text-sm font-bold text-emerald-600">{stats.verified.toLocaleString()}</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-emerald-500 h-2 rounded-full transition-all duration-700"
                  style={{ width: `${(stats.verified / stats.total) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-700">False (Debunked)</span>
                <span className="text-sm font-bold text-rose-600">{stats.false.toLocaleString()}</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-rose-500 h-2 rounded-full transition-all duration-700"
                  style={{ width: `${(stats.false / stats.total) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-6 shadow-sm border border-slate-200 hover-lift section-enter" style={{ animationDelay: '80ms' }}>
          <h3 className="text-lg font-semibold text-slate-900 mb-6 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-cyan-600" />
            Top Threat Categories
          </h3>
          <div className="space-y-4">
            {stats.top_threats.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between hover-lift rounded-lg p-2 -mx-2">
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-700">{item.category}</p>
                  <div className="w-full bg-slate-200 rounded-full h-2 mt-2 overflow-hidden">
                    <div
                      className="bg-cyan-500 h-2 rounded-full transition-all duration-700"
                      style={{ width: `${(item.count / stats.top_threats[0].count) * 100}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm font-bold text-slate-900 ml-4">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
