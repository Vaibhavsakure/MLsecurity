import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from "recharts";

export default function ShapChart({ importances }) {
  if (!importances || importances.length === 0) return null;

  const data = importances.map((item) => ({
    name: item.feature,
    value: item.value,
  }));

  return (
    <div className="shap-section">
      <h3 className="shap-title">
        <span className="shap-icon">🧠</span> Why This Prediction?
      </h3>
      <p className="shap-subtitle">
        Features that contributed most to the risk score (SHAP analysis)
      </p>
      <div className="shap-chart-wrapper">
        <ResponsiveContainer width="100%" height={data.length * 40 + 20}>
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
            <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: "#e2e8f0", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={95}
            />
            <Tooltip
              contentStyle={{
                background: "rgba(17,24,39,0.95)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "8px",
                color: "#f1f5f9",
                fontSize: "13px",
              }}
              formatter={(value) => [value > 0 ? `+${value.toFixed(4)} (↑ Risk)` : `${value.toFixed(4)} (↓ Risk)`, "SHAP"]}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {data.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.value > 0 ? "#ef4444" : "#22c55e"}
                  fillOpacity={0.8}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="shap-legend">
        <span className="shap-legend-item">
          <span className="shap-dot red" /> Increases Risk
        </span>
        <span className="shap-legend-item">
          <span className="shap-dot green" /> Decreases Risk
        </span>
      </div>
    </div>
  );
}
