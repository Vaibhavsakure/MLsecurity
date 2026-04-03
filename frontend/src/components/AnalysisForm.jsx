import { useState } from "react";

export default function AnalysisForm({ config, onSubmit, loading }) {
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

  const handleChange = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Convert to numbers
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
