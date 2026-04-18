import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Archived() {
  const [claims, setClaims] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClaims = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/archived?page=${page}`);
        if (response.ok) {
          const data = await response.json();
          setClaims(data.claims);
          setTotalPages(data.total_pages);
        }
      } catch (error) {
        console.error('Error fetching claims:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchClaims();
  }, [page]);

  const getVerdictBadge = (verdict) => {
    if (verdict === 'VERIFIED') return 'bg-emerald-100 text-emerald-800';
    if (verdict === 'FALSE') return 'bg-rose-100 text-rose-800';
    return 'bg-amber-100 text-amber-800';
  };

  if (loading) {
      return (
        <div className="p-8 flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Archived Claims</h1>
      <p className="text-slate-600 mb-8">Historical claim verification records</p>

      <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-slate-200">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700">Claim</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700">Verdict</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700">Confidence</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700">Date</th>
            </tr>
          </thead>
          <tbody>
            {claims.map((claim) => (
              <tr key={claim.id} className="border-b border-slate-100 hover:bg-slate-50 transition">
                <td className="px-6 py-4 text-sm text-slate-700">{claim.claim}</td>
                <td className="px-6 py-4">
                  <span className={`${getVerdictBadge(claim.verdict)} px-3 py-1 rounded-full text-xs font-semibold`}>
                    {claim.verdict}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-slate-700">{claim.confidence}%</td>
                <td className="px-6 py-4 text-sm text-slate-600">{claim.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 flex items-center justify-between">
        <p className="text-sm text-slate-600">
          Page {page} of {totalPages}
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="p-2 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => (
            <button
              key={i + 1}
              onClick={() => setPage(i + 1)}
              className={`px-3 py-1 rounded-lg transition ${
                page === i + 1 ? 'bg-indigo-600 text-white' : 'border border-slate-300 hover:bg-slate-50'
              }`}
            >
              {i + 1}
            </button>
          ))}
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="p-2 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
