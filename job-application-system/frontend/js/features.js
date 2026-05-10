/* ══════════════════════════════════════
   FEATURES JS — JobTrack
   Theme Toggle, Profile Completeness,
   Activity Log, Reactions, WebSocket
══════════════════════════════════════ */

// Ensure API_BASE is available (set by main.js, fallback here)
const _FEAT_API = (typeof API_BASE !== 'undefined') ? API_BASE : ((window.JT_CONFIG && window.JT_CONFIG.API_BASE) || "http://localhost:8000");
const _FEAT_FRONTEND = (window.JT_CONFIG && window.JT_CONFIG.FRONTEND_BASE) || "";

/* ── Share My Profile ── */
function shareMyProfile() {
  const user = getUser();
  if (!user) return;
  const base = _FEAT_FRONTEND || window.location.origin;
  const url = `${base}/pages/profile.html?id=${user.id}`;
  navigator.clipboard.writeText(url).then(() => {
    if (typeof showActionPopup === 'function') {
      showActionPopup({ title: "Copied!", message: "Your public profile link has been copied.", type: "success", duration: 1500 });
    } else {
      alert("Profile link copied: " + url);
    }
  }).catch(() => {
    prompt("Copy your profile link:", url);
  });
}

/* ── 1. DARK / LIGHT THEME TOGGLE ── */
(function initTheme() {
  const saved = localStorage.getItem("jt_theme") || "light";
  if (saved === "dark") document.documentElement.setAttribute("data-theme", "dark");
})();

function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  html.setAttribute("data-theme", next);
  localStorage.setItem("jt_theme", next);
  // Update toggle buttons
  document.querySelectorAll(".theme-toggle").forEach(btn => {
    btn.classList.toggle("dark", next === "dark");
  });
}

function renderThemeToggle(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  el.innerHTML = `
    <div class="theme-toggle ${isDark ? 'dark' : ''}" onclick="toggleTheme()" title="Toggle dark/light mode">
      <span class="theme-icon theme-icon-sun">☀️</span>
      <span class="theme-icon theme-icon-moon">🌙</span>
    </div>`;
}

/* ── 2. PROFILE COMPLETENESS INDICATOR ── */
async function loadProfileCompleteness(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const user = getUser();
  if (!user) return;
  try {
    const data = await api(`/profile/${user.id}/completeness`);
    const pct = data.percentage || 0;
    const barClass = pct < 40 ? "low" : pct < 70 ? "mid" : "";
    const missing = data.missing || [];
    container.innerHTML = `
      <div class="profile-completeness">
        <div class="pc-header">
          <span class="pc-title">Profile Completeness</span>
          <span class="pc-pct">${pct}%</span>
        </div>
        <div class="pc-bar">
          <div class="pc-bar-fill ${barClass}" style="width: ${pct}%"></div>
        </div>
        ${missing.length > 0 ? `
          <div class="pc-missing">
            ${missing.map(m => `<span class="pc-missing-tag">+ ${m}</span>`).join("")}
          </div>
        ` : `<div style="font-size:11px;color:var(--green);font-weight:500;">✓ Profile complete!</div>`}
      </div>`;
  } catch (e) {
    container.innerHTML = "";
  }
}

