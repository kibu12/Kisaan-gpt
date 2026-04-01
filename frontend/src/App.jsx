import { useState, useRef, useEffect } from 'react';
import { api } from './api';
import ReactMarkdown from 'react-markdown';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { TRANSLATIONS } from './i18n';

/* ── Benchmark data (ported from Streamlit) ── */
const BENCHMARK = {
  Coimbatore: { pH: 6.8, N: 320, P: 18, K: 220, OC: 0.68 },
  Erode:      { pH: 6.5, N: 290, P: 15, K: 195, OC: 0.62 },
  Salem:      { pH: 7.1, N: 340, P: 22, K: 240, OC: 0.71 },
  Tiruppur:   { pH: 6.6, N: 310, P: 17, K: 205, OC: 0.65 },
  Nilgiris:   { pH: 5.9, N: 380, P: 26, K: 280, OC: 0.91 },
};

/* ══════════════════════════════════════════════════════════════════════════════
   AUTH PAGE
   ══════════════════════════════════════════════════════════════════════════════ */
function AuthPage({ onLogin }) {
  const [tab, setTab] = useState('login');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // Login
  const [lId, setLId] = useState('');
  const [lPwd, setLPwd] = useState('');

  // Signup
  const [sId, setSId] = useState('');
  const [sName, setSName] = useState('');
  const [sLoc, setSLoc] = useState('');
  const [sDist, setSDist] = useState('');
  const [sPwd, setSPwd] = useState('');
  const [sPwd2, setSPwd2] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const data = await api.login(lId, lPwd);
      onLogin(data);
    } catch (err) {
      setError(err.message);
    } finally { setLoading(false); }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError(''); setSuccess('');
    if (!sId || !sName || !sPwd) { setError('Please fill in all required (*) fields.'); return; }
    if (sPwd !== sPwd2) { setError('Passwords do not match.'); return; }
    setLoading(true);
    try {
      await api.signup({ farm_id: sId, farmer_name: sName, password: sPwd, location: sLoc, district: sDist });
      setSuccess('Profile created! Switch to Login tab.');
    } catch (err) {
      setError(err.message);
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-page">
      <div className="brand">
        <img src="/logo.png" alt="KisaanGPT" />
        <h1>KisaanGPT</h1>
      </div>
      <p className="auth-subtitle">Your AI Agriculture Assistant — Please Log In</p>

      <div className="auth-card">
        <div className="auth-tabs">
          <button className={`auth-tab ${tab === 'login' ? 'active' : ''}`} onClick={() => { setTab('login'); setError(''); setSuccess(''); }}>Login</button>
          <button className={`auth-tab ${tab === 'signup' ? 'active' : ''}`} onClick={() => { setTab('signup'); setError(''); setSuccess(''); }}>Sign Up</button>
        </div>

        {error && <div className="error-msg">{error}</div>}
        {success && <div className="success-msg">{success}</div>}

        {tab === 'login' ? (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Farm Profile ID</label>
              <input value={lId} onChange={(e) => setLId(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={lPwd} onChange={(e) => setLPwd(e.target.value)} />
            </div>
            <button className="btn-primary" type="submit" disabled={loading}>
              {loading ? <><span className="spinner" /> Logging in…</> : 'Log In'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSignup}>
            <div className="form-group"><label>New Farm ID *</label><input value={sId} onChange={(e) => setSId(e.target.value)} /></div>
            <div className="form-group"><label>Farmer Name *</label><input value={sName} onChange={(e) => setSName(e.target.value)} /></div>
            <div className="form-row">
              <div className="form-group"><label>Location/Village</label><input value={sLoc} onChange={(e) => setSLoc(e.target.value)} /></div>
              <div className="form-group"><label>District</label><input value={sDist} onChange={(e) => setSDist(e.target.value)} /></div>
            </div>
            <div className="form-group"><label>Create Password *</label><input type="password" value={sPwd} onChange={(e) => setSPwd(e.target.value)} /></div>
            <div className="form-group"><label>Confirm Password *</label><input type="password" value={sPwd2} onChange={(e) => setSPwd2(e.target.value)} /></div>
            <button className="btn-primary" type="submit" disabled={loading}>
              {loading ? <><span className="spinner" /> Creating…</> : 'Create Profile'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   SLIDER COMPONENT
   ══════════════════════════════════════════════════════════════════════════════ */
function Slider({ label, value, onChange, min, max, step = 1 }) {
  return (
    <div className="slider-group">
      <label>{label} <span>{value}</span></label>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} />
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   MAIN DASHBOARD
   ══════════════════════════════════════════════════════════════════════════════ */
function Dashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState(0);

  // Sidebar state
  const [season, setSeason] = useState('Kharif 2025');
  const [soilType, setSoilType] = useState('Alluvial');
  const [language, setLanguage] = useState('English');
  const langCode = language === 'Tamil' ? 'ta' : 'en';
  const location = user.district || 'Coimbatore';
  const t = TRANSLATIONS[langCode];

  const tabs = [
    t.tabSoil,
    t.tabHistory,
    t.tabVoice,
    t.tabBench,
    t.tabChat
  ];

  // Soil params
  const [N, setN] = useState(320);
  const [P, setP] = useState(18);
  const [K, setK] = useState(220);
  const [ph, setPh] = useState(6.8);
  const [humidity, setHumidity] = useState(70);
  const [temperature, setTemperature] = useState(28);
  const [rainfall, setRainfall] = useState(150);
  const [ec, setEc] = useState(0.5);
  const [oc, setOc] = useState(0.75);
  const [landAcres, setLandAcres] = useState(1.0);

  // Results
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Chat
  const [chatMsgs, setChatMsgs] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [chatMsgs]);

  const runAnalysis = async () => {
    setLoading(true);
    try {
      const res = await api.analyzeSoil({
        soil_params: { N, P, K, ph, humidity, temperature, rainfall, ec, oc, soil_type: soilType, land_acres: landAcres },
        location, farmer_query: 'Which crop should I plant this season and how much fertilizer do I need?',
        language: langCode, season, farm_id: user.farm_id, farmer_name: user.farmer_name,
      });
      setResult(res);
    } catch (err) {
      alert('Error: ' + err.message);
    } finally { setLoading(false); }
  };

  const sendChat = async () => {
    if (!chatInput.trim()) return;
    const msg = chatInput;
    setChatInput('');
    setChatMsgs(prev => [...prev, { role: 'user', content: msg }]);
    setChatLoading(true);
    try {
      const res = await api.chat(msg, location, langCode);
      const advice = res.final_advice || '';
      setChatMsgs(prev => [...prev, { role: 'assistant', content: advice, data: res }]);
    } catch (err) {
      setChatMsgs(prev => [...prev, { role: 'assistant', content: 'Error: ' + err.message }]);
    } finally { setChatLoading(false); }
  };

  return (
    <div className="app-layout">
      {/* ── SIDEBAR ── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src="/logo.png" alt="" />
          {t.sidebarBrand}
        </div>
        <p className="sidebar-subtitle">{t.sidebarSub}</p>
        <hr className="divider" />

        <p style={{ fontWeight: 600, fontSize: 13, marginBottom: 4 }}>{t.farmProfile}</p>
        <div className="farm-info">
          <strong>👤 {user.farmer_name}</strong>
          <span className="farm-id">ID: {user.farm_id}</span>
        </div>

        <label>{t.season}</label>
        <select value={season} onChange={(e) => setSeason(e.target.value)}>
          <option>Kharif 2025</option><option>Rabi 2025-26</option><option>Summer 2026</option>
        </select>

        <label>{t.soilType}</label>
        <select value={soilType} onChange={(e) => setSoilType(e.target.value)}>
          {['Alluvial', 'Black (Regur)', 'Red', 'Laterite', 'Sandy', 'Clay', 'Loamy', 'Saline/Alkaline'].map(s => <option key={s}>{s}</option>)}
        </select>

        <label>{t.language}</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option>English</option><option>Tamil</option>
        </select>

        <div style={{ marginTop: '1rem' }}>
          <button className="btn-logout" onClick={onLogout}>{t.logout}</button>
        </div>

        <hr className="divider" />
        <p className="model-info">
          {t.modelInfo}<br />
          {t.ragInfo}
        </p>
      </aside>

      {/* ── MAIN ── */}
      <main className="main-content">
        <div className="page-header">
          <h1>{t.appTitle}</h1>
          <span className="header-tag">{t.tagTN}</span>
          <span className="header-tag">{t.tagAI}</span>
        </div>

        <div className="tabs">
          {tabs.map((t, i) => (
            <button key={i} className={`tab-btn ${activeTab === i ? 'active' : ''}`} onClick={() => setActiveTab(i)}>{t}</button>
          ))}
        </div>

        {/* ── TAB 1: SOIL ANALYSIS ── */}
        {activeTab === 0 && (
          <div className="fade-in-up">
            <div className="grid-2">
              <div>
                <h3>{t.soilParams}</h3>
                <div className="grid-2">
                  <div>
                    <Slider label={t.nitrogen} value={N} onChange={setN} min={0} max={450} />
                    <Slider label={t.phosphorus} value={P} onChange={setP} min={0} max={250} />
                    <Slider label={t.potassium} value={K} onChange={setK} min={0} max={450} />
                    <Slider label={t.ph} value={ph} onChange={setPh} min={3.5} max={9.5} step={0.1} />
                  </div>
                  <div>
                    <Slider label={t.humidity} value={humidity} onChange={setHumidity} min={14} max={100} step={0.1} />
                    <Slider label={t.temp} value={temperature} onChange={setTemperature} min={8} max={44} step={0.1} />
                    <Slider label={t.rainfall} value={rainfall} onChange={setRainfall} min={20} max={300} step={0.1} />
                  </div>
                </div>
                <div className="grid-3" style={{ marginTop: '0.5rem' }}>
                  <div className="form-group"><label>{t.ec}</label><input type="number" value={ec} step={0.1} min={0} max={10} onChange={(e) => setEc(Number(e.target.value))} style={{ width: '100%', padding: '8px 12px', border: '1px solid #E0E0E0', borderRadius: 10, fontFamily: 'Inter', fontSize: 13 }} /></div>
                  <div className="form-group"><label>{t.oc}</label><input type="number" value={oc} step={0.05} min={0} max={3} onChange={(e) => setOc(Number(e.target.value))} style={{ width: '100%', padding: '8px 12px', border: '1px solid #E0E0E0', borderRadius: 10, fontFamily: 'Inter', fontSize: 13 }} /></div>
                  <div className="form-group"><label>{t.land}</label><input type="number" value={landAcres} step={0.1} min={0.1} max={100} onChange={(e) => setLandAcres(Number(e.target.value))} style={{ width: '100%', padding: '8px 12px', border: '1px solid #E0E0E0', borderRadius: 10, fontFamily: 'Inter', fontSize: 13 }} /></div>
                </div>
                <button className="btn-primary" onClick={runAnalysis} disabled={loading} style={{ marginTop: '1rem' }}>
                  {loading ? <><span className="spinner" /> {t.consulting}</> : t.getRecBtn}
                </button>
                
                {result && (
                  <div style={{ marginTop: '2.5rem' }}>
                    <h3>{t.advisory}</h3>
                    <div className="advisory-card">
                      <ReactMarkdown>{result.final_advice}</ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>

              {/* RESULTS PANEL */}
              <div>
                {result && <ResultPanel result={result} inputs={{ N, P, K, ph, temperature }} t={t} />}
              </div>
            </div>
          </div>
        )}

        {/* ── TAB 2: FARM HISTORY ── */}
        {activeTab === 1 && (
          <div className="fade-in-up"><HistoryTab farmId={user.farm_id} location={location} t={t} /></div>
        )}

        {/* ── TAB 3: VOICE ADVISORY ── */}
        {activeTab === 2 && (
          <div className="fade-in-up"><VoiceTab language={langCode} t={t} /></div>
        )}

        {/* ── TAB 4: REGIONAL BENCHMARK ── */}
        {activeTab === 3 && (
          <div className="fade-in-up"><BenchmarkTab location={location} N={N} P={P} K={K} ph={ph} oc={oc} t={t} /></div>
        )}

        {/* ── TAB 5: AI CHAT ── */}
        {activeTab === 4 && (
          <div className="fade-in-up">
            <h3>{t.chatTitle}</h3>
            <p style={{ fontSize: 12, color: '#9E9E9E', marginBottom: '1rem' }}>
              {t.chatSub}
            </p>
            <div className="chat-container" style={{ minHeight: 300, maxHeight: 500, overflowY: 'auto', marginBottom: '1rem' }}>
              {chatMsgs.map((m, i) => (
                <div key={i} className={`chat-msg ${m.role}`}>
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                  {m.data?.sql_result && Array.isArray(m.data.sql_result) && m.data.sql_result.length > 0 && (
                    <DataTable data={m.data.sql_result} />
                  )}
                </div>
              ))}
              {chatLoading && <div className="loading-overlay"><span className="spinner" /> {t.chatThinking}</div>}
              <div ref={chatEndRef} />
            </div>
            <div className="chat-input-row">
              <input className="chat-input" placeholder={t.chatPlaceholder} value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendChat()} />
              <button className="btn-primary" style={{ width: 'auto', padding: '0.6rem 2rem' }} onClick={sendChat} disabled={chatLoading}>{t.chatSend}</button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

/* ── Result Panel ── */
function ResultPanel({ result, inputs, t }) {
  const health = result.soil_analysis?.overall_health || 'N/A';
  const badgeClass = health === 'GOOD' ? 'badge-good' : health === 'WARNING' ? 'badge-warning' : 'badge-critical';
  const top3 = result.crop_predictions?.top_3 || [];
  const fert = result.fertilizer || {};

  const phScore = inputs ? Math.max(0, 100 - Math.abs(inputs.ph - 6.5) * 30) : 0;
  const nutrientScore = inputs ? Math.min(100, (inputs.N/140 + inputs.P/145 + inputs.K/205) * 33) : 0;
  const climateScore = inputs ? Math.min(100, Math.max(0, 100 - Math.abs(inputs.temperature - 25) * 4)) : 0;
  const modelConf = result.crop_predictions?.top_crop_confidence || 0;

  const radarData = [
    { subject: 'Soil fit', A: modelConf, fullMark: 100 },
    { subject: 'Climate match', A: climateScore, fullMark: 100 },
    { subject: 'Nutrient level', A: nutrientScore, fullMark: 100 },
    { subject: 'pH score', A: phScore, fullMark: 100 },
  ];

  return (
    <div>
      {/* Soil Health */}
      <p style={{ fontWeight: 600, marginBottom: 8 }}>{t.soilHealth} <span className={badgeClass}>{health}</span></p>

      {(result.soil_analysis?.issues || []).map((issue, i) => (
        <div key={i} className="alert-critical"><strong>{issue.parameter}</strong> — {issue.message}<br /><em>{t.action} {issue.action}</em></div>
      ))}
      {(result.soil_analysis?.warnings || []).map((w, i) => (
        <div key={i} className="alert-warning"><strong>{w.parameter}</strong> — {w.message}</div>
      ))}

      {/* Confidence Breakdown */}
      <div style={{ marginTop: '1.25rem' }}>
        <p style={{ fontWeight: 600, fontSize: 13, marginBottom: '0.25rem', color: '#212121', textAlign: 'center' }}>
          {t.recConf} — {top3[0]?.[0] || 'Crop'}
        </p>
        <div style={{ height: 280, width: '100%', display: 'flex', justifyContent: 'center' }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#607D8B', fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar name="Confidence" dataKey="A" stroke="#2E7D32" strokeWidth={2} fill="#2E7D32" fillOpacity={0.08} />
              <Tooltip formatter={(value) => `${Math.round(value)}%`} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <hr className="section-divider" />

      {/* Crop Predictions */}
      <h3>{t.recCrops}</h3>
      {top3.map(([crop, conf], i) => (
        <div key={i} className="crop-card">
          <span className="crop-name">{i === 0 ? '→ ' : ''}{crop}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="crop-bar-outer"><div className="crop-bar-inner" style={{ width: conf * 1.2 }} /></div>
            <span className="crop-conf">{conf}%</span>
          </div>
        </div>
      ))}

      <hr className="section-divider" />

      {/* Advisory & Fertilizer */}
      <div>
        <h3>{t.fertPlan}</h3>
        <div className="fert-card">
          <div className="fert-title">{fert.primary_fertilizer}</div>
          <div className="fert-row">
            <div className="fert-item"><div className="val">{fert.n_dose_kg_ha}</div><div className="lbl">N kg/ha</div></div>
            <div className="fert-item"><div className="val">{fert.p_dose_kg_ha}</div><div className="lbl">P kg/ha</div></div>
            <div className="fert-item"><div className="val">{fert.k_dose_kg_ha}</div><div className="lbl">K kg/ha</div></div>
          </div>
          <p className="fert-note">{fert.application_note}</p>
          <p className="fert-source">{t.source} {fert.source}</p>
        </div>
      </div>

      {result.farm_saved && <div className="alert-info" style={{ marginTop: '1rem' }}>{t.readingSaved}</div>}
    </div>
  );
}

/* ── Benchmark Tab ── */
function BenchmarkTab({ location, N, P, K, ph, oc, t }) {
  const dist = BENCHMARK[location] || BENCHMARK['Coimbatore'];
  const metrics = [
    { name: 'Nitrogen (N)', user: N, dist: dist.N, unit: 'kg/ha' },
    { name: 'Phosphorus (P)', user: P, dist: dist.P, unit: 'kg/ha' },
    { name: 'Potassium (K)', user: K, dist: dist.K, unit: 'kg/ha' },
    { name: 'pH', user: ph, dist: dist.pH, unit: '' },
    { name: 'Organic Carbon', user: oc, dist: dist.OC, unit: '%' },
  ];

  return (
    <div>
      <h3>{t.benchTitle}</h3>
      <p style={{ fontSize: 12, color: '#9E9E9E', fontWeight: 500, marginBottom: '1.5rem' }}>
        {t.benchSource}
      </p>

      <h3>{t.farmVsDist}</h3>
      <div className="grid-5">
        {metrics.map((m, i) => {
          const diff = m.user - m.dist;
          const diffPct = m.dist ? Math.round((diff / m.dist) * 100) : 0;
          const arrow = diff > 0 ? '↑' : diff < 0 ? '↓' : '—';
          const color = diff >= 0 ? '#2E7D32' : '#C62828';
          return (
            <div key={i} className="metric-card">
              <div className="metric-label">{m.name}</div>
              <div className="metric-value">{m.user}<span className="metric-unit">{m.unit}</span></div>
              <div className="metric-diff" style={{ color }}>{arrow} {Math.abs(diffPct)}% {t.vsAvg} ({m.dist}{m.unit})</div>
            </div>
          );
        })}
      </div>

      <hr className="section-divider" />

      <h3>{t.fullDistData}</h3>
      <table className="data-table">
        <thead>
          <tr><th>District</th><th>pH</th><th>N</th><th>P</th><th>K</th><th>OC</th></tr>
        </thead>
        <tbody>
          {Object.entries(BENCHMARK).map(([dist, vals]) => (
            <tr key={dist}><td>{dist}</td><td>{vals.pH}</td><td>{vals.N}</td><td>{vals.P}</td><td>{vals.K}</td><td>{vals.OC}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ── History Tab ── */
function HistoryTab({ farmId, location, t }) {
  const [history, setHistory] = useState([]);
  const [trajectory, setTrajectory] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.farmHistory(farmId).then(data => {
      // API returns date strings, format them for the chart
      const formattedHistory = (data.history || []).map(h => ({
        ...h,
        date: new Date(h.reading_date).toLocaleDateString()
      })).reverse(); // Oldest to newest for the chart
      
      setHistory(formattedHistory);
      setTrajectory(data.trajectory || {});
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [farmId]);

  if (loading) return <div className="loading-overlay"><span className="spinner" /> Loading farm history...</div>;

  const dist = BENCHMARK[location] || BENCHMARK['Coimbatore'];
  const traj = trajectory.ph_trend || 'stable';
  const badgeClass = traj === 'degrading' ? 'badge-critical' : traj === 'improving' ? 'badge-good' : 'badge-warning';

  return (
    <div>
      <h3>{t.histTitle}</h3>
      
      {history.length < 2 ? (
        <div className="alert-info">{t.addReadingInfo}</div>
      ) : (
        <>
          <p style={{ marginBottom: '1.5rem' }}>
            <strong>{t.phTraj}</strong> <span className={badgeClass}>{traj.toUpperCase()}</span>
            &nbsp; {t.currentPh} <strong>{trajectory.ph_current || '–'}</strong>
          </p>

          {trajectory.alert && (
            <div className="alert-critical">
              pH ALERT — At current rate, pH will reach the critical threshold (5.5) in approximately <strong>{trajectory.seasons_to_critical_ph} seasons</strong>. Apply lime immediately.
            </div>
          )}

          <div className="grid-2" style={{ marginBottom: '2rem' }}>
            {/* pH Chart */}
            <div>
              <p style={{ fontWeight: 600, fontSize: 13, marginBottom: '1rem', textAlign: 'center' }}>Soil pH over time (vs {location})</p>
              <div style={{ height: 280, width: '100%' }}>
                <ResponsiveContainer>
                  <LineChart data={history} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis domain={[4, 9]} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <ReferenceLine y={dist.pH} stroke="#81C784" strokeWidth={2} label={{ value: `${location} Avg (${dist.pH})`, fill: '#81C784', fontSize: 10, position: 'insideTopLeft' }} />
                    <ReferenceLine y={5.5} stroke="#EF5350" strokeDasharray="3 3" label={{ value: 'Critical (5.5)', fill: '#EF5350', fontSize: 10, position: 'insideBottomLeft' }} />
                    <ReferenceLine y={6.0} stroke="#FFA726" strokeDasharray="1 1" label={{ value: 'Warning (6.0)', fill: '#FFA726', fontSize: 10, position: 'insideTopLeft' }} />
                    <Line type="monotone" dataKey="ph" stroke="#2E7D32" strokeWidth={2} activeDot={{ r: 6 }} name="pH Level" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* NPK Chart */}
            <div>
              <p style={{ fontWeight: 600, fontSize: 13, marginBottom: '1rem', textAlign: 'center' }}>NPK trend over time (vs {location})</p>
              <div style={{ height: 280, width: '100%' }}>
                <ResponsiveContainer>
                  <LineChart data={history} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <ReferenceLine y={dist.N} stroke="#2E7D32" strokeDasharray="3 3" label={{ value: `${location} N`, fill: '#2E7D32', fontSize: 9, position: 'insideRight' }} />
                    <ReferenceLine y={dist.P} stroke="#607D8B" strokeDasharray="3 3" label={{ value: `${location} P`, fill: '#607D8B', fontSize: 9, position: 'insideRight' }} />
                    <ReferenceLine y={dist.K} stroke="#FFA726" strokeDasharray="3 3" label={{ value: `${location} K`, fill: '#FFA726', fontSize: 9, position: 'insideRight' }} />
                    <Line type="monotone" dataKey="n_val" stroke="#2E7D32" strokeWidth={2} name="N" />
                    <Line type="monotone" dataKey="p_val" stroke="#607D8B" strokeWidth={2} name="P" />
                    <Line type="monotone" dataKey="k_val" stroke="#FFA726" strokeWidth={2} name="K" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}

      <h3>{t.readHist}</h3>
      <table className="data-table">
        <thead>
          <tr>
            <th>Date</th><th>Season</th><th>pH</th><th>N</th><th>P</th><th>K</th><th>OC</th><th>Crop</th><th>Model Conf (%)</th>
          </tr>
        </thead>
        <tbody>
          {[...history].reverse().map((h, i) => (
            <tr key={i}>
              <td>{h.reading_date}</td>
              <td>{h.season}</td>
              <td>{h.ph}</td>
              <td>{h.n_val}</td>
              <td>{h.p_val}</td>
              <td>{h.k_val}</td>
              <td>{h.oc}</td>
              <td>{h.recommended_crop}</td>
              <td>{h.confidence}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ── Voice Tab ── */
function VoiceTab({ language, t }) {
  return (
    <div>
      <h3>{t.voiceTitle}</h3>
      <div className="alert-info">
        {t.voiceUploadDesc}
      </div>

      <div className="grid-2" style={{ marginTop: '1.5rem' }}>
        <div>
          <p style={{ fontWeight: 600, fontSize: 14, marginBottom: '0.75rem' }}>{t.uploadNote}</p>
          <div className="file-upload" onClick={() => alert('Voice processing is handled via the separate audio API endpoint.')}>
            <div className="file-upload-text">
              {t.clickUpload}<br />
              <span style={{ fontSize: 11, color: '#9E9E9E', marginTop: 4, display: 'block' }}>{t.maxSize}</span>
            </div>
          </div>
        </div>
        
        <div>
          <p style={{ fontWeight: 600, fontSize: 14, marginBottom: '0.75rem' }}>{t.supportedLangs}</p>
          <div className="fert-card">
            <div style={{ marginBottom: 8, fontSize: 13, color: '#212121', fontWeight: 600 }}>{t.stt}</div>
            <div style={{ fontSize: 13, color: '#607D8B' }}>{t.sttDesc}</div>
            <div style={{ marginTop: 14, marginBottom: 8, fontSize: 13, color: '#212121', fontWeight: 600 }}>{t.tts}</div>
            <div style={{ fontSize: 13, color: '#607D8B' }}>{t.ttsDesc}</div>
            <div style={{ marginTop: 14, fontSize: 11, color: '#9E9E9E' }}>{t.selectLangSidebar}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Data Table ── */
function DataTable({ data }) {
  if (!data || data.length === 0) return null;
  const cols = Object.keys(data[0]);
  return (
    <table className="data-table" style={{ marginTop: '0.75rem' }}>
      <thead><tr>{cols.map(c => <th key={c}>{c}</th>)}</tr></thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i}>{cols.map(c => <td key={c}>{row[c]}</td>)}</tr>
        ))}
      </tbody>
    </table>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   ROOT APP
   ══════════════════════════════════════════════════════════════════════════════ */
export default function App() {
  const [user, setUser] = useState(null);

  const handleLogin = (data) => {
    setUser(data);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (!user) return <AuthPage onLogin={handleLogin} />;
  return <Dashboard user={user} onLogout={handleLogout} />;
}
