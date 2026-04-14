import { useEffect, useState } from "react";
import { useAuth } from "./AuthContext";
import { getAnalysisHistory } from "../firebase";
import { getModelComparison } from "../api";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  AreaChart, Area,
} from "recharts";

const COLORS = {
  low: "#22c55e",
  medium: "#f59e0b",
  high: "#ef4444",
};

const PLATFORM_COLORS = {
  instagram: "#E1306C",
  twitter: "#1DA1F2",
  reddit: "#FF4500",
  facebook: "#1877F2",
  linkedin: "#0A66C2",
  youtube: "#FF0000",
};

const PLATFORM_ICONS = {
  instagram: "📸",
  twitter: "🐦",
  reddit: "👽",
  facebook: "📘",
  linkedin: "💼",
  youtube: "🎬",
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    if (!user) return;
    Promise.all([
      getAnalysisHistory(user.uid).catch(() => []),
      getModelComparison().catch(() => null),
    ])
      .then(([hist, met]) => {
        setHistory(hist);
        setMetrics(met);
      })
      .finally(() => setLoading(false));
  }, [user]);

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="history-loading">
          <div className="auth-loading-spinner" />
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // History Stats
  const total = history.length;
  const lowCount = history.filter((h) => h.risk_level === "low").length;
  const medCount = history.filter((h) => h.risk_level === "medium").length;
  const highCount = history.filter((h) => h.risk_level === "high").length;
  const avgProb = total > 0 ? (history.reduce((s, h) => s + h.probability, 0) / total) : 0;

  const riskData = [
    { name: "Low Risk", value: lowCount, color: COLORS.low },
    { name: "Medium Risk", value: medCount, color: COLORS.medium },
    { name: "High Risk", value: highCount, color: COLORS.high },
  ].filter((d) => d.value > 0);

  const platformData = Object.entries(
    history.reduce((acc, h) => {
      acc[h.platform] = (acc[h.platform] || 0) + 1;
      return acc;
    }, {})
  ).map(([platform, count]) => ({
    name: platform.charAt(0).toUpperCase() + platform.slice(1),
    count,
    fill: PLATFORM_COLORS[platform] || "#8b5cf6",
  }));

  // Model metrics
  const metricsData = metrics?.available ? metrics.data : null;

  // Accuracy leaderboard
  const leaderboard = metricsData
    ? Object.entries(metricsData)
        .map(([platform, data]) => ({
          platform: platform.charAt(0).toUpperCase() + platform.slice(1),
          key: platform,
          accuracy: data.accuracy,
          f1: data.f1_score,
          auc: data.auc,
          precision: data.precision,
          recall: data.recall,
          samples: data.samples,
          features: data.features,
        }))
        .sort((a, b) => b.accuracy - a.accuracy)
    : [];

  // Radar chart data
  const radarData = leaderboard.map((item) => ({
    platform: item.platform,
    Accuracy: item.accuracy,
    "F1 Score": item.f1 * 100,
    "AUC": item.auc * 100,
    Precision: item.precision * 100,
    Recall: item.recall * 100,
  }));

  // Model comparison data
  const comparisonData = metricsData
    ? Object.entries(metricsData).map(([platform, data]) => ({
        platform: platform.charAt(0).toUpperCase() + platform.slice(1),
        XGBoost: data.comparison?.["XGBoost"]?.accuracy || 0,
        "Random Forest": data.comparison?.["Random Forest"]?.accuracy || 0,
        "Logistic Regression": data.comparison?.["Logistic Regression"]?.accuracy || 0,
      }))
    : [];

  // Threat heatmap data
  const threatData = ["instagram", "twitter", "reddit", "facebook", "linkedin", "youtube"].map(
    (platform) => {
      const platformHistory = history.filter((h) => h.platform === platform);
      const pTotal = platformHistory.length;
      const pHigh = platformHistory.filter((h) => h.risk_level === "high").length;
      const pMed = platformHistory.filter((h) => h.risk_level === "medium").length;
      const pLow = platformHistory.filter((h) => h.risk_level === "low").length;
      return {
        platform: platform.charAt(0).toUpperCase() + platform.slice(1),
        key: platform,
        total: pTotal,
        high: pHigh,
        medium: pMed,
        low: pLow,
        threatScore: pTotal > 0 ? Math.round(((pHigh * 3 + pMed * 1.5) / (pTotal * 3)) * 100) : 0,
      };
    }
  );

  // Recent 5
  const recent = history.slice(0, 5);

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "analytics", label: "Analytics" },
    { id: "models", label: "Model Performance" },
    { id: "threats", label: "Threat Map" },
  ];

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p className="dashboard-subtitle">Security analytics & model performance</p>
      </div>

      {/* Tab Navigation */}
      <div className="dashboard-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`dashboard-tab ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ===================== OVERVIEW TAB ===================== */}
      {activeTab === "overview" && (
        <>
          {/* Stat Cards */}
          <div className="stats-grid">
            <div className="stat-card glass-card">
              <div className="stat-icon">🔍</div>
              <div className="stat-value">{total}</div>
              <div className="stat-label">Total Scans</div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-icon">🚨</div>
              <div className="stat-value" style={{ color: COLORS.high }}>{highCount}</div>
              <div className="stat-label">High Risk</div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-icon">✅</div>
              <div className="stat-value" style={{ color: COLORS.low }}>{lowCount}</div>
              <div className="stat-label">Low Risk</div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-icon">📊</div>
              <div className="stat-value">{Math.round(avgProb * 100)}%</div>
              <div className="stat-label">Avg Risk Score</div>
            </div>
          </div>

          {total === 0 ? (
            <div className="history-empty glass-card">
              <p>📊 Run some analyses to see your dashboard data!</p>
            </div>
          ) : (
            <>
              {/* Charts */}
              <div className="charts-grid">
                {/* Risk Distribution Pie */}
                <div className="chart-card glass-card">
                  <h3>Risk Distribution</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={riskData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={90}
                        innerRadius={50}
                        paddingAngle={3}
                        stroke="none"
                      >
                        {riskData.map((entry, i) => (
                          <Cell key={i} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          background: "rgba(17,24,39,0.95)",
                          border: "1px solid rgba(255,255,255,0.1)",
                          borderRadius: "8px",
                          color: "#f1f5f9",
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="chart-legend">
                    {riskData.map((d) => (
                      <span key={d.name} className="chart-legend-item">
                        <span className="chart-legend-dot" style={{ background: d.color }} />
                        {d.name} ({d.value})
                      </span>
                    ))}
                  </div>
                </div>

                {/* Platform Bar Chart */}
                <div className="chart-card glass-card">
                  <h3>Scans by Platform</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={platformData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} />
                      <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{
                          background: "rgba(17,24,39,0.95)",
                          border: "1px solid rgba(255,255,255,0.1)",
                          borderRadius: "8px",
                          color: "#f1f5f9",
                        }}
                      />
                      <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                        {platformData.map((entry, i) => (
                          <Cell key={i} fill={entry.fill} fillOpacity={0.85} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="recent-section">
                <h3>Recent Activity</h3>
                <div className="recent-list">
                  {recent.map((item) => (
                    <div key={item.id} className="recent-item glass-card">
                      <div
                        className="recent-platform-dot"
                        style={{ background: PLATFORM_COLORS[item.platform] }}
                      />
                      <div className="recent-info">
                        <span className="recent-platform">
                          {item.platform?.charAt(0).toUpperCase() + item.platform?.slice(1)}
                        </span>
                        <span className="recent-date">
                          {item.createdAt
                            ? new Date(item.createdAt).toLocaleDateString("en-US", {
                                month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
                              })
                            : "Just now"}
                        </span>
                      </div>
                      <div className={`recent-badge ${item.risk_level}`}>
                        {Math.round(item.probability * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </>
      )}

      {/* ===================== ANALYTICS TAB ===================== */}
      {activeTab === "analytics" && (
        <>
          {total === 0 ? (
            <div className="history-empty glass-card">
              <p>📈 Run some analyses to see timeline analytics!</p>
            </div>
          ) : (
            <>
              {/* Risk Score Timeline */}
              <div className="chart-card glass-card" style={{ marginBottom: 24 }}>
                <h3>📈 Risk Score Timeline</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart
                    data={history
                      .filter(h => h.createdAt)
                      .sort((a, b) => (a.createdAt || "").localeCompare(b.createdAt || ""))
                      .map((h, i) => ({
                        index: i + 1,
                        date: h.createdAt ? new Date(h.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : `#${i+1}`,
                        risk: Math.round(h.probability * 100),
                        platform: h.platform,
                      }))
                    }
                    margin={{ top: 10, right: 20, left: -10, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} />
                    <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} domain={[0, 100]} />
                    <Tooltip
                      contentStyle={{
                        background: "rgba(17,24,39,0.95)",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: "8px",
                        color: "#f1f5f9",
                      }}
                      formatter={(v) => [`${v}%`, "Risk Score"]}
                    />
                    <Area
                      type="monotone"
                      dataKey="risk"
                      stroke="#00d4ff"
                      fill="url(#riskGradient)"
                      strokeWidth={2}
                      dot={{ r: 3, fill: "#00d4ff" }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="charts-grid">
                {/* Confidence Distribution */}
                <div className="chart-card glass-card">
                  <h3>🎯 Confidence Distribution</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart
                      data={(() => {
                        const buckets = [
                          { range: "0-20%", count: 0, fill: "#22c55e" },
                          { range: "20-40%", count: 0, fill: "#84cc16" },
                          { range: "40-60%", count: 0, fill: "#f59e0b" },
                          { range: "60-80%", count: 0, fill: "#f97316" },
                          { range: "80-100%", count: 0, fill: "#ef4444" },
                        ];
                        history.forEach(h => {
                          const pct = h.probability * 100;
                          if (pct < 20) buckets[0].count++;
                          else if (pct < 40) buckets[1].count++;
                          else if (pct < 60) buckets[2].count++;
                          else if (pct < 80) buckets[3].count++;
                          else buckets[4].count++;
                        });
                        return buckets;
                      })()}
                      margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="range" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} />
                      <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{
                          background: "rgba(17,24,39,0.95)",
                          border: "1px solid rgba(255,255,255,0.1)",
                          borderRadius: "8px",
                          color: "#f1f5f9",
                        }}
                      />
                      <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                        {[0,1,2,3,4].map(i => (
                          <Cell key={i} fill={["#22c55e","#84cc16","#f59e0b","#f97316","#ef4444"][i]} fillOpacity={0.85} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Weekly Activity */}
                <div className="chart-card glass-card">
                  <h3>📅 Weekly Scan Activity</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart
                      data={(() => {
                        const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
                        const counts = new Array(7).fill(0);
                        history.forEach(h => {
                          if (h.createdAt) {
                            const d = new Date(h.createdAt).getDay();
                            counts[d]++;
                          }
                        });
                        return days.map((day, i) => ({ day, scans: counts[i] }));
                      })()}
                      margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="day" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} />
                      <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{
                          background: "rgba(17,24,39,0.95)",
                          border: "1px solid rgba(255,255,255,0.1)",
                          borderRadius: "8px",
                          color: "#f1f5f9",
                        }}
                      />
                      <Bar dataKey="scans" fill="#8b5cf6" radius={[6, 6, 0, 0]} fillOpacity={0.85} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}
        </>
      )}

      {/* ===================== MODELS TAB ===================== */}
      {activeTab === "models" && (
        <>
          {!metricsData ? (
            <div className="history-empty glass-card">
              <p>⚙️ Run <code>python evaluate_models.py</code> to generate model metrics</p>
            </div>
          ) : (
            <>
              {/* Accuracy Leaderboard */}
              <div className="leaderboard-section">
                <h3>🏆 Model Accuracy Leaderboard</h3>
                <div className="leaderboard-table">
                  <div className="leaderboard-header">
                    <span className="lb-rank">#</span>
                    <span className="lb-platform">Platform</span>
                    <span className="lb-metric">Accuracy</span>
                    <span className="lb-metric">F1 Score</span>
                    <span className="lb-metric">AUC</span>
                    <span className="lb-metric">Samples</span>
                  </div>
                  {leaderboard.map((item, i) => (
                    <div key={item.key} className="leaderboard-row glass-card">
                      <span className="lb-rank">
                        {i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : `#${i + 1}`}
                      </span>
                      <span className="lb-platform">
                        <span className="lb-icon">{PLATFORM_ICONS[item.key]}</span>
                        {item.platform}
                      </span>
                      <span className="lb-metric" style={{ color: item.accuracy >= 95 ? COLORS.low : item.accuracy >= 90 ? COLORS.medium : COLORS.high }}>
                        {item.accuracy}%
                      </span>
                      <span className="lb-metric">{(item.f1 * 100).toFixed(1)}%</span>
                      <span className="lb-metric">{(item.auc * 100).toFixed(1)}%</span>
                      <span className="lb-metric lb-samples">{item.samples.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Model Comparison */}
              <div className="charts-grid">
                <div className="chart-card glass-card">
                  <h3>Algorithm Comparison</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={comparisonData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="platform" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} />
                      <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} domain={[80, 101]} />
                      <Tooltip
                        contentStyle={{
                          background: "rgba(17,24,39,0.95)",
                          border: "1px solid rgba(255,255,255,0.1)",
                          borderRadius: "8px",
                          color: "#f1f5f9",
                        }}
                        formatter={(v) => [`${v}%`, ""]}
                      />
                      <Bar dataKey="XGBoost" fill="#00d4ff" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Random Forest" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Logistic Regression" fill="#ec4899" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                  <div className="chart-legend">
                    <span className="chart-legend-item">
                      <span className="chart-legend-dot" style={{ background: "#00d4ff" }} /> XGBoost
                    </span>
                    <span className="chart-legend-item">
                      <span className="chart-legend-dot" style={{ background: "#8b5cf6" }} /> Random Forest
                    </span>
                    <span className="chart-legend-item">
                      <span className="chart-legend-dot" style={{ background: "#ec4899" }} /> Logistic Regression
                    </span>
                  </div>
                </div>

                {/* Radar Chart */}
                <div className="chart-card glass-card">
                  <h3>Performance Radar</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="rgba(255,255,255,0.1)" />
                      <PolarAngleAxis dataKey="platform" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                      <PolarRadiusAxis tick={{ fill: "#64748b", fontSize: 10 }} domain={[80, 100]} />
                      <Radar name="Accuracy" dataKey="Accuracy" stroke="#00d4ff" fill="#00d4ff" fillOpacity={0.15} strokeWidth={2} />
                      <Radar name="F1 Score" dataKey="F1 Score" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.1} strokeWidth={2} />
                      <Tooltip
                        contentStyle={{
                          background: "rgba(17,24,39,0.95)",
                          border: "1px solid rgba(255,255,255,0.1)",
                          borderRadius: "8px",
                          color: "#f1f5f9",
                        }}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}
        </>
      )}

      {/* ===================== THREATS TAB ===================== */}
      {activeTab === "threats" && (
        <>
          {total === 0 ? (
            <div className="history-empty glass-card">
              <p>🛡️ Run analyses to see threat intelligence data!</p>
            </div>
          ) : (
            <>
              {/* Threat Heatmap */}
              <div className="threat-section">
                <h3>🛡️ Platform Threat Map</h3>
                <p className="threat-subtitle">Based on your scan history</p>
                <div className="threat-grid">
                  {threatData.filter((t) => t.total > 0).map((item) => (
                    <div key={item.key} className="threat-card glass-card">
                      <div className="threat-card-header">
                        <span className="threat-platform-icon">{PLATFORM_ICONS[item.key]}</span>
                        <span className="threat-platform-name">{item.platform}</span>
                        <span
                          className="threat-score"
                          style={{
                            color: item.threatScore > 60 ? COLORS.high : item.threatScore > 30 ? COLORS.medium : COLORS.low,
                          }}
                        >
                          {item.threatScore}%
                        </span>
                      </div>
                      <div className="threat-bar-container">
                        <div className="threat-bar">
                          {item.high > 0 && (
                            <div
                              className="threat-bar-segment"
                              style={{
                                width: `${(item.high / item.total) * 100}%`,
                                background: COLORS.high,
                              }}
                            />
                          )}
                          {item.medium > 0 && (
                            <div
                              className="threat-bar-segment"
                              style={{
                                width: `${(item.medium / item.total) * 100}%`,
                                background: COLORS.medium,
                              }}
                            />
                          )}
                          {item.low > 0 && (
                            <div
                              className="threat-bar-segment"
                              style={{
                                width: `${(item.low / item.total) * 100}%`,
                                background: COLORS.low,
                              }}
                            />
                          )}
                        </div>
                      </div>
                      <div className="threat-stats">
                        <span>{item.total} scans</span>
                        <span style={{ color: COLORS.high }}>{item.high} high</span>
                        <span style={{ color: COLORS.medium }}>{item.medium} med</span>
                        <span style={{ color: COLORS.low }}>{item.low} low</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {threatData.every((t) => t.total === 0) && (
                <div className="history-empty glass-card">
                  <p>No threat data available yet. Scan some profiles!</p>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
