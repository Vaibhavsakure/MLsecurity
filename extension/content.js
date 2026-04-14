// SocialGuard AI — Content Script
// Runs on social media pages to detect profile information

(function () {
  "use strict";

  // Detect if current page is a profile page
  const url = window.location.href;

  const PLATFORM_PATTERNS = {
    instagram: /instagram\.com\/([^/?#]+)\/?$/i,
    twitter: /(?:twitter\.com|x\.com)\/([^/?#]+)\/?$/i,
    reddit: /reddit\.com\/(?:user|u)\/([^/?#]+)/i,
    facebook: /facebook\.com\/([^/?#]+)\/?$/i,
    linkedin: /linkedin\.com\/in\/([^/?#]+)/i,
    youtube: /youtube\.com\/(?:@|channel\/|c\/)([^/?#]+)/i,
  };

  let detectedPlatform = null;
  let detectedUsername = null;

  for (const [platform, regex] of Object.entries(PLATFORM_PATTERNS)) {
    const match = url.match(regex);
    if (match) {
      const username = match[1];
      const skipPages = [
        "explore", "reels", "stories", "home", "settings",
        "notifications", "messages", "search", "feed", "jobs",
        "premium", "watch", "shorts", "trending", "results",
      ];
      if (!skipPages.includes(username.toLowerCase())) {
        detectedPlatform = platform;
        detectedUsername = username;
        break;
      }
    }
  }

  // Send detected info to background script
  if (detectedPlatform && detectedUsername) {
    chrome.runtime.sendMessage({
      type: "PROFILE_DETECTED",
      platform: detectedPlatform,
      username: detectedUsername,
      url: url,
    });
  }
})();
