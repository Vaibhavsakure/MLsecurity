const API_BASE = import.meta.env.PROD ? (import.meta.env.VITE_API_URL || "") : "http://127.0.0.1:8000";

// ---------------------------------------------------------------------------
// Auth header helper — injects Firebase ID token if available
// ---------------------------------------------------------------------------
let _getIdToken = null;

/**
 * Call this once from App.jsx to wire up the token provider.
 * This avoids circular dependencies with AuthContext.
 */
export function setTokenProvider(fn) {
  _getIdToken = fn;
}

async function getAuthHeaders() {
  const headers = { "Content-Type": "application/json" };
  if (_getIdToken) {
    try {
      const token = await _getIdToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    } catch {
      // Silently continue without auth in dev mode
    }
  }
  return headers;
}

// ---------------------------------------------------------------------------
// Fetch wrapper with timeout, retry on 401/429
// ---------------------------------------------------------------------------
async function apiFetch(url, options = {}) {
  const headers = await getAuthHeaders();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000); // 15s timeout

  try {
    let resp = await fetch(url, {
      ...options,
      headers: { ...headers, ...options.headers },
      signal: controller.signal,
    });

    // Retry once on 401 with fresh token
    if (resp.status === 401 && _getIdToken) {
      const freshToken = await _getIdToken();
      if (freshToken) {
        headers["Authorization"] = `Bearer ${freshToken}`;
        resp = await fetch(url, {
          ...options,
          headers: { ...headers, ...options.headers },
          signal: controller.signal,
        });
      }
    }

    // Rate limited — show user-friendly error
    if (resp.status === 429) {
      throw new Error("Rate limit exceeded. Please wait a moment and try again.");
    }

    return resp;
  } finally {
    clearTimeout(timeout);
  }
}

// ---------------------------------------------------------------------------
// API Functions
// ---------------------------------------------------------------------------

export async function predictPlatform(platform, data, { ensemble = false } = {}) {
  const params = ensemble ? "?ensemble=true" : "";
  const res = await apiFetch(`${API_BASE}/api/predict/${platform}${params}`, {
    method: "POST",
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

export async function fetchRedditUser(username) {
  const res = await apiFetch(`${API_BASE}/api/fetch/reddit/${encodeURIComponent(username)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch Reddit user data");
  }
  return res.json();
}

export async function downloadReport(reportData) {
  const res = await apiFetch(`${API_BASE}/api/report/generate`, {
    method: "POST",
    body: JSON.stringify(reportData),
  });

  if (!res.ok) {
    throw new Error("Failed to generate report");
  }

  const { token } = await res.json();
  window.open(`${API_BASE}/api/report/download/${token}`, "_blank");
}

export async function scanUrl(url) {
  const res = await apiFetch(`${API_BASE}/api/scan/url`, {
    method: "POST",
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to scan URL");
  }

  return res.json();
}

export async function batchPredict(platform, records) {
  const res = await apiFetch(`${API_BASE}/api/predict/batch/${platform}`, {
    method: "POST",
    body: JSON.stringify({ records }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Batch prediction failed");
  }

  return res.json();
}

export async function downloadBatchReport(reports) {
  const res = await apiFetch(`${API_BASE}/api/report/batch`, {
    method: "POST",
    body: JSON.stringify(reports),
  });

  if (!res.ok) {
    throw new Error("Failed to generate batch report");
  }

  const { token } = await res.json();
  window.open(`${API_BASE}/api/report/download-zip/${token}`, "_blank");
}

export async function getModelComparison() {
  const res = await fetch(`${API_BASE}/api/models/comparison`);
  if (!res.ok) {
    throw new Error("Failed to fetch model comparison data");
  }
  return res.json();
}

// --- Chatbot (routed through backend proxy) ---
export async function sendChatMessage(messages) {
  const res = await apiFetch(`${API_BASE}/api/chat`, {
    method: "POST",
    body: JSON.stringify({ messages }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Chat request failed");
  }

  return res.json();
}
