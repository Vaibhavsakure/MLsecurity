import { useState } from "react";
import { useAuth } from "./AuthContext";

export default function ApiKeysPage() {
  const { user } = useAuth();
  const [keys, setKeys] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(null);

  const generateKey = () => {
    setGenerating(true);
    // Generate a local API key (in production, this would be server-side)
    const key = "sg_" + Array.from(crypto.getRandomValues(new Uint8Array(24)))
      .map(b => b.toString(16).padStart(2, "0")).join("");
    const newKey = {
      id: Date.now().toString(),
      key,
      name: `API Key ${keys.length + 1}`,
      created: new Date().toISOString(),
      lastUsed: null,
      requests: 0,
    };
    setKeys([newKey, ...keys]);
    setGenerating(false);
  };

  const revokeKey = (id) => {
    if (window.confirm("Are you sure you want to revoke this API key? This cannot be undone.")) {
      setKeys(keys.filter(k => k.id !== id));
    }
  };

  const copyKey = (key, id) => {
    navigator.clipboard.writeText(key);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const getCurlExample = (key) => {
    return `curl -X POST "http://127.0.0.1:8000/api/v1/analyze/instagram" \\
  -H "X-API-Key: ${key}" \\
  -H "Content-Type: application/json" \\
  -d '{"profile_pic": 1, "username_has_numbers": 0, "bio_present": 1, "posts": 42, "followers": 1500, "following": 800}'`;
  };

  return (
    <div className="api-keys-page">
      <div className="api-keys-header">
        <div>
          <h1>🔑 API Keys</h1>
          <p className="api-keys-subtitle">Manage API keys for programmatic access to SocialGuard AI</p>
        </div>
        <button className="generate-key-btn" onClick={generateKey} disabled={generating}>
          {generating ? "Generating..." : "+ Generate New Key"}
        </button>
      </div>

      {/* API Documentation */}
      <div className="api-docs-card glass-card">
        <h3>📖 Quick Start</h3>
        <p>Use your API key to analyze profiles programmatically. Include it as an <code>X-API-Key</code> header.</p>
        <div className="api-endpoint-list">
          <div className="api-endpoint">
            <span className="api-method post">POST</span>
            <code>/api/v1/analyze/{"{platform}"}</code>
            <span className="api-desc">Analyze a profile</span>
          </div>
          <div className="api-endpoint">
            <span className="api-method get">GET</span>
            <code>/api/v1/platforms</code>
            <span className="api-desc">List supported platforms</span>
          </div>
        </div>
      </div>

      {/* Keys List */}
      {keys.length === 0 ? (
        <div className="api-keys-empty glass-card">
          <p>🔐 No API keys yet. Generate one to get started!</p>
        </div>
      ) : (
        <div className="api-keys-list">
          {keys.map(k => (
            <div key={k.id} className="api-key-card glass-card">
              <div className="api-key-header">
                <h4>{k.name}</h4>
                <span className="api-key-created">
                  Created {new Date(k.created).toLocaleDateString()}
                </span>
              </div>
              <div className="api-key-value">
                <code>{k.key.slice(0, 12)}...{k.key.slice(-8)}</code>
                <button
                  className={`copy-btn ${copied === k.id ? "copied" : ""}`}
                  onClick={() => copyKey(k.key, k.id)}
                >
                  {copied === k.id ? "✅ Copied!" : "📋 Copy"}
                </button>
              </div>
              <div className="api-key-stats">
                <span>📊 {k.requests} requests</span>
                <span>🕐 {k.lastUsed ? new Date(k.lastUsed).toLocaleDateString() : "Never used"}</span>
              </div>
              <details className="api-key-curl">
                <summary>cURL Example</summary>
                <pre>{getCurlExample(k.key)}</pre>
              </details>
              <div className="api-key-actions">
                <button className="revoke-btn" onClick={() => revokeKey(k.id)}>
                  🗑️ Revoke
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
