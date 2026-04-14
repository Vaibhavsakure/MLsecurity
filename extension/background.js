// SocialGuard AI — Background Service Worker

// Listen for profile detection from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "PROFILE_DETECTED") {
    // Store the detected profile info for the popup
    chrome.storage.session.set({
      detectedProfile: {
        platform: message.platform,
        username: message.username,
        url: message.url,
        tabId: sender.tab?.id,
      },
    });

    // Update the extension badge to indicate a scannable profile
    chrome.action.setBadgeText({
      text: "!",
      tabId: sender.tab?.id,
    });
    chrome.action.setBadgeBackgroundColor({
      color: "#00d4ff",
      tabId: sender.tab?.id,
    });
  }
});

// Clear badge when navigating away
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "loading") {
    chrome.action.setBadgeText({ text: "", tabId });
  }
});
