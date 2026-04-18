import React, { useState } from 'react';
import { CheckCircle, XCircle, Clock, Bot } from 'lucide-react';

export default function Intelligence() {
  const [claim, setClaim] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

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
        claim: data.claim,
        verdict: data.verdict,
        confidence: Math.round(data.confidence * 100),
        explanation: data.explanation,
        evidence_summary: data.evidence_summary,
        sources: data.sources || [],
      });
    } catch (error) {
      console.error('Error:', error);
      alert('Error analyzing claim: ' + error.message);
    }
    setIsLoading(false);
  };

  const getVerdictIcon = (verdict) => {
    if (verdict === 'VERIFIED' || verdict === 'TRUE') return <CheckCircle className="w-7 h-7 text-emerald-600" />;
    if (verdict === 'FALSE') return <XCircle className="w-7 h-7 text-rose-600" />;
    return <Clock className="w-7 h-7 text-amber-600" />;
  };

  const getVerdictColor = (verdict) => {
    if (verdict === 'VERIFIED' || verdict === 'TRUE') return { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-800' };
    if (verdict === 'FALSE') return { bg: 'bg-rose-50', border: 'border-rose-200', text: 'text-rose-700', badge: 'bg-rose-100 text-rose-800' };
    return { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' };
  };

  const verdictStyle = result ? getVerdictColor(result.verdict) : null;
  const truncateText = (text, maxLength = 120) => {
    if (!text) return '';
    return text.length > maxLength ? `${text.slice(0, maxLength - 3)}...` : text;
  };

  return (
    <div className="px-8 py-6">
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-3 space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Bot size={18} className="text-indigo-600" />
              <h3 className="text-lg font-semibold text-slate-900">AI Analysis Engine</h3>
            </div>
            <p className="text-sm text-slate-600 mb-4">Analyze claims against the verified crisis dataset and retrieve the strongest supporting evidence.</p>
            <form onSubmit={handleSubmit}>
              <textarea
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                placeholder="Enter or paste a claim for verification..."
                className="w-full h-36 p-4 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none text-slate-700"
              />
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  type="submit"
                  disabled={isLoading || !claim.trim()}
                  className="px-5 py-2.5 bg-indigo-700 text-white rounded-lg text-sm font-semibold hover:bg-indigo-800 disabled:bg-slate-400 disabled:cursor-not-allowed transition"
                >
                  {isLoading ? 'Analyzing...' : 'Run Verification'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setClaim('');
                    setResult(null);
                  }}
                  className="px-5 py-2.5 border border-slate-300 text-slate-700 rounded-lg text-sm font-semibold hover:bg-slate-50 transition"
                >
                  Reset
                </button>
              </div>
            </form>
          </div>

          {result && (
            <div className={`${verdictStyle.bg} border ${verdictStyle.border} rounded-xl p-5`}>
              <div className="flex items-start gap-4">
                <div>{getVerdictIcon(result.verdict)}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <h2 className={`text-2xl font-bold ${verdictStyle.text}`}>{result.verdict}</h2>
                    <span className={`${verdictStyle.badge} px-3 py-1 rounded-full text-sm font-semibold`}>
                      {result.confidence}% Confidence
                    </span>
                  </div>

                  <div className="bg-white rounded-xl p-4 border border-slate-200 mb-4">
                    <p className="text-xs uppercase tracking-[0.12em] font-bold text-slate-500 mb-2">Claim</p>
                    <p className="text-slate-700">{result.claim}</p>
                  </div>

                  <div className="analysis-container">
                    <div className="analysis-grid">
                      <div className="left-panel bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
                        <p className="text-[11px] uppercase tracking-[0.14em] font-bold text-slate-500 mb-2">AI Explanation</p>
                        <p className="text-[15px] leading-7 text-slate-800">
                          {result.explanation || 'Explanation is not available for this claim.'}
                        </p>

                        <div className="mt-5 pt-4 border-t border-slate-200">
                          <p className="text-[11px] uppercase tracking-[0.14em] font-bold text-slate-500 mb-2">Summary</p>
                          <p className="text-sm leading-6 text-slate-600">
                            {result.evidence_summary || 'No summary available from retrieved evidence.'}
                          </p>
                        </div>
                      </div>

                      <div className="right-panel bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
                        <p className="text-[11px] uppercase tracking-[0.14em] font-bold text-slate-500 mb-3">Evidence Panel</p>
                        <div className="space-y-3">
                          {(result.sources || []).slice(0, 5).map((src, idx) => {
                            const relation = (src.relation || '').toLowerCase();
                            const relationLabel = relation === 'supports' ? 'SUPPORTS' : 'CONTRADICTS';
                            const relationClass = relation === 'supports'
                              ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
                              : 'bg-rose-100 text-rose-700 border-rose-200';
                            const similarity = typeof src.similarity === 'number' ? src.similarity.toFixed(2) : '0.00';

                            return (
                              <div key={`${idx}-${src.text || idx}`} className="rounded-lg border border-slate-200 p-3 bg-slate-50/70">
                                <p className="text-sm text-slate-700 leading-5 mb-3">{truncateText(src.text, 120)}</p>
                                <div className="flex items-center justify-between gap-2">
                                  <span className="text-xs font-medium text-slate-500">Similarity: {similarity}</span>
                                  <span className={`text-[11px] font-bold px-2 py-1 rounded-md border ${relationClass}`}>
                                    {relationLabel}
                                  </span>
                                </div>
                              </div>
                            );
                          })}
                          {(!result.sources || result.sources.length === 0) && (
                            <div className="rounded-lg border border-slate-200 p-3 bg-slate-50/70">
                              <p className="text-sm text-slate-500">No evidence sources available for this claim.</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="xl:col-span-3 space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <p className="text-xs uppercase tracking-[0.12em] font-bold text-slate-500 mb-3">System Metrics</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="rounded-lg border border-slate-200 p-3">
                <p className="text-xs text-slate-500">Dataset Claims Indexed</p>
                <p className="text-xl font-bold text-slate-900">26,232</p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <p className="text-xs text-slate-500">Average Response Time</p>
                <p className="text-xl font-bold text-slate-900">1.8s</p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <p className="text-xs text-slate-500">Engine State</p>
                <p className="text-xl font-bold text-emerald-600">Operational</p>
              </div>
            </div>
          </div>

          {isLoading && (
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <p className="text-sm text-slate-600">Running deterministic verification and evidence retrieval...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
