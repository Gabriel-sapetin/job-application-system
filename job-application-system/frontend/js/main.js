const API_BASE = "http://localhost:8000";

async function api(endpoint, method = "GET", body = null) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(`${API_BASE}${endpoint}`, options);
  const data = await res.json();
  if (!res.ok) {
    // FastAPI validation errors return {detail: [...array...]}
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
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "/job-application-system/frontend/index.html";
}

function showAlert(id, message, type = "success") {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `<span class="alert-icon">${type === "success" ? "✓" : "✕"}</span><span>${message}</span>`;
  el.className = `alert ${type}`;
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

document.addEventListener("DOMContentLoaded", () => {
  document.body.style.opacity = "0";
  document.body.style.transition = "opacity 0.3s";
  requestAnimationFrame(() => document.body.style.opacity = "1");
});
