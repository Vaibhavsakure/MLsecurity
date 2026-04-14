import { useState, useRef } from "react";
import { batchPredict, downloadBatchReport } from "../api";
import { PLATFORMS } from "../platforms";

const PLATFORM_COLORS = {
  instagram: "#E1306C",
  twitter: "#1DA1F2",
  reddit: "#FF4500",
  facebook: "#1877F2",
  linkedin: "#0A66C2",
  youtube: "#FF0000",
};

export default function BatchAnalysis() {
  const [platform, setPlatform] = useState("instagram");
  const [file, setFile] = useState(null);
  const [records, setRecords] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [downloadingZip, setDownloadingZip] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setError(null);
    setResults(null);

    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const text = evt.target.result;
        const lines = text.trim().split("\n");
        if (lines.length < 2) {
          setError("CSV must have a header row and at least one data row.");
          return;
        }
        const headers = lines[0].split(",").map((h) => h.trim().toLowerCase());
        const parsed = [];
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(",").map((v) => v.trim());
          if (values.length !== headers.length) continue;
          const record = {};
          headers.forEach((h, idx) => {
            const val = values[idx];
            record[h] = isNaN(val) ? val : parseFloat(val);
          });
          parsed.push(record);
        }
        setRecords(parsed);
      } catch (err) {
        setError("Failed to parse CSV file: " + err.message);
      }
    };
    reader.readAsText(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const f = e.dataTransfer.files[0];
    if (f && f.name.endsWith(".csv")) {
      const fakeEvent = { target: { files: [f] } };
      handleFileChange(fakeEvent);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleAnalyze = async () => {
    if (records.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const res = await batchPredict(platform, records);
      setResults(res);
    } catch (err) {
      setError(err.message || "Batch analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadZip = async () => {
    if (!results?.results) return;
    setDownloadingZip(true);
    try {
      const reports = results.results
        .filter((r) => r.probability !== null)
        .map((r) => ({
          platform: r.platform,
          probability: r.probability,
          risk_level: r.risk_level,
          label: r.label,
          message: r.message,
          input_data: r.input_data || {},
          feature_importances: r.feature_importances || [],
          timestamp: new Date().toLocaleString(),
        }));
      await downloadBatchReport(reports);
    } catch (err) {
      console.error("ZIP download failed:", err);
    } finally {
      setDownloadingZip(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setRecords([]);
    setResults(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const riskIcon = { low: "✅", medium: "⚠️", high: "🚨", unknown: "❓" };
  const config = PLATFORMS[platform];
  const expectedFields = config?.fields?.map((f) => f.key).join(", ") || "";

  return (
    <div className="batch-page">
      <div className="batch-header">
        <h1>📊 Batch Analysis</h1>
        <p className="batch-subtitle">
          Upload a CSV file to analyze multiple accounts at once
        </p>
      </div>

      {!results ? (
        <div className="batch-upload-section">
          {/* Platform Selector */}
          <div className="batch-platform-select glass-card">
            <h3>1. Select Platform</h3>
            <div className="batch-platform-chips">
              {Object.entries(PLATFORMS).map(([key, cfg]) => (
                <button
                  key={key}
                  className={`batch-platform-chip ${platform === key ? "active" : ""}`}
                  onClick={() => {
                    setPlatform(key);
                    setRecords([]);
                    setFile(null);
                    setResults(null);
                    if (fileInputRef.current) fileInputRef.current.value = "";
                  }}
                  style={
                    platform === key
                      ? { borderColor: cfg.color, color: cfg.color, background: `${cfg.color}12` }
                      : {}
                  }
                >
                  {cfg.name}
                </button>
              ))}
            </div>
            <div className="batch-expected-fields">
              <strong>Expected CSV columns:</strong>
              <code>{expectedFields}</code>
            </div>
          </div>

          {/* File Upload */}
          <div
            className="batch-dropzone glass-card"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              accept=".csv"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: "none" }}
            />
            <div className="dropzone-content">
              <div className="dropzone-icon">📁</div>
              <h3>2. Upload CSV File</h3>
              {file ? (
                <p className="dropzone-filename">
                  ✅ {file.name} — {records.length} records loaded
                </p>
              ) : (
                <p>Drag & drop your CSV file here, or click to browse</p>
              )}
            </div>
          </div>

          {error && <div className="batch-error">⚠️ {error}</div>}

          {records.length > 0 && (
            <button
              className="batch-analyze-btn"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner" /> Analyzing {records.length} records...
                </>
              ) : (
                `🔍 Analyze ${records.length} Accounts`
              )}
            </button>
          )}
        </div>
      ) : (
        <div className="batch-results-section">
          {/* Summary Cards */}
          <div className="batch-summary">
            <div className="batch-summary-card glass-card">
              <div className="batch-summary-value">{results.summary.total}</div>
              <div className="batch-summary-label">Total</div>
            </div>
            <div className="batch-summary-card glass-card">
              <div className="batch-summary-value" style={{ color: "#ef4444" }}>
                {results.summary.high_risk}
              </div>
              <div className="batch-summary-label">High Risk</div>
            </div>
            <div className="batch-summary-card glass-card">
              <div className="batch-summary-value" style={{ color: "#f59e0b" }}>
                {results.summary.medium_risk}
              </div>
              <div className="batch-summary-label">Medium</div>
            </div>
            <div className="batch-summary-card glass-card">
              <div className="batch-summary-value" style={{ color: "#22c55e" }}>
                {results.summary.low_risk}
              </div>
              <div className="batch-summary-label">Low Risk</div>
            </div>
          </div>

          {/* Results Table */}
          <div className="batch-table-wrapper glass-card">
            <table className="batch-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Risk Level</th>
                  <th>Probability</th>
                  <th>Assessment</th>
                </tr>
              </thead>
              <tbody>
                {results.results.map((r, i) => (
                  <tr key={i} className={`batch-row-${r.risk_level}`}>
                    <td>{i + 1}</td>
                    <td>
                      <span className={`batch-risk-badge ${r.risk_level}`}>
                        {riskIcon[r.risk_level] || "❓"} {r.label}
                      </span>
                    </td>
                    <td>
                      {r.probability !== null
                        ? `${Math.round(r.probability * 100)}%`
                        : "Error"}
                    </td>
                    <td className="batch-message">{r.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Action Buttons */}
          <div className="batch-actions">
            <button className="batch-reset-btn" onClick={handleReset}>
              ← Upload New File
            </button>
            <button
              className="batch-download-btn"
              onClick={handleDownloadZip}
              disabled={downloadingZip}
            >
              {downloadingZip ? (
                <>
                  <span className="spinner" /> Generating...
                </>
              ) : (
                "📦 Download All Reports (ZIP)"
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
