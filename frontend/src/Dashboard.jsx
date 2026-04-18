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

  const generateVerification = () => {
    const verdicts = [
      { label: 'Verified', color: '#10B981' },
      { label: 'False', color: '#ff6b35' },
      { label: 'Manipulated', color: '#ff6b35' },
      { label: 'Unverified', color: '#ff6b35' },
    ];
    
    const verdict = verdicts[Math.floor(Math.random() * verdicts.length)];
    const confidence = Math.floor(Math.random() * 50) + 35;
    
    return {
      id: Date.now(),
      claim: claim || 'No claim provided',
      verdict: verdict.label,
      color: verdict.color,
      confidence,
      analysis: `The claim regarding "${claim.substring(0, 40)}..." is highly speculative and lacks empirical validation from official channels.`,
      supportingSources: [
        { name: 'Reuters', quote: 'Authorities investigating the incident' },
        { name: 'NDTV', quote: 'No official infrastructure failure confirmed' }
      ],
      missingSources: [
        'No confirmation from government agencies',
        'Negative Result: No corroborating data found from Disaster Management Authority'
      ],
      hasExifWarning: Math.random() > 0.7,
      sourcesChecked: Math.floor(Math.random() * 8) + 8,
    };
  };

  const handleAnalyze = (e) => {
    e.preventDefault();
    if (!claim.trim()) return;

    setIsLoading(true);

    setTimeout(() => {
      const newVerification = generateVerification();
      setVerifications([newVerification, ...verifications]);
      setClaim('');
      setIsLoading(false);
    }, 2000);
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
      </aside>

      {/* MAIN CONTENT */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* HEADER */}
        <header style={{ borderBottom: '1px solid #2d2d2d' }}>
          <div style={{ padding: '16px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h1 style={{ color: '#e0e0e0', fontSize: '16px', fontWeight: '600', letterSpacing: '1px' }}>
              SENTINEL PROTOCOL
            </h1>
            <div style={{ display: 'flex', gap: '20px', fontSize: '12px', color: '#9a9a9a' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '8px', height: '8px', background: '#10B981', borderRadius: '50%' }}></span>
                SYSTEM LIVE
              </span>
              <span>RESPONSE ~1.8s</span>
            </div>
          </div>

          {/* ALERT BANNER */}
          <div style={{ background: '#ff6b35', padding: '12px 32px', display: 'flex', gap: '12px', alignItems: 'center' }}>
            <AlertTriangle size={16} style={{ color: '#1a1a1a', flexShrink: 0 }} />
            <span style={{ color: '#1a1a1a', fontSize: '12px', fontWeight: '500', letterSpacing: '0.5px' }}>
              CRITICAL: MISINFORMATION DETECTED | CLAIMS TRENDING (23 ACTIVE) | HIGH IMPACT CONTENT | CLAIM CONFIDENCE
            </span>
          </div>
        </header>

        {/* CONTENT AREA */}
        <div style={{ flex: 1, overflow: 'auto', padding: '32px' }}>
          {/* FORM */}
          <form onSubmit={handleAnalyze} style={{ marginBottom: '32px' }}>
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ color: '#e0e0e0', fontSize: '14px', fontWeight: '600', letterSpacing: '1px', marginBottom: '8px' }}>
                CLAIMS PROCESSOR
              </h2>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <textarea
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                placeholder="Paste claim to analyze..."
                style={{
                  width: '100%',
                  padding: '16px',
                  background: '#2d2d2d',
                  border: '1px solid #3d3d3d',
                  color: '#e0e0e0',
                  fontSize: '14px',
                  fontFamily: 'monospace',
                  borderRadius: '0px',
                  minHeight: '120px',
                  outline: 'none',
                }}
                onFocus={(e) => e.target.style.borderColor = '#ff6b35'}
                onBlur={(e) => e.target.style.borderColor = '#3d3d3d'}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button
                type="submit"
                disabled={isLoading || !claim.trim()}
                style={{
                  padding: '12px 24px',
                  background: '#1a1a1a',
                  color: '#e0e0e0',
                  border: '1px solid #ff6b35',
                  cursor: isLoading || !claim.trim() ? 'not-allowed' : 'pointer',
                  fontSize: '12px',
                  fontWeight: '600',
                  letterSpacing: '0.5px',
                  opacity: isLoading || !claim.trim() ? 0.5 : 1,
                  transition: 'all 200ms',
                }}
                onMouseEnter={(e) => !isLoading && !claim.trim() ? null : (e.target.style.background = '#ff6b35', e.target.style.color = '#1a1a1a')}
                onMouseLeave={(e) => { e.target.style.background = '#1a1a1a'; e.target.style.color = '#e0e0e0'; }}
              >
                {isLoading ? '⟳ ANALYZING...' : 'ANALYZE CREDIBILITY ▶'}
              </button>
              <span style={{ fontSize: '11px', color: '#6a6a6a' }}>
                USES SOURCE VALIDATION + CROSS-VERIFICATION PROTOCOL
              </span>
            </div>
          </form>

          {/* RESULTS */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {verifications.map((verification, idx) => (
              <div key={verification.id}>
                {/* VERDICT CARD */}
                <div
                  style={{
                    background: '#222a3d',
                    borderLeft: '4px solid ' + verification.color,
                    padding: '24px',
                    marginBottom: '24px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                        <AlertTriangle size={20} style={{ color: verification.color }} />
                        <h3 style={{ color: '#e0e0e0', fontSize: '24px', fontWeight: '700', letterSpacing: '0.5px' }}>
                          VERDICT: {verification.verdict.toUpperCase()}
                        </h3>
                      </div>
                    </div>
                    <div style={{
                      background: '#ff6b35',
                      color: '#1a1a1a',
                      padding: '16px',
                      textAlign: 'center',
                      minWidth: '120px',
                    }}>
                      <div style={{ fontSize: '10px', fontWeight: '600', letterSpacing: '0.5px', marginBottom: '8px' }}>
                        CONFIDENCE SCORE
                      </div>
                      <div style={{ fontSize: '28px', fontWeight: '700', fontFamily: 'monospace' }}>
                        {verification.confidence}/100
                      </div>
                    </div>
                  </div>

                  <p style={{ color: '#b0b0b0', fontSize: '14px', lineHeight: '1.6', marginBottom: '20px' }}>
                    {verification.analysis}
                  </p>
                </div>

                {/* WHY THIS DECISION */}
                <div style={{ marginBottom: '24px' }}>
                  <h4 style={{ color: '#e0e0e0', fontSize: '12px', fontWeight: '600', letterSpacing: '1px', marginBottom: '12px' }}>
                    WHY THIS DECISION?
                  </h4>
                  <div style={{ marginLeft: '16px' }}>
                    {['Claim originates from low-trust platform with high history of manipulated media dissemination.',
                      'No confirmation or acknowledgement from verified municipal or government emergency services.',
                      'Syntactic and spreading patterns match known misinformation templates previously identified in this sector.'].map((item, i) => (
                      <div key={i} style={{ display: 'flex', gap: '12px', marginBottom: '12px', fontSize: '13px', color: '#9a9a9a' }}>
                        <span style={{ color: '#ff6b35', fontWeight: '700', minWidth: '20px' }}>{String(i + 1).padStart(2, '0')})</span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* EVIDENCE PANEL */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                  {/* Left: Analysis */}
                  <div>
                    <h5 style={{ color: '#e0e0e0', fontSize: '12px', fontWeight: '600', letterSpacing: '1px', marginBottom: '12px' }}>
                      ■ ANALYSIS REPORT
                    </h5>
                    <p style={{ color: '#9a9a9a', fontSize: '13px', lineHeight: '1.6', marginBottom: '16px' }}>
                      The claim regarding "{verification.claim.substring(0, 40)}..." is likely {verification.verdict.toUpperCase()}. Initial keyword detection on the raw social media post, and visual evidence evaluation has resulted in a moderate level of structural failure claim validation.
                    </p>
                    <div style={{ background: '#1a1a1a', borderLeft: '3px solid #ff6b35', padding: '12px', fontSize: '12px', fontWeight: '600', color: '#e0e0e0', letterSpacing: '0.5px' }}>
                      HIGH PROBABILITY OF COORDINATED MISINFORMATION OR LOCALIZED PANIC-TRIGGER
                    </div>
                  </div>

                  {/* Right: Evidence */}
                  <div>
                    <h5 style={{ color: '#e0e0e0', fontSize: '12px', fontWeight: '600', letterSpacing: '1px', marginBottom: '16px' }}>
                      ■ SOURCE EVIDENCE
                    </h5>
                    
                    <div style={{ marginBottom: '16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10B981', fontSize: '12px', fontWeight: '600', marginBottom: '8px' }}>
                        <span>✓</span>
                        <span>SUPPORTING SOURCES</span>
                      </div>
                      {verification.supportingSources.map((src, i) => (
                        <div key={i} style={{ marginBottom: '8px' }}>
                          <div style={{ color: '#89ceff', fontSize: '12px', fontWeight: '600' }}>{src.name}</div>
                          <div style={{ color: '#6a6a6a', fontSize: '11px' }}>"{src.quote}"</div>
                        </div>
                      ))}
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#ff6b35', fontSize: '12px', fontWeight: '600', marginBottom: '8px' }}>
                        <span>✗</span>
                        <span>MISSING / CONTRADICTING</span>
                      </div>
                      {verification.missingSources.map((src, i) => (
                        <div key={i} style={{ color: '#6a6a6a', fontSize: '11px', marginBottom: '4px' }}>
                          • {src}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* METADATA WARNING */}
                {verification.hasExifWarning && (
                  <div style={{ background: 'rgba(255, 107, 53, 0.1)', border: '1px solid #ff6b35', padding: '12px 16px', marginBottom: '24px' }}>
                    <p style={{ color: '#ffb3ad', fontSize: '12px', fontWeight: '600' }}>
                      ⚠ EXIF METADATA CONTRADICTS THE CLAIM TIMELINE
                    </p>
                  </div>
                )}

                {/* SOURCE NETWORK BUTTON */}
                <button
                  onClick={() => setShowGraphModal(showGraphModal === idx ? null : idx)}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    background: 'transparent',
                    border: '1px solid #ff6b35',
                    color: '#e0e0e0',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: '600',
                    letterSpacing: '0.5px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    marginBottom: '24px',
                    transition: 'all 200ms',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = '#ff6b35', e.currentTarget.style.color = '#1a1a1a')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent', e.currentTarget.style.color = '#e0e0e0')}
                >
                  <Network size={16} />
                  <span>VIEW SOURCE NETWORK</span>
                  <ChevronDown size={16} style={{ transform: showGraphModal === idx ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 200ms' }} />
                </button>

                {/* GRAPH */}
                {showGraphModal === idx && (
                  <div style={{ background: '#222a3d', padding: '24px', marginBottom: '24px', border: '1px solid #2d2d2d' }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={trustData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#3d3d3d" />
                        <XAxis dataKey="time" stroke="#6a6a6a" />
                        <YAxis stroke="#6a6a6a" />
                        <Tooltip 
                          contentStyle={{ background: '#1a1a1a', border: '1px solid #3d3d3d', borderRadius: '0px' }}
                          labelStyle={{ color: '#e0e0e0' }}
                        />
                        <Line type="monotone" dataKey="reuters" stroke="#ff6b35" strokeWidth={2} dot={{ r: 3 }} />
                        <Line type="monotone" dataKey="apnews" stroke="#89ceff" strokeWidth={2} dot={{ r: 3 }} />
                        <Line type="monotone" dataKey="bbc" stroke="#10B981" strokeWidth={2} dot={{ r: 3 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* ACTION BUTTONS */}
                <div style={{ display: 'flex', gap: '12px', paddingTop: '16px', borderTop: '1px solid #3d3d3d' }}>
                  {['MAIN', 'NEWS', 'RECENT'].map((label) => (
                    <button
                      key={label}
                      style={{
                        padding: '8px 16px',
                        background: 'transparent',
                        border: '1px solid #3d3d3d',
                        color: '#9a9a9a',
                        cursor: 'pointer',
                        fontSize: '11px',
                        fontWeight: '600',
                        letterSpacing: '0.5px',
                      }}
                      onMouseEnter={(e) => (e.target.style.color = '#e0e0e0', e.target.style.borderColor = '#ff6b35')}
                      onMouseLeave={(e) => (e.target.style.color = '#9a9a9a', e.target.style.borderColor = '#3d3d3d')}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            ))}

            {verifications.length === 0 && !isLoading && (
              <div style={{ textAlign: 'center', padding: '48px 0', color: '#6a6a6a' }}>
                <p style={{ fontSize: '14px' }}>Submit a claim above to see verification results</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
