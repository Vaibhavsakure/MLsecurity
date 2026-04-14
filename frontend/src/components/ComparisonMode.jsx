import { useState } from "react";
import AnalysisForm from "./AnalysisForm";
import ShapChart from "./ShapChart";
import { PLATFORMS } from "../platforms";
import { predictPlatform } from "../api";

const CIRCUMFERENCE = 2 * Math.PI * 60;

function MiniGauge({ probability, riskLevel }) {
  const pct = Math.round(probability * 100);
  const offset = CIRCUMFERENCE - (pct / 100) * CIRCUMFERENCE;
  const color =
    riskLevel === "low" ? "var(--risk-low)" :
    riskLevel === "medium" ? "var(--risk-medium)" : "var(--risk-high)";

  return (
    <div className="compare-gauge">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="60" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
        <circle cx="70" cy="70" r="60" fill="none" stroke={color} strokeWidth="8"
          strokeLinecap="round" strokeDasharray={CIRCUMFERENCE} strokeDashoffset={offset}
          style={{ transform: "rotate(-90deg)", transformOrigin: "center", transition: "stroke-dashoffset 1s ease" }} />
      </svg>
      <div className="compare-gauge-text">
        <span className="compare-gauge-pct" style={{ color }}>{pct}%</span>
        <span className="compare-gauge-label">Risk</span>
      </div>
    </div>
  );
}

function CompareResult({ result, label }) {
  if (!result) return null;
  return (
    <div className="compare-result-card glass-card">
      <h4>{label}</h4>
      <MiniGauge probability={result.probability} riskLevel={result.risk_level} />
      <div className={`compare-risk-badge ${result.risk_level}`}>
        {result.risk_level === "low" && "✅"}{result.risk_level === "medium" && "⚠️"}{result.risk_level === "high" && "🚨"} {result.label}
      </div>
      <p className="compare-message">{result.message}</p>
      <ShapChart importances={result.feature_importances} />
    </div>
  );
}

export default function ComparisonMode() {
  const [platform, setPlatform] = useState("instagram");
  const [resultA, setResultA] = useState(null);
  const [resultB, setResultB] = useState(null);
  const [loadingA, setLoadingA] = useState(false);
  const [loadingB, setLoadingB] = useState(false);
  const [errorA, setErrorA] = useState(null);
  const [errorB, setErrorB] = useState(null);

  const config = PLATFORMS[platform];

  const handleSubmitA = async (data) => {
    setLoadingA(true); setErrorA(null);
    try {
      const res = await predictPlatform(platform, data);
      setResultA(res);
    } catch (e) { setErrorA(e.message); }
    finally { setLoadingA(false); }
  };

  const handleSubmitB = async (data) => {
    setLoadingB(true); setErrorB(null);
    try {
      const res = await predictPlatform(platform, data);
      setResultB(res);
    } catch (e) { setErrorB(e.message); }
    finally { setLoadingB(false); }
  };

  const handleSwap = () => {
    setResultA(resultB);
    setResultB(resultA);
  };

  const handleReset = () => {
    setResultA(null);
    setResultB(null);
    setErrorA(null);
    setErrorB(null);
  };

  // Compute feature diffs when both results exist
  let featureDiffs = [];
  if (resultA?.input_data && resultB?.input_data) {
    const keysA = Object.keys(resultA.input_data);
    featureDiffs = keysA.map(key => {
      const valA = resultA.input_data[key];
      const valB = resultB.input_data[key];
      const diff = typeof valA === "number" && typeof valB === "number" ? valB - valA : null;
      return { key, valA, valB, diff };
    }).filter(d => d.diff !== null && d.diff !== 0)
      .sort((a, b) => Math.abs(b.diff) - Math.abs(a.diff))
      .slice(0, 6);
  }

  return (
    <div className="comparison-page">
      <div className="comparison-header">
        <h1>🔀 Profile Comparison</h1>
        <p className="comparison-subtitle">Compare two profiles side-by-side to spot differences</p>
      </div>

      <div className="comparison-platform-select">
        <label>Platform:</label>
        <select value={platform} onChange={e => { setPlatform(e.target.value); handleReset(); }}>
          {Object.entries(PLATFORMS).map(([key, cfg]) => (
            <option key={key} value={key}>{cfg.name}</option>
          ))}
        </select>
      </div>

      <div className="comparison-grid">
        {/* Profile A */}
        <div className="comparison-side">
          <div className="comparison-side-header">
            <span className="comparison-label-badge a">Profile A</span>
          </div>
          {errorA && <div className="error-message">⚠️ {errorA}</div>}
          {!resultA ? (
            <div className="comparison-form-wrap glass-card">
              <AnalysisForm config={config} platform={platform} onSubmit={handleSubmitA} loading={loadingA} />
            </div>
          ) : (
            <CompareResult result={resultA} label="Profile A" />
          )}
        </div>

        {/* Center Controls */}
        <div className="comparison-center">
          {resultA && resultB && (
            <>
              <button className="swap-btn" onClick={handleSwap} title="Swap profiles">⇄</button>
              <div className="comparison-vs">VS</div>
              <button className="compare-reset-btn" onClick={handleReset}>Reset</button>
            </>
          )}
          {(!resultA || !resultB) && <div className="comparison-vs-waiting">VS</div>}
        </div>

        {/* Profile B */}
        <div className="comparison-side">
          <div className="comparison-side-header">
            <span className="comparison-label-badge b">Profile B</span>
          </div>
          {errorB && <div className="error-message">⚠️ {errorB}</div>}
          {!resultB ? (
            <div className="comparison-form-wrap glass-card">
              <AnalysisForm config={config} platform={platform} onSubmit={handleSubmitB} loading={loadingB} />
            </div>
          ) : (
            <CompareResult result={resultB} label="Profile B" />
          )}
        </div>
      </div>

      {/* Feature Diff Table */}
      {featureDiffs.length > 0 && (
        <div className="comparison-diff glass-card">
          <h3>📊 Key Differences</h3>
          <div className="diff-table">
            <div className="diff-header">
              <span>Feature</span><span>Profile A</span><span>Profile B</span><span>Diff</span>
            </div>
            {featureDiffs.map(d => (
              <div key={d.key} className="diff-row">
                <span className="diff-feature">{d.key.replace(/_/g, " ")}</span>
                <span>{typeof d.valA === "number" ? d.valA.toLocaleString() : d.valA}</span>
                <span>{typeof d.valB === "number" ? d.valB.toLocaleString() : d.valB}</span>
                <span className={`diff-value ${d.diff > 0 ? "positive" : "negative"}`}>
                  {d.diff > 0 ? "+" : ""}{typeof d.diff === "number" ? d.diff.toLocaleString() : d.diff}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
