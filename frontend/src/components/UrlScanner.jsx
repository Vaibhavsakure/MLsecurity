import { useState } from "react";
import { scanUrl } from "../api";

const PLATFORM_LABELS = {
  instagram: { name: "Instagram", color: "#E1306C", icon: "📸" },
  twitter: { name: "Twitter", color: "#1DA1F2", icon: "🐦" },
  reddit: { name: "Reddit", color: "#FF4500", icon: "👽" },
  facebook: { name: "Facebook", color: "#1877F2", icon: "📘" },
  linkedin: { name: "LinkedIn", color: "#0A66C2", icon: "💼" },
  youtube: { name: "YouTube", color: "#FF0000", icon: "▶️" },
};

const SCAN_STAGES = [
  "Detecting platform...",
  "Connecting to profile...",
  "Fetching account data...",
  "Running AI analysis...",
];

export default function UrlScanner({ onResult, onPlatformDetected }) {
  const [url, setUrl] = useState("");
  const [scanning, setScanning] = useState(false);
  const [scanStage, setScanStage] = useState(0);
  const [error, setError] = useState(null);
  const [detected, setDetected] = useState(null);
  const [manualInfo, setManualInfo] = useState(null);

  const detectPlatformLocal = (input) => {
    const patterns = {
      instagram: /(?:instagram\.com)\//i,
      twitter: /(?:twitter\.com|x\.com)\//i,
      reddit: /(?:reddit\.com\/(?:user|u))\//i,
      facebook: /(?:facebook\.com)\//i,
      linkedin: /(?:linkedin\.com\/in)\//i,
      youtube: /(?:youtube\.com\/(?:@|channel|c))\//i,
    };
    for (const [platform, regex] of Object.entries(patterns)) {
      if (regex.test(input)) return platform;
    }
    return null;
  };

  const handleUrlChange = (e) => {
    const val = e.target.value;
    setUrl(val);
    setError(null);
    setManualInfo(null);
    if (val.length > 10) {
      setDetected(detectPlatformLocal(val));
    } else {
      setDetected(null);
    }
  };

  const handleScan = async () => {
    if (!url.trim()) return;
    setScanning(true);
    setError(null);
    setManualInfo(null);
    setScanStage(0);

    const stageTimer = setInterval(() => {
      setScanStage((prev) => Math.min(prev + 1, SCAN_STAGES.length - 1));
    }, 700);

    try {
      const result = await scanUrl(url.trim());
      clearInterval(stageTimer);

      if (result.probability !== undefined && result.auto_fetched) {
        // Reddit auto-fetch success — show result directly!
        onResult(result);
      } else if (result.needs_manual_input) {
        // Other platform — show helpful redirect
        setManualInfo(result);
      } else if (result.auto_detected) {
        onPlatformDetected(result.platform, result.username);
      }
    } catch (err) {
      clearInterval(stageTimer);
      setError(err.message || "Failed to scan URL");
    } finally {
      clearInterval(stageTimer);
      setScanning(false);
      setScanStage(0);
    }
  };

  const handleGoToForm = () => {
    if (manualInfo) {
      onPlatformDetected(manualInfo.platform, manualInfo.username);
      setManualInfo(null);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleScan();
  };

  const platformInfo = detected ? PLATFORM_LABELS[detected] : null;

  return (
    <div className="url-scanner">
      <div className="url-scanner-inner glass-card">
        <div className="url-scanner-header">
          <span className="url-scanner-badge">🔗 Smart Scan</span>
          <span className="url-scanner-label">
            Paste any social media profile URL for instant analysis
          </span>
        </div>

        <div className="url-scanner-input-row">
          <div className="url-input-wrapper">
            {platformInfo && (
              <span
                className="url-detected-badge"
                style={{ background: `${platformInfo.color}20`, color: platformInfo.color }}
              >
                {platformInfo.icon} {platformInfo.name}
              </span>
            )}
            <input
              type="url"
              className="url-scanner-input"
              placeholder="https://reddit.com/u/username, instagram.com/user, twitter.com/user ..."
              value={url}
              onChange={handleUrlChange}
              onKeyDown={handleKeyDown}
              id="url-scanner-input"
            />
          </div>
          <button
            className="url-scan-btn"
            onClick={handleScan}
            disabled={scanning || !url.trim()}
          >
            {scanning ? (
              <>
                <span className="spinner" /> Analyzing...
              </>
            ) : (
              <>🔍 Scan Profile</>
            )}
          </button>
        </div>

        {/* Scanning Progress */}
        {scanning && (
          <div className="scan-progress">
            <div className="scan-progress-bar">
              <div
                className="scan-progress-fill"
                style={{ width: `${((scanStage + 1) / SCAN_STAGES.length) * 100}%` }}
              />
            </div>
            <div className="scan-stage-text">{SCAN_STAGES[scanStage]}</div>
          </div>
        )}

        {error && <div className="url-scanner-error">⚠️ {error}</div>}

        {/* Manual Input Redirect Card */}
        {manualInfo && (
          <div className="manual-redirect-card">
            <div className="manual-redirect-header">
              <span className="manual-redirect-icon">
                {PLATFORM_LABELS[manualInfo.platform]?.icon}
              </span>
              <div className="manual-redirect-info">
                <strong>
                  {PLATFORM_LABELS[manualInfo.platform]?.name} profile detected: @{manualInfo.username}
                </strong>
                <p>{manualInfo.why_manual}</p>
              </div>
            </div>

            {manualInfo.fields_help && Object.keys(manualInfo.fields_help).length > 0 && (
              <div className="manual-fields-preview">
                <span className="fields-preview-label">What you'll need to fill in:</span>
                <div className="fields-preview-list">
                  {Object.entries(manualInfo.fields_help).slice(0, 4).map(([key, desc]) => (
                    <div key={key} className="field-preview-item">
                      <span className="field-preview-name">{key.replace(/_/g, " ")}</span>
                      <span className="field-preview-desc">{desc}</span>
                    </div>
                  ))}
                  {Object.keys(manualInfo.fields_help).length > 4 && (
                    <div className="field-preview-item more">
                      +{Object.keys(manualInfo.fields_help).length - 4} more fields...
                    </div>
                  )}
                </div>
              </div>
            )}

            <button className="manual-redirect-btn" onClick={handleGoToForm}>
              Fill in {PLATFORM_LABELS[manualInfo.platform]?.name} Details →
            </button>
          </div>
        )}

        <div className="url-scanner-platforms">
          <span className="url-support-label">Auto-analyze:</span>
          <span className="url-platform-chip auto" style={{ color: "#FF4500" }}>
            👽 Reddit ✓
          </span>
          <span className="url-support-divider">|</span>
          <span className="url-support-label">Quick-detect:</span>
          {["instagram", "twitter", "facebook", "linkedin", "youtube"].map((key) => {
            const info = PLATFORM_LABELS[key];
            return (
              <span key={key} className="url-platform-chip" style={{ color: info.color }}>
                {info.icon} {info.name}
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
}
