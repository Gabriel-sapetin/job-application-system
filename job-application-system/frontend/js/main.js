// API_BASE is set by config.js — do not hardcode here
const API_BASE = (window.JT_CONFIG && window.JT_CONFIG.API_BASE) || "http://localhost:8000";

// Ensure auth cookies are sent cross-origin for API requests.
const _nativeFetch = window.fetch.bind(window);
window.fetch = (input, init = {}) => _nativeFetch(input, { credentials: "include", ...init });

async function api(endpoint, method = "GET", body = null) {
  const headers = { "Content-Type": "application/json" };
  const token = localStorage.getItem("token");
  if (token && token !== "null" && token !== "undefined") {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const options = { method, headers, credentials: "include" };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(`${API_BASE}${endpoint}`, options);
  const data = await res.json();
  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    }
    let msg = "Something went wrong";
    if (data.detail) {
      if (typeof data.detail === "string") msg = data.detail;
      else if (Array.isArray(data.detail)) msg = data.detail.map(e => e.msg || JSON.stringify(e)).join(", ");
      else msg = JSON.stringify(data.detail);
    }
    throw new Error(msg);
  }
  return data;
}

function getUser() {
  try { return JSON.parse(localStorage.getItem("user")); } catch { return null; }
}
function logout() {
  const target = ((window.JT_CONFIG && window.JT_CONFIG.FRONTEND_BASE) || "") + "/index.html";
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  showActionPopup({
    title: "Signed out",
    message: "You have been logged out successfully.",
    type: "success",
    duration: 900,
    redirectUrl: target,
  });
}

function showAlert(id, message, type = "success") {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `<span class="alert-icon">${type === "success" ? "✓" : "✕"}</span><span>${message}</span>`;
  el.className = `alert ${type}`;
}

function showActionPopup({ title = "Done", message = "", type = "success", duration = 1400, redirectUrl = null } = {}) {
  let overlay = document.getElementById("actionPopupOverlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "actionPopupOverlay";
    overlay.className = "action-popup-overlay";
    overlay.innerHTML = `<div class="action-popup-box">
      <div class="action-popup-icon" id="actionPopupIcon">✓</div>
      <h4 id="actionPopupTitle"></h4>
      <p id="actionPopupMsg"></p>
      <div class="action-popup-bar"><div id="actionPopupBarFill"></div></div>
    </div>`;
    document.body.appendChild(overlay);
  }
  const iconMap = { success: "✓", error: "✕", info: "i", warning: "!" };
  const iconEl = document.getElementById("actionPopupIcon");
  iconEl.textContent = iconMap[type] || "✓";
  iconEl.className = `action-popup-icon ${type}`;
  document.getElementById("actionPopupTitle").textContent = title;
  document.getElementById("actionPopupMsg").textContent = message;
  overlay.classList.add("open");
  const bar = document.getElementById("actionPopupBarFill");
  if (bar) {
    bar.style.transition = "none";
    bar.style.width = "0%";
    requestAnimationFrame(() => {
      bar.style.transition = `width ${Math.max(duration, 300)}ms linear`;
      bar.style.width = "100%";
    });
  }
  clearTimeout(overlay._timer);
  const close = () => {
    overlay.classList.remove("open");
    if (redirectUrl) window.location.href = redirectUrl;
  };
  overlay._timer = setTimeout(close, duration);
}

function showConfirm(title, message) {
  return new Promise(resolve => {
    let overlay = document.getElementById("confirmOverlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "confirmOverlay";
      overlay.className = "confirm-overlay";
      overlay.innerHTML = `<div class="confirm-box">
        <h4 id="confirmTitle"></h4><p id="confirmMsg"></p>
        <div class="confirm-actions">
          <button class="btn btn-ghost btn-sm" id="confirmCancel">Cancel</button>
          <button class="btn btn-danger btn-sm" id="confirmOk">Confirm</button>
        </div></div>`;
      document.body.appendChild(overlay);
    }
    document.getElementById("confirmTitle").textContent = title;
    document.getElementById("confirmMsg").textContent = message;
    overlay.classList.add("open");
    const cleanup = (r) => {
      overlay.classList.remove("open");
      document.getElementById("confirmOk").replaceWith(document.getElementById("confirmOk").cloneNode(true));
      document.getElementById("confirmCancel").replaceWith(document.getElementById("confirmCancel").cloneNode(true));
      resolve(r);
    };
    document.getElementById("confirmOk").addEventListener("click", () => cleanup(true));
    document.getElementById("confirmCancel").addEventListener("click", () => cleanup(false));
  });
}

/* ══════════════════════════════════
   MOBILE SIDEBAR — hamburger drawer
══════════════════════════════════ */
function initMobileSidebar() {
  const sidebar   = document.querySelector(".sidebar");
  const hamburger = document.getElementById("hamburgerBtn");
  const overlay   = document.getElementById("sidebarOverlay");
  if (!sidebar || !hamburger) return;

  function openSidebar() {
    sidebar.classList.add("open");
    hamburger.classList.add("open");
    if (overlay) overlay.classList.add("open");
    document.body.style.overflow = "hidden";
  }
  function closeSidebar() {
    sidebar.classList.remove("open");
    hamburger.classList.remove("open");
    if (overlay) overlay.classList.remove("open");
    document.body.style.overflow = "";
  }

  hamburger.addEventListener("click", () => {
    sidebar.classList.contains("open") ? closeSidebar() : openSidebar();
  });
  if (overlay) overlay.addEventListener("click", closeSidebar);

  sidebar.querySelectorAll("a, button.sidebar-link").forEach(el => {
    el.addEventListener("click", () => {
      if (window.innerWidth <= 900) closeSidebar();
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.body.style.opacity = "0";
  document.body.style.transition = "opacity 0.3s";
  requestAnimationFrame(() => document.body.style.opacity = "1");
  initMobileSidebar();
});