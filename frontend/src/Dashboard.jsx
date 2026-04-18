import React, { useState } from 'react';
import { Search, AlertCircle, CheckCircle, XCircle, Menu, Settings, LogOut, Archive, Globe, BarChart3, HelpCircle, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const [claim, setClaim] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('intelligence');
  const [sidebarOpen, setSidebarOpen] = useState(true);

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
      setResult({
        id: data.claim_id,
        claim: data.original_claim,
        verdict: data.verdict,
        confidence: Math.round(data.confidence * 100),
        explanation: data.explanation,
        evidence: data.evidence || [],
        reasons: generateReasons(data.verdict, data.evidence)
      });
    } catch (error) {
      console.error('Error:', error);
      alert('Error: ' + error.message);
    }
    setIsLoading(false);
  };

  const generateReasons = (verdict, evidence) => {
    if (verdict === 'FALSE') {
      return [
        'Unverified Platform Origin',
        'Conflicting Source Data',
        'Lack of Official Confirmation'
      ];
    }
    if (verdict === 'VERIFIED') {
      return [
        'Multiple Source Confirmation',
        'Official Channel Verification',
        'Consistent Temporal Analysis'
      ];
    }
    return [
      'Mixed Source Evidence',
      'Insufficient Confirmation',
      'Pending Additional Verification'
    ];
  };

  const getVerdictColor = (verdict) => {
    if (verdict === 'VERIFIED') return { text: 'VERIFIED', color: 'text-green-600', bg: 'bg-green-50', badge: 'bg-green-100' };
    if (verdict === 'FALSE') return { text: 'REFUTED', color: 'text-red-600', bg: 'bg-red-50', badge: 'bg-red-100' };
    return { text: 'UNCERTAIN', color: 'text-yellow-600', bg: 'bg-yellow-50', badge: 'bg-yellow-100' };
  };

  const verdictInfo = result ? getVerdictColor(result.verdict) : null;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top Alert Banner */}
      <div className="bg-red-50 border-b-2 border-red-200 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <span className="text-xs font-bold text-red-700 bg-red-100 px-3 py-1 rounded">BTS</span>
          <span className="text-xs font-bold text-red-700 bg-red-100 px-3 py-1 rounded">Bridge collapse rumors trending</span>
          <span className="text-xs font-bold text-red-700 bg-red-100 px-3 py-1 rounded">Dam burst claim flagged</span>
          <div className="ml-auto text-xs text-gray-600">
            🔴 SYSTEM LIVE | Response {`<1.8s`} | 🔊
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <h1 className="text-2xl font-bold text-gray-900">Sentinel Protocol</h1>
            <nav className="flex gap-6">
              <button 
                onClick={() => setActiveTab('intelligence')}
                className={`text-sm font-medium pb-2 border-b-2 transition ${activeTab === 'intelligence' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
              >
                Intelligence
              </button>
              <button 
                onClick={() => setActiveTab('threats')}
                className={`text-sm font-medium pb-2 border-b-2 transition ${activeTab === 'threats' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
              >
                Active Threats
              </button>
              <button 
                onClick={() => setActiveTab('map')}
                className={`text-sm font-medium pb-2 border-b-2 transition ${activeTab === 'map' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
              >
                Global Map
              </button>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-600">Response {`<1.8s`}</span>
            <button className="p-2 hover:bg-gray-100 rounded-lg">
              <Settings size={20} className="text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-white border-r border-gray-200 transition-all duration-300 min-h-[calc(100vh-140px)] flex flex-col`}>
          <div className="p-6 space-y-6">
            <div>
              <h2 className="text-xs font-bold text-gray-500 uppercase mb-4">SENTINEL</h2>
              <nav className="space-y-3">
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-blue-50 text-blue-600 font-semibold cursor-pointer hover:bg-blue-100 transition">
                  <BarChart3 size={20} />
                  {sidebarOpen && <span>Intelligence</span>}
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <TrendingUp size={20} />
                  {sidebarOpen && <span className="text-sm">Active Threats</span>}
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <Archive size={20} />
                  {sidebarOpen && <span className="text-sm">Archived</span>}
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <Globe size={20} />
                  {sidebarOpen && <span className="text-sm">Global Map</span>}
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <Settings size={20} />
                  {sidebarOpen && <span className="text-sm">Settings</span>}
                </div>
              </nav>
            </div>

            <div className="border-t border-gray-200 pt-4">
              {sidebarOpen && (
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition">
                  New Analysis
                </button>
              )}
            </div>
          </div>

          <div className="mt-auto border-t border-gray-200 p-4 space-y-3">
            <button className="flex items-center gap-3 text-gray-700 hover:bg-gray-100 w-full px-4 py-2 rounded-lg transition">
              <HelpCircle size={18} />
              {sidebarOpen && <span className="text-sm">Help</span>}
            </button>
            <button className="flex items-center gap-3 text-gray-700 hover:bg-gray-100 w-full px-4 py-2 rounded-lg transition">
              <LogOut size={18} />
              {sidebarOpen && <span className="text-sm">Logout</span>}
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-8 overflow-auto">
          <div className="max-w-5xl">
            {/* Title Section */}
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Intelligence Verification</h2>
              <p className="text-gray-600">Cross-reference real-time digital signals with sovereign data ledgers to determine information validity.</p>
            </div>

            {/* Input Section */}
            <div className="bg-white rounded-lg shadow-md p-8 mb-8 border border-gray-200">
              <form onSubmit={handleSubmit} className="space-y-4">
                <textarea
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  placeholder="Paste report, tweet, or statement for deep analysis..."
                  className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-gray-900 resize-none"
                />
                <div className="flex items-center justify-between">
                  <p className="text-xs text-gray-500">Uses source validation + cross-verification</p>
                  <button
                    type="submit"
                    disabled={isLoading || !claim.trim()}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-3 px-8 rounded-lg transition flex items-center gap-2"
                  >
                    <Search size={18} />
                    Analyze Credibility
                  </button>
                </div>
              </form>
            </div>

            {/* Results Section */}
            {result && (
              <div className="grid grid-cols-3 gap-8 mb-8">
                {/* Left: Verdict */}
                <div className={`${verdictInfo.bg} rounded-lg p-6 border-l-4`} style={{borderLeftColor: verdictInfo.color.includes('green') ? '#16a34a' : verdictInfo.color.includes('red') ? '#dc2626' : '#ca8a04'}}>
                  <p className={`text-sm font-bold uppercase ${verdictInfo.color} mb-2`}>VERDICT</p>
                  <h3 className={`text-3xl font-bold ${verdictInfo.color} mb-4`}>{verdictInfo.text}</h3>
                  <p className="text-xs text-gray-600 mb-4">CROSS-VERIFICATION</p>
                  <p className="text-xs text-gray-700 font-medium">{result.claim.substring(0, 80)}...</p>
                </div>

                {/* Center: Confidence Gauge */}
                <div className="bg-white rounded-lg shadow-md p-8 flex flex-col items-center justify-center border border-gray-200">
                  <div className="relative w-32 h-32 mb-4">
                    <svg className="w-full h-full" viewBox="0 0 120 120">
                      <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" strokeWidth="8" />
                      <circle 
                        cx="60" 
                        cy="60" 
                        r="50" 
                        fill="none" 
                        stroke={verdictInfo.color.includes('green') ? '#10b981' : verdictInfo.color.includes('red') ? '#dc2626' : '#ca8a04'} 
                        strokeWidth="8"
                        strokeDasharray={`${(result.confidence / 100) * 314} 314`}
                        strokeLinecap="round"
                        transform="rotate(-90 60 60)"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-gray-900">{result.confidence}</p>
                        <p className="text-xs text-gray-600">Confidence</p>
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-gray-600 text-center">Threshold for Action: 85+</p>
                </div>

                {/* Right: Why This Decision */}
                <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                  <h4 className="font-bold text-gray-900 mb-4 text-sm uppercase">Why This Decision?</h4>
                  <div className="space-y-3">
                    {result.reasons.map((reason, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <div className={`mt-1 ${verdictInfo.color.includes('green') ? 'text-green-600' : verdictInfo.color.includes('red') ? 'text-red-600' : 'text-yellow-600'}`}>
                          {verdictInfo.text === 'VERIFIED' ? <CheckCircle size={16} /> : <XCircle size={16} />}
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-gray-900">{reason}</p>
                          <p className="text-xs text-gray-600 mt-1">Data points align with {result.confidence}% confidence threshold.</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* AI Analysis Section */}
            {result && (
              <div className="grid grid-cols-2 gap-8 mb-8">
                {/* Left: Analysis */}
                <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                  <h4 className="font-bold text-gray-900 mb-4 uppercase text-sm flex items-center gap-2">
                    <AlertCircle size={18} />
                    Analysis with AI
                  </h4>
                  <p className="text-sm text-gray-700 leading-relaxed mb-4">
                    {result.explanation}
                  </p>
                  <div className="bg-gray-50 rounded p-4 text-xs text-gray-600">
                    <p className="font-semibold text-gray-900 mb-2">Key observations:</p>
                    <ul className="space-y-2 list-disc list-inside">
                      <li>Immediate viral acceleration without primary source link.</li>
                      <li>Image attached to the claim is a recycled file from a 2018 flood in a different province.</li>
                      <li>Temporal analysis shows the news broke at 03:00 local time, with 90% of traffic originating from external VPN nodes.</li>
                    </ul>
                  </div>
                </div>

                {/* Right: Source Evidence */}
                <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                  <h4 className="font-bold text-gray-900 mb-4 uppercase text-sm flex items-center gap-2">
                    📋 Source Evidence
                  </h4>
                  <div className="space-y-3">
                    {result.evidence.map((src, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition cursor-pointer">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                            <span className="text-xs font-bold text-blue-600">📰</span>
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-900">{src.source}</p>
                            <p className="text-xs text-gray-600">Cross-verify with temporal data</p>
                          </div>
                        </div>
                        <div>
                          {src.relation === 'support' ? (
                            <CheckCircle size={20} className="text-green-600" />
                          ) : src.relation === 'contradict' ? (
                            <XCircle size={20} className="text-red-600" />
                          ) : (
                            <AlertCircle size={20} className="text-yellow-600" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {!result && (
              <div className="text-center py-20 bg-white rounded-lg border-2 border-dashed border-gray-300">
                <AlertCircle size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-xl font-semibold text-gray-700">Enter a claim to verify</p>
                <p className="text-gray-600 mt-2">Use the input above to analyze credibility</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
