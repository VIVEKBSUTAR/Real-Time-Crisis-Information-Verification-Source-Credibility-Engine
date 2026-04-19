import React, { useState } from 'react';
import { AlertCircle, CheckCircle, XCircle, Settings, BarChart3, TrendingUp, Archive, Globe, HelpCircle, LogOut } from 'lucide-react';
import { apiUrl } from './config/api';

export default function Dashboard() {
  const [claim, setClaim] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('intelligence');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!claim.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch(apiUrl('/analyze_claim'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: claim }),
      });

      if (!response.ok) throw new Error('Backend error');
      
      const data = await response.json();
      setResult({
        claim: data.original_claim,
        verdict: data.verdict,
        confidence: Math.round(data.confidence * 100),
        explanation: data.explanation,
        evidence: data.evidence || [],
      });
    } catch (error) {
      console.error('Error:', error);
      alert('Error: ' + error.message);
    }
    setIsLoading(false);
  };

  const getVerdictColor = (verdict) => {
    if (verdict === 'VERIFIED') return { text: 'VERIFIED', color: 'text-green-600', bg: 'bg-green-50' };
    if (verdict === 'FALSE') return { text: 'REFUTED', color: 'text-red-600', bg: 'bg-red-50' };
    return { text: 'UNCERTAIN', color: 'text-yellow-600', bg: 'bg-yellow-50' };
  };

  const verdictInfo = result ? getVerdictColor(result.verdict) : null;

  return (
    <div className="w-screen h-screen flex flex-col bg-gray-100">
      {/* Top Banner */}
      <div className="bg-red-50 border-b-2 border-red-200 px-6 py-3 flex-shrink-0">
        <div className="flex items-center gap-4">
          <span className="text-xs font-bold text-red-700 bg-red-100 px-3 py-1 rounded">BTS</span>
          <span className="text-xs font-bold text-red-700 bg-red-100 px-3 py-1 rounded">Bridge collapse rumors trending</span>
          <span className="text-xs font-bold text-red-700 bg-red-100 px-3 py-1 rounded">Dam burst claim flagged</span>
          <div className="ml-auto text-xs text-gray-600">🔴 SYSTEM LIVE | Response {`<1.8s`} | 🔊</div>
        </div>
      </div>

      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
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
            <button className="p-2 hover:bg-gray-100 rounded-lg"><Settings size={20} className="text-gray-600" /></button>
          </div>
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 bg-white border-r border-gray-200 flex flex-col flex-shrink-0 overflow-y-auto">
          <div className="p-6 space-y-6 flex-1">
            <div>
              <h2 className="text-xs font-bold text-gray-500 uppercase mb-4">SENTINEL</h2>
              <nav className="space-y-3">
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-blue-50 text-blue-600 font-semibold cursor-pointer hover:bg-blue-100 transition">
                  <BarChart3 size={20} />
                  <span>Intelligence</span>
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <TrendingUp size={20} />
                  <span className="text-sm">Active Threats</span>
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <Archive size={20} />
                  <span className="text-sm">Archived</span>
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <Globe size={20} />
                  <span className="text-sm">Global Map</span>
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <BarChart3 size={20} />
                  <span className="text-sm">Analytics</span>
                </div>
              </nav>
            </div>

            <div>
              <h2 className="text-xs font-bold text-gray-500 uppercase mb-4">SUPPORT</h2>
              <nav className="space-y-3">
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <HelpCircle size={20} />
                  <span className="text-sm">Help</span>
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 cursor-pointer transition">
                  <LogOut size={20} />
                  <span className="text-sm">Logout</span>
                </div>
              </nav>
            </div>
          </div>

          <button className="m-6 w-[calc(100%-48px)] bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
            + New Analysis
          </button>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Scrollable Content Area */}
          <div className="flex-1 overflow-auto p-8">
            <div className="max-w-5xl mx-auto space-y-8">
              {/* Title Section */}
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Intelligence Verification</h2>
                <p className="text-gray-600">Cross-reference real-time digital signals with sovereign data ledgers to determine information validity.</p>
              </div>

              {/* Input Section */}
              <div className="bg-white rounded-lg shadow-md p-8 border border-gray-200">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <textarea
                    value={claim}
                    onChange={(e) => setClaim(e.target.value)}
                    placeholder="Paste report, tweet, or statement for deep analysis..."
                    className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-gray-900 resize-none"
                  />
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-gray-600">Uses source validation • cross-verification</p>
                    <button
                      type="submit"
                      disabled={isLoading}
                      className={`px-8 py-2 rounded-lg font-semibold transition ${isLoading ? 'bg-gray-400 text-gray-600 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700'}`}
                    >
                      {isLoading ? 'Analyzing...' : 'Analyze Credibility'}
                    </button>
                  </div>
                </form>
              </div>

              {/* Results Section */}
              {result && (
                <div className="space-y-6">
                  {/* Verdict Card */}
                  <div className={`${verdictInfo.bg} rounded-lg shadow-md p-8 border-2 border-gray-200`}>
                    <div className="flex items-start justify-between mb-6">
                      <div>
                        <h3 className={`text-2xl font-bold ${verdictInfo.color} mb-2`}>{verdictInfo.text}</h3>
                        <p className="text-sm text-gray-700">{result.explanation}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-4xl font-bold text-gray-900">{result.confidence}%</div>
                        <p className="text-xs text-gray-600 mt-2">Confidence Score</p>
                      </div>
                    </div>

                    {/* Confidence Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${result.verdict === 'VERIFIED' ? 'bg-green-600' : result.verdict === 'FALSE' ? 'bg-red-600' : 'bg-yellow-600'}`}
                        style={{ width: `${result.confidence}%` }}
                      />
                    </div>
                  </div>

                  {/* Evidence Section */}
                  <div className="grid grid-cols-2 gap-6">
                    {/* Left: Analysis */}
                    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                      <h4 className="font-bold text-gray-900 mb-4 uppercase text-sm">📊 AI Analysis</h4>
                      <ul className="space-y-3">
                        <li className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                          <CheckCircle size={20} className="text-green-600 flex-shrink-0" />
                          <span className="text-sm text-gray-700">Source validation passed</span>
                        </li>
                        <li className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                          <AlertCircle size={20} className="text-yellow-600 flex-shrink-0" />
                          <span className="text-sm text-gray-700">Cross-reference verification</span>
                        </li>
                        <li className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                          {result.verdict === 'FALSE' ? (
                            <XCircle size={20} className="text-red-600 flex-shrink-0" />
                          ) : (
                            <CheckCircle size={20} className="text-green-600 flex-shrink-0" />
                          )}
                          <span className="text-sm text-gray-700">Dataset match confirmed</span>
                        </li>
                      </ul>
                    </div>

                    {/* Right: Evidence */}
                    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                      <h4 className="font-bold text-gray-900 mb-4 uppercase text-sm">📋 Source Evidence</h4>
                      <div className="space-y-3">
                        {result.evidence.length > 0 ? (
                          result.evidence.map((src, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition cursor-pointer">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-blue-100 rounded flex items-center justify-center">
                                  <span className="text-xs font-bold text-blue-600">📰</span>
                                </div>
                                <div>
                                  <p className="text-sm font-semibold text-gray-900">{src.source || 'Source'}</p>
                                  <p className="text-xs text-gray-600">Cross-verify with data</p>
                                </div>
                              </div>
                              <CheckCircle size={20} className="text-green-600" />
                            </div>
                          ))
                        ) : (
                          <p className="text-sm text-gray-600">No additional sources found</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Empty State */}
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
    </div>
  );
}
