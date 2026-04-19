import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Search, FileText } from 'lucide-react';
import { apiUrl } from '../config/api';

export default function Archived() {
  const [claims, setClaims] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [verdictFilter, setVerdictFilter] = useState('ALL');
  const [selectedClaim, setSelectedClaim] = useState(null);

  useEffect(() => {
    const fetchClaims = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${apiUrl('/archived')}?page=${page}`);
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

  const visibleClaims = claims.filter((claim) => {
    const matchesSearch = claim.claim.toLowerCase().includes(search.toLowerCase());
    const matchesVerdict = verdictFilter === 'ALL' || claim.verdict === verdictFilter;
    return matchesSearch && matchesVerdict;
  });

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Archived Claims</h1>
      <p className="text-slate-600 mb-8">Historical claim verification records</p>

      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm mb-4 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[240px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search claims..."
            className="w-full border border-slate-300 rounded-lg pl-9 pr-3 py-2 text-sm"
          />
        </div>
        <select
          value={verdictFilter}
          onChange={(e) => setVerdictFilter(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="ALL">All Verdicts</option>
          <option value="VERIFIED">Verified</option>
          <option value="FALSE">False</option>
        </select>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 bg-white rounded-2xl shadow-sm overflow-hidden border border-slate-200">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700">Claim</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700">Verdict</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700">Confidence</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700">Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700">Action</th>
              </tr>
            </thead>
            <tbody>
              {visibleClaims.map((claim) => (
                <tr key={claim.id} className="border-b border-slate-100 hover:bg-slate-50 transition">
                  <td className="px-6 py-4 text-sm text-slate-700">{claim.claim}</td>
                  <td className="px-6 py-4">
                    <span className={`${getVerdictBadge(claim.verdict)} px-3 py-1 rounded-full text-xs font-semibold`}>
                      {claim.verdict}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-700">{claim.confidence}%</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{claim.date}</td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => setSelectedClaim(claim)}
                      className="text-xs font-semibold px-3 py-1.5 rounded-md bg-indigo-600 text-white hover:bg-indigo-700 transition"
                    >
                      View Audit Narrative
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-800 mb-3">Claim Detail Preview</h3>
          {selectedClaim ? (
            <div className="space-y-3">
              <p className="text-sm text-slate-700">{selectedClaim.claim}</p>
              <p className="text-xs text-slate-500">Verdict: {selectedClaim.verdict}</p>
              <p className="text-xs text-slate-500">Confidence: {selectedClaim.confidence}%</p>
              <p className="text-xs text-slate-500">Timestamp: {selectedClaim.date}</p>
              <button className="inline-flex items-center gap-2 text-xs font-semibold px-3 py-2 rounded-md border border-slate-300 text-slate-700 hover:bg-slate-50 transition">
                <FileText size={14} />
                View Full Report
              </button>
            </div>
          ) : (
            <p className="text-sm text-slate-500">Select a claim row to preview its audit details.</p>
          )}
        </div>
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
