import React, { useMemo, useState } from 'react';
import { CheckCircle, XCircle, Clock, Bot, GitBranch, ChevronDown, ChevronUp, Upload } from 'lucide-react';
import ReactFlow, { Background, Controls, MiniMap, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';
import { apiUrl } from '../config/api';

export default function Intelligence() {
  const [claim, setClaim] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showGraph, setShowGraph] = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);
  const [imageBase64, setImageBase64] = useState('');
  const [imageName, setImageName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!claim.trim() && !imageBase64) return;

    setIsLoading(true);
    try {
      const response = await fetch(apiUrl('/analyze_claim'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: claim, image_base64: imageBase64 }),
      });

      if (!response.ok) throw new Error('Backend error');

      const data = await response.json();
      const normalizedSources = Array.isArray(data.sources) && data.sources.length > 0
        ? data.sources
        : (data.supporting_sources || []).map((src) => ({
            text: src.text || src.quote || '',
            similarity: typeof src.similarity === 'number'
              ? src.similarity
              : (typeof src.confidence === 'number' ? src.confidence : 0.0),
            label: src.relation === 'support' ? 'TRUE' : 'FALSE',
            relation: src.relation === 'support' ? 'supports' : 'neutral',
            score: typeof src.confidence === 'number' ? src.confidence : 0.0,
            source: src.source_name || 'Dataset Source',
          }));
      setResult({
        claim: data.claim,
        verdict: data.verdict,
        confidence: Math.round(data.confidence * 100),
        explanation: data.explanation,
        evidence_summary: data.evidence_summary,
        sources: normalizedSources,
        extracted_text: data.extracted_text || '',
        sourceGraph: data.source_credibility_graph || { nodes: [], edges: [], source_evidence: {} },
      });
      setShowGraph(false);
      setSelectedSource(null);
    } catch (error) {
      console.error('Error:', error);
      alert('Error analyzing claim: ' + error.message);
    }
    setIsLoading(false);
  };

  const handleImageUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const result = typeof reader.result === 'string' ? reader.result : '';
      setImageBase64(result);
      setImageName(file.name);
    };
    reader.readAsDataURL(file);
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

  const graphNodesAndEdges = useMemo(() => {
    if (!result) return { nodes: [], edges: [], stats: { nodes: 0, edges: 0, avgTrust: 0 } };
    const graphNodes = (result.sourceGraph?.nodes || []).slice();
    const graphEdges = (result.sourceGraph?.edges || []).slice();
    const sourceEvidence = result.sourceGraph?.source_evidence || {};
    const hasSingleGenericNode =
      graphNodes.length === 1 &&
      ['dataset', 'unknown', 'unknown source', 'dataset source'].includes(String(graphNodes[0]?.id || '').toLowerCase());

    // Fallback graph synthesis for responses that don't return source_credibility_graph.
    if ((graphNodes.length === 0 || hasSingleGenericNode) && Array.isArray(result.sources) && result.sources.length > 0) {
      const grouped = {};
      result.sources.forEach((item, idx) => {
        const rawSource = String(item.source || '').trim();
        const relation = String(item.relation || 'neutral').toLowerCase();
        const useSyntheticSource = !rawSource || ['dataset', 'unknown', 'unknown source', 'dataset source'].includes(rawSource.toLowerCase());
        const sourceName = useSyntheticSource
          ? `Evidence ${idx + 1} (${relation})`
          : rawSource;
        if (!grouped[sourceName]) grouped[sourceName] = [];
        grouped[sourceName].push(item);
      });
      const sourceNames = Object.keys(grouped);
      sourceNames.forEach((name) => {
        const evidence = grouped[name];
        const avgSimilarity = evidence.reduce((acc, e) => acc + (Number(e.similarity) || 0), 0) / Math.max(evidence.length, 1);
        const supportCount = evidence.filter((e) => (e.relation || '').toLowerCase() === 'supports').length;
        const trust = Math.max(0.2, Math.min(0.95, (avgSimilarity * 0.7) + ((supportCount / Math.max(evidence.length, 1)) * 0.3)));
        graphNodes.push({
          id: name,
          trust,
          influence: 0,
          low_credibility: trust < 0.3,
        });
        sourceEvidence[name] = evidence.slice(0, 5).map((e) => ({
          text: e.text || '',
          relation: e.relation || 'neutral',
          label: e.label || 'UNKNOWN',
          similarity: Number(e.similarity) || 0,
        }));
      });
      for (let i = 0; i < sourceNames.length; i += 1) {
        for (let j = i + 1; j < sourceNames.length; j += 1) {
          const left = grouped[sourceNames[i]];
          const right = grouped[sourceNames[j]];
          const leftSim = left.reduce((acc, e) => acc + (Number(e.similarity) || 0), 0) / Math.max(left.length, 1);
          const rightSim = right.reduce((acc, e) => acc + (Number(e.similarity) || 0), 0) / Math.max(right.length, 1);
          graphEdges.push({
            source: sourceNames[i],
            target: sourceNames[j],
            weight: Number(((leftSim + rightSim) / 2).toFixed(2)),
          });
        }
      }
    }

    const total = graphNodes.length || 1;
    const radius = Math.min(220, 80 + total * 18);
    const centerX = 260;
    const centerY = 190;

    const getTrustColor = (trust) => {
      if (trust > 0.7) return { bg: '#dcfce7', border: '#16a34a', text: '#166534' };
      if (trust >= 0.4) return { bg: '#fef9c3', border: '#ca8a04', text: '#713f12' };
      return { bg: '#fee2e2', border: '#dc2626', text: '#7f1d1d' };
    };

    const nodes = graphNodes.map((node, index) => {
      const angle = (2 * Math.PI * index) / total;
      const color = getTrustColor(node.trust || 0);
      const tooltip = `Trust: ${(node.trust || 0).toFixed(2)} | Influence: ${(node.influence || 0).toFixed(2)}`;
      return {
        id: node.id,
        position: {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        },
        data: {
          label: (
            <div title={tooltip} className="text-center">
              <div className="text-xs font-semibold">{node.id}</div>
              <div className="text-[11px]">Trust {(node.trust || 0).toFixed(2)}</div>
              <div className="text-[10px] text-slate-500">Influence {(node.influence || 0).toFixed(2)}</div>
              {node.low_credibility && (
                <div className="text-[10px] font-semibold text-rose-700">⚠ Low credibility</div>
              )}
            </div>
          ),
          trust: node.trust || 0,
          influence: node.influence || 0,
          low_credibility: !!node.low_credibility,
        },
        style: {
          background: color.bg,
          border: `2px solid ${color.border}`,
          color: color.text,
          borderRadius: 14,
          padding: 8,
          minWidth: 130,
          boxShadow: '0 8px 24px rgba(15, 23, 42, 0.08)',
        },
      };
    });

    const edges = graphEdges.map((edge, idx) => ({
      id: `e-${edge.source}-${edge.target}-${idx}`,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: (edge.weight || 0) > 0.7,
      label: `${(edge.weight || 0).toFixed(2)}`,
      style: {
        strokeWidth: Math.max(1, Math.round((edge.weight || 0) * 5)),
        stroke: '#475569',
      },
      labelStyle: { fill: '#475569', fontSize: 10 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 14,
        height: 14,
        color: '#475569',
      },
    }));

    const avgTrust = graphNodes.length > 0
      ? graphNodes.reduce((acc, n) => acc + (Number(n.trust) || 0), 0) / graphNodes.length
      : 0;

    return {
      nodes,
      edges,
      stats: {
        nodes: graphNodes.length,
        edges: graphEdges.length,
        avgTrust: Number(avgTrust.toFixed(2)),
      },
    };
  }, [result]);

  const selectedSourceEvidence = result?.sourceGraph?.source_evidence?.[selectedSource] || [];

  const truncateText = (text, maxLength = 120) => {
    if (!text) return '';
    return text.length > maxLength ? `${text.slice(0, maxLength - 3)}...` : text;
  };

  return (
    <div className="px-8 py-6 page-enter">
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-3 space-y-6">
          <div className="glass-panel border border-slate-200 rounded-xl p-5 shadow-sm section-enter hover-lift">
            <p className="kicker mb-2">AI Verification Studio</p>
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
                className="w-full h-36 p-4 input-pro rounded-xl focus:outline-none resize-none text-slate-700 transition-all duration-200"
              />
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  type="submit"
                  disabled={isLoading || (!claim.trim() && !imageBase64)}
                  className="px-5 py-2.5 btn-primary-pro rounded-lg text-sm font-semibold disabled:bg-slate-400 disabled:cursor-not-allowed transition hover-lift"
                >
                  {isLoading ? 'Analyzing...' : 'Run Verification'}
                </button>
                <label className="px-5 py-2.5 border border-slate-300 bg-white/75 text-slate-700 rounded-lg text-sm font-semibold hover:bg-slate-50 transition cursor-pointer inline-flex items-center gap-2 hover-lift">
                  <Upload size={16} />
                  Upload Image
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/jpg"
                    className="hidden"
                    onChange={handleImageUpload}
                  />
                </label>
                <button
                  type="button"
                    onClick={() => {
                      setClaim('');
                      setResult(null);
                      setShowGraph(false);
                      setSelectedSource(null);
                      setImageBase64('');
                      setImageName('');
                    }}
                    className="px-5 py-2.5 border border-slate-300 bg-white/75 text-slate-700 rounded-lg text-sm font-semibold hover:bg-slate-50 transition hover-lift"
                  >
                  Reset
                </button>
              </div>
              {imageName && (
                <p className="mt-3 text-xs text-slate-500">Image selected: {imageName}</p>
              )}
            </form>
          </div>

          {result && (
            <div className={`${verdictStyle.bg} border ${verdictStyle.border} rounded-xl p-5 section-enter`}>
              <div className="flex items-start gap-4">
                <div>{getVerdictIcon(result.verdict)}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <h2 className={`text-2xl font-bold ${verdictStyle.text}`}>{result.verdict}</h2>
                    <span className={`${verdictStyle.badge} px-3 py-1 rounded-full text-sm font-semibold`}>
                      {result.confidence}% Confidence
                    </span>
                  </div>

                  <div className="glass-panel rounded-xl p-4 border border-slate-200 mb-4 hover-lift">
                    <p className="text-xs uppercase tracking-[0.12em] font-bold text-slate-500 mb-2">Claim</p>
                    <p className="text-slate-700">{result.claim}</p>
                  </div>

                  {result.extracted_text && (
                    <div className="glass-panel rounded-xl p-4 border border-slate-200 mb-4 hover-lift">
                      <p className="text-xs uppercase tracking-[0.12em] font-bold text-slate-500 mb-2">Extracted OCR Text</p>
                      <p className="text-slate-700">{result.extracted_text}</p>
                    </div>
                  )}

                  <div className="analysis-container">
                    <div className="analysis-grid">
                      <div className="left-panel glass-panel rounded-xl p-5 border border-slate-200 shadow-sm hover-lift">
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

                      <div className="right-panel glass-panel rounded-xl p-4 border border-slate-200 shadow-sm hover-lift">
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
                              <div key={`${idx}-${src.text || idx}`} className="rounded-lg border border-slate-200 p-3 bg-slate-50/70 hover-lift transition-all duration-200">
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

                  <div className="mt-5 glass-panel rounded-xl p-4 border border-slate-200 shadow-sm hover-lift">
                    <button
                      type="button"
                      onClick={() => setShowGraph((prev) => !prev)}
                      className="w-full flex items-center justify-between text-left"
                    >
                      <div className="flex items-center gap-2">
                        <GitBranch size={16} className="text-indigo-600" />
                        <span className="text-sm font-semibold text-slate-800">Dynamic Source Credibility Graph</span>
                      </div>
                      {showGraph ? <ChevronUp size={16} className="text-slate-500" /> : <ChevronDown size={16} className="text-slate-500" />}
                    </button>

                    {showGraph && (
                      <div className="mt-4 grid grid-cols-1 xl:grid-cols-3 gap-4">
                        <div className="xl:col-span-2 border border-slate-200 rounded-lg overflow-hidden bg-gradient-to-br from-slate-50 to-slate-100 hover-lift" style={{ height: 420 }}>
                          {graphNodesAndEdges.nodes.length > 0 ? (
                            <ReactFlow
                              nodes={graphNodesAndEdges.nodes}
                              edges={graphNodesAndEdges.edges}
                              fitView
                              minZoom={0.5}
                              maxZoom={1.7}
                              onNodeClick={(_, node) => setSelectedSource(node.id)}
                            >
                              <MiniMap pannable zoomable />
                              <Controls showInteractive />
                              <Background gap={16} size={1} color="#cbd5e1" />
                            </ReactFlow>
                          ) : (
                            <div className="h-full w-full flex items-center justify-center text-center p-8">
                              <div>
                                <p className="text-sm font-semibold text-slate-700">No graph data available for this query</p>
                                <p className="mt-2 text-xs text-slate-500">
                                  Try a more specific claim or include an image with readable source text.
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                        <div className="border border-slate-200 rounded-lg bg-slate-50 p-3 hover-lift">
                          <div className="grid grid-cols-3 gap-2 mb-3">
                            <div className="rounded-md border border-slate-200 bg-white px-2 py-1.5">
                              <p className="text-[10px] text-slate-500">Nodes</p>
                              <p className="text-sm font-semibold text-slate-800">{graphNodesAndEdges.stats?.nodes || 0}</p>
                            </div>
                            <div className="rounded-md border border-slate-200 bg-white px-2 py-1.5">
                              <p className="text-[10px] text-slate-500">Edges</p>
                              <p className="text-sm font-semibold text-slate-800">{graphNodesAndEdges.stats?.edges || 0}</p>
                            </div>
                            <div className="rounded-md border border-slate-200 bg-white px-2 py-1.5">
                              <p className="text-[10px] text-slate-500">Avg Trust</p>
                              <p className="text-sm font-semibold text-slate-800">{(graphNodesAndEdges.stats?.avgTrust || 0).toFixed(2)}</p>
                            </div>
                          </div>
                          <div className="mb-3 rounded-md border border-slate-200 bg-white p-2">
                            <p className="text-[10px] uppercase tracking-[0.1em] text-slate-500 mb-1">Legend</p>
                            <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-600">
                              <span className="inline-flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />High Trust</span>
                              <span className="inline-flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-yellow-500" />Medium Trust</span>
                              <span className="inline-flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-rose-500" />Low Trust</span>
                            </div>
                          </div>
                          <p className="text-xs uppercase tracking-[0.12em] font-bold text-slate-500 mb-2">
                            {selectedSource ? `Source: ${selectedSource}` : 'Source Evidence'}
                          </p>
                          {selectedSource ? (
                            <div className="space-y-2 max-h-[360px] overflow-auto pr-1">
                              {selectedSourceEvidence.length > 0 ? (
                                selectedSourceEvidence.map((item, idx) => (
                                  <div key={`${selectedSource}-${idx}`} className="rounded-md border border-slate-200 bg-white p-2">
                                    <p className="text-xs text-slate-700">{truncateText(item.text, 110)}</p>
                                    <p className="mt-1 text-[11px] text-slate-500">
                                      {item.relation?.toUpperCase()} • {String(item.label).toUpperCase()} • sim {(item.similarity || 0).toFixed(2)}
                                    </p>
                                  </div>
                                ))
                              ) : (
                                <p className="text-xs text-slate-500">No evidence linked to this source.</p>
                              )}
                            </div>
                          ) : (
                            <p className="text-xs text-slate-500">Click a node to inspect evidence and trust context.</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="xl:col-span-3 space-y-5">
          <div className="glass-panel border border-slate-200 rounded-xl p-4 shadow-sm section-enter hover-lift">
            <p className="text-xs uppercase tracking-[0.12em] font-bold text-slate-500 mb-3">System Metrics</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="rounded-lg border border-slate-200 p-3 kpi-card hover-lift">
                <p className="text-xs text-slate-500">Dataset Claims Indexed</p>
                <p className="text-xl font-bold text-slate-900">26,232</p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3 kpi-card hover-lift">
                <p className="text-xs text-slate-500">Average Response Time</p>
                <p className="text-xl font-bold text-slate-900">1.8s</p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3 kpi-card hover-lift">
                <p className="text-xs text-slate-500">Engine State</p>
                <p className="text-xl font-bold text-emerald-600">Operational</p>
              </div>
            </div>
          </div>

          {isLoading && (
            <div className="glass-panel border border-slate-200 rounded-xl p-4 shadow-sm section-enter">
              <p className="text-sm text-slate-600 mb-2">Running deterministic verification and evidence retrieval...</p>
              <div className="h-2 w-full rounded-full animated-shimmer" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
