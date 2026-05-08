const user = getUser();
if (!user) window.location.href = "login.html";

const CATEGORIES = [
  {id:"arts",label:"Arts & Media",icon:"🎬"},{id:"business",label:"Business",icon:"💼"},
  {id:"cleaning",label:"Cleaning",icon:"🧹"},{id:"construction",label:"Construction",icon:"🏗️"},
  {id:"customer",label:"Customer Svc",icon:"🎧"},{id:"design",label:"Design",icon:"🎨"},
  {id:"education",label:"Education",icon:"📚"},{id:"engineering",label:"Engineering",icon:"⚙️"},
  {id:"finance",label:"Finance",icon:"💰"},{id:"government",label:"Government",icon:"🏛️"},
  {id:"healthcare",label:"Healthcare",icon:"🏥"},{id:"hospitality",label:"Hospitality",icon:"🏨"},
  {id:"marketing",label:"Marketing",icon:"📣"},{id:"software",label:"Software & IT",icon:"💻"},
  {id:"teaching",label:"Teaching",icon:"🏫"},
  // Individual / Personal Hire
  {id:"freelance",label:"Freelance / Project",icon:"💡",individual:true},
  {id:"errand",label:"Errands & Delivery",icon:"🛵",individual:true},
  {id:"homeservice",label:"Home Services",icon:"🏠",individual:true},
  {id:"repair",label:"Repair & Maintenance",icon:"🔧",individual:true},
  {id:"caregiving",label:"Caregiving / Domestic",icon:"🤝",individual:true},
  {id:"event",label:"Events & Assistance",icon:"🎉",individual:true},
];
const catMap  = Object.fromEntries(CATEGORIES.map(c=>[c.id,`${c.icon} ${c.label}`]));
const typeMap = {"Full-Time":"full-time","Part-Time":"part-time","Internship":"internship","Remote":"remote"};
const LOGO_IG = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>`;
const LOGO_FB = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>`;
const LOGO_TG = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M21.8 2.15L2.05 9.84c-1.3.52-1.29 1.25-.24 1.57l5.1 1.59 11.83-7.47c.56-.34 1.07-.16.65.21L8.1 16.17l-.39 5.27c.57 0 .82-.26 1.14-.57l2.73-2.65 5.68 4.19c1.05.58 1.8.28 2.06-.97l3.73-17.57c.38-1.52-.58-2.21-1.25-1.72z"/></svg>`;
const LOGO_PHONE = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.38 2 2 0 0 1 3.6 1.22h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.86a16 16 0 0 0 6 6l.95-.95a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21.78 16z"/></svg>`;
const LOGO_WEB = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>`;

document.getElementById("sidebarRoleLabel").textContent = `/ ${user.role}`;
document.getElementById("topbarTitle").textContent = user.role==="employer"?"Employer Dashboard":"Dashboard";

// Welcome greeting
const _hour = new Date().getHours();
const _greet = _hour < 12 ? "Good morning" : _hour < 17 ? "Good afternoon" : "Good evening";
const _firstName = user.name.split(" ")[0];
const _welcomeEl = document.getElementById("welcomeGreeting");
if (_welcomeEl) _welcomeEl.textContent = `${_greet}, ${_firstName}`;
const _dateEl = document.getElementById("welcomeDate");
if (_dateEl) _dateEl.textContent = new Date().toLocaleDateString("en-US", { weekday:"long", month:"long", day:"numeric", year:"numeric" });

const _cachedPic = user.profile_pic && user.profile_pic.startsWith("http") ? user.profile_pic : null;
document.getElementById("sidebarUser").innerHTML = `
  <div class="sidebar-avatar" id="sidebarAvatar">${_cachedPic ? `<img src="${_cachedPic}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="this.parentElement.textContent='${user.name[0].toUpperCase()}'"/>` : user.name[0].toUpperCase()}</div>
  <div class="sidebar-user-info">
    <div class="sidebar-user-name">${user.name}</div>
    <div class="sidebar-user-role">${user.email}</div>
  </div>`;

if (user.role==="employer") {
  document.getElementById("employerView").style.display="block";
  document.getElementById("empSideNav").style.display="block";
  document.getElementById("tabEmpApps").classList.add("active");
} else {
  document.getElementById("applicantView").style.display="block";
  document.getElementById("appSideNav").style.display="block";
  document.getElementById("tabProfile").classList.add("active");
  const grid=document.getElementById("interestGrid");
  let addedIndivHeader = false;
  // Sequential alphabet: A-O corporate, P-U individual — simple index guarantees correct mapping
  CATEGORIES.forEach((c, idx)=>{
    if (c.individual && !addedIndivHeader) {
      const sep = document.createElement("div");
      sep.style.cssText = "grid-column:1/-1;display:flex;align-items:center;gap:10px;margin-top:6px;margin-bottom:2px;";
      sep.innerHTML = '<span style="flex:1;height:1px;background:var(--border);"></span><span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#a78bfa;white-space:nowrap;">👤 Individual / Personal Hire</span><span style="flex:1;height:1px;background:var(--border);"></span>';
      grid.appendChild(sep);
      addedIndivHeader = true;
    }
    const chip=document.createElement("div");
    chip.className="int-chip" + (c.individual?" individual-chip":"");
    if (c.individual) chip.style.cssText = "border-color:rgba(167,139,250,0.25);";
    chip.innerHTML=`<span class="int-chip-letter">${String.fromCharCode(65+idx)}</span><span class="int-chip-label">${c.label}</span>`;
    chip.onclick=()=>searchByInterest(c.id,c.label,c.icon,chip);
    grid.appendChild(chip);
  });
}

/* ── TAB SWITCHES ── */
function showAppTab(id, btn) {
  document.querySelectorAll("#applicantView .tab-panel").forEach(t=>t.classList.remove("active"));
  document.querySelectorAll(".app-tab-btn").forEach(b=>b.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  btn.classList.add("active");
}
function showEmpTab(id, btn) {
  document.querySelectorAll("#employerView .tab-panel").forEach(t=>t.classList.remove("active"));
  document.querySelectorAll(".emp-tab-btn").forEach(b=>b.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  if(btn) btn.classList.add("active");
}

/* ── LOAD ── */
async function loadDashboard() {
  if (user.role==="employer") {
    await loadEmployerData();
  } else {
    await Promise.all([loadProfile(), loadApplicantApps()]);
  }
}

/* ── APPLICANT PROFILE ── */
async function loadProfile() {
  try {
    const p=await api(`/users/${user.id}`);
    renderProfileCard(p); renderProfileStrip(p);
    document.getElementById("picUrlInput").value      = p.profile_pic||"";
    document.getElementById("aboutInput").value       = p.about_me||"";
    document.getElementById("igInput").value          = p.instagram||"";
    document.getElementById("fbInput").value          = p.facebook||"";
    document.getElementById("defaultResumeInput").value = p.default_resume||"";
    document.getElementById("defaultCoverInput").value  = p.default_cover||"";
    if (p.profile_pic) {
      document.getElementById("sidebarAvatar").innerHTML=`<img src="${p.profile_pic}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="this.parentElement.textContent='${user.name[0].toUpperCase()}'"/>`;
      const u=getUser(); u.profile_pic=p.profile_pic; localStorage.setItem("user",JSON.stringify(u));
    }
  } catch(e){ renderProfileCard(user); renderProfileStrip(user); }
}
function renderProfileStrip(p) {
  const av=document.getElementById("stripAvatar");
  av.innerHTML=p.profile_pic?`<img src="${p.profile_pic}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;" onerror="this.parentElement.textContent='${(p.name||user.name)[0].toUpperCase()}'"/>`:((p.name||user.name)[0].toUpperCase());
  document.getElementById("stripName").textContent=p.name||user.name;
  document.getElementById("stripBio").textContent=p.about_me?p.about_me.substring(0,80)+(p.about_me.length>80?"…":""):"No bio yet.";
  const social=document.getElementById("stripSocial"); social.innerHTML="";
  if(p.instagram) social.innerHTML+=`<a href="https://instagram.com/${p.instagram}" target="_blank" style="display:inline-flex;align-items:center;gap:5px;">${LOGO_IG} @${p.instagram}</a>`;
  if(p.facebook)  social.innerHTML+=`<a href="https://facebook.com/${p.facebook}" target="_blank" style="display:inline-flex;align-items:center;gap:5px;">${LOGO_FB} ${p.facebook}</a>`;
}
function renderProfileCard(p) {
  const av=document.getElementById("profileAvatarDisplay");
  av.innerHTML=p.profile_pic?`<img src="${p.profile_pic}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" onerror="this.parentElement.textContent='${(p.name||user.name)[0].toUpperCase()}'"/>`:((p.name||user.name)[0].toUpperCase());
  document.getElementById("profileName").textContent=p.name||user.name;
  const ab=document.getElementById("profileAboutDisplay");
  ab.textContent=p.about_me||"No bio yet."; ab.style.fontStyle=p.about_me?"normal":"italic";
  const social=document.getElementById("profileSocialDisplay");
  if(p.instagram||p.facebook){ social.innerHTML="";
    if(p.instagram) social.innerHTML+=`<div class="ppc-social-row" style="display:flex;align-items:center;gap:8px;">${LOGO_IG} @${p.instagram}</div>`;
    if(p.facebook)  social.innerHTML+=`<div class="ppc-social-row" style="display:flex;align-items:center;gap:8px;">${LOGO_FB} ${p.facebook}</div>`;
  } else { social.innerHTML=`<div style="font-size:12px;color:var(--ink-muted);text-align:center;">No social links yet.</div>`; }
}
async function handlePicFile(input) {
  const file = input.files[0];
  if (!file) return;
  if (file.size > 2 * 1024 * 1024) {
    showAlert("profileAlert", "Image too large. Max 2MB.", "error"); return;
  }
  // Preview immediately
  const reader = new FileReader();
  reader.onload = e => {
    const av = document.getElementById("profileAvatarDisplay");
    av.innerHTML = `<img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;"/>`;
  };
  reader.readAsDataURL(file);

  // Upload to Supabase Storage via backend
  try {
    showAlert("profileAlert", "Uploading photo...", "success");
    const formData = new FormData();
    formData.append("file", file);
    const token = localStorage.getItem("token");
    const res   = await fetch(((window.JT_CONFIG&&window.JT_CONFIG.API_BASE)||"http://localhost:8000")+"/upload/profile-pic", {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` },
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");

    // Save CDN URL permanently to DB so it persists across refreshes
    await api(`/users/${user.id}`, "PATCH", { profile_pic: data.url });

    // Update localStorage cache
    const u = getUser(); u.profile_pic = data.url;
    localStorage.setItem("user", JSON.stringify(u));

    showAlert("profileAlert", "Profile picture saved! ✓", "success");
    await loadProfile();
  } catch(e) { showAlert("profileAlert", e.message, "error"); }
}

async function saveProfile() {
  try {
    const picUrl = document.getElementById("picUrlInput").value.trim() || null;
    await api(`/users/${user.id}`, "PATCH", {
      profile_pic:    picUrl,
      about_me:       document.getElementById("aboutInput").value.trim() || null,
      instagram:      document.getElementById("igInput").value.replace("@","").trim() || null,
      facebook:       document.getElementById("fbInput").value.trim() || null,
      default_resume: document.getElementById("defaultResumeInput").value.trim() || null,
      default_cover:  document.getElementById("defaultCoverInput").value.trim() || null,
    });
    // Keep localStorage in sync so pic doesn't vanish on refresh
    if (picUrl) {
      const u = getUser(); u.profile_pic = picUrl;
      localStorage.setItem("user", JSON.stringify(u));
    }
    showAlert("profileAlert", "Profile saved! ✓", "success");
    await loadProfile();
  } catch(e) { showAlert("profileAlert", e.message, "error"); }
}

/* ── APPLICANT APPS — paginated (#4) ── */
let _allApps = [], _appPage = 1;
const APP_PAGE_SIZE = 10;

async function loadApplicantApps(){
  try{
    const apps = await api(`/applications/me`);
    _allApps = apps;
    _appPage = 1;
    document.getElementById("statTotal").textContent    = apps.length;
    document.getElementById("statPending").textContent  = apps.filter(a=>a.status==="pending").length;
    document.getElementById("statAccepted").textContent = apps.filter(a=>a.status==="accepted").length;
    document.getElementById("statRejected").textContent = apps.filter(a=>a.status==="rejected").length;
    document.getElementById("appCountBadge").textContent = apps.length;
    renderAppPage();
  } catch(e){
    document.getElementById("appTableBody").innerHTML=`<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--red);font-family:var(--mono);font-size:12px;">Error: ${e.message}</td></tr>`;
  }
}

function appChangePage(dir) {
  const totalPages = Math.ceil(_allApps.length / APP_PAGE_SIZE);
  _appPage = Math.max(1, Math.min(_appPage + dir, totalPages));
  renderAppPage();
}

function renderAppPage() {
  const totalPages = Math.max(1, Math.ceil(_allApps.length / APP_PAGE_SIZE));
  const start = (_appPage - 1) * APP_PAGE_SIZE;
  const slice = _allApps.slice(start, start + APP_PAGE_SIZE);
  const tbody = document.getElementById("appTableBody");
  const table = tbody ? tbody.closest("table") : null;
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  if (table) table.classList.toggle("mobile-cards", isMobile);

  document.getElementById("appPageInfo").textContent =
    _allApps.length > 0 ? `Page ${_appPage} of ${totalPages} · ${_allApps.length} total` : "";
  document.getElementById("appPrevBtn").disabled = _appPage <= 1;
  document.getElementById("appNextBtn").disabled = _appPage >= totalPages;

  if (!_allApps.length) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--ink-muted);font-family:var(--mono);font-size:12px;">No applications yet. <a href="jobs.html" style="color:var(--accent);">Browse jobs →</a></td></tr>`;
    return;
  }

  if (isMobile) {
    tbody.innerHTML = slice.map(a => {
      const date = a.created_at ? a.created_at.split("T")[0] : "—";
      const appStCls = {pending:"gc-gold",accepted:"",rejected:"gc-red",reviewed:"gc-blue"}[a.status]||"";
      return `<tr data-status="${a.status}">
        <td colspan="7">
          <div class="mobile-app-card">
            <div class="mobile-app-title">${a.jobs?.title||"—"}</div>
            <div class="mobile-app-sub">${a.jobs?.company||"—"} · ${date}</div>
            <div class="mobile-app-status"><span class="g-chip ${appStCls}">${a.status}</span></div>
            <div class="mobile-app-actions">
              <button class="btn btn-ghost btn-sm" onclick="viewMyApp(${a.id})" style="color:var(--accent3);border-color:rgba(77,159,255,0.3);">View</button>
              <button class="btn btn-ghost btn-sm" style="color:var(--accent);border-color:rgba(232,149,109,0.3);"
                onclick="openChatModal(${a.id},'${(a.jobs?.company||'Employer').replace(/'/g,"\\'")}','','${(a.jobs?.title||'Position').replace(/'/g,"\\'")}')">Chat</button>
              <button class="btn btn-danger btn-sm" onclick="withdrawApp(${a.id})">Withdraw</button>
            </div>
          </div>
        </td>
      </tr>`;
    }).join("");
    return;
  }

  tbody.innerHTML = slice.map(a => {
    const date = a.created_at ? a.created_at.split("T")[0] : "—";
    const dl   = a.jobs?.deadline ? new Date(a.jobs.deadline).toLocaleDateString("en-PH",{month:"short",day:"numeric"}) : "—";
    const max  = a.jobs?.max_applicants;
    const jst  = a.jobs?.status||"open";
    const jstCls = jst==="closed"?"gc-red":jst==="full"?"gc-gold":"";
    const appStCls = {pending:"gc-gold",accepted:"",rejected:"gc-red",reviewed:"gc-blue"}[a.status]||"";
    return `<tr data-status="${a.status}">
      <td>
        <div class="td-title">${a.jobs?.title||"—"}</div>
        <span class="g-chip ${jstCls}" style="margin-top:4px;">${jst}</span>
      </td>
      <td class="td-muted">${a.jobs?.company||"—"}</td>
      <td><span class="g-chip gc-muted">${dl}</span></td>
      <td><span class="g-chip gc-muted">${max?max+" max":"Unlimited"}</span></td>
      <td><span class="g-chip gc-muted">${date}</span></td>
      <td><span class="g-chip ${appStCls}">${a.status}</span></td>
      <td style="display:flex;gap:5px;flex-wrap:wrap;">
        <button class="btn btn-ghost btn-sm" onclick="viewMyApp(${a.id})" style="color:var(--accent3);border-color:rgba(77,159,255,0.3);">View</button>
        <button class="btn btn-ghost btn-sm" style="color:var(--accent);border-color:rgba(232,149,109,0.3);"
          onclick="openChatModal(${a.id},'${(a.jobs?.company||'Employer').replace(/'/g,"\\'")}','','${(a.jobs?.title||'Position').replace(/'/g,"\\'")}')">
          Chat
        </button>
        <button class="btn btn-danger btn-sm" onclick="withdrawApp(${a.id})">Withdraw</button>
      </td>
    </tr>`;
  }).join("");
}

