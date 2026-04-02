export const PLATFORMS = {
  instagram: {
    name: "Instagram",
    icon: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="ig-grad" x1="0.5" y1="1" x2="0.5" y2="0">
          <stop offset="0%" stop-color="#FFDD55"/>
          <stop offset="25%" stop-color="#FF543E"/>
          <stop offset="50%" stop-color="#C837AB"/>
          <stop offset="100%" stop-color="#515BD4"/>
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="20" height="20" rx="5" stroke="url(#ig-grad)" stroke-width="2"/>
      <circle cx="12" cy="12" r="4.5" stroke="url(#ig-grad)" stroke-width="2"/>
      <circle cx="17.5" cy="6.5" r="1.5" fill="url(#ig-grad)"/>
    </svg>`,
    color: "#E1306C",
    description: "Detect fake profiles and bot accounts on Instagram",
    fields: [
      { key: "profile_pic", label: "Profile Picture Present?", type: "select", options: [{ value: 1, label: "Yes" }, { value: 0, label: "No" }] },
      { key: "username_has_numbers", label: "Username Has Many Numbers?", type: "select", options: [{ value: 1, label: "Yes" }, { value: 0, label: "No" }] },
      { key: "bio_present", label: "Bio Present?", type: "select", options: [{ value: 1, label: "Yes" }, { value: 0, label: "No" }] },
      { key: "posts", label: "Number of Posts", type: "number", placeholder: "e.g. 42" },
      { key: "followers", label: "Followers", type: "number", placeholder: "e.g. 1500" },
      { key: "following", label: "Following", type: "number", placeholder: "e.g. 800" },
    ],
  },

  twitter: {
    name: "Twitter",
    icon: `<svg viewBox="0 0 24 24" fill="#1DA1F2" xmlns="http://www.w3.org/2000/svg">
      <path d="M22.46 6c-.77.35-1.6.58-2.46.69a4.28 4.28 0 0 0 1.88-2.37 8.59 8.59 0 0 1-2.72 1.04 4.28 4.28 0 0 0-7.32 3.91A12.16 12.16 0 0 1 3.11 4.7a4.28 4.28 0 0 0 1.33 5.71c-.7-.02-1.37-.21-1.95-.53v.05a4.28 4.28 0 0 0 3.43 4.19c-.36.1-.74.15-1.13.15-.28 0-.54-.03-.8-.07a4.29 4.29 0 0 0 4 2.98A8.6 8.6 0 0 1 2 19.54a12.13 12.13 0 0 0 6.56 1.92c7.88 0 12.2-6.53 12.2-12.2 0-.19 0-.37-.01-.56A8.72 8.72 0 0 0 22.96 6h-.5z"/>
    </svg>`,
    color: "#1DA1F2",
    description: "Identify bot accounts and automated behavior on Twitter",
    fields: [
      { key: "statuses_count", label: "Number of Tweets", type: "number", placeholder: "e.g. 3200" },
      { key: "followers_count", label: "Followers", type: "number", placeholder: "e.g. 500" },
      { key: "friends_count", label: "Friends", type: "number", placeholder: "e.g. 300" },
      { key: "favourites_count", label: "Favourites", type: "number", placeholder: "e.g. 1200" },
      { key: "listed_count", label: "Listed Count", type: "number", placeholder: "e.g. 10" },
      { key: "verified", label: "Verified Account?", type: "select", options: [{ value: 1, label: "Yes" }, { value: 0, label: "No" }] },
      { key: "default_profile_image", label: "Default Profile Image?", type: "select", options: [{ value: 1, label: "Yes" }, { value: 0, label: "No" }] },
    ],
  },

  reddit: {
    name: "Reddit",
    icon: `<svg viewBox="0 0 24 24" fill="#FF4500" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.74c.69 0 1.25.56 1.25 1.25a1.25 1.25 0 0 1-1.25 1.25c-.49 0-.91-.28-1.11-.69-.84.52-1.89.86-3.04.95l1.07-3.37 2.61.56-.02.11a1.26 1.26 0 0 1 .49-.06zM8.44 7.12l2.21-.47L11.6 9.6c-1.27-.06-2.44-.44-3.37-1.03a1.24 1.24 0 0 0-.59-1.14 1.25 1.25 0 0 0 .8-.31zm-3.7 3.02a1.55 1.55 0 0 1 2.75-.97c.97-.73 2.28-1.2 3.74-1.29l1.26-3.96a.41.41 0 0 1 .49-.28l3.04.65a1.55 1.55 0 0 1 1.23-.62c.86 0 1.55.7 1.55 1.55 0 .86-.7 1.55-1.55 1.55-.86 0-1.55-.7-1.55-1.55v-.08l-2.72-.58-1.12 3.53c1.4.12 2.66.59 3.6 1.3a1.55 1.55 0 0 1 2.21.52 1.55 1.55 0 0 1-.52 2.13c.03.17.04.34.04.52 0 2.67-3.11 4.84-6.95 4.84-3.83 0-6.94-2.17-6.94-4.84 0-.18.01-.36.04-.53a1.55 1.55 0 0 1-.61-2.6zM9 13.61c0 .6.49 1.09 1.09 1.09.6 0 1.09-.49 1.09-1.09 0-.6-.49-1.09-1.09-1.09-.6 0-1.09.49-1.09 1.09zm5.93 2.74c-.73.73-1.87.92-2.93.92-1.06 0-2.2-.19-2.93-.92a.36.36 0 0 1 .51-.51c.53.53 1.42.72 2.42.72s1.89-.19 2.42-.72a.36.36 0 0 1 .51.51zm-.22-1.65c-.6 0-1.09-.49-1.09-1.09 0-.6.49-1.09 1.09-1.09.6 0 1.09.49 1.09 1.09 0 .6-.49 1.09-1.09 1.09z"/>
    </svg>`,
    color: "#FF4500",
    description: "Detect AI bots and fake engagement on Reddit",
    fields: [
      { key: "account_age_days", label: "Account Age (Days)", type: "number", placeholder: "e.g. 365" },
      { key: "user_karma", label: "User Karma", type: "number", placeholder: "e.g. 5000" },
      { key: "sentiment_score", label: "Sentiment Score", type: "float", placeholder: "e.g. 0.15" },
      { key: "avg_word_length", label: "Avg Word Length", type: "float", placeholder: "e.g. 5.2" },
      { key: "contains_links", label: "Contains Links?", type: "select", options: [{ value: 1, label: "Yes" }, { value: 0, label: "No" }] },
    ],
  },

  facebook: {
    name: "Facebook",
    icon: `<svg viewBox="0 0 24 24" fill="#1877F2" xmlns="http://www.w3.org/2000/svg">
      <path d="M24 12c0-6.627-5.373-12-12-12S0 5.373 0 12c0 5.99 4.388 10.954 10.125 11.854V15.47H7.078V12h3.047V9.356c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.926-1.956 1.875V12h3.328l-.532 3.469H13.875v8.385C19.612 22.954 24 17.99 24 12z"/>
    </svg>`,
    color: "#1877F2",
    description: "Identify spam accounts and fake profiles on Facebook",
    fields: [
      { key: "friends", label: "Number of Friends", type: "number", placeholder: "e.g. 500" },
      { key: "following", label: "Following", type: "number", placeholder: "e.g. 200" },
      { key: "community", label: "Communities Joined", type: "number", placeholder: "e.g. 10" },
      { key: "age", label: "Account Age (Years)", type: "float", placeholder: "e.g. 3.5" },
      { key: "postshared", label: "Posts Shared", type: "number", placeholder: "e.g. 100" },
      { key: "urlshared", label: "URLs Shared", type: "number", placeholder: "e.g. 20" },
      { key: "photos_videos", label: "Photos/Videos", type: "number", placeholder: "e.g. 30" },
      { key: "fpurls", label: "Fraction Profile URLs", type: "float", placeholder: "e.g. 0.2" },
      { key: "fpphotos_videos", label: "Fraction Photos/Videos", type: "float", placeholder: "e.g. 0.5" },
      { key: "avgcomment_per_post", label: "Avg Comments/Post", type: "float", placeholder: "e.g. 2.5" },
      { key: "likes_per_post", label: "Likes/Post", type: "float", placeholder: "e.g. 10.0" },
      { key: "tags_per_post", label: "Tags/Post", type: "float", placeholder: "e.g. 1.5" },
      { key: "num_tags_per_post", label: "# Tags/Post", type: "float", placeholder: "e.g. 3.0" },
    ],
  },
};
