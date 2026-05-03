(function () {
  window.JobTrackShell = window.JobTrackShell || {};
  const stateRegistry = window.JobTrackShell._state || (window.JobTrackShell._state = {});
  const ICON = { status_change: "📋", new_message: "💬", application: "📩", system: "📢" };

  function formatAgo(iso) {
    const ago = Math.floor((Date.now() - new Date(iso)) / 60000);
    if (ago < 60) return `${ago}m ago`;
    if (ago < 1440) return `${Math.floor(ago / 60)}h ago`;
    return `${Math.floor(ago / 1440)}d ago`;
  }

  function renderListHtml(items, readHandlerName) {
    if (!items.length) {
      return '<div style="padding:24px;text-align:center;color:var(--ink-muted);font-size:12px;font-family:var(--mono);">No notifications yet.</div>';
    }
    return items.map((n) => {
      const bg = n.is_read ? "transparent" : "rgba(30,168,60,0.04)";
      const safeLink = (n.link || "").replace(/"/g, "&quot;");
      return `<div onclick="${readHandlerName}(${n.id},this.dataset.link)" data-link="${safeLink}" style="padding:12px 16px;border-bottom:1px solid var(--border);cursor:pointer;background:${bg};display:flex;gap:10px;align-items:flex-start;" onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background='${bg}'">
        <span style="font-size:16px;flex-shrink:0;">${ICON[n.type] || "🔔"}</span>
        <div style="flex:1;min-width:0;">
          <div style="font-size:13px;font-weight:${n.is_read ? 400 : 600};color:var(--ink);margin-bottom:2px;">${n.title}</div>
          ${n.body ? `<div style="font-size:11px;color:var(--ink-muted);line-height:1.5;">${n.body}</div>` : ""}
          <div style="font-size:10px;color:var(--ink-muted);font-family:var(--mono);margin-top:3px;">${formatAgo(n.created_at)}</div>
        </div>
        ${!n.is_read ? '<div style="width:7px;height:7px;border-radius:50%;background:var(--accent);flex-shrink:0;margin-top:4px;"></div>' : ""}
      </div>`;
    }).join("");
  }

  function attachOutsideClose(containerId, stateRef, panelId) {
    document.addEventListener("click", function (e) {
      const wrap = document.getElementById(containerId);
      const panel = document.getElementById(panelId);
      if (wrap && panel && !wrap.contains(e.target) && stateRef.open) {
        panel.style.display = "none";
        stateRef.open = false;
      }
    });
  }

  function initJobsNotifications() {
    if (stateRegistry.jobsNotificationsInited) return;
    stateRegistry.jobsNotificationsInited = true;
    const state = { open: false };

    window.loadNotifCount = async function () {
      if (!getUser()) return;
      try {
        const data = await api("/notifications/unread-count");
        const badge = document.getElementById("notifBadge");
        const bell = document.getElementById("notifBellWrap");
        if (bell) bell.style.display = "block";
        if (badge) {
          if (data.count > 0) {
            badge.textContent = data.count > 9 ? "9+" : data.count;
            badge.style.display = "inline-block";
          } else {
            badge.style.display = "none";
          }
        }
      } catch (_) {}
    };

    window.loadNotifList = async function () {
      const list = document.getElementById("notifList");
      if (!list) return;
      try {
        const notifs = await api("/notifications?limit=20");
        list.innerHTML = renderListHtml(notifs, "readAndGo");
      } catch (e) {
        list.innerHTML = `<div style="padding:16px;color:var(--red);font-size:12px;">${e.message}</div>`;
      }
    };

    window.toggleNotifPanel = async function () {
      const panel = document.getElementById("notifPanel");
      if (!panel) return;
      state.open = !state.open;
      panel.style.display = state.open ? "block" : "none";
      if (state.open) await window.loadNotifList();
    };

    window.readAndGo = async function (notifId, link) {
      try {
        await api(`/notifications/${notifId}/read`, "PATCH");
      } catch (_) {}
      state.open = false;
      const panel = document.getElementById("notifPanel");
      if (panel) panel.style.display = "none";
      if (link && !window.location.href.includes(link.replace(/^\//, ""))) {
        window.location.href = link;
      }
    };

    window.markAllNotifRead = async function () {
      try {
        await api("/notifications/read-all", "PATCH");
        const badge = document.getElementById("notifBadge");
        if (badge) badge.style.display = "none";
        await window.loadNotifList();
      } catch (_) {}
    };

    attachOutsideClose("notifBellWrap", state, "notifPanel");
  }

  function initDashboardNotifications() {
    if (stateRegistry.dashboardNotificationsInited) return;
    stateRegistry.dashboardNotificationsInited = true;
    const state = { open: false };

    window.loadDashNotifCount = async function () {
      try {
        const data = await api("/notifications/unread-count");
        const badge = document.getElementById("dashNotifBadge");
        if (!badge) return;
        if (data.count > 0) {
          badge.textContent = data.count > 9 ? "9+" : data.count;
          badge.style.display = "inline-block";
        } else {
          badge.style.display = "none";
        }
      } catch (_) {}
    };

    window.loadDashNotifList = async function () {
      const list = document.getElementById("dashNotifList");
      if (!list) return;
      try {
        const notifs = await api("/notifications?limit=20");
        list.innerHTML = renderListHtml(notifs, "dashReadAndGo");
      } catch (e) {
        list.innerHTML = `<div style="padding:16px;color:var(--red);font-size:12px;">${e.message}</div>`;
      }
    };

    window.toggleDashNotif = async function () {
      const panel = document.getElementById("dashNotifPanel");
      if (!panel) return;
      state.open = !state.open;
      panel.style.display = state.open ? "block" : "none";
      if (state.open) await window.loadDashNotifList();
    };

    window.dashReadAndGo = async function (id, link) {
      try {
        await api(`/notifications/${id}/read`, "PATCH");
      } catch (_) {}
      state.open = false;
      const panel = document.getElementById("dashNotifPanel");
      if (panel) panel.style.display = "none";
      await window.loadDashNotifList();
      if (link && !window.location.href.includes(link.replace(/^\//, ""))) {
        window.location.href = link;
      }
    };

    window.dashMarkAllRead = async function () {
      try {
        await api("/notifications/read-all", "PATCH");
        const badge = document.getElementById("dashNotifBadge");
        if (badge) badge.style.display = "none";
        await window.loadDashNotifList();
      } catch (_) {}
    };

    attachOutsideClose("dashNotifBell", state, "dashNotifPanel");
  }

  window.JobTrackShell.notifications = {
    initJobsNotifications,
    initDashboardNotifications,
  };
})();
