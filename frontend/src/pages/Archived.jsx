import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Archived() {
  const [claims, setClaims] = useState([]);
  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    // Mock archived claims
    const mockClaims = Array.from({ length: 45 }, (_, i) => ({
      id: i + 1,
      claim: `Sample claim ${i + 1}: A detailed misinformation claim that was analyzed and archived.`,
      verdict: ['VERIFIED', 'FALSE', 'UNCERTAIN'][i % 3],
      confidence: Math.floor(Math.random() * 40) + 60,
      date: new Date(Date.now() - i * 86400000).toLocaleDateString(),
    }));
    setClaims(mockClaims);
  }, []);

  const start = (page - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const displayClaims = claims.slice(start, end);
  const totalPages = Math.ceil(claims.length / itemsPerPage);

  const getVerdictBadge = (verdict) => {
    if (verdict === 'VERIFIED') return 'bg-green-100 text-green-800';
    if (verdict === 'FALSE') return 'bg-red-100 text-red-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Archived Claims</h1>
      <p className="text-gray-600 mb-8">Historical claim verification records</p>

      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Claim</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Verdict</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Confidence</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700">Date</th>
            </tr>
          </thead>
          <tbody>
            {displayClaims.map((claim) => (
              <tr key={claim.id} className="border-b border-gray-100 hover:bg-gray-50 transition">
                <td className="px-6 py-4 text-sm text-gray-700">{claim.claim.substring(0, 50)}...</td>
                <td className="px-6 py-4">
                  <span className={`${getVerdictBadge(claim.verdict)} px-3 py-1 rounded-full text-xs font-semibold`}>
                    {claim.verdict}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-700">{claim.confidence}%</td>
                <td className="px-6 py-4 text-sm text-gray-600">{claim.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Showing {start + 1}–{Math.min(end, claims.length)} of {claims.length} claims
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          {Array.from({ length: totalPages }, (_, i) => (
            <button
              key={i + 1}
              onClick={() => setPage(i + 1)}
              className={`px-3 py-1 rounded-lg transition ${
                page === i + 1 ? 'bg-blue-600 text-white' : 'border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {i + 1}
            </button>
          ))}
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
