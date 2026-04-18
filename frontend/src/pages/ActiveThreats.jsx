import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp } from 'lucide-react';

export default function ActiveThreats() {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch recent false claims marked as threats
    const mockThreats = [
      {
        id: 1,
        claim: 'Major bridge collapsed in Mumbai, 200+ casualties',
        severity: 'CRITICAL',
        confidence: 95,
        threats: 1245,
        shares: 3402,
      },
      {
        id: 2,
        claim: 'New virus affecting mobile phones detected',
        severity: 'HIGH',
        confidence: 87,
        threats: 652,
        shares: 1823,
      },
      {
        id: 3,
        claim: 'Government implementing secret policy change',
        severity: 'MEDIUM',
        confidence: 72,
        threats: 289,
        shares: 892,
      },
    ];
    setThreats(mockThreats);
    setLoading(false);
  }, []);

  const getSeverityColor = (severity) => {
    if (severity === 'CRITICAL') return { badge: 'bg-red-100 text-red-800', icon: 'text-red-600' };
    if (severity === 'HIGH') return { badge: 'bg-orange-100 text-orange-800', icon: 'text-orange-600' };
    return { badge: 'bg-yellow-100 text-yellow-800', icon: 'text-yellow-600' };
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Active Threats</h1>
      <p className="text-gray-600 mb-8">High-confidence false claims spreading rapidly</p>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {threats.map((threat) => {
            const color = getSeverityColor(threat.severity);
            return (
              <div key={threat.id} className="bg-white border-l-4 border-red-500 rounded-lg p-6 shadow-sm hover:shadow-md transition">
                <div className="flex items-start gap-4">
                  <AlertTriangle className={`w-6 h-6 flex-shrink-0 ${color.icon}`} />
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{threat.claim}</h3>
                      <span className={`${color.badge} px-3 py-1 rounded-full text-xs font-semibold`}>
                        {threat.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">False Claim Detected • Confidence: {threat.confidence}%</p>
                    <div className="flex gap-8 text-sm">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-red-600" />
                        <span className="text-gray-700"><strong>{threat.threats}</strong> active threats</span>
                      </div>
                      <div className="text-gray-600">
                        <strong>{threat.shares}</strong> shares detected
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
