import React, { useState } from 'react';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

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
        evidenceSummary: data.evidence_summary,
        sources: data.sources || [],
      });
    } catch (error) {
      console.error('Error:', error);
      alert('Error analyzing claim: ' + error.message);
    }
    setIsLoading(false);
  };

  const getVerdictIcon = (verdict) => {
    if (verdict === 'VERIFIED' || verdict === 'TRUE') return <CheckCircle className="w-8 h-8 text-emerald-600" />;
    if (verdict === 'FALSE') return <XCircle className="w-8 h-8 text-rose-600" />;
    return <Clock className="w-8 h-8 text-amber-600" />;
  };

  const getVerdictColor = (verdict) => {
    if (verdict === 'VERIFIED' || verdict === 'TRUE') return { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', badge: 'bg-emerald-100 text-emerald-800' };
    if (verdict === 'FALSE') return { bg: 'bg-rose-50', border: 'border-rose-200', text: 'text-rose-700', badge: 'bg-rose-100 text-rose-800' };
    return { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', badge: 'bg-amber-100 text-amber-800' };
  };

  const verdictStyle = result ? getVerdictColor(result.verdict) : null;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Intelligence Center</h1>
      <p className="text-slate-600 mb-8">Verify claims in real-time using semantic analysis and NLI reasoning</p>

      <form onSubmit={handleSubmit} className="mb-12">
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <label className="block text-sm font-semibold text-slate-700 mb-4">Enter a claim to verify</label>
          <textarea
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            placeholder="Paste a claim you want to verify..."
            className="w-full h-32 p-4 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none text-slate-700"
          />
          <div className="mt-4 flex gap-4">
            <button
              type="submit"
              disabled={isLoading || !claim.trim()}
              className="px-6 py-2 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 disabled:bg-slate-400 disabled:cursor-not-allowed transition shadow-sm"
            >
              {isLoading ? 'Analyzing...' : 'Analyze Claim'}
            </button>
            <button
              type="button"
              onClick={() => {
                setClaim('');
                setResult(null);
              }}
              className="px-6 py-2 border border-slate-300 text-slate-700 rounded-xl font-semibold hover:bg-slate-50 transition"
            >
              Clear
            </button>
          </div>
        </div>
      </form>

      {result && (
        <div className={`${verdictStyle.bg} border-2 ${verdictStyle.border} rounded-lg p-8`}>
          <div className="flex items-start gap-6">
            <div>{getVerdictIcon(result.verdict)}</div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-4">
                <h2 className={`text-2xl font-bold ${verdictStyle.text}`}>{result.verdict}</h2>
                <span className={`${verdictStyle.badge} px-3 py-1 rounded-full text-sm font-semibold`}>
                  {result.confidence}% Confidence
                </span>
              </div>

              <div className="bg-white rounded-xl p-4 mb-4 border border-slate-200">
                <p className="text-slate-700 font-medium mb-2">Original Claim:</p>
                <p className="text-slate-600">{result.claim}</p>
              </div>

              {result.explanation && (
                <div className="bg-white rounded-xl p-4 border border-slate-200">
                  <p className="text-slate-700 font-medium mb-2">Analysis:</p>
                  <p className="text-slate-600">{result.explanation}</p>
                </div>
              )}

              {result.evidenceSummary && (
                <div className="bg-white rounded-xl p-4 border border-slate-200 mt-4">
                  <p className="text-slate-700 font-medium mb-2">Evidence Summary:</p>
                  <p className="text-slate-600">{result.evidenceSummary}</p>
                </div>
              )}

              {result.sources && result.sources.length > 0 && (
                <div className="bg-white rounded-xl p-4 border border-slate-200 mt-4">
                  <p className="text-slate-700 font-medium mb-3">Evidence Panel</p>
                  <div className="space-y-3">
                    {result.sources.slice(0, 3).map((src, idx) => (
                      <div key={`${idx}-${src.similarity}`} className="rounded-lg border border-slate-200 p-3">
                        <p className="text-sm text-slate-600">{src.text}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="ml-4 text-slate-600">Analyzing claim...</p>
        </div>
      )}
    </div>
  );
}
