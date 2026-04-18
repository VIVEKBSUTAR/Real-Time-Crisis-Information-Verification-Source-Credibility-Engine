import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, PieChart as PieChartIcon } from 'lucide-react';

export default function Analytics() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const mockStats = {
      total: 26232,
      verified: 15913,
      false: 10319,
      accuracy: 87.5,
      avgConfidence: 82.3,
      topThreats: [
        { category: 'Health Misinformation', count: 3421, trend: 'up' },
        { category: 'Political Claims', count: 2890, trend: 'up' },
        { category: 'Natural Disasters', count: 2145, trend: 'down' },
        { category: 'Technology Rumors', count: 1876, trend: 'stable' },
      ],
    };
    setStats(mockStats);
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
      <p className="text-gray-600 mb-8">System-wide statistics and insights</p>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg p-6 shadow-sm border-l-4 border-green-500">
          <p className="text-gray-600 text-sm font-medium mb-2">Total Analyzed</p>
          <p className="text-4xl font-bold text-gray-900">{stats.total.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-2">Claims in dataset</p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm border-l-4 border-blue-500">
          <p className="text-gray-600 text-sm font-medium mb-2">System Accuracy</p>
          <p className="text-4xl font-bold text-blue-600">{stats.accuracy}%</p>
          <p className="text-xs text-gray-500 mt-2">Overall verification accuracy</p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm border-l-4 border-orange-500">
          <p className="text-gray-600 text-sm font-medium mb-2">Avg Confidence</p>
          <p className="text-4xl font-bold text-orange-600">{stats.avgConfidence}%</p>
          <p className="text-xs text-gray-500 mt-2">Average confidence score</p>
        </div>
      </div>

      {/* Distribution Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <PieChartIcon className="w-5 h-5 text-blue-600" />
            Verdict Distribution
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Verified (True)</span>
                <span className="text-sm font-bold text-green-600">{stats.verified.toLocaleString()}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${(stats.verified / stats.total) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">False (Debunked)</span>
                <span className="text-sm font-bold text-red-600">{stats.false.toLocaleString()}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full"
                  style={{ width: `${(stats.false / stats.total) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Top Threat Categories */}
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-orange-600" />
            Top Threat Categories
          </h3>
          <div className="space-y-4">
            {stats.topThreats.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-700">{item.category}</p>
                  <div className="w-64 bg-gray-200 rounded-full h-2 mt-2">
                    <div
                      className="bg-orange-500 h-2 rounded-full"
                      style={{ width: `${(item.count / stats.topThreats[0].count) * 100}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm font-bold text-gray-900">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