/* ── 3. ACTIVITY LOG ── */
async function loadActivityLog(containerId) {
  const container = document.getElementById(containerId);
  if (!container) { console.warn("[ActivityLog] Container not found:", containerId); return; }
  container.innerHTML = '<div class="empty-msg">Loading...</div>';
  try {
    // Use a timeout wrapper to prevent hanging forever
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

    const token = localStorage.getItem("token");
    const headers = { "Content-Type": "application/json" };
    if (token && token !== "null" && token !== "undefined") {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(`${_FEAT_API}/activity-log/?limit=30`, {
      method: "GET",
      headers,
      credentials: "include",
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const errText = await res.text().catch(() => "Unknown error");
      console.warn("[ActivityLog] API error:", res.status, errText);
      container.innerHTML = `<div class="empty-msg">Activity log is not available yet.</div>`;
      return;
    }

    let logs;
    try {
      logs = await res.json();
    } catch (parseErr) {
      console.warn("[ActivityLog] JSON parse error:", parseErr);
      container.innerHTML = `<div class="empty-msg">Activity log is not available yet.</div>`;
      return;
    }

    if (!Array.isArray(logs) || !logs.length) {
      container.innerHTML = `<div class="empty-msg">No activity recorded yet.</div>`;
      return;
    }
    const iconMap = {
      login: "🔐", logout: "👋", profile_update: "✏️",
      application_submit: "📄", password_reset: "🔑",
    };
    container.innerHTML = `<div class="activity-log">${logs.map(l => {
      const icon = iconMap[l.action] || "📌";
      const iconClass = l.action === "login" ? "login" : l.action.includes("profile") ? "profile" : "application";
      const time = l.created_at ? timeAgo(l.created_at) : "";
      const actionLabel = {
        login: "Signed in",
        logout: "Signed out",
        profile_update: "Updated profile",
        application_submit: "Submitted application",
        password_reset: "Reset password",
      }[l.action] || l.action;
      return `<div class="activity-item">
        <div class="activity-icon ${iconClass}">${icon}</div>
        <div class="activity-info">
          <div class="activity-action">${actionLabel}</div>
          <div class="activity-details">${l.details || ""}${l.ip_address ? ` · IP: ${l.ip_address}` : ""}</div>
        </div>
        <div class="activity-time">${time}</div>
      </div>`;
    }).join("")}</div>`;
  } catch (e) {
    // AbortError = timeout, TypeError = network error, etc.
    const msg = e.name === "AbortError" ? "Request timed out." : "Activity log is not available yet.";
    container.innerHTML = `<div class="empty-msg">${msg}</div>`;
    console.warn("[ActivityLog]", e.name, e.message);
  }
}

async function clearActivityLog(containerId) {
  if (!confirm("Clear all activity history?")) return;
  try {
    await api("/activity-log/clear/", "DELETE");
    loadActivityLog(containerId);
  } catch (e) { alert("Error: " + e.message); }
}

function timeAgo(dateStr) {
  const d = new Date(dateStr.replace("Z", "+00:00"));
  const now = new Date();
  const s = Math.floor((now - d) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  if (s < 604800) return `${Math.floor(s / 86400)}d ago`;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

/* ── 4. MESSAGE REACTIONS ── */
const REACTION_EMOJIS = ["👍", "❤️", "😂", "🎉", "😢", "🔥", "👏", "💯", "✅", "👀"];
let _reactionsCache = {};

async function loadReactionsForMessages(messageIds) {
  if (!messageIds.length) return;
  try {
    const data = await api(`/reactions/messages/batch?message_ids=${messageIds.join(",")}`);
    _reactionsCache = { ..._reactionsCache, ...data };
    messageIds.forEach(id => renderReactions(id));
  } catch (e) { /* silent */ }
}

function renderReactions(messageId) {
  const container = document.getElementById(`reactions-${messageId}`);
  if (!container) return;
  const reactions = _reactionsCache[messageId] || [];
  const user = getUser();
  const uid = user ? user.id : 0;

  // Group by emoji
  const groups = {};
  reactions.forEach(r => {
    if (!groups[r.emoji]) groups[r.emoji] = { count: 0, mine: false, users: [] };
    groups[r.emoji].count++;
    groups[r.emoji].users.push(r.users?.name || "User");
    if (r.user_id === uid) groups[r.emoji].mine = true;
  });

  let html = "";
  Object.entries(groups).forEach(([emoji, data]) => {
    html += `<span class="msg-reaction ${data.mine ? 'mine' : ''}"
      onclick="toggleReaction(${messageId},'${emoji}')"
      title="${data.users.join(', ')}">${emoji} <span class="msg-reaction-count">${data.count}</span></span>`;
  });
  html += `<span class="msg-reaction-add" onclick="showEmojiPicker(event,${messageId})" title="Add reaction"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="14" height="14"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg></span>`;
  container.innerHTML = html;
}

async function toggleReaction(messageId, emoji) {
  try {
    await api(`/reactions/message/${messageId}`, "POST", { emoji });
    // Refresh reactions for this message
    const data = await api(`/reactions/message/${messageId}`);
    _reactionsCache[messageId] = data;
    renderReactions(messageId);
    // Broadcast via WebSocket if connected
    if (_ws && _ws.readyState === WebSocket.OPEN) {
      _ws.send(JSON.stringify({ type: "reaction", message_id: messageId, emoji }));
    }
  } catch (e) { /* silent */ }
}

function showEmojiPicker(event, messageId) {
  event.stopPropagation();
  // Remove existing pickers
  document.querySelectorAll(".emoji-picker-popup").forEach(p => p.remove());
  const picker = document.createElement("div");
  picker.className = "emoji-picker-popup show";
  picker.innerHTML = REACTION_EMOJIS.map(e =>
    `<span class="emoji-pick" onclick="event.stopPropagation();toggleReaction(${messageId},'${e}');this.closest('.emoji-picker-popup').remove()">${e}</span>`
  ).join("");
  const parent = event.target.closest(".msg-reactions") || event.target.parentElement;
  parent.style.position = "relative";
  parent.appendChild(picker);
  // Close on outside click
  setTimeout(() => {
    document.addEventListener("click", function _close() {
      picker.remove();
      document.removeEventListener("click", _close);
    }, { once: true });
  }, 10);
}

/* ── 5. WEBSOCKET REAL-TIME CHAT ── */
let _ws = null;
let _wsAppId = null;
let _typingTimeout = null;

function connectWebSocket(applicationId) {
  const token = localStorage.getItem("token");
  if (!token) return;
  // Close existing connection
  if (_ws) { try { _ws.close(); } catch (e) { } }
  _wsAppId = applicationId;

  const wsBase = (API_BASE || "http://localhost:8000").replace("http", "ws");
  const wsUrl = `${wsBase}/ws/chat/${applicationId}?token=${token}`;

  try {
    _ws = new WebSocket(wsUrl);
  } catch (e) {
    console.log("[WS] WebSocket not available, using polling");
    return;
  }

  _ws.onopen = () => {
    console.log("[WS] Connected to chat", applicationId);
    // Show online indicator
    const dot = document.getElementById("chatOnlineDot");
    if (dot) dot.classList.add("show");
    // Mark messages as read
    _ws.send(JSON.stringify({ type: "read" }));
  };

  _ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "new_message") {
      appendWsMessage(data.message);
    } else if (data.type === "typing") {
      showTypingIndicator();
    } else if (data.type === "read_receipt") {
      // Could update read receipts UI
    } else if (data.type === "presence") {
      const dot = document.getElementById("chatOnlineDot");
      if (dot) dot.classList.toggle("show", data.status === "online");
    } else if (data.type === "reaction") {
      // Refresh reactions for that message
      if (_reactionsCache[data.message_id] !== undefined) {
        api(`/reactions/message/${data.message_id}`).then(r => {
          _reactionsCache[data.message_id] = r;
          renderReactions(data.message_id);
        });
      }
    }
  };

  _ws.onclose = () => {
    console.log("[WS] Disconnected");
    const dot = document.getElementById("chatOnlineDot");
    if (dot) dot.classList.remove("show");
    _ws = null;
  };

  _ws.onerror = () => { _ws = null; };
}

function disconnectWebSocket() {
  if (_ws) { try { _ws.close(); } catch (e) { } _ws = null; }
  _wsAppId = null;
}

function sendWsTyping() {
  if (_ws && _ws.readyState === WebSocket.OPEN) {
    _ws.send(JSON.stringify({ type: "typing" }));
  }
}

function showTypingIndicator() {
  const el = document.getElementById("chatTypingIndicator");
  if (el) {
    el.classList.add("show");
    clearTimeout(_typingTimeout);
    _typingTimeout = setTimeout(() => el.classList.remove("show"), 2500);
  }
}

function appendWsMessage(msg) {
  const container = document.getElementById("chatMessages");
  if (!container) return;
  const user = getUser();
  const isMine = msg.sender_id === user?.id;
  // Check for empty state
  const empty = container.querySelector(".chat-empty");
  if (empty) empty.remove();

  const sender = msg.users || {};
  const senderName = sender.name || "User";
  const senderPic = sender.profile_pic || "";
  const avatar = senderPic
    ? `<img src="${senderPic}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" onerror="this.parentElement.textContent='${senderName[0]}'"/>`
    : senderName[0].toUpperCase();

  const div = document.createElement("div");
  div.className = `chat-msg ${isMine ? "mine" : ""}`;
  div.innerHTML = `
    ${!isMine ? `<div class="chat-msg-avatar">${avatar}</div>` : ""}
    <div class="chat-msg-content">
      ${!isMine ? `<div class="chat-msg-name">${senderName}</div>` : ""}
      ${msg.image_url ? `<img src="${msg.image_url}" class="chat-msg-img" onclick="document.getElementById('chatLightboxImg').src=this.src;document.getElementById('chatLightbox').classList.add('open')"/>` : ""}
      ${msg.body ? `<div class="chat-msg-text">${msg.body}</div>` : ""}
      <div class="chat-msg-time">${msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "now"}</div>
      <div class="msg-reactions" id="reactions-${msg.id}"></div>
    </div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;

  // Hide typing indicator
  const ti = document.getElementById("chatTypingIndicator");
  if (ti) ti.classList.remove("show");
}

/* ── 6. ATTACHMENT HELPERS ── */
async function loadAttachments(applicationId, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  try {
    const attachments = await api(`/attachments/application/${applicationId}`);
    if (!attachments.length) { container.innerHTML = ""; return; }
    container.innerHTML = `<div style="margin-top:8px;"><div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;color:var(--ink-muted);margin-bottom:6px;">Attachments</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">${attachments.map(a => {
      const icon = a.file_type?.includes("pdf") ? "📄" : a.file_type?.includes("image") ? "🖼️" : "📎";
      return `<a href="${a.file_url}" target="_blank" class="attachment-chip">
          <span class="att-icon">${icon}</span>
          <span>${a.label || a.file_name || "File"}</span>
        </a>`;
    }).join("")}</div></div>`;
  } catch (e) { container.innerHTML = ""; }
}

/* ── INIT ON LOAD ── */
document.addEventListener("DOMContentLoaded", () => {
  // Sync theme toggle state
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  document.querySelectorAll(".theme-toggle").forEach(btn => {
    btn.classList.toggle("dark", isDark);
  });
});