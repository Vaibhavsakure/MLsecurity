import { useEffect, useState } from "react";
import ShapChart from "./ShapChart";
import { downloadReport } from "../api";

const CIRCUMFERENCE = 2 * Math.PI * 85;

const SECURITY_TIPS = {
  high: [
    "Do not accept friend/follow requests from this account",
    "Report this profile to the platform for review",
    "Never share personal information with suspected fake accounts",
    "Check if mutual connections actually know this person",
  ],
  medium: [
    "Verify this account through alternative channels before engaging",
    "Be cautious about clicking any links shared by this account",
    "Look for inconsistencies in posting patterns or profile information",
    "Check the account's follower-to-following ratio manually",
  ],
  low: [
    "This account shows genuine behavioral patterns",
    "Continue to stay vigilant — even genuine accounts can be compromised",
    "Enable two-factor authentication on your own accounts",
  ],
};

const CONFIDENCE_LEVELS = [
  { min: 0.0, max: 0.15, label: "Very High Confidence", sublabel: "Strong genuine signals", icon: "🟢" },
  { min: 0.15, max: 0.3, label: "High Confidence", sublabel: "Likely genuine account", icon: "🟢" },
  { min: 0.3, max: 0.45, label: "Moderate Confidence", sublabel: "Some ambiguity detected", icon: "🟡" },
  { min: 0.45, max: 0.55, label: "Low Confidence", sublabel: "Borderline — manual review advised", icon: "🟠" },
  { min: 0.55, max: 0.7, label: "Moderate Confidence", sublabel: "Likely fake/bot patterns", icon: "🟠" },
  { min: 0.7, max: 0.85, label: "High Confidence", sublabel: "Strong fake/bot signals", icon: "🔴" },
  { min: 0.85, max: 1.01, label: "Very High Confidence", sublabel: "Almost certainly fake/bot", icon: "🔴" },
];

function getConfidence(probability) {
  return CONFIDENCE_LEVELS.find(c => probability >= c.min && probability < c.max) || CONFIDENCE_LEVELS[6];
}

export default function ResultDisplay({ result, onReset }) {
  const [animatedPct, setAnimatedPct] = useState(0);
  const [downloading, setDownloading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const pct = Math.round(result.probability * 100);
  const confidence = getConfidence(result.probability);
  const tips = SECURITY_TIPS[result.risk_level] || SECURITY_TIPS.low;
  const isSynthetic = result.data_source === "synthetic";

  useEffect(() => {
    const timeout = setTimeout(() => setAnimatedPct(pct), 100);
    return () => clearTimeout(timeout);
  }, [pct]);

  const offset = CIRCUMFERENCE - (animatedPct / 100) * CIRCUMFERENCE;

  const riskColor =
    result.risk_level === "low"
      ? "var(--risk-low)"
      : result.risk_level === "medium"
      ? "var(--risk-medium)"
      : "var(--risk-high)";

  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      await downloadReport({
        platform: result.platform,
        probability: result.probability,
        risk_level: result.risk_level,
        label: result.label,
        message: result.message,
        input_data: result.input_data || {},
        feature_importances: result.feature_importances || [],
        timestamp: new Date().toLocaleString(),
      });
    } catch (err) {
      console.error("PDF download failed:", err);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="result-container glass-card">
      {/* Synthetic Data Disclaimer */}
      {isSynthetic && (
        <div className="synthetic-disclaimer">
          <span className="synthetic-disclaimer-icon">⚗️</span>
          <div>
            <strong>Synthetic Model</strong>
            <p>{result.model_disclaimer || "This model was trained on synthetic data. Results are demonstrative only."}</p>
          </div>
        </div>
      )}

      {/* Gauge */}
      <div className="gauge-wrapper">
        <svg className="gauge-svg" viewBox="0 0 200 200">
          <circle className="gauge-bg" cx="100" cy="100" r="85" />
          <circle
            className="gauge-fill"
            cx="100"
            cy="100"
            r="85"
            stroke={riskColor}
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="gauge-center-text">
          <div className="gauge-percentage" style={{ color: riskColor }}>
            {animatedPct}%
          </div>
          <div className="gauge-label">Probability</div>
        </div>
      </div>

      {/* Risk Badge */}
      <div className={`result-risk-badge ${result.risk_level}`}>
        {result.risk_level === "low" && "✅"}
        {result.risk_level === "medium" && "⚠️"}
        {result.risk_level === "high" && "🚨"}
        {result.label}
      </div>

      {/* Confidence Indicator */}
      <div className="confidence-indicator">
        <span className="confidence-icon">{confidence.icon}</span>
        <div className="confidence-text">
          <span className="confidence-label">{confidence.label}</span>
          <span className="confidence-sublabel">{confidence.sublabel}</span>
        </div>
      </div>

      {/* Message */}
      <p className="result-message">{result.message}</p>

      {/* Security Tips */}
      <div className="security-tips">
        <h4 className="tips-title">
          🛡️ Security Recommendations
        </h4>
        <ul className="tips-list">
          {tips.map((tip, i) => (
            <li key={i} className="tip-item">
              <span className="tip-bullet" style={{ background: riskColor }} />
              {tip}
            </li>
          ))}
        </ul>
      </div>

      {/* Ensemble Results */}
      {result.ensemble && (
        <div className="ensemble-section">
          <div className="ensemble-header">
            <h4>🧠 Ensemble Analysis ({result.ensemble.models_used} Models)</h4>
            <span className={`ensemble-agreement ${result.ensemble.ensemble_agreement}`}>
              {result.ensemble.models_unanimous ? "✅ Unanimous" : 
               result.ensemble.ensemble_agreement === "high" ? "✅ High Agreement" :
               result.ensemble.ensemble_agreement === "moderate" ? "⚠️ Moderate" : "🔀 Split Vote"}
            </span>
          </div>
          <div className="ensemble-models">
            {Object.entries(result.ensemble.individual_predictions || {}).map(([name, data]) => {
              const pct = Math.round(data.probability * 100);
              const barClass = name === "XGBoost" ? "xgb" : name === "Random Forest" ? "rf" : "lr";
              return (
                <div key={name} className="ensemble-model-row">
                  <span className="ensemble-model-name">{name}</span>
                  <div className="ensemble-model-bar-wrap">
                    <div className={`ensemble-model-bar ${barClass}`} style={{ width: `${pct}%` }} />
                  </div>
                  <span className="ensemble-model-pct">{pct}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* SHAP Explanation */}
      <ShapChart importances={result.feature_importances} />

      {/* Input Data Details (expandable) */}
      {result.input_data && Object.keys(result.input_data).length > 0 && (
        <div className="details-section">
          <button
            className="details-toggle"
            onClick={() => setShowDetails(!showDetails)}
          >
            {showDetails ? "▼" : "▶"} Input Parameters Used
          </button>
          {showDetails && (
            <div className="details-grid">
              {Object.entries(result.input_data).map(([key, val]) => (
                <div key={key} className="detail-item">
                  <span className="detail-key">{key.replace(/_/g, " ")}</span>
                  <span className="detail-value">{String(val)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="result-actions">
        <button className="analyze-another-btn" onClick={onReset}>
          ← Analyze Another Account
        </button>
        <button
          className="download-report-btn"
          onClick={handleDownloadPDF}
          disabled={downloading}
        >
          {downloading ? (
            <>
              <span className="spinner" /> Generating...
            </>
          ) : (
            "📄 Download PDF Report"
          )}
        </button>
      </div>
    </div>
  );
}
