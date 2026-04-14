// SocialGuard AI — Extension Popup Logic

const CIRCUMFERENCE = 2 * Math.PI * 50; // r=50

const PLATFORM_INFO = {
  instagram: { icon: "📸", name: "Instagram" },
  twitter: { icon: "🐦", name: "Twitter" },
  reddit: { icon: "👽", name: "Reddit" },
  facebook: { icon: "📘", name: "Facebook" },
  linkedin: { icon: "💼", name: "LinkedIn" },
  youtube: { icon: "▶️", name: "YouTube" },
};

// Load saved API URL
chrome.storage.local.get(["apiUrl"], (data) => {
  document.getElementById("api-url").value = data.apiUrl || "http://127.0.0.1:8000";
});

// Save API URL
document.getElementById("save-url").addEventListener("click", () => {
  const url = document.getElementById("api-url").value.trim();
  chrome.storage.local.set({ apiUrl: url });
});

// On popup open, detect if we're on a social media profile
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  const tab = tabs[0];
  if (!tab?.url) return;

  const detected = detectPlatform(tab.url);
  if (detected) {
    showScanSection(detected.platform, detected.username);
  } else {
    document.getElementById("status-text").textContent =
      "Navigate to a social media profile to scan it.";
  }
});

function detectPlatform(url) {
  const patterns = {
    instagram: /instagram\.com\/([^/?#]+)/i,
    twitter: /(?:twitter\.com|x\.com)\/([^/?#]+)/i,
    reddit: /reddit\.com\/(?:user|u)\/([^/?#]+)/i,
    facebook: /facebook\.com\/([^/?#]+)/i,
    linkedin: /linkedin\.com\/in\/([^/?#]+)/i,
    youtube: /youtube\.com\/(?:@|channel\/|c\/)([^/?#]+)/i,
  };

  for (const [platform, regex] of Object.entries(patterns)) {
    const match = url.match(regex);
    if (match) {
      const username = match[1];
      // Filter out non-profile pages
      const skipPages = ["explore", "reels", "stories", "home", "settings", "notifications", "messages", "search", "feed", "jobs", "premium"];
      if (skipPages.includes(username.toLowerCase())) continue;
      return { platform, username };
    }
  }
  return null;
}

function showScanSection(platform, username) {
  const info = PLATFORM_INFO[platform] || { icon: "🌐", name: platform };

  document.getElementById("status-section").classList.add("hidden");
  document.getElementById("scan-section").classList.remove("hidden");
  document.getElementById("platform-icon").textContent = info.icon;
  document.getElementById("platform-name").textContent = info.name;
  document.getElementById("username-display").textContent = `@${username}`;

  document.getElementById("scan-btn").addEventListener("click", () => {
    scanProfile(platform, username);
  });
}

async function scanProfile(platform, username) {
  // Show loading
  document.getElementById("scan-section").classList.add("hidden");
  document.getElementById("loading-section").classList.remove("hidden");

  try {
    const data = await chrome.storage.local.get(["apiUrl"]);
    const apiUrl = data.apiUrl || "http://127.0.0.1:8000";

    const response = await fetch(`${apiUrl}/api/scan/url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: `https://www.${platform === "twitter" ? "twitter" : platform}.com/${platform === "reddit" ? "user/" : platform === "linkedin" ? "in/" : platform === "youtube" ? "@" : ""}${username}`,
      }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const result = await response.json();

    if (result.probability !== undefined) {
      showResult(result);
    } else {
      // Platform detected but can't auto-scrape
      document.getElementById("loading-section").classList.add("hidden");
      document.getElementById("status-section").classList.remove("hidden");
      document.getElementById("status-text").textContent =
        `Profile detected on ${platform}. Open the web app for full analysis.`;
    }
  } catch (err) {
    document.getElementById("loading-section").classList.add("hidden");
    document.getElementById("status-section").classList.remove("hidden");
    document.getElementById("status-icon").textContent = "⚠️";
    document.getElementById("status-text").textContent =
      `Error: ${err.message}. Make sure the backend is running.`;
  }
}

function showResult(result) {
  document.getElementById("loading-section").classList.add("hidden");
  document.getElementById("result-section").classList.remove("hidden");

  const pct = Math.round(result.probability * 100);
  const offset = CIRCUMFERENCE - (pct / 100) * CIRCUMFERENCE;

  const riskColors = { low: "#22c55e", medium: "#f59e0b", high: "#ef4444" };
  const color = riskColors[result.risk_level] || "#00d4ff";

  const gaugeFill = document.getElementById("gauge-fill");
  gaugeFill.style.strokeDashoffset = offset;
  gaugeFill.style.stroke = color;

  const gaugePct = document.getElementById("gauge-pct");
  gaugePct.textContent = `${pct}%`;
  gaugePct.style.color = color;

  const badge = document.getElementById("risk-badge");
  badge.textContent = result.label;
  badge.className = `risk-badge ${result.risk_level}`;

  document.getElementById("risk-message").textContent = result.message;

  // Reset button
  document.getElementById("reset-btn").addEventListener("click", () => {
    document.getElementById("result-section").classList.add("hidden");
    // Re-detect
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const detected = detectPlatform(tabs[0]?.url || "");
      if (detected) {
        showScanSection(detected.platform, detected.username);
      } else {
        document.getElementById("status-section").classList.remove("hidden");
      }
    });
  });
}