/* #5 — View own application detail */
function viewMyApp(appId) {
  const a = _allApps.find(x => x.id === appId);
  if (!a) return;
  document.getElementById("adJobTitle").textContent   = a.jobs?.title   || "—";
  document.getElementById("adJobCompany").textContent = a.jobs?.company  || "—";
  document.getElementById("adStatus").innerHTML       = `<span class="pill pill-${a.status}">${a.status}</span>`;
  document.getElementById("adDate").textContent       = a.created_at ? a.created_at.split("T")[0] : "—";
  document.getElementById("adName").textContent       = a.name  || "—";
  document.getElementById("adEmail").textContent      = a.email || "—";
  const cl = document.getElementById("adCoverLetter");
  cl.textContent = a.cover_letter || "No cover letter provided.";
  cl.style.fontStyle = a.cover_letter ? "normal" : "italic";
  const rw = document.getElementById("adResumeWrap");
  if (a.resume_url) {
    document.getElementById("adResumeLink").href = a.resume_url;
    rw.style.display = "block";
  } else {
    rw.style.display = "none";
  }
  document.getElementById("appDetailModal").classList.add("open");
}


/* ── INTEREST ── */
async function searchByInterest(catId,label,icon,chip){
  document.querySelectorAll(".int-chip").forEach(c=>c.classList.remove("active"));
  chip.classList.add("active");
  const panel=document.getElementById("interestResults");
  panel.classList.add("show");
  document.getElementById("interestResultTitle").textContent=`${icon} ${label} Jobs`;
  document.getElementById("interestJobList").innerHTML=`<div style="padding:24px;text-align:center;color:var(--ink-muted);font-family:var(--mono);font-size:12px;">Loading...</div>`;
  try{
    const jobs=await api(`/jobs?category=${catId}`);
    if(!jobs.length){document.getElementById("interestJobList").innerHTML=`<div style="padding:24px;text-align:center;color:var(--ink-muted);font-family:var(--mono);font-size:12px;">No jobs in this category yet.</div>`;return;}
    document.getElementById("interestJobList").innerHTML=jobs.map(j=>{
      const closed=j.status!=="open";
      return `<div class="job-item${closed?" closed":""}" style="padding:14px 18px;">
        <div style="flex:1;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">
            ${j.image_url?`<img src="${j.image_url}" style="width:36px;height:36px;object-fit:cover;border-radius:6px;flex-shrink:0;" onerror="this.style.display='none'"/>` :""}
            <span class="job-item-title">${j.title}</span>
            <span class="pill pill-${j.status}">${j.status}</span>
          </div>
          <div class="job-item-meta">
            <span>${j.company}</span><span>📍 ${j.location}</span>
            <span class="type-tag ${typeMap[j.type]||""}">${j.type}</span>
            ${j.salary?`<span>${j.salary}</span>`:""}
          </div>
        </div>
        <a href="jobs.html" class="btn btn-ghost btn-sm">${closed?"Closed":"Apply →"}</a>
      </div>`;
    }).join("");
  } catch(e){document.getElementById("interestJobList").innerHTML=`<div style="padding:24px;text-align:center;color:var(--red);font-family:var(--mono);font-size:12px;">Error: ${e.message}</div>`;}
}
function clearInterest(){
  document.querySelectorAll(".int-chip").forEach(c=>c.classList.remove("active"));
  document.getElementById("interestResults").classList.remove("show");
}

