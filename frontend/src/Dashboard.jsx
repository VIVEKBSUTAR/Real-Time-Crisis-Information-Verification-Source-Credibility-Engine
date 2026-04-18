import React, { useState } from 'react';
import { 
  AlertCircle, Zap, Menu, Brain, Archive, Clock, Settings,
  ChevronDown, Share2, Bookmark, Flag, Download, Network,
  AlertTriangle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [claim, setClaim] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [verifications, setVerifications] = useState([]);
  const [showGraphModal, setShowGraphModal] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const trustData = [
    { time: '10:00', reuters: 91, apnews: 93, bbc: 83 },
    { time: '10:15', reuters: 92, apnews: 91, bbc: 85 },
    { time: '10:30', reuters: 94, apnews: 90, bbc: 86 },
    { time: '10:45', reuters: 93, apnews: 91, bbc: 88 },
    { time: '11:00', reuters: 94, apnews: 89, bbc: 87 },
  ];

  // Professional API-integrated handler
  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!claim.trim()) return;

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/analyze_claim', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_type: 'text',
          source: 'direct_input',
          content: claim,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const data = await response.json();

      const newVerification = {
        id: data.claim_id || Date.now(),
        claim: claim || 'No claim provided',
        verdict: data.label || 'Unverified',
        color: data.label === 'TRUE' ? '#10B981' : '#ff6b35',
        confidence: Math.round(data.confidence * 100) || 52,
        analysis: data.explanation || 'Unable to determine claim veracity at this time.',
        supportingSources: data.supporting_sources || [
          { name: 'No sources found', quote: 'Dataset search in progress' }
        ],
        missingSources: data.missing_sources || [
          'No corroborating sources found in dataset'
        ],
        hasExifWarning: false,
        sourcesChecked: data.sources_checked || 0,
      };

      setVerifications([newVerification, ...verifications]);
      setClaim('');
    } catch (error) {
      console.error('Error analyzing claim:', error);
      
      const errorVerification = {
        id: Date.now(),
        claim: claim || 'No claim provided',
        verdict: 'Error',
        color: '#ff6b35',
        confidence: 0,
        analysis: `Error connecting to verification service: ${error.message}. Please ensure backend is running on http://localhost:8000`,
        supportingSources: [],
        missingSources: ['Backend connection failed'],
        hasExifWarning: false,
        sourcesChecked: 0,
      };
      
      setVerifications([errorVerification, ...verifications]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ background: '#1a1a1a', minHeight: '100vh', display: 'flex' }}>
      {/* SIDEBAR */}
      <aside 
        style={{
          background: '#0f0f0f',
          width: sidebarOpen ? '280px' : '60px',
          borderRight: '1px solid #2d2d2d',
          transition: 'width 300ms',
          padding: '20px 0',
        }}
        className="flex flex-col"
      >
        <div style={{ padding: '0 16px', marginBottom: '40px' }}>
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{ background: 'transparent', border: 'none', color: '#e0e0e0', cursor: 'pointer' }}
          >
            <Menu size={20} />
          </button>
        </div>

        <nav style={{ flex: 1 }}>
          {[
            { icon: Brain, label: 'INTELLIGENCE' },
            { icon: Archive, label: 'ARCHIVES' },
            { icon: Clock, label: 'HISTORY' },
            { icon: Settings, label: 'SETTINGS' },
          ].map((item, idx) => (
            <button
              key={idx}
              style={{
                width: '100%',
                padding: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                background: 'transparent',
                border: 'none',
                color: '#9a9a9a',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500',
                letterSpacing: '0.5px',
                transition: 'color 200ms',
              }}
              onMouseEnter={(e) => e.target.style.color = '#e0e0e0'}
              onMouseLeave={(e) => e.target.style.color = '#9a9a9a'}
            >
              <item.icon size={18} />
              {sidebarOpen && <span>{item.label}</span>}
            </button>
          ))}
        </nav>

        <div style={{ padding: '0 16px', borderTop: '1px solid #2d2d2d', paddingTop: '16px' }}>
          <div style={{ color: '#6a6a6a', fontSize: '11px', letterSpacing: '0.5px' }}>
            SYSTEM STATUS
          </div>
          <div style={{ color: '#10B981', fontSize: '12px', fontWeight: 'bold', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '6px', height: '6px', background: '#10B981', borderRadius: '50%' }}></span>
            LIVE
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* HEADER */}
        <header style={{ borderBottom: '1px solid #2d2d2d', padding: '20px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ color: '#e0e0e0', fontSize: '18px', fontWeight: '700', margin: 0, letterSpacing: '1px' }}>Sentinel Protocol</h1>
            <p style={{ color: '#6a6a6a', fontSize: '11px', margin: '4px 0 0 0', letterSpacing: '0.5px' }}>Real-Time Crisis Information Verification</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <div style={{ textAlign: 'right', fontSize: '12px', color: '#e0e0e0', letterSpacing: '0.5px' }}>
              <div style={{ color: '#10B981', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '8px', height: '8px', background: '#10B981', borderRadius: '50%' }}></span>
                System Live
              </div>
              <div style={{ color: '#6a6a6a', fontSize: '11px', marginTop: '2px' }}>Response ~1.8s</div>
            </div>
          </div>
        </header>

        {/* ALERT STRIP */}
        <div style={{ background: '#2d1a1a', borderBottom: '1px solid #5f2626', padding: '12px 32px', display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: '#ff6b35', letterSpacing: '0.5px' }}>
          <AlertCircle size={16} />
          <span style={{ fontWeight: '600' }}>🔥 ACTIVE MISINFORMATION ALERTS</span>
          <span style={{ color: '#6a6a6a' }}>•</span>
          <span>Bridge collapse rumor trending (23 mentions)</span>
          <span style={{ color: '#6a6a6a' }}>•</span>
          <span>Dam burst claim flagged (low credibility)</span>
        </div>

        {/* BODY */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', flex: 1, gap: '0' }}>
          {/* LEFT PANEL */}
          <div style={{ borderRight: '1px solid #2d2d2d', padding: '32px', display: 'flex', flexDirection: 'column', background: '#0f0f0f' }}>
            {/* INPUT SECTION */}
            <div>
              <h3 style={{ color: '#e0e0e0', fontSize: '14px', fontWeight: '700', margin: '0 0 12px 0', letterSpacing: '1px' }}>SIGNAL INGESTION</h3>
              <p style={{ color: '#6a6a6a', fontSize: '11px', margin: '0 0 20px 0', letterSpacing: '0.5px' }}>Submit claims for real-time verification</p>

              <form onSubmit={handleAnalyze} style={{ marginBottom: '32px' }}>
                <textarea
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  placeholder="Enter claim for verification..."
                  style={{
                    width: '100%',
                    height: '120px',
                    background: '#1a1a1a',
                    border: '1px solid #3a3a3a',
                    color: '#e0e0e0',
                    fontFamily: 'monospace',
                    padding: '12px',
                    fontSize: '12px',
                    resize: 'none',
                    marginBottom: '12px',
                    boxSizing: 'border-box',
                  }}
                />
                
                <button
                  type="submit"
                  disabled={isLoading || !claim.trim()}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: isLoading || !claim.trim() ? '#3a3a3a' : '#1a1a1a',
                    border: '1px solid #3a3a3a',
                    color: isLoading || !claim.trim() ? '#6a6a6a' : '#e0e0e0',
                    fontWeight: '700',
                    fontSize: '12px',
                    cursor: isLoading || !claim.trim() ? 'not-allowed' : 'pointer',
                    letterSpacing: '1px',
                    transition: 'all 200ms',
                  }}
                  onMouseEnter={(e) => !isLoading && !claim.trim() ? null : (e.target.style.background = '#ff6b35', e.target.style.color = '#1a1a1a')}
                  onMouseLeave={(e) => { e.target.style.background = '#1a1a1a'; e.target.style.color = '#e0e0e0'; }}
                >
                  {isLoading ? '⟳ ANALYZING...' : 'ANALYZE CREDIBILITY ▶'}
                </button>
              </form>
            </div>

            {/* TRUST REGISTRY */}
            <div style={{ marginTop: 'auto' }}>
              <h3 style={{ color: '#e0e0e0', fontSize: '14px', fontWeight: '700', margin: '0 0 12px 0', letterSpacing: '1px' }}>LIVE TRUST REGISTRY</h3>
              <p style={{ color: '#6a6a6a', fontSize: '11px', margin: '0 0 16px 0', letterSpacing: '0.5px' }}>Domain credibility scores</p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                {[
                  { name: 'Reuters', score: 94 },
                  { name: 'AP News', score: 92 },
                  { name: 'BBC', score: 88 },
                ].map((source, idx) => (
                  <button
                    key={idx}
                    style={{
                      padding: '12px',
                      background: '#1a1a1a',
                      border: '1px solid #3a3a3a',
                      color: '#e0e0e0',
                      textAlign: 'left',
                      cursor: 'pointer',
                      fontSize: '12px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      letterSpacing: '0.5px',
                      transition: 'all 200ms',
                    }}
                    onMouseEnter={(e) => e.target.style.background = '#2d2d2d'}
                    onMouseLeave={(e) => e.target.style.background = '#1a1a1a'}
                  >
                    <span>{source.name}</span>
                    <span style={{ color: '#10B981', fontWeight: 'bold', fontFamily: 'monospace' }}>{source.score}%</span>
                  </button>
                ))}
              </div>

              <ResponsiveContainer width="100%" height={150}>
                <LineChart data={trustData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" />
                  <XAxis dataKey="time" tick={{ fill: '#6a6a6a', fontSize: 10 }} />
                  <YAxis tick={{ fill: '#6a6a6a', fontSize: 10 }} domain={[70, 100]} />
                  <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #3a3a3a', color: '#e0e0e0' }} />
                  <Line type="monotone" dataKey="reuters" stroke="#10B981" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* RIGHT PANEL - VERIFICATION FEED */}
          <div style={{ padding: '32px', overflowY: 'auto', background: '#1a1a1a' }}>
            <h3 style={{ color: '#e0e0e0', fontSize: '14px', fontWeight: '700', margin: '0 0 20px 0', letterSpacing: '1px' }}>INCIDENT VERIFICATION FEED</h3>

            {verifications.length === 0 ? (
              <div style={{ color: '#6a6a6a', fontSize: '12px', textAlign: 'center', paddingTop: '60px', letterSpacing: '0.5px' }}>
                No verifications yet. Submit a claim to begin analysis.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {verifications.map((v) => (
                  <div
                    key={v.id}
                    style={{
                      border: '1px solid #3a3a3a',
                      background: '#0f0f0f',
                      padding: '20px',
                    }}
                  >
                    {/* VERDICT HEADER */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                      <div style={{ fontWeight: '700', fontSize: '16px', color: v.color, letterSpacing: '1px' }}>
                        {v.verdict === 'Error' ? '⚠ CONNECTION ERROR' : (
                          v.verdict === 'TRUE' ? '🟢 VERIFIED' :
                          v.verdict === 'FALSE' ? '🔴 DEBUNKED' :
                          v.verdict === 'UNVERIFIED' ? '⚫ UNVERIFIED' :
                          `• ${v.verdict.toUpperCase()}`
                        )}
                      </div>
                      <div style={{ background: v.color, color: '#1a1a1a', padding: '4px 12px', fontSize: '11px', fontFamily: 'monospace', fontWeight: '700' }}>
                        {v.confidence}/100
                      </div>
                    </div>

                    {/* CLAIM BOX */}
                    <div style={{ background: '#1a1a1a', padding: '12px', marginBottom: '16px', borderLeft: `2px solid ${v.color}` }}>
                      <p style={{ margin: 0, color: '#b0b0b0', fontSize: '12px', fontFamily: 'monospace', lineHeight: '1.5' }}>
                        "{v.claim}"
                      </p>
                    </div>

                    {/* ANALYSIS */}
                    <div style={{ marginBottom: '16px' }}>
                      <h4 style={{ color: '#e0e0e0', fontSize: '12px', fontWeight: '700', margin: '0 0 8px 0', letterSpacing: '1px' }}>ANALYSIS</h4>
                      <p style={{ color: '#a0a0a0', fontSize: '11px', margin: 0, lineHeight: '1.6' }}>
                        {v.analysis}
                      </p>
                    </div>

                    {/* EVIDENCE PANEL */}
                    {v.verdict !== 'Error' && (
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                        <div>
                          <h4 style={{ color: '#10B981', fontSize: '11px', fontWeight: '700', margin: '0 0 8px 0', letterSpacing: '1px' }}>✓ SUPPORTING</h4>
                          {v.supportingSources.map((src, idx) => (
                            <div key={idx} style={{ background: '#1a1a1a', padding: '8px', marginBottom: '4px', borderLeft: '2px solid #10B981' }}>
                              <div style={{ color: '#10B981', fontSize: '10px', fontWeight: '700', letterSpacing: '0.5px' }}>{src.name}</div>
                              <div style={{ color: '#8a8a8a', fontSize: '10px', marginTop: '2px', fontStyle: 'italic' }}>"{src.quote}"</div>
                            </div>
                          ))}
                        </div>
                        <div>
                          <h4 style={{ color: '#ff6b35', fontSize: '11px', fontWeight: '700', margin: '0 0 8px 0', letterSpacing: '1px' }}>✗ MISSING</h4>
                          {v.missingSources.map((src, idx) => (
                            <div key={idx} style={{ background: '#1a1a1a', padding: '8px', marginBottom: '4px', borderLeft: '2px solid #ff6b35', color: '#8a8a8a', fontSize: '10px' }}>
                              {src}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* ACTIONS */}
                    {v.verdict !== 'Error' && (
                      <div style={{ display: 'flex', gap: '12px', paddingTop: '12px', borderTop: '1px solid #2d2d2d', justifyContent: 'space-around' }}>
                        <button style={{ background: 'transparent', border: 'none', color: '#6a6a6a', cursor: 'pointer', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', letterSpacing: '0.5px' }} onMouseEnter={(e) => e.target.style.color = '#e0e0e0'} onMouseLeave={(e) => e.target.style.color = '#6a6a6a'}>
                          <Share2 size={12} /> SHARE
                        </button>
                        <button style={{ background: 'transparent', border: 'none', color: '#6a6a6a', cursor: 'pointer', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', letterSpacing: '0.5px' }} onMouseEnter={(e) => e.target.style.color = '#e0e0e0'} onMouseLeave={(e) => e.target.style.color = '#6a6a6a'}>
                          <Flag size={12} /> REPORT
                        </button>
                        <button onClick={() => setShowGraphModal(v.id)} style={{ background: 'transparent', border: 'none', color: '#6a6a6a', cursor: 'pointer', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', letterSpacing: '0.5px' }} onMouseEnter={(e) => e.target.style.color = '#e0e0e0'} onMouseLeave={(e) => e.target.style.color = '#6a6a6a'}>
                          <Network size={12} /> NETWORK
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
