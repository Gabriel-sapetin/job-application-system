/**
 * JobTrack — Frontend Configuration
 * ─────────────────────────────────
 * ONE place to change before deploying.
 *
 * HOW TO USE:
 *   Add <script src="../js/config.js"></script> BEFORE main.js in every HTML file.
 *   (index.html uses  <script src="js/config.js"></script>  — no leading ../)
 *
 * FOR PRODUCTION:
 *   Change API_BASE to your deployed backend URL, e.g.:
 *     window.JT_CONFIG.API_BASE = "https://api.yoursite.com";
 *   Change FRONTEND_BASE to your deployed frontend URL, e.g.:
 *     window.JT_CONFIG.FRONTEND_BASE = "https://yoursite.com";
 */

(function () {
  // ── Detect environment automatically ──────────────────
  const host = window.location.hostname;
  const isDev = host === "localhost" || host === "127.0.0.1";

  window.JT_CONFIG = {
    // Backend API base URL — no trailing slash
    API_BASE: isDev
      ? "http://localhost:8000"
      : (window.JT_API_BASE || "https://api.yoursite.com"),   // override in prod

    // Frontend base URL — no trailing slash
    FRONTEND_BASE: isDev
      ? ("http://" + window.location.host + "/job-application-system/frontend")
      : (window.JT_FRONTEND_BASE || "https://yoursite.com"),

    // App name shown in emails / notifications
    APP_NAME: "JobTrack",
  };
})();