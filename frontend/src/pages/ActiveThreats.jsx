import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp, Filter, FileDown } from 'lucide-react';

export default function ActiveThreats() {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('ALL');

  useEffect(() => {
    const fetchThreats = async () => {
      try {
        const response = await fetch('http://localhost:8000/threats');
        if (response.ok) {
          const data = await response.json();
          setThreats(data);
        }
      } catch (error) {
        console.error('Error fetching threats:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchThreats();
  }, []);

  const getSeverityColor = (severity) => {
    if (severity === 'CRITICAL') return { badge: 'bg-rose-100 text-rose-800', icon: 'text-rose-600', border: 'border-rose-500' };
    if (severity === 'HIGH') return { badge: 'bg-orange-100 text-orange-800', icon: 'text-orange-600', border: 'border-orange-500' };
    return { badge: 'bg-amber-100 text-amber-800', icon: 'text-amber-600', border: 'border-amber-500' };
  };

  if (loading) {
      return (
        <div className="p-8 flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      );
  }

  const filteredThreats =
    severityFilter === 'ALL'
      ? threats
      : threats.filter((item) => item.severity === severityFilter);

  const totalThreats = threats.reduce((sum, item) => sum + (item.threats || 0), 0);
  const criticalCount = threats.filter((item) => item.severity === 'CRITICAL').length;
  const highCount = threats.filter((item) => item.severity === 'HIGH').length;
  const avgConfidence =
    threats.length > 0
      ? Math.round(threats.reduce((sum, item) => sum + (item.confidence || 0), 0) / threats.length)
      : 0;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Active Threats</h1>
      <p className="text-slate-600 mb-8">High-confidence false claims spreading rapidly</p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs text-slate-500">Total Active</p>
          <p className="text-2xl font-bold text-slate-900">{totalThreats.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs text-slate-500">Critical Claims</p>
          <p className="text-2xl font-bold text-rose-600">{criticalCount}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs text-slate-500">High Claims</p>
          <p className="text-2xl font-bold text-orange-600">{highCount}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs text-slate-500">Avg Confidence</p>
          <p className="text-2xl font-bold text-indigo-600">{avgConfidence}%</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-wrap gap-3 mb-6 items-center">
        <div className="flex items-center gap-2 text-slate-600 text-sm font-medium">
          <Filter size={16} />
          Filters
        </div>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="ALL">All Severity</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
        </select>
        <button className="ml-auto inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold hover:bg-indigo-700 transition">
          <FileDown size={16} />
          Export Report
        </button>
      </div>

      <div className="space-y-4">
        {filteredThreats.map((threat) => {
          const color = getSeverityColor(threat.severity);
          return (
            <div key={threat.id} className={`bg-white border-l-4 ${color.border} rounded-2xl p-6 shadow-sm hover:shadow-md transition border border-slate-200`}>
              <div className="flex items-start gap-4">
                <AlertTriangle className={`w-6 h-6 flex-shrink-0 ${color.icon}`} />
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-slate-900">{threat.claim}</h3>
                    <span className={`${color.badge} px-3 py-1 rounded-full text-xs font-semibold`}>
                      {threat.severity}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mb-4">False Claim Detected • Confidence: {threat.confidence}%</p>
                  <div className="flex gap-8 text-sm">
                    <div className="flex items-center gap-2">
                      <TrendingUp className={`w-4 h-4 ${color.icon}`} />
                      <span className="text-slate-700"><strong>{threat.threats}</strong> active threats</span>
                    </div>
                    <div className="text-slate-600">
                      <strong>{threat.shares}</strong> shares detected
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button className="px-3 py-1.5 text-xs font-semibold rounded-md border border-slate-300 text-slate-700 hover:bg-slate-50 transition">
                      View Evidence
                    </button>
                    <button className="px-3 py-1.5 text-xs font-semibold rounded-md bg-indigo-600 text-white hover:bg-indigo-700 transition">
                      Investigate
                    </button>
                    <button className="px-3 py-1.5 text-xs font-semibold rounded-md border border-slate-300 text-slate-700 hover:bg-slate-50 transition">
                      Archive
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
