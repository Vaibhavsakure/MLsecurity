import { useEffect, useState } from "react";
import ShapChart from "./ShapChart";
import { downloadReport } from "../api";

const CIRCUMFERENCE = 2 * Math.PI * 85;

export default function ResultDisplay({ result, onReset }) {
  const [animatedPct, setAnimatedPct] = useState(0);
  const [downloading, setDownloading] = useState(false);

  const pct = Math.round(result.probability * 100);

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

      {/* Message */}
      <p className="result-message">{result.message}</p>

      {/* SHAP Explanation */}
      <ShapChart importances={result.feature_importances} />

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