/* #6 — Real full-text search wired to API */
let _searchTimer = null;
function debounceSearch(val) {
  clearTimeout(_searchTimer);
  const clearBtn = document.getElementById("clearSearchBtn");
  if (clearBtn) clearBtn.style.display = val.trim() ? "inline-flex" : "none";
  if (!val.trim()) { clearInterest(); return; }
  _searchTimer = setTimeout(() => runJobSearch(val.trim()), 350);
}

function clearSearch() {
  const inp = document.getElementById("jobSearchInput");
  if (inp) inp.value = "";
  const clearBtn = document.getElementById("clearSearchBtn");
  if (clearBtn) clearBtn.style.display = "none";
  clearInterest();
}

async function runJobSearch(query) {
  const panel = document.getElementById("interestResults");
  panel.classList.add("show");
  document.getElementById("interestResultTitle").textContent = `Search: "${query}"`;
  document.getElementById("interestJobList").innerHTML = `<div style="padding:24px;text-align:center;color:var(--ink-muted);font-family:var(--mono);font-size:12px;">Searching...</div>`;
  try {
    const jobs = await api(`/jobs?search=${encodeURIComponent(query)}`);
    if (!jobs.length) {
      document.getElementById("interestJobList").innerHTML = `<div style="padding:24px;text-align:center;color:var(--ink-muted);font-family:var(--mono);font-size:12px;">No jobs found for "${query}".</div>`;
      return;
    }
    document.getElementById("interestJobList").innerHTML = jobs.map(j => {
      const closed = j.status !== "open";
      return `<div class="job-item${closed?" closed":""}" style="padding:14px 18px;">
        <div style="flex:1;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">
            ${j.image_url ? `<img src="${j.image_url}" style="width:36px;height:36px;object-fit:cover;border-radius:6px;flex-shrink:0;" onerror="this.style.display='none'"/>` : ""}
            <span class="job-item-title">${j.title}</span>
            <span class="pill pill-${j.status}">${j.status}</span>
          </div>
          <div class="job-item-meta">
            <span>${j.company}</span><span>📍 ${j.location}</span>
            <span class="type-tag ${typeMap[j.type]||""}">${j.type}</span>
            ${j.salary ? `<span>${j.salary}</span>` : ""}
          </div>
        </div>
        <a href="jobs.html" class="btn btn-ghost btn-sm">${closed ? "Closed" : "Apply →"}</a>
      </div>`;
    }).join("");
  } catch(e) {
    document.getElementById("interestJobList").innerHTML = `<div style="padding:24px;text-align:center;color:var(--red);font-family:var(--mono);font-size:12px;">Error: ${e.message}</div>`;
  }
}

/* ── EMPLOYER DATA ── */
async function loadEmployerData(){
  try{
    const [apps,jobs]=await Promise.all([api(`/applications/employer`),api(`/jobs?employer_id=${user.id}`)]);
    document.getElementById("empStatTotal").textContent=apps.length;
    document.getElementById("empStatPending").textContent=apps.filter(a=>a.status==="pending").length;
    document.getElementById("empStatAccepted").textContent=apps.filter(a=>a.status==="accepted").length;
    document.getElementById("empStatRejected").textContent=apps.filter(a=>a.status==="rejected").length;
    document.getElementById("empAppBadge").textContent=apps.length;
    renderEmployerApps(apps); renderMyJobs(jobs); loadEmpProfile(); populateAnalyticsSelect(jobs);
  } catch(e){document.getElementById("empAppTableBody").innerHTML=`<tr><td colspan="6" style="text-align:center;padding:24px;color:var(--red);font-family:var(--mono);font-size:12px;">Error: ${e.message}</td></tr>`;}
}

/* ── EMPLOYER PROFILE ── */
async function loadEmpProfile(){
  // Pre-fill from cache so UI doesn't flash empty while fetching
  const _cached = user.profile_pic && user.profile_pic.startsWith("http") ? user.profile_pic : null;
  const _avEl = document.getElementById("empAvatarDisplay");
  if (_cached) {
    _avEl.innerHTML = `<img src="${_cached}" style="width:100%;height:100%;object-fit:cover;border-radius:13px;" onerror="this.parentElement.textContent='${user.name[0].toUpperCase()}'"/>`;
  } else {
    _avEl.textContent = user.name[0].toUpperCase();
  }
  document.getElementById("empProfileName").textContent = user.name;
  try{
    const p=await api(`/users/${user.id}`);
    // Avatar — only show http URLs (skip data:image/svg from Pan-Pan)
    const av=document.getElementById("empAvatarDisplay");
    const _picOk = p.profile_pic && p.profile_pic.startsWith("http");
    if(_picOk) av.innerHTML=`<img src="${p.profile_pic}" style="width:100%;height:100%;object-fit:cover;border-radius:13px;" onerror="this.parentElement.textContent='${user.name[0].toUpperCase()}'"/>`;
    else av.textContent=user.name[0].toUpperCase();
    // Banner — only show http URLs
    const _bannerOk = p.banner_url && p.banner_url.startsWith("http");
    if(_bannerOk){
      const bImg=document.getElementById("empBannerImg");
      bImg.src=p.banner_url; bImg.style.display="block";
    }
    document.getElementById("empProfileName").textContent=p.name||user.name;
    document.getElementById("empProfileBio").textContent=p.about_me||"No company description yet.";
    renderVerifiedBadge(p.is_verified||false);
    // Contact tags
    const contact=document.getElementById("empProfileContact"); contact.innerHTML="";
    if(p.instagram) contact.innerHTML+=`<a href="https://instagram.com/${p.instagram}" target="_blank" class="emp-contact-tag" style="display:inline-flex;align-items:center;gap:6px;background:linear-gradient(135deg,rgba(131,58,180,0.15),rgba(253,29,29,0.15));border-color:rgba(253,29,29,0.3);">${LOGO_IG} @${p.instagram}</a>`;
    if(p.facebook)  contact.innerHTML+=`<a href="https://facebook.com/${p.facebook}" target="_blank" class="emp-contact-tag" style="display:inline-flex;align-items:center;gap:6px;background:rgba(24,119,242,0.12);border-color:rgba(24,119,242,0.35);">${LOGO_FB} ${p.facebook}</a>`;
    // Telegram stored in phone field as "num | tg:@handle"
    const _ph = p.phone||""; const _tgM = _ph.match(/\| tg:@(\S+)/);
    const _phoneDisplay = _tgM ? _ph.split(" | tg:")[0].trim() : _ph;
    const _tgHandle = _tgM ? _tgM[1] : null;
    if(_phoneDisplay) contact.innerHTML+=`<span class="emp-contact-tag" style="display:inline-flex;align-items:center;gap:6px;">${LOGO_PHONE} ${_phoneDisplay}</span>`;
    if(_tgHandle)     contact.innerHTML+=`<a href="https://t.me/${_tgHandle}" target="_blank" class="emp-contact-tag" style="display:inline-flex;align-items:center;gap:6px;background:rgba(34,158,217,0.12);border-color:rgba(34,158,217,0.35);">${LOGO_TG} @${_tgHandle}</a>`;
    if(p.website)     contact.innerHTML+=`<a href="${p.website}" target="_blank" class="emp-contact-tag" style="display:inline-flex;align-items:center;gap:6px;background:rgba(77,159,255,0.1);border-color:rgba(77,159,255,0.3);">${LOGO_WEB} Website</a>`;
    // Fill edit form — skip data: URIs (too large / invalid for URL fields)
    const _isHttpUrl = v => v && v.startsWith("http");
    document.getElementById("empPicUrl").value    = _isHttpUrl(p.profile_pic) ? p.profile_pic : "";
    document.getElementById("empBannerUrl").value = _isHttpUrl(p.banner_url)  ? p.banner_url  : "";
    document.getElementById("empAbout").value     = p.about_me||"";
    document.getElementById("empIg").value        = p.instagram||"";
    document.getElementById("empFb").value        = p.facebook||"";
    // Parse telegram out of phone field if stored as "phone | tg:@handle"
    const _phoneRaw = p.phone||"";
    const _tgMatch  = _phoneRaw.match(/\| tg:@(\S+)/);
    document.getElementById("empPhone").value    = _tgMatch ? _phoneRaw.split(" | tg:")[0].trim() : _phoneRaw;
    document.getElementById("empTelegram").value = _tgMatch ? _tgMatch[1] : "";
    document.getElementById("empWebsite").value  = p.website||"";
    // Sidebar avatar
    if(p.profile_pic && p.profile_pic.startsWith("http")) {
      document.getElementById("sidebarAvatar").innerHTML=`<img src="${p.profile_pic}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;"/>`;
      // Keep localStorage in sync so profile persists when navigating away and back
      const _u = getUser(); _u.profile_pic = p.profile_pic; localStorage.setItem("user", JSON.stringify(_u));
    }
  } catch(e){ document.getElementById("empProfileName").textContent=user.name; }
}
async function handleEmpPicFile(input){
  const file=input.files[0]; if(!file) return;
  if(file.size>2*1024*1024){showAlert("empProfileAlert","Image too large. Max 2MB.","error");return;}
  const reader=new FileReader();
  reader.onload=e=>{document.getElementById("empAvatarDisplay").innerHTML=`<img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:13px;"/>`;};
  reader.readAsDataURL(file);
  try{
    showAlert("empProfileAlert","Uploading...","success");
    const fd=new FormData();fd.append("file",file);
    const res=await fetch(((window.JT_CONFIG&&window.JT_CONFIG.API_BASE)||"http://localhost:8000")+"/upload/profile-pic",{method:"POST",headers:{"Authorization":`Bearer ${localStorage.getItem("token")}`},body:fd});
    const data=await res.json();
    if(!res.ok)throw new Error(data.detail||"Upload failed");
    await api(`/users/${user.id}`,"PATCH",{profile_pic:data.url});
    document.getElementById("empPicUrl").value=data.url;
    const u=getUser();u.profile_pic=data.url;localStorage.setItem("user",JSON.stringify(u));
    showAlert("empProfileAlert","Picture saved! ✓","success");
    await loadEmpProfile();
  }catch(e){showAlert("empProfileAlert",e.message,"error");}
}
async function handleBannerFile(input){
  const file=input.files[0]; if(!file) return;
  if(file.size>2*1024*1024){showAlert("empProfileAlert","Image too large. Max 2MB.","error");return;}
  const reader=new FileReader();
  reader.onload=e=>{const b=document.getElementById("empBannerImg");b.src=e.target.result;b.style.display="block";};
  reader.readAsDataURL(file);
  try{
    showAlert("empProfileAlert","Uploading banner...","success");
    const fd=new FormData();fd.append("file",file);
    const res=await fetch(((window.JT_CONFIG&&window.JT_CONFIG.API_BASE)||"http://localhost:8000")+"/upload/job-image",{method:"POST",headers:{"Authorization":`Bearer ${localStorage.getItem("token")}`},body:fd});
    const data=await res.json();
    if(!res.ok)throw new Error(data.detail||"Upload failed");
    await api(`/users/${user.id}`,"PATCH",{banner_url:data.url});
    document.getElementById("empBannerUrl").value=data.url;
    showAlert("empProfileAlert","Banner saved! ✓","success");
  }catch(e){showAlert("empProfileAlert",e.message,"error");}
}
function previewEmpPic(){
  const url=document.getElementById("empPicUrl").value;
  const av=document.getElementById("empAvatarDisplay");
  av.innerHTML=url?`<img src="${url}" style="width:100%;height:100%;object-fit:cover;border-radius:13px;"/>`:user.name[0].toUpperCase();
}
function previewEmpBanner(){
  const url=document.getElementById("empBannerUrl").value;
  const bImg=document.getElementById("empBannerImg");
  if(url){ bImg.src=url; bImg.style.display="block"; }
  else { bImg.style.display="none"; }
}
async function saveEmpProfile(){
  try{
    const _toHttpUrl = v => { const s=v.trim(); return (s && s.startsWith("http")) ? s : null; };
    await api(`/users/${user.id}`,"PATCH",{
      profile_pic: _toHttpUrl(document.getElementById("empPicUrl").value),
      banner_url:  _toHttpUrl(document.getElementById("empBannerUrl").value),
      about_me:    document.getElementById("empAbout").value||null,
      instagram:   document.getElementById("empIg").value.replace("@","")||null,
      facebook:    document.getElementById("empFb").value||null,
      phone:       (document.getElementById("empPhone").value||"") + (document.getElementById("empTelegram").value ? " | tg:@"+document.getElementById("empTelegram").value.replace("@","") : "")||null,
      website:     document.getElementById("empWebsite").value||null,
    });
    showAlert("empProfileAlert","Profile saved!","success"); loadEmpProfile();
  } catch(e){showAlert("empProfileAlert",e.message,"error");}
}

