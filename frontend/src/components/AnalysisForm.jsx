import { useState } from "react";
import { fetchRedditUser } from "../api";

export default function AnalysisForm({ config, platform, onSubmit, loading }) {
  const buildInitial = () => {
    const init = {};
    config.fields.forEach((f) => {
      if (f.type === "select") {
        init[f.key] = f.options[0].value;
      } else {
        init[f.key] = "";
      }
    });
    return init;
  };

  const [formData, setFormData] = useState(buildInitial);
  const [username, setUsername] = useState("");
  const [fetching, setFetching] = useState(false);
  const [fetchError, setFetchError] = useState(null);
  const [fetchSuccess, setFetchSuccess] = useState(false);

  const canAutoFetch = platform === "reddit";

  const handleChange = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleAutoFetch = async () => {
    if (!username.trim()) return;
    setFetching(true);
    setFetchError(null);
    setFetchSuccess(false);
    try {
      const res = await fetchRedditUser(username.trim());
      if (res.success && res.data) {
        setFormData(res.data);
        setFetchSuccess(true);
      }
    } catch (err) {
      setFetchError(err.message || "Failed to fetch user data");
    } finally {
      setFetching(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {};
    config.fields.forEach((f) => {
      const raw = formData[f.key];
      if (f.type === "number") {
        payload[f.key] = parseInt(raw, 10) || 0;
      } else if (f.type === "float") {
        payload[f.key] = parseFloat(raw) || 0;
      } else if (f.type === "select") {
        payload[f.key] = parseInt(raw, 10);
      }
    });
    onSubmit(payload);
  };

  return (
    <form className="analysis-form glass-card" onSubmit={handleSubmit}>
      {/* Auto-Fetch Section (Reddit only) */}
      {canAutoFetch && (
        <div className="auto-fetch-section">
          <div className="auto-fetch-header">
            <span className="auto-fetch-badge">⚡ Auto-Fetch</span>
            <span className="auto-fetch-label">Enter a Reddit username to auto-fill</span>
          </div>
          <div className="auto-fetch-row">
            <span className="auto-fetch-prefix">u/</span>
            <input
              type="text"
              className="auto-fetch-input"
              placeholder="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <button
              type="button"
              className="auto-fetch-btn"
              onClick={handleAutoFetch}
              disabled={fetching || !username.trim()}
            >
              {fetching ? (
                <><span className="spinner" /> Fetching...</>
              ) : (
                "🔍 Fetch"
              )}
            </button>
          </div>
          {fetchError && <div className="auto-fetch-error">⚠️ {fetchError}</div>}
          {fetchSuccess && <div className="auto-fetch-success">✅ Data fetched for u/{username}! Fields filled below.</div>}
          <div className="auto-fetch-divider">
            <span>or enter manually</span>
          </div>
        </div>
      )}

      <div className="form-grid">
        {config.fields.map((field) => (
          <div key={field.key} className="form-group">
            <label htmlFor={`field-${field.key}`}>{field.label}</label>
            {field.type === "select" ? (
              <select
                id={`field-${field.key}`}
                value={formData[field.key]}
                onChange={(e) => handleChange(field.key, e.target.value)}
              >
                {field.options.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            ) : (
              <input
                id={`field-${field.key}`}
                type="number"
                step={field.type === "float" ? "0.01" : "1"}
                placeholder={field.placeholder}
                value={formData[field.key]}
                onChange={(e) => handleChange(field.key, e.target.value)}
                required
              />
            )}
          </div>
        ))}
        <button
          type="submit"
          className="submit-btn"
          disabled={loading}
          id="analyze-btn"
        >
          {loading && <span className="spinner" />}
          {loading ? "Analyzing..." : "🔍 Analyze Account"}
        </button>
      </div>
    </form>
  );
}
