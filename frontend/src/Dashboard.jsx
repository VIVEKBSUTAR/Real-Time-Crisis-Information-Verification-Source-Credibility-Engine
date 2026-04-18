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

      if (!response.ok) {
        const error = await response.text();
        console.error('Backend error:', error);
        alert('Backend error: ' + error);
        throw new Error('Backend error');
      }
      
      const data = await response.json();
      console.log('Backend response:', data);
      
      setVerifications([{
        id: Date.now(),
        claim: data.original_claim || claim,
        verdict: data.verdict || 'UNCERTAIN',
        confidence: data.confidence || 0.5,
        reasoning: data.explanation || 'Analyzing...', 
        sources: data.evidence || [],
        timestamp: new Date().toLocaleTimeString()
      }]);
      
      setClaim('');
    } catch (error) {
      console.error('Error:', error);
      alert('Error: ' + error.message);
    }
    setIsLoading(false);
  };

  const getVerdictColor = (verdict) => {
    if (!verdict) return 'bg-yellow-50 border-yellow-400 border-2';
    const v = verdict.toUpperCase();
    if (v === 'VERIFIED' || v === 'TRUE') return 'bg-green-50 border-green-400 border-2';
    if (v === 'FALSE' || v === 'DEBUNKED') return 'bg-red-50 border-red-400 border-2';
    return 'bg-yellow-50 border-yellow-400 border-2';
  };

  const getVerdictBadge = (verdict) => {
    if (!verdict) return 'bg-yellow-600 text-white font-semibold';
    const v = verdict.toUpperCase();
    if (v === 'VERIFIED' || v === 'TRUE') return 'bg-green-600 text-white font-semibold';
    if (v === 'FALSE' || v === 'DEBUNKED') return 'bg-red-600 text-white font-semibold';
    return 'bg-yellow-600 text-white font-semibold';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b-2 border-gray-300 shadow-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-700 to-blue-900 rounded-lg flex items-center justify-center text-white font-bold text-lg">
              SP
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Sentinel Protocol</h1>
              <p className="text-sm text-gray-700 font-medium">Crisis Information Verification Engine</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-gray-100 rounded-lg transition border border-gray-300">
              <Settings size={20} className="text-gray-700" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg transition border border-gray-300">
              <Menu size={20} className="text-gray-700" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-white border-r-2 border-gray-300 p-6 hidden lg:block shadow-sm">
          <nav className="space-y-3">
            <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-blue-700 text-white font-bold">
              <Home size={20} />
              <span>Dashboard</span>
            </div>
            <div className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-800 hover:bg-gray-100 cursor-pointer transition border-l-4 border-gray-300 hover:border-blue-600 font-semibold">
              <AlertCircle size={20} />
              <span>Active Alerts</span>
            </div>
            <div className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-800 hover:bg-gray-100 cursor-pointer transition border-l-4 border-gray-300 hover:border-blue-600 font-semibold">
              <CheckCircle size={20} />
              <span>Verified Claims</span>
            </div>
          </nav>

          <hr className="my-6 border-gray-300" />

          <div className="p-4 bg-blue-50 rounded-lg border-2 border-blue-300">
            <p className="text-sm text-gray-800 font-semibold">Connected to Dataset</p>
            <p className="text-xs text-gray-700 mt-2">26,232 news claims loaded</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-8">
          {/* Search Section */}
          <div className="max-w-3xl mx-auto mb-12">
            <div className="bg-white rounded-2xl shadow-lg p-8 border-2 border-gray-300">
              <h2 className="text-3xl font-bold text-gray-900 mb-3">Verify a Claim</h2>
              <p className="text-gray-800 mb-8 text-lg font-medium">Enter any claim, news headline, or social media post to verify its credibility</p>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-4 top-4 text-gray-600" size={22} />
                  <input
                    type="text"
                    value={claim}
                    onChange={(e) => setClaim(e.target.value)}
                    placeholder="Paste claim, news headline, or URL..."
                    className="w-full pl-14 pr-4 py-4 border-2 border-gray-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-700 focus:border-blue-700 text-gray-900 font-medium text-lg"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading || !claim.trim()}
                  className="w-full bg-blue-700 hover:bg-blue-800 disabled:bg-gray-400 text-white font-bold py-4 rounded-xl transition text-lg shadow-lg border-2 border-blue-900"
                >
                  {isLoading ? '⟳ ANALYZING...' : 'ANALYZE CREDIBILITY ▶'}
                </button>
              </form>
            </div>
          </div>

          {/* Results Section */}
          <div className="max-w-3xl mx-auto space-y-6">
            {verifications.length === 0 ? (
              <div className="text-center py-16 bg-white rounded-xl border-2 border-gray-300 shadow-md">
                <p className="text-gray-700 text-xl font-semibold">Results will appear here</p>
                <p className="text-gray-600 text-lg mt-2">Enter a claim above to get started</p>
              </div>
            ) : (
              verifications.map((v) => (
                <div key={v.id} className={`rounded-2xl ${getVerdictColor(v.verdict)} p-8 shadow-lg transition transform hover:shadow-xl`}>
                  <div className="flex items-start justify-between mb-6">
                    <h3 className="font-bold text-gray-900 flex-1 text-lg">{v.claim}</h3>
                    <span className={`px-4 py-2 rounded-full text-sm font-bold whitespace-nowrap ml-4 ${getVerdictBadge(v.verdict)}`}>
                      {v.verdict}
                    </span>
                  </div>

                  <div className="space-y-4 text-base">
                    <div>
                      <p className="text-gray-800 font-bold mb-2">Confidence Level</p>
                      <div className="w-full bg-gray-400 rounded-full h-3 border border-gray-500">
                        <div 
                          className="bg-blue-700 h-3 rounded-full transition-all"
                          style={{ width: `${Math.min(v.confidence * 100, 100)}%` }}
                        />
                      </div>
                      <p className="text-gray-800 font-semibold mt-2">{Math.round(v.confidence * 100)}% Confidence</p>
                    </div>

                    <div>
                      <p className="text-gray-800 font-bold mb-2">Analysis</p>
                      <p className="text-gray-900 leading-relaxed font-medium">{v.reasoning}</p>
                    </div>

                    {v.sources && v.sources.length > 0 && (
                      <div>
                        <p className="text-gray-800 font-bold mb-2">Supporting Sources</p>
                        <div className="space-y-2">
                          {v.sources.map((src, idx) => (
                            <div key={idx} className="bg-white bg-opacity-60 p-3 rounded-lg border border-gray-400">
                              <p className="font-semibold text-gray-800">{src.source}</p>
                              <p className="text-sm text-gray-700">Relation: <span className="font-bold">{src.relation}</span> ({Math.round(src.confidence * 100)}%)</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <p className="text-gray-700 text-sm font-semibold pt-2">🕐 {v.timestamp}</p>
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
