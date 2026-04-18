import React, { useState } from 'react';
import { Search, Menu, Settings, Home, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

export default function DashboardLight() {
  const [claim, setClaim] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [verifications, setVerifications] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!claim.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/analyze_claim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: claim }),
      });

      if (!response.ok) throw new Error('Backend error');
      const data = await response.json();
      
      setVerifications([{
        id: Date.now(),
        claim: data.claim || claim,
        verdict: data.label,
        confidence: (data.confidence * 100).toFixed(1),
        reasoning: data.reasoning || 'Analyzing...', 
        sources: data.similar_claims || [],
        timestamp: new Date().toLocaleTimeString()
      }]);
      
      setClaim('');
    } catch (error) {
      console.error('Error:', error);
    }
    setIsLoading(false);
  };

  const getVerdictColor = (verdict) => {
    if (verdict === 'VERIFIED') return 'bg-green-50 border-green-200';
    if (verdict === 'FALSE') return 'bg-red-50 border-red-200';
    return 'bg-yellow-50 border-yellow-200';
  };

  const getVerdictBadge = (verdict) => {
    if (verdict === 'VERIFIED') return 'bg-green-100 text-green-800';
    if (verdict === 'FALSE') return 'bg-red-100 text-red-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center text-white font-bold">
              SP
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Sentinel Protocol</h1>
              <p className="text-xs text-gray-500">Crisis Information Verification</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-gray-100 rounded-lg transition">
              <Settings size={20} className="text-gray-600" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg transition">
              <Menu size={20} className="text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-white border-r border-gray-200 p-6 hidden lg:block">
          <nav className="space-y-2">
            <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-blue-50 text-blue-600 font-medium">
              <Home size={20} />
              <span>Dashboard</span>
            </div>
            <div className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-600 hover:bg-gray-50 cursor-pointer transition">
              <AlertCircle size={20} />
              <span>Active Alerts</span>
            </div>
            <div className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-600 hover:bg-gray-50 cursor-pointer transition">
              <CheckCircle size={20} />
              <span>Verified Claims</span>
            </div>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 lg:p-10">
          {/* Search Section */}
          <div className="max-w-2xl mx-auto mb-12">
            <div className="bg-white rounded-2xl shadow-md p-8 border border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Verify a Claim</h2>
              <p className="text-gray-600 mb-6">Enter any claim to verify its credibility</p>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-4 top-3 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={claim}
                    onChange={(e) => setClaim(e.target.value)}
                    placeholder="Paste claim, news headline, or URL..."
                    className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading || !claim.trim()}
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-400 text-white font-semibold py-3 rounded-xl transition"
                >
                  {isLoading ? '⟳ ANALYZING...' : 'ANALYZE CREDIBILITY ▶'}
                </button>
              </form>
            </div>
          </div>

          {/* Results Section */}
          <div className="max-w-2xl mx-auto space-y-4">
            {verifications.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">Results will appear here</p>
              </div>
            ) : (
              verifications.map((v) => (
                <div key={v.id} className={`rounded-xl border-2 p-6 ${getVerdictColor(v.verdict)} transition`}>
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="font-semibold text-gray-900 flex-1">{v.claim}</h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getVerdictBadge(v.verdict)}`}>
                      {v.verdict}
                    </span>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div>
                      <p className="text-gray-600 font-medium">Confidence</p>
                      <div className="w-full bg-gray-300 rounded-full h-2 mt-1">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${v.confidence}%` }}
                        />
                      </div>
                      <p className="text-gray-500 mt-1">{v.confidence}% confidence</p>
                    </div>

                    <div>
                      <p className="text-gray-600 font-medium">Reasoning</p>
                      <p className="text-gray-700 mt-1">{v.reasoning}</p>
                    </div>

                    <p className="text-xs text-gray-500 pt-2">{v.timestamp}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