/* ── ID VERIFICATION ── */
let _idFileToUpload = null;

function handleIdFileSelect(input) {
  const file = input.files[0];
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) { showAlert("idUploadAlert","File too large. Max 5MB.","error"); return; }
  _idFileToUpload = file;
  const placeholder = document.getElementById("idUploadPlaceholder");
  const preview = document.getElementById("idPreviewImg");
  if (file.type.startsWith("image/")) {
    const reader = new FileReader();
    reader.onload = e => { preview.src = e.target.result; preview.style.display = "block"; placeholder.style.display = "none"; };
    reader.readAsDataURL(file);
  } else {
    placeholder.innerHTML = `<div style="font-size:20px;">📄</div><div style="font-size:12px;color:var(--ink-soft);">${file.name}</div>`;
  }
}

async function submitIdVerification() {
  const idType = document.getElementById("idType").value;
  if (!idType) { showAlert("idUploadAlert","Please select an ID type.","error"); return; }
  if (!_idFileToUpload) { showAlert("idUploadAlert","Please upload your ID photo.","error"); return; }
  showAlert("idUploadAlert","Uploading ID...","success");
  try {
    const fd = new FormData();
    fd.append("file", _idFileToUpload);
    fd.append("id_type", idType);
    const token = localStorage.getItem("token");
    const res = await fetch(((window.JT_CONFIG&&window.JT_CONFIG.API_BASE)||"http://localhost:8000")+"/upload/verification-id", {
      method:"POST", headers:{"Authorization":`Bearer ${token}`}, body:fd
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail||"Upload failed");
    showAlert("idUploadAlert","✓ ID submitted for review! Admin will verify your account shortly.","success");
    _idFileToUpload = null;
    document.getElementById("idFileInput").value = "";
    document.getElementById("idType").value = "";
    document.getElementById("idPreviewImg").style.display = "none";
    document.getElementById("idUploadPlaceholder").innerHTML = '<div style="font-size:20px;margin-bottom:4px;">🪪</div><div style="font-size:12px;color:var(--ink-muted);">Click to upload ID</div><div style="font-size:10px;color:var(--ink-muted);margin-top:2px;">JPG, PNG, or PDF · Max 5MB</div>';
    document.getElementById("idVerifStatus").innerHTML = '<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;background:rgba(160,104,0,0.08);border:1px solid rgba(160,104,0,0.25);border-radius:var(--radius);font-size:12px;color:var(--gold);">⏳ Verification pending admin review</div>';
  } catch(e) { showAlert("idUploadAlert",e.message,"error"); }
}

/* ── EMPLOYER APPS TABLE ── */
// Store apps by ID so onclick handlers reference by ID, not inline JSON
const _appStore = {};

function renderEmployerApps(apps){
  const tbody=document.getElementById("empAppTableBody");
  const table = tbody ? tbody.closest("table") : null;
  const isMobile = window.matchMedia("(max-width: 768px)").matches;
  if (table) table.classList.toggle("mobile-cards", isMobile);
  if(!apps.length){tbody.innerHTML=`<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--ink-muted);font-family:var(--mono);font-size:12px;">No applications received yet.</td></tr>`;return;}
  // Populate store
  apps.forEach(a => { _appStore[a.id] = a; });
  if (isMobile) {
    tbody.innerHTML = apps.map(a=>{
      const date=a.created_at?a.created_at.split("T")[0]:"—";
      const hasProfile=(a.users?.about_me||a.users?.instagram||a.users?.facebook||a.users?.profile_pic);
      return `<tr data-status="${a.status}">
        <td colspan="6">
          <div class="mobile-app-card">
            <div class="mobile-app-title" style="${hasProfile?"cursor:pointer;color:var(--accent3);":""}" onclick="${hasProfile?`viewApplicantProfile(${a.id})`:""}">${a.name||"Applicant"}</div>
            <div class="mobile-app-sub">${a.jobs?.title||"—"} · ${date}</div>
            <div class="mobile-app-status"><span class="g-chip ${{pending:"gc-gold",accepted:"",rejected:"gc-red",reviewed:"gc-blue"}[a.status]||""}">${a.status}</span></div>
            <div class="mobile-app-actions">
              <button class="btn btn-success btn-sm" onclick="updateStatus(${a.id},'accepted',this)">Accept</button>
              <button class="btn btn-danger btn-sm"  onclick="updateStatus(${a.id},'rejected',this)">Reject</button>
              <button class="btn btn-ghost btn-sm"   onclick="updateStatus(${a.id},'reviewed',this)">Review</button>
              <button class="btn btn-ghost btn-sm" style="color:var(--accent);border-color:rgba(232,149,109,0.3);"
                onclick="openChatModal(${a.id},'${(a.name||'Applicant').replace(/'/g,"\\'")}','${(a.users?.profile_pic||'')}','${(a.jobs?.title||'Position').replace(/'/g,"\\'")}')">Chat</button>
              <button class="btn btn-ghost btn-sm" style="color:var(--red);border-color:rgba(255,68,68,0.3);"
                onclick="openReportUserModal(${a.users?.id||a.user_id},'${(a.name||'').replace(/'/g,"\\'")}','${a.email||''}','${a.users?.profile_pic||''}')">Report</button>
            </div>
          </div>
        </td>
      </tr>`;
    }).join("");
    return;
  }
  tbody.innerHTML=apps.map(a=>{
    const date=a.created_at?a.created_at.split("T")[0]:"—";
    const profile=a.users||{};
    const hasProfile=profile.about_me||profile.instagram||profile.facebook||profile.profile_pic;
    const hasCover=!!a.cover_letter;
    return `<tr data-status="${a.status}">
      <td>
        <div style="display:flex;align-items:center;gap:9px;">
          <div style="width:28px;height:28px;border-radius:50%;background:var(--surface3);display:grid;place-items:center;font-size:11px;font-weight:700;overflow:hidden;flex-shrink:0;cursor:${hasProfile?"pointer":"default"};" onclick="${hasProfile?`viewApplicantProfile(${a.id})`:""}">${profile.profile_pic?`<img src="${profile.profile_pic}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;"/>`:((a.name||"?")[0].toUpperCase())}</div>
          <div>
            <div class="td-title" style="${hasProfile?"cursor:pointer;color:var(--accent3);":""}" onclick="${hasProfile?`viewApplicantProfile(${a.id})`:""}">${a.name}</div>
            <div class="td-mono">${a.email}</div>
          </div>
        </div>
      </td>
      <td><span class="g-chip gc-muted">${a.jobs?.title||"—"}</span></td>
      <td><span class="g-chip gc-muted">${date}</span></td>
      <td>${hasCover
        ?`<button class="btn btn-ghost btn-sm" style="color:var(--gold);border-color:rgba(255,204,68,0.3);" onclick="openCoverModal(${a.id})">Read ↗</button>`
        :`<span class="td-muted" style="font-size:12px;">—</span>`
      }</td>
      <td><span class="g-chip ${{pending:"gc-gold",accepted:"",rejected:"gc-red",reviewed:"gc-blue"}[a.status]||""}">${a.status}</span></td>
      <td style="display:flex;gap:5px;flex-wrap:wrap;">
        <button class="btn btn-success btn-sm" onclick="updateStatus(${a.id},'accepted',this)">Accept</button>
        <button class="btn btn-danger btn-sm"  onclick="updateStatus(${a.id},'rejected',this)">Reject</button>
        <button class="btn btn-ghost btn-sm"   onclick="updateStatus(${a.id},'reviewed',this)">Review</button>
        <button class="btn btn-ghost btn-sm" style="color:var(--accent);border-color:rgba(232,149,109,0.3);"
          onclick="openChatModal(${a.id},'${(a.name||'Applicant').replace(/'/g,"\\'")}','${(a.users?.profile_pic||'')}','${(a.jobs?.title||'Position').replace(/'/g,"\\'")}')">
          Chat
        </button>
        <button class="btn btn-ghost btn-sm" style="color:var(--red);border-color:rgba(255,68,68,0.3);"
        onclick="openReportUserModal(${a.users?.id||a.user_id},'${(a.name||'').replace(/'/g,"\\'")}','${a.email||''}','${a.users?.profile_pic||''}')">
        Report
      </button>

      </td>
    </tr>`;
  }).join("");
}

let currentCoverAppId = null;
function openCoverModal(appId){
  const a = _appStore[appId];
  if (!a) return;
  currentCoverAppId = a.id;
  const profile = a.users || {};
  const av = document.getElementById("cmaAvatar");
  av.innerHTML = profile.profile_pic
    ? `<img src="${profile.profile_pic}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;"/>`
    : (a.name||"?")[0].toUpperCase();
  document.getElementById("cmaName").textContent  = a.name  || "—";
  document.getElementById("cmaEmail").textContent = a.email || "—";
  document.getElementById("cmaJob").textContent   = a.jobs?.title || "Position";
  document.getElementById("coverText").textContent = a.cover_letter || "No cover letter provided.";
  const rl = document.getElementById("coverResumeLink");
  const rh = document.getElementById("coverResumeHint");
  if (a.resume_url) {
    rl.href = a.resume_url; rl.style.display = "inline-flex";
    rh.style.display = "block";
  } else {
    rl.style.display = "none"; rh.style.display = "none";
  }
  // #3 Load existing notes
  document.getElementById("coverNotesInput").value = a.employer_notes || "";
  const sb = document.getElementById("notesSavedBadge");
  sb.classList.remove("show");
  const statusColors = {pending:"var(--gold)",reviewed:"var(--accent3)",accepted:"var(--green)",rejected:"var(--red)"};
  const csb = document.getElementById("coverStatusBadge");
  csb.innerHTML = `<span style="width:6px;height:6px;border-radius:50%;background:${statusColors[a.status]||"var(--ink-muted)"};display:inline-block;margin-right:4px;"></span>${a.status}`;
  csb.style.color = statusColors[a.status] || "var(--ink-muted)";
  document.getElementById("coverAcceptBtn").onclick = () => { updateStatus(a.id,"accepted",null); closeCoverModal(); };
  document.getElementById("coverRejectBtn").onclick = () => { updateStatus(a.id,"rejected",null); closeCoverModal(); };
  document.getElementById("coverModal").classList.add("open");
}
function closeCoverModal(){ document.getElementById("coverModal").classList.remove("open"); }
(function () {
  var cm = document.getElementById("coverModal");
  if (cm) cm.addEventListener("click", function (e) {
    if (e.target === cm) closeCoverModal();
  });
})();

/* #3 Save employer notes */
async function saveNotes() {
  if (!currentCoverAppId) return;
  const notes = document.getElementById("coverNotesInput").value.trim() || null;
  try {
    await api(`/applications/${currentCoverAppId}/notes`, "PATCH", { notes });
    // Update local store so re-opening modal shows saved value
    if (_appStore[currentCoverAppId]) _appStore[currentCoverAppId].employer_notes = notes;
    const badge = document.getElementById("notesSavedBadge");
    badge.classList.add("show");
    setTimeout(() => badge.classList.remove("show"), 2500);
  } catch(e) { alert("Failed to save notes: " + e.message); }
}

/* ── APPLICANT PROFILE MODAL ── */
function viewApplicantProfile(appId){
  const a = _appStore[appId];
  if (!a) return;
  const p = {...(a.users||{}), name: a.name, email: a.email};
  const _rid = a.users?.id || a.user_id || 0;
  const _rn  = (p.name||'').replace(/'/g,"\\'");
  const _re  = (p.email||'');
  const _rp  = (p.profile_pic||'');
  document.getElementById("profileModalBody").innerHTML=`
    <div class="ap-modal-header">
      <div class="ap-modal-avatar">${p.profile_pic?`<img src="${p.profile_pic}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;"/>`:((p.name||"?")[0].toUpperCase())}</div>
      <div><h3 style="font-size:16px;font-weight:600;margin-bottom:2px;">${p.name||"—"}</h3><p style="font-size:12px;color:var(--ink-muted);">${p.email||""}</p></div>
    </div>
    <div class="ap-about-box">${p.about_me||`<span style="color:var(--ink-muted);font-style:italic;">No bio provided.</span>`}</div>
    <div class="ap-social-links">
      ${p.instagram?`<a href="https://instagram.com/${p.instagram}" target="_blank" style="display:inline-flex;align-items:center;gap:5px;">${LOGO_IG} @${p.instagram}</a>`:""}
      ${p.facebook?`<a href="https://facebook.com/${p.facebook}" target="_blank" style="display:inline-flex;align-items:center;gap:5px;">${LOGO_FB} ${p.facebook}</a>`:""}
      ${!p.instagram&&!p.facebook?`<span style="color:var(--ink-muted);font-size:12px;">No social links.</span>`:""}
    </div>
    <div style="margin-top:14px;border-top:1px solid var(--border);padding-top:12px;">
      <button class="btn btn-ghost btn-sm" style="color:var(--red);border-color:rgba(255,68,68,0.3);"
        onclick="document.getElementById('profileModal').classList.remove('open');openReportUserModal(${_rid},'${_rn}','${_re}','${_rp}')">
        Report this User
      </button>
    </div>`;
  document.getElementById("profileModal").classList.add("open");
}




/* ── MY JOBS TABLE (#7 edit button) ── */
let _myJobs = [];
function renderMyJobs(jobs){
  _myJobs = jobs;
  const tbody=document.getElementById("myJobsTableBody");
  if(!jobs.length){tbody.innerHTML=`<tr><td colspan="8" style="text-align:center;padding:40px;color:var(--ink-muted);font-family:var(--mono);font-size:12px;">No jobs posted yet.</td></tr>`;return;}
  tbody.innerHTML=jobs.map(j=>{
    const dl=j.deadline?new Date(j.deadline).toLocaleDateString("en-PH",{month:"short",day:"numeric"}):"—";
    const imgCell=j.image_url
      ?`<img src="${j.image_url}" style="width:48px;height:32px;object-fit:cover;border-radius:4px;border:1px solid var(--border);" onerror="this.style.display='none'"/>`
      :`<span style="font-size:11px;color:var(--ink-muted);">—</span>`;
    return `<tr data-status="${j.status||'open'}">
      <td><div class="td-title">${j.title}</div><div class="td-muted">${j.company} · 📍 ${j.location}</div></td>
      <td>${imgCell}</td>
      <td><span class="g-chip gc-muted">${catMap[j.category]||"—"}</span></td>
      <td><span class="g-chip gc-muted">${j.type}</span></td>
      <td><span class="g-chip gc-muted">${j.max_applicants?j.max_applicants+" slots":"Unlimited"}</span></td>
      <td><span class="g-chip gc-muted">${dl}</span></td>
      <td><span class="g-chip ${{open:"",closed:"gc-red",full:"gc-gold"}[j.status||"open"]||""}">${j.status||"open"}</span></td>
      <td style="display:flex;gap:5px;flex-wrap:wrap;">
        <button class="btn btn-ghost btn-sm" onclick="openEditJobModal(${j.id})" style="color:var(--accent3);border-color:rgba(77,159,255,0.3);">Edit</button>
        <button class="btn btn-success btn-sm" onclick="toggleStatus(${j.id},'open')" ${j.status==="open"?"disabled style='opacity:0.35;cursor:not-allowed'":""}>Open</button>
        <button class="btn btn-warning btn-sm" onclick="toggleStatus(${j.id},'closed')" ${j.status==="closed"?"disabled style='opacity:0.35;cursor:not-allowed'":""}>Close</button>
        <button class="btn btn-danger btn-sm"  onclick="deleteJob(${j.id})">Delete</button>
      </td>
    </tr>`;
  }).join("");
}

/* #7 — Edit Job Modal */
function openEditJobModal(jobId) {
  const j = _myJobs.find(x => x.id === jobId);
  if (!j) return;
  document.getElementById("editJobId").value       = j.id;
  document.getElementById("editJobModalTitle").textContent = j.title;
  document.getElementById("ejTitle").value         = j.title || "";
  document.getElementById("ejLocation").value      = j.location || "";
  document.getElementById("ejType").value          = j.type || "Full-Time";
  document.getElementById("ejCategory").value      = j.category || "";
  document.getElementById("ejSalary").value        = j.salary || "";
  document.getElementById("ejMaxApplicants").value = j.max_applicants || "";
  document.getElementById("ejDeadline").value      = j.deadline || "";
  document.getElementById("ejStatus").value        = j.status || "open";
  document.getElementById("ejDesc").value          = j.description || "";
  document.getElementById("ejImageUrl").value      = j.image_url || "";
  document.getElementById("editJobAlert").className = "alert";
  document.getElementById("editJobModal").classList.add("open");
}
function closeEditJobModal() {
  document.getElementById("editJobModal").classList.remove("open");
}
async function saveEditJob() {
  const id = parseInt(document.getElementById("editJobId").value);
  const updates = {
    title:          document.getElementById("ejTitle").value.trim() || undefined,
    location:       document.getElementById("ejLocation").value.trim() || undefined,
    type:           document.getElementById("ejType").value,
    category:       document.getElementById("ejCategory").value || null,
    salary:         document.getElementById("ejSalary").value.trim() || null,
    max_applicants: document.getElementById("ejMaxApplicants").value ? parseInt(document.getElementById("ejMaxApplicants").value) : null,
    deadline:       document.getElementById("ejDeadline").value || null,
    status:         document.getElementById("ejStatus").value,
    description:    document.getElementById("ejDesc").value.trim() || null,
    image_url:      document.getElementById("ejImageUrl").value.trim() || null,
  };
  // Remove undefined keys
  Object.keys(updates).forEach(k => updates[k] === undefined && delete updates[k]);
  try {
    await api(`/jobs/${id}`, "PATCH", updates);
    showAlert("editJobAlert", "Job updated successfully! ✓", "success");
    setTimeout(() => { closeEditJobModal(); loadDashboard(); }, 1200);
  } catch(e) { showAlert("editJobAlert", e.message, "error"); }
}

/* ── JOB IMAGE PREVIEW ── */
function previewJobImage(input){
  const file=input.files[0]; if(!file) return;
  const reader=new FileReader();
  reader.onload=e=>{
    const preview=document.getElementById("jobImgPreview");
    preview.src=e.target.result; preview.style.display="block";
    document.getElementById("jobImgPlaceholder").style.display="none";
    document.getElementById("jobImgUrl").value=e.target.result;
  };
  reader.readAsDataURL(file);
}
function previewJobImageUrl(input){
  const url=input.value;
  const preview=document.getElementById("jobImgPreview");
  if(url){ preview.src=url; preview.style.display="block"; document.getElementById("jobImgPlaceholder").style.display="none"; }
  else { preview.style.display="none"; document.getElementById("jobImgPlaceholder").style.display="block"; }
}

/* ── POST JOB ── */
// Store selected job image file globally
let _jobImgFile = null;

function previewJobImage(input) {
  const file = input.files[0];
  if (!file) return;
  _jobImgFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    const preview = document.getElementById("jobImgPreview");
    const placeholder = document.getElementById("jobImgPlaceholder");
    preview.src = e.target.result;
    preview.style.display = "block";
    if (placeholder) placeholder.style.display = "none";
  };
  reader.readAsDataURL(file);
}

function previewJobImageUrl(input) {
  const preview = document.getElementById("jobImgPreview");
  const placeholder = document.getElementById("jobImgPlaceholder");
  if (input.value) {
    preview.src = input.value;
    preview.style.display = "block";
    if (placeholder) placeholder.style.display = "none";
    _jobImgFile = null; // clear file if URL is typed
  } else {
    preview.style.display = "none";
    if (placeholder) placeholder.style.display = "block";
  }
}

function _fmtError(e) {
  // FastAPI validation errors come as arrays — format them readably
  if (e && e.message) {
    try {
      const parsed = JSON.parse(e.message);
      if (Array.isArray(parsed)) return parsed.map(x => x.msg || JSON.stringify(x)).join(", ");
      if (typeof parsed === "object") return parsed.detail || JSON.stringify(parsed);
    } catch {}
    return e.message;
  }
  return String(e);
}

async function postJob(){
  const maxVal = document.getElementById("jobMaxApplicants").value;
  showAlert("postAlert","Posting...","success");
  try {
    // Step 1: If a file was selected, upload it first and get CDN URL
    let imageUrl = document.getElementById("jobImgUrl").value || null;
    if (_jobImgFile) {
      showAlert("postAlert","Uploading banner image...","success");
      const fd = new FormData();
      fd.append("file", _jobImgFile);
      const token = localStorage.getItem("token");
      const res = await fetch(((window.JT_CONFIG&&window.JT_CONFIG.API_BASE)||"http://localhost:8000")+"/upload/job-image", {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: fd,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Image upload failed");
      imageUrl = data.url;
      showAlert("postAlert","Posting...","success");
    }
    // Only accept http(s) URLs — data: URIs too large for API
    if (imageUrl && !imageUrl.startsWith("http")) imageUrl = null;

    await api("/jobs","POST",{
      title:        document.getElementById("jobTitle").value,
      company:      document.getElementById("jobCompany").value,
      location:     document.getElementById("jobLocation").value,
      type:         document.getElementById("jobType").value,
      category:     document.getElementById("jobCategory").value || null,
      salary:       document.getElementById("jobSalary").value   || null,
      max_applicants: maxVal ? parseInt(maxVal) : null,
      deadline:     document.getElementById("jobDeadline").value || null,
      description:  document.getElementById("jobDesc").value     || null,
      image_url:    imageUrl,
      employer_id:  user.id,
      status:       "open",
    });
    showAlert("postAlert","Position posted successfully!","success");
    ["jobTitle","jobCompany","jobLocation","jobSalary","jobDesc","jobMaxApplicants","jobDeadline","jobImgUrl"]
      .forEach(id => document.getElementById(id).value = "");
    document.getElementById("jobCategory").value = "";
    const preview = document.getElementById("jobImgPreview");
    const placeholder = document.getElementById("jobImgPlaceholder");
    if (preview) { preview.src = ""; preview.style.display = "none"; }
    if (placeholder) placeholder.style.display = "block";
    document.getElementById("jobImgFile").value = "";
    _jobImgFile = null;
    loadDashboard();
  } catch(e) { showAlert("postAlert", _fmtError(e), "error"); }
}

async function toggleStatus(id,status){try{await api(`/jobs/${id}`,"PATCH",{status});loadDashboard();}catch(e){alert(e.message);}}
async function updateStatus(id,status){
  try{
    await api(`/applications/${id}`,"PATCH",{status});
    if (status === "accepted" || status === "rejected") {
      showActionPopup({
        title: status === "accepted" ? "Application accepted" : "Application rejected",
        message: status === "accepted" ? "The applicant has been marked as accepted." : "The applicant has been marked as rejected.",
        type: status === "accepted" ? "success" : "info",
        duration: 1200,
      });
    }
    loadDashboard();
  }catch(e){alert(e.message);}
}
async function deleteJob(id){const ok=await showConfirm("Delete Posting","Permanently remove this listing?");if(!ok)return;try{await api(`/jobs/${id}`,"DELETE");loadDashboard();}catch(e){alert(e.message);}}
async function withdrawApp(id){const ok=await showConfirm("Withdraw","Withdraw this application?");if(!ok)return;try{await api(`/applications/${id}`,"DELETE");loadApplicantApps();}catch(e){alert(e.message);}}

/* #9 — Smart refresh: only reload the active visible tab, not everything */
function _getActiveTab() {
  if (user.role === "employer") {
    const panels = ["tabEmpApps","tabMyJobs","tabPost","tabEmpProfile","tabAnalytics"];
    return panels.find(id => document.getElementById(id)?.classList.contains("active")) || "tabEmpApps";
  }
  const panels = ["tabProfile","tabApps","tabInterest"];
  return panels.find(id => document.getElementById(id)?.classList.contains("active")) || "tabProfile";
}

function smartRefresh() {
  const active = _getActiveTab();
  if (user.role === "employer") {
    if (active === "tabEmpApps" || active === "tabMyJobs" || active === "tabAnalytics") {
      loadEmployerData();
    }
    if (active === "tabEmpMessages") loadEmpConversations();
  } else {
    if (active === "tabApps") loadApplicantApps();
    if (active === "tabProfile") loadProfile();
    if (active === "tabMessages") loadAppConversations();
  }
}

function populateAnalyticsSelect(jobs) {
  var sel = document.getElementById("analyticsJobSelect");
  if (!sel) return;
  var prev = sel.value;
  sel.innerHTML = '<option value="">-- Choose a job --</option>';
  (jobs||[]).forEach(function(j) {
    var opt = document.createElement("option");
    opt.value = j.id;
    opt.textContent = j.title + " (" + j.status + ")";
    sel.appendChild(opt);
  });
  if (prev) sel.value = prev;
}

async function loadAnalytics(jobId) {
  var content = document.getElementById("analyticsContent");
  var empty   = document.getElementById("analyticsEmpty");
  var isMobile = window.matchMedia("(max-width: 768px)").matches;
  if (!jobId) {
    content.style.display = "none";
    empty.style.display = "block";
    empty.textContent = "Select a job above to see its analytics.";
    return;
  }
  content.style.display = "none";
  empty.style.display = "block";
  empty.textContent = "Loading...";
  try {
    var d = await api("/analytics/jobs/" + jobId);
    empty.style.display = "none";
    content.style.display = "block";
    var cards = [
      { label:"Total Apps",  value: d.total_applications,      color:"",       tone:"total"    },
      { label:"Accepted",    value: d.accepted,                 color:"green",  tone:"accepted" },
      { label:"Pending",     value: d.pending,                  color:"gold",   tone:"pending"  },
      { label:"Accept Rate", value: (d.acceptance_rate||0)+"%", color:"",       tone:"rate"     },
    ];
    document.getElementById("analyticsCards").innerHTML = cards.map(function(card) {
      return '<div class="stat-card analytics-stat-card analytics-tone-' + card.tone + '"><div class="stat-card-label">' + card.label + '</div>' +
             '<div class="stat-card-num ' + card.color + '">' + card.value + '</div></div>';
    }).join("");
    var timeline = d.timeline || [];
    var maxVal = Math.max.apply(null, timeline.map(function(t){ return t.applications; }));
    var safeMax = maxVal > 0 ? maxVal : 1;
    document.getElementById("analyticsChart").innerHTML = timeline.map(function(t) {
      var h  = Math.max(Math.round((t.applications / safeMax) * 120), t.applications > 0 ? 4 : 1);
      var bg = t.applications > 0 ? "linear-gradient(180deg, rgba(30,168,60,0.95) 0%, rgba(30,168,60,0.7) 100%)" : "var(--surface3)";
      return '<div class="analytics-bar-wrap" title="' + t.date + ': ' + t.applications + ' apps">' +
        '<div class="analytics-bar-count">' + t.applications + '</div>' +
        '<div class="analytics-bar" style="height:' + h + 'px;background:' + bg + ';"></div>' +
      '</div>';
    }).join("");
    var labelStep = isMobile ? 10 : 7;
    var labels = timeline.filter(function(_, i){ return i % labelStep === 0 || i === timeline.length - 1; });
    document.getElementById("analyticsChartLabels").innerHTML = labels.map(function(t) {
      var dt = new Date(t.date);
      return "<span>" + (dt.getMonth()+1) + "/" + dt.getDate() + "</span>";
    }).join("");
    document.getElementById("analyticsBreakdown").innerHTML = (d.status_breakdown||[]).map(function(s) {
      var pct = d.total_applications > 0 ? Math.round((s.value / d.total_applications) * 100) : 0;
      return '<div class="analytics-break-row">' +
        '<div class="analytics-break-head">' +
          '<span class="analytics-break-label">' + s.label + '</span>' +
          '<span class="analytics-break-value">' + s.value + ' (' + pct + '%)</span>' +
        '</div>' +
        '<div class="analytics-break-track">' +
          '<div class="analytics-break-fill" style="width:' + pct + '%;background:' + s.color + ';"></div>' +
        '</div></div>';
    }).join("");
  } catch(e) {
    empty.textContent = "Error: " + e.message;
    empty.style.display = "block";
    content.style.display = "none";
  }
}

// ══ CHAT VARS ══
let _activeChatAppId  = null;
let _chatPollInterval = null;
let _unreadCounts     = {};
let _replyToMsg       = null;
let _pendingImageUrl  = null;
let _pendingImageFile = null;

loadDashboard();
setInterval(smartRefresh, 30000);

// Shared shell modules initialize deduplicated dashboard notifications + saved-jobs tab.
window.JobTrackShell.notifications.initDashboardNotifications();

// ══ EMPLOYER VERIFIED BADGE ══════════════════════════
function renderVerifiedBadge(isVerified) {
  const el = document.getElementById("empProfileRole");
  if (!el) return;
  el.innerHTML = isVerified
    ? `Employer / Recruiter &nbsp;<span style="display:inline-flex;align-items:center;gap:3px;background:rgba(30,168,60,0.12);border:1px solid rgba(30,168,60,0.35);color:var(--green);font-size:10px;font-weight:700;padding:2px 7px;border-radius:100px;font-family:var(--mono);">✓ VERIFIED</span>`
    : `Employer / Recruiter`;
}

// Patch showAppTab to load saved jobs
const _origShowAppTab2 = showAppTab;
showAppTab = function(id, btn) {
  _origShowAppTab2(id, btn);
  if (id === "tabSaved") loadSavedJobsTab();
};

// Start notification polling
loadDashNotifCount();
setInterval(loadDashNotifCount, 30000);



// ── Report User ──────────────────────────────────────────
function openReportUserModal(userId, name, email, profilePic) {
  document.getElementById("reportedUserId").value = userId;
  document.getElementById("reportUserTitle").textContent = "Report: " + name;
  document.getElementById("ruModalName").textContent = name;
  document.getElementById("ruModalEmail").textContent = email || "";
  const av = document.getElementById("ruModalAvatar");
  av.innerHTML = profilePic
    ? `<img src="${profilePic}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;"/>`
    : (name[0] || "?").toUpperCase();
  document.getElementById("reportUserReason").value = "";
  document.getElementById("reportUserDetails").value = "";
  document.getElementById("reportUserAlert").className = "alert";
  document.getElementById("reportUserAlert").innerHTML = "";
  document.getElementById("reportUserModal").classList.add("open");
}
 
function closeReportUserModal() {
  document.getElementById("reportUserModal").classList.remove("open");
}
 
async function submitUserReport() {
  const reportedId = parseInt(document.getElementById("reportedUserId").value);
  const reason     = document.getElementById("reportUserReason").value;
  const details    = document.getElementById("reportUserDetails").value.trim();
  if (!reason) { showAlert("reportUserAlert", "Please select a reason.", "error"); return; }
  try {
    await api("/admin/user-reports", "POST", {
      reported_id: reportedId,
      reason,
      details: details || null,
    });
    showAlert("reportUserAlert", "✓ Report submitted.", "success");
    showActionPopup({
      title: "User reported",
      message: "Your report has been submitted for review.",
      type: "success",
      duration: 1300,
    });
    setTimeout(closeReportUserModal, 1500);
  } catch(e) { showAlert("reportUserAlert", e.message, "error"); }
}
 
document.addEventListener("DOMContentLoaded", function() {
  var rum = document.getElementById("reportUserModal");
  if (rum) rum.addEventListener("click", function(e) {
    if (e.target === rum) closeReportUserModal();
  });
});

// ══════════════════════════════════════════════
// CHAT SYSTEM
// ══════════════════════════════════════════════
// (variables declared above loadDashboard call)

function _fmtTime(iso) {
  if (!iso) return "";
  const d = new Date(iso), now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  if (isToday) return d.toLocaleTimeString("en-PH", { hour:"2-digit", minute:"2-digit" });
  return d.toLocaleDateString("en-PH", { month:"short", day:"numeric" }) + " " +
         d.toLocaleTimeString("en-PH", { hour:"2-digit", minute:"2-digit" });
}
function _fmtDateLabel(iso) {
  const d = new Date(iso), now = new Date();
  const yesterday = new Date(now); yesterday.setDate(now.getDate()-1);
  if (d.toDateString()===now.toDateString()) return "Today";
  if (d.toDateString()===yesterday.toDateString()) return "Yesterday";
  return d.toLocaleDateString("en-PH",{weekday:"short",month:"short",day:"numeric"});
}

function escHtml(s) { return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/'/g,"&#39;").replace(/"/g,"&quot;"); }
function escapeHtml(str) { return (str||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/\n/g,"<br/>"); }

async function openChatModal(applicationId, otherName, otherPic, jobTitle) {
  _activeChatAppId = applicationId;
  clearReply();
  clearPendingImage();
  document.getElementById("chatModalName").textContent = otherName || "—";
  document.getElementById("chatModalSub").textContent  = jobTitle  || "Application";
  const av = document.getElementById("chatModalAvatar");
  av.innerHTML = otherPic
    ? `<img src="${otherPic}" onerror="this.parentElement.textContent='${(otherName||"?")[0].toUpperCase()}'"/>`
    : (otherName||"?")[0].toUpperCase();
  document.getElementById("chatInput").value = "";
  document.getElementById("chatModal").classList.add("open");
  await fetchChatMessages();
  clearInterval(_chatPollInterval);
  _chatPollInterval = setInterval(fetchChatMessages, 5000);
}

function closeChatModal() {
  document.getElementById("chatModal").classList.remove("open");
  clearInterval(_chatPollInterval);
  _activeChatAppId = null;
  clearReply();
  clearPendingImage();
  loadUnreadCounts();
}

document.addEventListener("DOMContentLoaded", function() {
  var cm = document.getElementById("chatModal");
  if (cm) cm.addEventListener("click", function(e){ if(e.target===cm) closeChatModal(); });
  var lb = document.getElementById("chatLightbox");
  if (lb) lb.addEventListener("click", function(){ lb.classList.remove("open"); });
});

async function fetchChatMessages() {
  if (!_activeChatAppId) return;
  try {
    const msgs = await api(`/chat/application/${_activeChatAppId}`);
    renderChatMessages(msgs);
  } catch(e) { console.error("Chat fetch:", e.message); }
}

function renderChatMessages(msgs) {
  const container = document.getElementById("chatMessages");
  if (!msgs || !msgs.length) {
    container.innerHTML = `<div class="chat-empty"><div class="chat-empty-icon">💬</div>No messages yet.<br/>Start the conversation!</div>`;
    return;
  }
  const wasAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 60;
  let lastDateLabel = "", html = "";
  msgs.forEach(m => {
    const isMine = m.sender_id === user.id;
    const sender = m.users || {};
    const dateLabel = _fmtDateLabel(m.created_at);
    if (dateLabel !== lastDateLabel) {
      html += `<div class="chat-date-sep">${dateLabel}</div>`;
      lastDateLabel = dateLabel;
    }
    const av = sender.profile_pic
      ? `<img src="${sender.profile_pic}" onerror="this.parentElement.textContent='${(sender.name||"?")[0].toUpperCase()}'"/>`
      : (sender.name || "?")[0].toUpperCase();
    // Reply preview
    let replyHtml = "";
    if (m.reply_to_id && m.reply) {
      const rBody = (m.reply.image_url && !m.reply.body) ? "📷 Photo" : escHtml(m.reply.body||"");
      const rName = m.reply.users?.name || "Unknown";
      replyHtml = `<div class="chat-reply-preview" onclick="scrollToMsg(${m.reply_to_id})">
        <div class="crp-name">${escHtml(rName)}</div>
        <div class="crp-body">${rBody.substring(0,80)}</div>
      </div>`;
    }
    const imgHtml = m.image_url
      ? `<img class="chat-msg-img" src="${escHtml(m.image_url)}" alt="Photo" onclick="openLightbox('${escHtml(m.image_url)}')" loading="lazy"/>`
      : "";
    const bodyHtml = m.body ? `<div>${escapeHtml(m.body)}</div>` : "";
    const senderNameEsc = escHtml(sender.name||"You");
    const bodyForReply = escHtml((m.body||"Photo").substring(0,60).replace(/'/g,"\\'"));
    html += `<div class="chat-msg${isMine?" mine":""}" id="cmsg-${m.id}">
      <div class="chat-msg-avatar">${av}</div>
      <div class="chat-msg-content">
        ${replyHtml}
        <div class="chat-msg-bubble">${imgHtml}${bodyHtml}</div>
        <div class="chat-msg-meta">
          <span class="chat-msg-time">${_fmtTime(m.created_at)}${m.is_read&&isMine?" · ✓":""}</span>
          <button class="chat-reply-btn" onclick="setReply(${m.id},'${senderNameEsc}','${bodyForReply}')">↩ Reply</button>
        </div>
      </div>
    </div>`;
  });
  container.innerHTML = html;
  if (wasAtBottom) container.scrollTop = container.scrollHeight;
}

function scrollToMsg(id) {
  const el = document.getElementById(`cmsg-${id}`);
  if (!el) return;
  el.scrollIntoView({behavior:"smooth",block:"center"});
  el.style.transition="background 0.3s";
  el.style.background="rgba(30,168,60,0.14)";
  setTimeout(()=>{ el.style.background=""; }, 1400);
}

function setReply(msgId, senderName, body) {
  _replyToMsg = { id: msgId, body, senderName };
  document.getElementById("chatReplyBarText").textContent = body || "📷 Photo";
  document.getElementById("chatReplyBar").classList.add("show");
  document.getElementById("chatInput").focus();
}
function clearReply() {
  _replyToMsg = null;
  const bar = document.getElementById("chatReplyBar");
  if (bar) bar.classList.remove("show");
}

async function handleChatImageSelect(input) {
  const file = input.files[0];
  if (!file) return;
  if (file.size > 5*1024*1024) { alert("Max image size is 5MB."); return; }
  _pendingImageFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    document.getElementById("chatImgThumb").src = e.target.result;
    document.getElementById("chatImgPreviewLabel").textContent = file.name;
    document.getElementById("chatImgPreviewBar").classList.add("show");
  };
  reader.readAsDataURL(file);
  try {
    document.getElementById("chatImgPreviewLabel").textContent = "Uploading…";
    const fd = new FormData();
    fd.append("file", file);
    const token = localStorage.getItem("token");
    const res = await fetch(((window.JT_CONFIG&&window.JT_CONFIG.API_BASE)||"http://localhost:8000")+"/upload/job-image", {
      method:"POST", headers:{"Authorization":`Bearer ${token}`}, body:fd
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail||"Upload failed");
    _pendingImageUrl = data.url;
    document.getElementById("chatImgPreviewLabel").textContent = "✓ Ready to send";
  } catch(e) {
    clearPendingImage();
    alert("Image upload failed: " + e.message);
  }
  input.value = "";
}

function clearPendingImage() {
  _pendingImageUrl = null;
  _pendingImageFile = null;
  const bar = document.getElementById("chatImgPreviewBar");
  if (bar) bar.classList.remove("show");
  const thumb = document.getElementById("chatImgThumb");
  if (thumb) thumb.src = "";
  const label = document.getElementById("chatImgPreviewLabel");
  if (label) label.textContent = "Image ready to send";
}

function openLightbox(url) {
  document.getElementById("chatLightboxImg").src = url;
  document.getElementById("chatLightbox").classList.add("open");
}

async function sendChatMessage() {
  if (!_activeChatAppId) return;
  const input = document.getElementById("chatInput");
  const body  = input.value.trim();
  if (!body && !_pendingImageUrl) return;
  const btn = document.getElementById("chatSendBtn");
  btn.disabled = true;
  try {
    await api(`/chat/application/${_activeChatAppId}`, "POST", {
      body:        body || "",
      reply_to_id: _replyToMsg ? _replyToMsg.id : null,
      image_url:   _pendingImageUrl || null,
    });
    input.value = "";
    input.style.height = "auto";
    clearReply();
    clearPendingImage();
    await fetchChatMessages();
  } catch(e) { alert("Send failed: " + e.message); }
  finally { btn.disabled = false; input.focus(); }
}

async function loadUnreadCounts() {
  try {
    _unreadCounts = await api("/chat/unread-counts");
    const total = Object.values(_unreadCounts).reduce((a,b) => a+b, 0);
    const badge = document.getElementById(user.role==="employer" ? "empMsgBadge" : "appMsgBadge");
    if (badge) {
      if (total > 0) { badge.textContent = total; badge.style.display = "inline-flex"; }
      else badge.style.display = "none";
    }
  } catch(e) { /* silent */ }
}

async function loadAppConversations() {
  const container = document.getElementById("appConversationList");
  try {
    await loadUnreadCounts();
    const apps = _allApps.length ? _allApps : await api(`/applications/me`);
    if (!apps.length) { container.innerHTML = `<div class="empty-msg">No applications yet.</div>`; return; }
    // Fetch employer profiles for profile pics
    const employerIds = [...new Set(apps.map(a => a.jobs?.employer_id).filter(Boolean))];
    const empProfiles = {};
    await Promise.all(employerIds.map(async id => {
      try { empProfiles[id] = await api(`/users/${id}/public`); } catch(e) { /* silent */ }
    }));
    container.innerHTML = apps.map(a => {
      const unread   = _unreadCounts[a.id] || 0;
      const company  = a.jobs?.company || "Employer";
      const jobTitle = a.jobs?.title   || "Position";
      const empId    = a.jobs?.employer_id;
      const empProfile = empProfiles[empId] || {};
      const pic = empProfile.profile_pic || "";
      return `<div class="conv-item" onclick="openChatModal(${a.id},'${escHtml(company)}','${pic}','${escHtml(jobTitle)}')">
        <div class="conv-item-avatar">
          ${pic?`<img src="${pic}" onerror="this.parentElement.textContent='${company[0].toUpperCase()}'"/>`:company[0].toUpperCase()}
          ${unread>0?`<div class="conv-unread-dot"></div>`:""}
        </div>
        <div class="conv-item-info">
          <div class="conv-item-name">${escapeHtml(company)}</div>
          <div class="conv-item-sub">${escapeHtml(jobTitle)}</div>
        </div>
        <div class="conv-item-meta">
          ${unread>0?`<span class="g-chip" style="animation:pulse 2s infinite;">${unread} new</span>`:`<span class="g-chip gc-muted">read</span>`}
        </div>
      </div>`;
    }).join("");
  } catch(e) { container.innerHTML = `<div class="empty-msg" style="color:var(--red);">Error: ${e.message}</div>`; }
}

async function loadEmpConversations() {
  const container = document.getElementById("empConversationList");
  try {
    await loadUnreadCounts();
    const apps = await api(`/applications/employer`);
    if (!apps.length) { container.innerHTML = `<div class="empty-msg">No applications received yet.</div>`; return; }
    apps.forEach(a => { _appStore[a.id] = a; });
    container.innerHTML = apps.map(a => {
      const unread   = _unreadCounts[a.id] || 0;
      const profile  = a.users || {};
      const name     = a.name || profile.name || "Applicant";
      const pic      = profile.profile_pic || "";
      const jobTitle = a.jobs?.title || "Position";
      return `<div class="conv-item" onclick="openChatModal(${a.id},'${escHtml(name)}','${pic}','${escHtml(jobTitle)}')">
        <div class="conv-item-avatar">
          ${pic?`<img src="${pic}" onerror="this.parentElement.textContent='${name[0].toUpperCase()}'"/>`:name[0].toUpperCase()}
          ${unread>0?`<div class="conv-unread-dot"></div>`:""}
        </div>
        <div class="conv-item-info">
          <div class="conv-item-name">${escapeHtml(name)}</div>
          <div class="conv-item-sub">${escapeHtml(jobTitle)}</div>
        </div>
        <div class="conv-item-meta">
          ${unread>0?`<span class="g-chip" style="animation:pulse 2s infinite;">${unread} new</span>`:`<span class="g-chip gc-muted">read</span>`}
        </div>
      </div>`;
    }).join("");
  } catch(e) { container.innerHTML = `<div class="empty-msg" style="color:var(--red);">Error: ${e.message}</div>`; }
}

// Patch tab switches to load conversations
const _origShowAppTab = showAppTab;
showAppTab = function(id, btn) { _origShowAppTab(id, btn); if (id==="tabMessages")    loadAppConversations(); };
const _origShowEmpTab = showEmpTab;
showEmpTab = function(id, btn) { _origShowEmpTab(id, btn); if (id==="tabEmpMessages") loadEmpConversations(); };

// Poll unread every 30s
loadUnreadCounts();
setInterval(loadUnreadCounts, 30000);