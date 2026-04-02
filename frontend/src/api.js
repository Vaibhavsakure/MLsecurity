// Use the environment variable if available (e.g., when deployed on Railway/Vercel)
// Fall back to localhost:8000 for local development
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function predictPlatform(platform, data) {
  const res = await fetch(`${API_BASE}/api/predict/${platform}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error (${res.status})`);
  }

  return res.json();
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  return res.json();
}
