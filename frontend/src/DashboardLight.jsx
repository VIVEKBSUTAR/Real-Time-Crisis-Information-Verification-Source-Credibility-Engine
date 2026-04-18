import React, { useState, useEffect } from 'react';
import { Search, Menu, Settings, Home, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

export default function DashboardLight() {
  const [claim, setClaim] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [verifications, setVerifications] = useState([]);
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

      if (!response.ok) throw new Error(`API Error: ${response.statusText}`);

      const data = await response.json();

      const verdictColor = {
        'Verified': 'bg-green-100 text-green-900 border-l-4 border-green-500',
        'Debunked': 'bg-red-100 text-red-900 border-l-4 border-red-500',
        'Uncertain': 'bg-yellow-100 text-yellow-900 border-l-4 border-yellow-500',
      }[data.verdict] || 'bg-gray-100 text-gray-900';

      const newVerification = {
        id: data.claim_id,
        claim: claim,
        verdict: data.verdict,
        confidence: Math.round(data.confidence * 100),
        explanation: data.explanation,
        evidence: data.evidence || [],
        similar_claims: data.similar_claims_found || 0,
        color: verdictColor,
      };

      setVerifications([newVerification, ...verifications]);
      setClaim('');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const SidebarItem = ({ icon: Icon, label, active = false }) => (
    <div className={`px-4 py-3 flex items-center gap-3 cursor-pointer rounded-lg transition ${
      active ? 'bg-blue-100 text-blue-900 font-semibold' : 'text-gray-700 hover:bg-gray-100'
    }`}>
      <Icon size={20} />
      <span>{label}</span>
    </div>
  );

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gray-50 border-r border-gray-200 transition-all`}>
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-blue-900">SENTINEL</h1>
          <p className="text-xs text-gray-600 mt-1">Verification Engine</p>
        </div>
        <nav className="p-4 space-y-2">
          <SidebarItem icon={Home} label="Intelligence" active />
          <SidebarItem icon={AlertCircle} label="Active Threats" />
          <SidebarItem icon={Search} label="Archived" />
          <SidebarItem icon={Menu} label="Global Map" />
          <SidebarItem icon={Settings} label="Settings" />
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Intelligence Verification</h2>
            <p className="text-sm text-gray-600 mt-1">Cross-reference real-time digital signals with sovereign data ledgers</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-green-700 bg-green-100 px-3 py-1 rounded">● SYSTEM LIVE</span>
            <span className="text-xs text-gray-600">Response ~1.8s</span>
          </div>
        </div>

        {/* Alert Strip */}
        {verifications.length === 0 && (
          <div className="bg-red-50 border-b border-red-200 px-8 py-3">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle size={18} />
              <span className="font-semibold">🔥 ACTIVE MISINFORMATION ALERTS</span>
            </div>
            <div className="text-sm text-red-700 mt-2 ml-6">
              • Bridge collapse rumor trending (23 mentions)
              • Dam burst claim flagged (low credibility)
            </div>
          </div>
        )}

        {/* Content Area */}
        <div className="flex-1 overflow-auto flex">
          {/* Input Panel - Left */}
          <div className="w-96 bg-gray-50 border-r border-gray-200 p-8">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-3">SIGNAL INGESTION</label>
                <p className="text-xs text-gray-600 mb-4">Submit claims for real-time verification</p>
                
                <textarea
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  placeholder="Paste report, tweet, or statement for deep analysis..."
                  className="w-full h-32 p-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              <button
                onClick={handleSubmit}
                disabled={isLoading}
                className="w-full bg-blue-900 hover:bg-blue-800 text-white font-bold py-3 px-4 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? '⟳ ANALYZING...' : 'ANALYZE CREDIBILITY ▶'}
              </button>

              <div className="pt-4 border-t border-gray-200">
                <label className="block text-sm font-semibold text-gray-900 mb-3">LIVE TRUST REGISTRY</label>
                <p className="text-xs text-gray-600 mb-4">Domain credibility scores</p>
                
                <div className="space-y-2">
                  {['Reuters', 'AP News', 'BBC'].map((source) => (
                    <div key={source} className="flex justify-between items-center p-3 bg-white rounded border border-gray-200">
                      <span className="text-sm text-gray-700">{source}</span>
                      <span className="text-sm font-bold text-green-700">94%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Results Panel - Right */}
          <div className="flex-1 p-8 overflow-auto bg-white">
            <label className="block text-sm font-semibold text-gray-900 mb-6 uppercase">INCIDENT VERIFICATION FEED</label>
            
            {isLoading && (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-900"></div>
              </div>
            )}

            {verifications.length === 0 && !isLoading && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-sm">No analysis yet. Submit a claim above.</p>
              </div>
            )}

            <div className="space-y-4">
              {verifications.map((verification) => (
                <div key={verification.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition">
                  {/* Verdict Header */}
                  <div className={`p-4 ${verification.color}`}>
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-xs font-bold uppercase tracking-wide">VERDICT</div>
                        <h3 className="text-2xl font-bold mt-1">{verification.verdict}</h3>
                      </div>
                      <div className="text-right bg-white bg-opacity-20 px-3 py-2 rounded">
                        <div className="text-2xl font-bold">{verification.confidence}%</div>
                        <div className="text-xs">Confidence</div>
                      </div>
                    </div>
                  </div>

                  {/* Claim */}
                  <div className="p-4 bg-gray-50 border-b border-gray-200">
                    <p className="text-sm text-gray-700 italic">"{verification.claim}"</p>
                  </div>

                  {/* Analysis */}
                  <div className="p-4">
                    <div className="mb-4">
                      <h4 className="text-xs font-bold text-gray-900 mb-2">WHY THIS DECISION?</h4>
                      <p className="text-sm text-gray-700">{verification.explanation}</p>
                    </div>

                    {/* Evidence */}
                    {verification.evidence.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <h4 className="text-xs font-bold text-gray-900 mb-3">SOURCE EVIDENCE</h4>
                        <div className="space-y-2">
                          {verification.evidence.map((ev, idx) => (
                            <div key={idx} className="flex items-start gap-3 p-2 bg-gray-50 rounded">
                              {ev.relation === 'support' ? (
                                <CheckCircle size={16} className="text-green-600 mt-0.5 flex-shrink-0" />
                              ) : (
                                <XCircle size={16} className="text-red-600 mt-0.5 flex-shrink-0" />
                              )}
                              <div className="text-sm">
                                <div className="font-semibold text-gray-900">{ev.source}</div>
                                <div className="text-xs text-gray-600 capitalize">{ev.relation}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-600">
                      <span>Similar claims found: {verification.similar_claims}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
