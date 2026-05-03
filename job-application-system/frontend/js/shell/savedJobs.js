(function () {
  window.savedIds = window.savedIds || new Set();

  function updateSavedChip(count) {
    const chip = document.getElementById("savedCountChip");
    if (chip) chip.textContent = count;
    const chipWrap = document.getElementById("savedJobsChip");
    if (chipWrap) chipWrap.style.display = count > 0 ? "flex" : "none";
  }

  async function loadSavedIds() {
    if (!getUser()) return;
    try {
      const ids = await api("/saved-jobs/ids");
      window.savedIds = new Set(ids);
      updateSavedChip(ids.length);
    } catch (_) {}
  }

  async function toggleBookmark(jobId) {
    if (!getUser()) {
      window.location.href = "login.html";
      return;
    }
    const isSaved = window.savedIds.has(jobId);
    try {
      if (isSaved) {
        await api(`/saved-jobs/${jobId}`, "DELETE");
        window.savedIds.delete(jobId);
        document.querySelectorAll(`[data-jid="${jobId}"]`).forEach((b) => {
          b.style.color = "";
          b.style.borderColor = "";
        });
        if (typeof window.showToast === "function") window.showToast("Bookmark removed");
      } else {
        await api(`/saved-jobs/${jobId}`, "POST");
        window.savedIds.add(jobId);
        document.querySelectorAll(`[data-jid="${jobId}"]`).forEach((b) => {
          b.style.color = "var(--gold)";
          b.style.borderColor = "rgba(255,204,68,0.45)";
        });
        if (typeof window.showToast === "function") window.showToast("✓ Job saved! View in Dashboard → Saved Jobs");
      }
      updateSavedChip(window.savedIds.size);
    } catch (e) {
      if (typeof window.showToast === "function") window.showToast(e.message, "error");
    }
  }

  async function loadSavedJobsTab() {
    const container = document.getElementById("savedJobsList");
    if (!container) return;
    container.innerHTML = '<div class="empty-msg">Loading...</div>';
    try {
      const items = await api("/saved-jobs/");
      const badge = document.getElementById("savedJobsBadge");
      if (badge) badge.textContent = items.length;
      if (!items.length) {
        container.innerHTML = '<div class="empty-msg">No saved jobs yet. <a href="jobs.html" style="color:var(--accent);">Browse and bookmark jobs →</a></div>';
        return;
      }
      container.innerHTML = items.map((item) => {
        const j = item.jobs || {};
        const closed = j.status && j.status !== "open";
        return `<div class="job-item${closed ? " closed" : ""}" style="padding:14px 18px;">
          <div style="flex:1;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">
              ${j.image_url ? `<img src="${j.image_url}" style="width:36px;height:36px;object-fit:cover;border-radius:6px;flex-shrink:0;" onerror="this.style.display='none'"/>` : ""}
              <span class="job-item-title">${j.title || "—"}</span>
              <span class="pill pill-${j.status || "open"}">${j.status || "open"}</span>
            </div>
            <div class="job-item-meta">
              <span>${j.company || "—"}</span><span>📍 ${j.location || ""}</span>
              ${j.salary ? `<span style="color:var(--ink);font-weight:600;font-family:var(--mono);">${j.salary}</span>` : ""}
            </div>
          </div>
          <div style="display:flex;gap:6px;">
            <a href="jobs.html" class="btn btn-ghost btn-sm" style="color:var(--accent3);">View</a>
            <button class="btn btn-ghost btn-sm" style="color:var(--red);border-color:rgba(192,57,43,0.3);" onclick="unsaveJob(${item.job_id},this)">Remove</button>
          </div>
        </div>`;
      }).join("");
    } catch (e) {
      container.innerHTML = `<div class="empty-msg" style="color:var(--red);">Error: ${e.message}</div>`;
    }
  }

  async function unsaveJob(jobId, btn) {
    try {
      await api(`/saved-jobs/${jobId}`, "DELETE");
      const row = btn && btn.closest(".job-item");
      if (row) row.remove();
      const list = document.getElementById("savedJobsList");
      const remaining = list ? list.querySelectorAll(".job-item").length : 0;
      const badge = document.getElementById("savedJobsBadge");
      if (badge) badge.textContent = remaining;
      if (!remaining && list) {
        list.innerHTML = '<div class="empty-msg">No saved jobs. <a href="jobs.html" style="color:var(--accent);">Browse jobs →</a></div>';
      }
    } catch (e) {
      alert(e.message);
    }
  }

  window.loadSavedIds = loadSavedIds;
  window.toggleBookmark = toggleBookmark;
  window.loadSavedJobsTab = loadSavedJobsTab;
  window.unsaveJob = unsaveJob;

  window.JobTrackShell = window.JobTrackShell || {};
  window.JobTrackShell.savedJobs = {
    loadSavedIds,
    toggleBookmark,
    loadSavedJobsTab,
    unsaveJob,
  };
})();
