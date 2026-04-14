import { useEffect, useState } from "react";
import { useAuth } from "./AuthContext";
import { getAnalysisHistory } from "../firebase";

export default function HistoryPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    getAnalysisHistory(user.uid)
      .then(setHistory)
      .catch((err) => console.error("Failed to load history:", err))
      .finally(() => setLoading(false));
  }, [user]);

  const filtered = filter === "all" ? history : history.filter((h) => h.platform === filter);

  const platformColors = {
    instagram: "#E1306C",
    twitter: "#1DA1F2",
    reddit: "#FF4500",
    facebook: "#1877F2",
    linkedin: "#0A66C2",
    youtube: "#FF0000",
  };

  const riskIcons = { low: "✅", medium: "⚠️", high: "🚨" };

  if (loading) {
    return (
      <div className="history-page">
        <div className="history-loading">
          <div className="auth-loading-spinner" />
          <p>Loading history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="history-page">
      <div className="history-header">
        <div>
          <h1>Analysis History</h1>
          <p className="history-subtitle">
            {history.length} scan{history.length !== 1 ? "s" : ""} performed
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="history-filters">
        {["all", "instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"].map((p) => (
          <button
            key={p}
            className={`filter-chip ${filter === p ? "active" : ""}`}
            onClick={() => setFilter(p)}
            style={filter === p && p !== "all" ? { borderColor: platformColors[p], color: platformColors[p] } : {}}
          >
            {p === "all" ? "All Platforms" : p.charAt(0).toUpperCase() + p.slice(1)}
          </button>
        ))}
      </div>

      {/* History List */}
      {filtered.length === 0 ? (
        <div className="history-empty glass-card">
          <p>🔍 No analyses found{filter !== "all" ? ` for ${filter}` : ""}.</p>
          <p className="history-empty-sub">Run your first scan from the home page!</p>
        </div>
      ) : (
        <div className="history-list">
          {filtered.map((item) => (
            <div key={item.id} className="history-item glass-card">
              <div className="history-item-left">
                <div
                  className="history-platform-badge"
                  style={{ backgroundColor: `${platformColors[item.platform]}20`, color: platformColors[item.platform] }}
                >
                  {item.platform?.charAt(0).toUpperCase() + item.platform?.slice(1)}
                </div>
                <div className="history-item-details">
                  <span className="history-prob">
                    {Math.round(item.probability * 100)}% probability
                  </span>
                  <span className="history-date">
                    {item.createdAt
                      ? new Date(item.createdAt).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "Just now"}
                  </span>
                </div>
              </div>
              <div className={`history-risk-badge ${item.risk_level}`}>
                {riskIcons[item.risk_level]} {item.label}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
