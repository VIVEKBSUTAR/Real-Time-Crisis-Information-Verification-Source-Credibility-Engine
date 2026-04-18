import React, { useState, useEffect } from 'react';
import { Globe, AlertCircle } from 'lucide-react';

export default function GlobalMap() {
  const [regions, setRegions] = useState([]);

  useEffect(() => {
    const mockRegions = [
      { name: 'North India', threats: 234, severity: 'HIGH', color: 'bg-red-100 border-red-400' },
      { name: 'South India', threats: 156, severity: 'MEDIUM', color: 'bg-yellow-100 border-yellow-400' },
      { name: 'East India', threats: 189, severity: 'HIGH', color: 'bg-red-100 border-red-400' },
      { name: 'West India', threats: 267, severity: 'CRITICAL', color: 'bg-red-200 border-red-500' },
      { name: 'Central India', threats: 98, severity: 'LOW', color: 'bg-green-100 border-green-400' },
    ];
    setRegions(mockRegions);
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Global Map</h1>
      <p className="text-gray-600 mb-8">Geographic distribution of active threats</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Map Visualization */}
        <div className="lg:col-span-2 bg-white rounded-lg p-8 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <Globe className="w-5 h-5 text-blue-600" />
            India Threat Map
          </h3>
          
          {/* Simplified map representation */}
          <div className="bg-gray-100 rounded-lg p-8 text-center">
            <svg viewBox="0 0 400 300" className="w-full h-full max-h-96 mx-auto">
              <rect width="400" height="300" fill="#f3f4f6" />
              
              {/* Regional zones */}
              <circle cx="100" cy="60" r="35" fill="#fecaca" opacity="0.7" stroke="#dc2626" strokeWidth="2" />
              <text x="100" y="70" textAnchor="middle" fill="#991b1b" fontSize="12" fontWeight="bold">North</text>
              
              <circle cx="280" cy="100" r="35" fill="#fca5a5" opacity="0.7" stroke="#dc2626" strokeWidth="2" />
              <text x="280" y="110" textAnchor="middle" fill="#991b1b" fontSize="12" fontWeight="bold">West</text>
              
              <circle cx="200" cy="150" r="28" fill="#d1d5db" opacity="0.7" stroke="#6b7280" strokeWidth="2" />
              <text x="200" y="158" textAnchor="middle" fill="#374151" fontSize="11" fontWeight="bold">Central</text>
              
              <circle cx="280" cy="200" r="30" fill="#fef3c7" opacity="0.7" stroke="#eab308" strokeWidth="2" />
              <text x="280" y="210" textAnchor="middle" fill="#78350f" fontSize="11" fontWeight="bold">South</text>
              
              <circle cx="120" cy="240" r="30" fill="#fca5a5" opacity="0.7" stroke="#dc2626" strokeWidth="2" />
              <text x="120" y="250" textAnchor="middle" fill="#991b1b" fontSize="11" fontWeight="bold">East</text>
            </svg>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-200 border-2 border-red-500 rounded"></div>
              <span>Critical (250+)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-100 border-2 border-red-400 rounded"></div>
              <span>High (150-250)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-100 border-2 border-yellow-400 rounded"></div>
              <span>Medium (50-150)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-100 border-2 border-green-400 rounded"></div>
              <span>Low (&lt;50)</span>
            </div>
          </div>
        </div>

        {/* Regional Stats */}
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Regional Threats</h3>
          <div className="space-y-3">
            {regions.map((region, idx) => (
              <div key={idx} className={`${region.color} border-l-4 p-4 rounded`}>
                <p className="font-semibold text-gray-900 text-sm">{region.name}</p>
                <p className="text-xs text-gray-600 mt-1">{region.threats} active threats</p>
                <p className={`text-xs font-semibold mt-2 ${
                  region.severity === 'CRITICAL' ? 'text-red-700' :
                  region.severity === 'HIGH' ? 'text-red-600' :
                  region.severity === 'MEDIUM' ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {region.severity} SEVERITY
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
