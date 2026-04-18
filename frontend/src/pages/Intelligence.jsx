import React, { useState } from 'react';
import { AlertCircle, CheckCircle, XCircle, Clock } from 'lucide-react';

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
      });
    } catch (error) {
      console.error('Error:', error);
      alert('Error analyzing claim: ' + error.message);
    }
    setIsLoading(false);
  };

  const getVerdictIcon = (verdict) => {
    if (verdict === 'VERIFIED') return <CheckCircle className="w-8 h-8 text-green-600" />;
    if (verdict === 'FALSE') return <XCircle className="w-8 h-8 text-red-600" />;
    return <Clock className="w-8 h-8 text-yellow-600" />;
  };

  const getVerdictColor = (verdict) => {
    if (verdict === 'VERIFIED') return { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', badge: 'bg-green-100 text-green-800' };
    if (verdict === 'FALSE') return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', badge: 'bg-red-100 text-red-800' };
    return { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700', badge: 'bg-yellow-100 text-yellow-800' };
  };

  const verdictStyle = result ? getVerdictColor(result.verdict) : null;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Intelligence Center</h1>
      <p className="text-gray-600 mb-8">Verify claims in real-time using semantic analysis and NLI reasoning</p>

      <form onSubmit={handleSubmit} className="mb-12">
        <div className="bg-white rounded-lg border-2 border-gray-200 p-6 shadow-sm">
          <label className="block text-sm font-semibold text-gray-700 mb-4">Enter a claim to verify</label>
          <textarea
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            placeholder="Paste a claim you want to verify..."
            className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
          <div className="mt-4 flex gap-4">
            <button
              type="submit"
              disabled={isLoading || !claim.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {isLoading ? 'Analyzing...' : 'Analyze Claim'}
            </button>
            <button
              type="button"
              onClick={() => {
                setClaim('');
                setResult(null);
              }}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
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

              <div className="bg-white rounded-lg p-4 mb-4">
                <p className="text-gray-700 font-medium mb-2">Original Claim:</p>
                <p className="text-gray-600">{result.claim}</p>
              </div>

              {result.explanation && (
                <div className="bg-white rounded-lg p-4">
                  <p className="text-gray-700 font-medium mb-2">Analysis:</p>
                  <p className="text-gray-600">{result.explanation}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Analyzing claim...</p>
        </div>
      )}
    </div>
  );
}
