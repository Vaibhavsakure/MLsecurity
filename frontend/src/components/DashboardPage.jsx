import { useEffect, useState } from "react";
import { useAuth } from "./AuthContext";
import { getAnalysisHistory } from "../firebase";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
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
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    getAnalysisHistory(user.uid)
      .then(setHistory)
      .catch(console.error)
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

  // Stats
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

  // Recent 5
  const recent = history.slice(0, 5);

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p className="dashboard-subtitle">Your analysis overview at a glance</p>
      </div>

      {total === 0 ? (
        <div className="history-empty glass-card">
          <p>📊 No data yet. Run some analyses to see your dashboard!</p>
        </div>
      ) : (
        <>
          {/* Stat Cards */}
          <div className="stats-grid">
            <div className="stat-card glass-card">
              <div className="stat-value">{total}</div>
              <div className="stat-label">Total Scans</div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-value" style={{ color: COLORS.high }}>{highCount}</div>
              <div className="stat-label">High Risk</div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-value" style={{ color: COLORS.low }}>{lowCount}</div>
              <div className="stat-label">Low Risk</div>
            </div>
            <div className="stat-card glass-card">
              <div className="stat-value">{Math.round(avgProb * 100)}%</div>
              <div className="stat-label">Avg Probability</div>
            </div>
          </div>

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
    </div>
  );
}
