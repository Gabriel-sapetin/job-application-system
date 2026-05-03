const CATEGORIES = [
  {id:"arts",label:"Arts & Media",icon:"🎬"},{id:"business",label:"Business",icon:"💼"},
  {id:"agriculture",label:"Agriculture & Forestry",icon:"🌾"},
  {id:"cleaning",label:"Cleaning",icon:"🧹"},{id:"construction",label:"Construction",icon:"🏗️"},
  {id:"customer",label:"Customer Service",icon:"🎧"},{id:"design",label:"Design",icon:"🎨"},
  {id:"education",label:"Education",icon:"📚"},{id:"engineering",label:"Engineering",icon:"⚙️"},
  {id:"finance",label:"Finance",icon:"💰"},{id:"government",label:"Gov / NGO",icon:"🏛️"},
  {id:"healthcare",label:"Healthcare",icon:"🏥"},{id:"hospitality",label:"Hospitality",icon:"🏨"},
  {id:"marketing",label:"Marketing",icon:"📣"},{id:"software",label:"Software & IT",icon:"💻"},
  {id:"teaching",label:"Teaching",icon:"🏫"},
  {id:"freelance",label:"Freelance / Project",icon:"💡",individual:true},
  {id:"errand",label:"Errands & Delivery",icon:"🛵",individual:true},
  {id:"homeservice",label:"Home Services",icon:"🏠",individual:true},
  {id:"repair",label:"Repair & Maintenance",icon:"🔧",individual:true},
  {id:"caregiving",label:"Caregiving / Domestic",icon:"🤝",individual:true},
  {id:"event",label:"Events & Assistance",icon:"🎉",individual:true},
];
const CAT_MAP  = Object.fromEntries(CATEGORIES.map(c=>[c.id,c]));
const TYPE_MAP = {"Full-Time":"full-time","Part-Time":"part-time","Internship":"internship","Remote":"remote"};
const TYPE_ICON = {"Full-Time":"🏢","Part-Time":"⏰","Internship":"🎓","Remote":"🌐"};

let allJobs=[], activeFilters={type:"",status:"",category:""}, selectedJob=null, currentView="grid";

/* ── Category pills ── */
const catRow=document.getElementById("categoryRow");
let lastWasIndividual=false;
CATEGORIES.forEach(c=>{
  if(c.individual&&!lastWasIndividual){
    const div=document.createElement("div");
    div.style.cssText="display:flex;align-items:center;gap:6px;flex-shrink:0;padding:0 4px;";
    div.innerHTML='<span style="width:1px;height:28px;background:var(--border);"></span><span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#a78bfa;white-space:nowrap;">👤 Individual</span>';
    catRow.appendChild(div);
    lastWasIndividual=true;
  }
  const pill=document.createElement("div");
  pill.className="cat-pill"+(c.individual?" individual":"");
  pill.dataset.cat=c.id;
  pill.innerHTML=c.label;
  pill.onclick=()=>toggleCategory(c.id,pill);
  catRow.appendChild(pill);
});

/* ── Scroll arrows ── */
function scrollCats(dir){
  catRow.scrollBy({left:dir*200,behavior:"smooth"});
}
// Show/hide arrows based on scroll position
catRow.addEventListener("scroll",updateScrollBtns);
function updateScrollBtns(){
  const atStart=catRow.scrollLeft<=4;
  const atEnd=catRow.scrollLeft+catRow.clientWidth>=catRow.scrollWidth-4;
  document.getElementById("catScrollLeft").style.opacity=atStart?"0.3":"1";
  document.getElementById("catScrollRight").style.opacity=atEnd?"0.3":"1";
}
setTimeout(updateScrollBtns,100);

/* ── Auth ── */
const user=getUser();
if(user){
  document.getElementById("authBtn").textContent="Dashboard";
  document.getElementById("authBtn").href="dashboard.html";
  document.getElementById("sidebarBottom").innerHTML=`
    <div class="sidebar-user">
      <div class="sidebar-avatar">${user.profile_pic?`<img src="${user.profile_pic}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;"/>`:user.name[0].toUpperCase()}</div>
      <div class="sidebar-user-info"><div class="sidebar-user-name">${user.name}</div><div class="sidebar-user-role">${user.role}</div></div>
    </div>
    <button class="sidebar-link" onclick="logout()" style="color:var(--red);margin-top:4px;">Sign Out</button>`;
}

function setFilter(key,val,btn,navId){
  activeFilters[key]=val;
  document.getElementById(navId).querySelectorAll(".sidebar-link").forEach(b=>b.classList.remove("active"));
  btn.classList.add("active"); filterJobs();
}
function toggleCategory(id,pill){
  if(activeFilters.category===id){ activeFilters.category=""; pill.classList.remove("active"); document.getElementById("clearCatBtn").style.display="none"; }
  else{ document.querySelectorAll(".cat-pill").forEach(p=>p.classList.remove("active")); pill.classList.add("active"); activeFilters.category=id; document.getElementById("clearCatBtn").style.display="inline-flex"; }
  filterJobs();
}
function clearCategory(){ activeFilters.category=""; document.querySelectorAll(".cat-pill").forEach(p=>p.classList.remove("active")); document.getElementById("clearCatBtn").style.display="none"; filterJobs(); }
function setView(v){ currentView=v; document.getElementById("gridViewBtn").classList.toggle("active",v==="grid"); document.getElementById("listViewBtn").classList.toggle("active",v==="list"); filterJobs(); }

async function loadJobs(){
  try{ allJobs=await api("/jobs"); }
  catch{
    allJobs=[
      {id:1,title:"Frontend Developer",company:"TechCorp Philippines",location:"Davao City",type:"Full-Time",salary:"₱35k–₱45k",status:"open",category:"software",max_applicants:10,deadline:"2026-05-01",image_url:""},
      {id:2,title:"Data Analyst",company:"Insights Inc.",location:"Remote",type:"Remote",salary:"₱28k–₱38k",status:"open",category:"business",image_url:""},
      {id:3,title:"IT Support Intern",company:"StartupHub Cebu",location:"Cebu City",type:"Internship",salary:"₱8k/mo",status:"full",category:"software",max_applicants:5,image_url:""},
      {id:4,title:"Backend Engineer",company:"CloudSoft Solutions",location:"Manila",type:"Full-Time",salary:"₱50k–₱65k",status:"open",category:"software",image_url:""},
      {id:5,title:"UI/UX Designer",company:"Creative Co.",location:"Davao City",type:"Part-Time",salary:"₱18k–₱25k",status:"closed",category:"design",max_applicants:3,image_url:""},
    ];
  }
  document.getElementById("countAll").textContent=allJobs.length;
  document.getElementById("liveCount").textContent=allJobs.filter(j=>j.status==="open").length;
  await loadSavedIds();
  filterJobs();
}

function filterJobs(){
  const q=document.getElementById("searchInput").value.toLowerCase();
  const {type,status,category}=activeFilters;
  const jobs=allJobs.filter(j=>(j.title.toLowerCase().includes(q)||j.company.toLowerCase().includes(q))&&(!type||j.type===type)&&(!status||j.status===status)&&(!category||j.category===category));
  document.getElementById("jobCount").textContent=`${jobs.length} position${jobs.length!==1?"s":""} found`;
  renderJobs(jobs);
}

function renderJobs(jobs){
  const c=document.getElementById("jobsContainer");
  if(!jobs.length){
    c.innerHTML=`<div class="empty-state-panpan">
      <div id="espSvgWrap"></div>
      <div class="esp-text">No positions match your filters.</div>
      <div class="esp-sub">Try clearing your category or type filter.</div>
    </div>`;
    // inject Pan-Pan SVG into empty state
    const wrap = document.getElementById("espSvgWrap");
    if(wrap && window._panpanSVG) wrap.innerHTML = window._panpanSVG;
    return;
  }
  if(currentView==="grid") renderGrid(jobs,c);
  else renderList(jobs,c);
}

function catIcon(j){ return (CAT_MAP[j.category]?.icon)||TYPE_ICON[j.type]||"📋"; }

function slotsHtml(j){
  if(!j.max_applicants) return "";
  const filled=j.applicant_count||0, pct=Math.min((filled/j.max_applicants)*100,100);
  const cls=pct>=100?"full":pct>=70?"warn":"";
  return `<div class="jc-slots"><span>${filled}/${j.max_applicants}</span><div class="jc-slots-bar"><div class="jc-slots-fill ${cls}" style="width:${pct}%"></div></div></div>`;
}

function dlHtml(j){
  if(!j.deadline) return "";
  const d=new Date(j.deadline), diff=Math.ceil((d-Date.now())/(86400000));
  const label=diff<0?"Expired":diff===0?"Today":diff<=3?`${diff}d left`:d.toLocaleDateString("en-PH",{month:"short",day:"numeric"});
  const color=diff<0?"var(--red)":diff<=3?"var(--gold)":"var(--ink-muted)";
  return `<span style="font-size:10px;color:${color};font-family:var(--mono);">⏰ ${label}</span>`;
}

function renderGrid(jobs,c){
  const indivCats=new Set(["freelance","errand","homeservice","repair","caregiving","event"]);
  c.innerHTML=`<div class="jobs-grid">${jobs.map(j=>{
    const closed=j.status==="closed"||j.status==="full";
    const cat=CAT_MAP[j.category];
    const hasBanner=j.image_url&&j.image_url.length>0;
    const isIndiv=indivCats.has(j.category);
    return `<div class="job-card${closed?" closed-card":""}">
      ${hasBanner
        ?`<img class="job-card-banner" src="${j.image_url}" alt="${j.title}" onerror="this.style.display='none'"/>`
        :`<div class="job-card-banner-placeholder"></div>`
      }
      <div class="job-card-body">
        <div class="jc-header">
          <div>
            <div class="jc-title">${j.title}</div>
            <div class="jc-company">${j.company} &nbsp;·&nbsp; 📍 ${j.location}${j.employer_is_verified?'<span style="display:inline-flex;align-items:center;gap:3px;background:rgba(30,168,60,0.1);border:1px solid rgba(30,168,60,0.3);color:var(--green);font-size:9px;font-weight:700;padding:1px 6px;border-radius:100px;margin-left:6px;font-family:var(--mono);">✓ VERIFIED</span>':''}</div>
          </div>
          <div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px;">
            <span class="pill pill-${j.status}">${j.status}</span>
            ${isIndiv?`<span class="pill-individual">👤 Individual</span>`:""}
          </div>
        </div>
        <div class="jc-meta">
          <span class="jc-meta-item">${TYPE_ICON[j.type]||""} ${j.type}</span>
          ${cat?`<span class="jc-meta-item">${cat.label}</span>`:""}
          ${j.deadline?`<span class="jc-meta-item">${dlHtml(j)}</span>`:""}
        </div>
        ${j.max_applicants?slotsHtml(j):""}
        <div class="jc-footer">
          <div class="jc-salary">${j.salary||"Negotiable"}</div>
          <div style="display:flex;gap:6px;align-items:center;">
            ${getUser()?`<button class="btn btn-ghost btn-sm bm-btn" data-jid="${j.id}" onclick="toggleBookmark(${j.id},this)" title="Save job" style="${savedIds.has(j.id)?"color:var(--gold);border-color:rgba(255,204,68,0.4);":""}">🔖</button>`:""}
            <button class="btn btn-ghost btn-sm" onclick="openDetailModal(${j.id})">Details</button>
            <button class="btn btn-${closed?"ghost":"primary"} btn-sm"
              onclick="openModal(${JSON.stringify(j).replace(/"/g,'&quot;')})"
              ${closed?`disabled style="opacity:0.5;cursor:not-allowed;"`:""}>
              ${closed?(j.status==="full"?"Full":"Closed"):"Apply →"}
            </button>
          </div>
        </div>
      </div>
    </div>`;
  }).join("")}</div>`;
}

function renderList(jobs,c){
  c.innerHTML=`<div class="jobs-list-view">${jobs.map(j=>{
    const closed=j.status==="closed"||j.status==="full";
    const cat=CAT_MAP[j.category];
    return `<div class="job-list-row${closed?" closed-row":""}">
      <div class="jlr-thumb">
        ${j.image_url?`<img src="${j.image_url}" onerror="this.style.display='none'"/>`:catIcon(j)}
      </div>
      <div class="jlr-main">
        <div class="jlr-title">
          ${j.title}
          <span class="pill pill-${j.status}">${j.status}</span>
          <span class="type-tag ${TYPE_MAP[j.type]||""}">${j.type}</span>
        </div>
        <div class="jlr-meta">
          <span>${j.company}</span><span>📍 ${j.location}</span>
          ${cat?`<span>${cat.label}</span>`:""}
          ${j.salary?`<span style="color:var(--ink);font-weight:600;font-family:var(--mono);">${j.salary}</span>`:""}
          ${j.deadline?dlHtml(j):""}
          ${j.max_applicants?slotsHtml(j):""}
        </div>
      </div>
      <div class="jlr-right">
        ${getUser()?`<button class="btn btn-ghost btn-sm bm-btn" data-jid="${j.id}" onclick="toggleBookmark(${j.id},this)" title="Save job" style="${savedIds.has(j.id)?"color:var(--gold);border-color:rgba(255,204,68,0.4);":""}">🔖</button>`:""}
        <button class="btn btn-ghost btn-sm" onclick="openDetailModal(${j.id})">Details</button>
        <button class="btn btn-${closed?"ghost":"primary"} btn-sm"
          onclick="openModal(${JSON.stringify(j).replace(/"/g,'&quot;')})"
          ${closed?`disabled style="opacity:0.5;cursor:not-allowed;"`:""}>
          ${closed?(j.status==="full"?"Full":"Closed"):"Apply →"}
        </button>
      </div>
    </div>`;
  }).join("")}</div>`;
}

function openModal(jObj){
  const j=typeof jObj==="string"?JSON.parse(jObj.replace(/&quot;/g,'"')):jObj;
  if(!getUser()){ window.location.href="login.html"; return; }
  selectedJob=j;
  document.getElementById("modalJobTitle").textContent=j.title;
  document.getElementById("modalJobMeta").textContent=j.company+(j.max_applicants?` · ${j.applicant_count||0}/${j.max_applicants} applicants`:"");
  // Show banner in modal if available
  const mb=document.getElementById("modalBannerImg");
  if(j.image_url){ mb.src=j.image_url; mb.style.display="block"; }
  else { mb.style.display="none"; }
  const u=getUser();
  const _p=window._userProfile||{};
  document.getElementById("applyName").value=u?.name||"";
  document.getElementById("applyEmail").value=u?.email||"";
  document.getElementById("applyCover").value=_p.default_cover||"";
  document.getElementById("applyResume").value=_p.default_resume||"";
  const _hint=document.getElementById("applyPrefillHint");
  if(_hint) _hint.style.display=(_p.default_resume||_p.default_cover)?"flex":"none";
  document.getElementById("applyModal").classList.add("open");
}
function closeModal(){ document.getElementById("applyModal").classList.remove("open"); const a=document.getElementById("applyAlert"); a.innerHTML=""; a.className="alert"; }

async function submitApplication(){
  const u=getUser();
  if(!u){ window.location.href="login.html"; return; }
  try{
    await api("/applications","POST",{
      job_id:selectedJob.id, user_id:u.id,
      name:document.getElementById("applyName").value,
      email:document.getElementById("applyEmail").value,
      cover_letter:document.getElementById("applyCover").value,
      resume_url:document.getElementById("applyResume").value,
    });
    showAlert("applyAlert","Application submitted successfully!","success");
    setTimeout(()=>{ closeModal(); loadJobs(); },1600);
  } catch(e){ showAlert("applyAlert",e.message,"error"); }
}

/* ── Job Detail Modal ── */
function openDetailModal(jobId) {
  const j = allJobs.find(x => x.id === jobId);
  if (!j) return;
  selectedJob = j;

  // Banner
  const bi = document.getElementById("jdBannerImg");
  const bp = document.getElementById("jdBannerPlaceholder");
  if (j.image_url) { bi.src = j.image_url; bi.style.display = "block"; bp.style.display = "none"; }
  else { bi.style.display = "none"; bp.style.display = "flex"; bp.textContent = catIcon(j); }

  // Header
  document.getElementById("jdTitle").textContent = j.title;
  document.getElementById("jdCompany").textContent = j.company + "  ·  📍 " + j.location;

  const cat = CAT_MAP[j.category];
  const closed = j.status === "closed" || j.status === "full";
  const tagParts = [
    '<span class="jd-tag">' + (TYPE_ICON[j.type]||"") + " " + j.type + '</span>',
    '<span class="pill pill-' + j.status + '" style="margin:0;">' + j.status + '</span>',
    cat ? '<span class="jd-tag">' + cat.label + '</span>' : "",
    j.view_count ? '<span class="jd-tag">👁 ' + j.view_count + ' views</span>' : "",
  ];
  document.getElementById("jdTags").innerHTML = tagParts.join("");

  // Deadline color + label
  var dlColor = "var(--ink-muted)", dlLabel = "No deadline";
  if (j.deadline) {
    var d = new Date(j.deadline);
    var diff = Math.ceil((d - Date.now()) / 86400000);
    dlColor = diff < 0 ? "var(--red)" : diff <= 3 ? "var(--gold)" : "var(--ink)";
    dlLabel = d.toLocaleDateString("en-PH",{month:"long",day:"numeric",year:"numeric"})
      + (diff < 0 ? " (Expired)" : diff === 0 ? " (Today)" : diff <= 3 ? " (" + diff + "d left)" : "");
  }

  // Slots color + label
  var slotsColor = "var(--ink-muted)", slotsLabel = "Unlimited slots";
  if (j.max_applicants) {
    var pct = ((j.applicant_count||0) / j.max_applicants) * 100;
    slotsColor = pct >= 100 ? "var(--red)" : pct >= 70 ? "var(--gold)" : "var(--green)";
    slotsLabel = (j.applicant_count||0) + " / " + j.max_applicants + " applied";
  }

  // Posted
  var posted = "—";
  if (j.created_at) {
    var days = Math.floor((Date.now() - new Date(j.created_at)) / 86400000);
    posted = days === 0 ? "Today" : days === 1 ? "Yesterday" : days + " days ago";
  }

  document.getElementById("jdMetaGrid").innerHTML =
    '<div class="jd-meta-item"><span class="jd-meta-icon" style="display:none"></span><div><div class="jd-meta-key">Deadline</div><div class="jd-meta-val" style="color:' + dlColor + '">' + dlLabel + '</div></div></div>' +
    '<div class="jd-meta-item"><span class="jd-meta-icon" style="display:none"></span><div><div class="jd-meta-key">Applicants / Slots</div><div class="jd-meta-val" style="color:' + slotsColor + '">' + slotsLabel + '</div></div></div>' +
    '<div class="jd-meta-item"><span class="jd-meta-icon" style="display:none"></span><div><div class="jd-meta-key">Job Type</div><div class="jd-meta-val">' + j.type + '</div></div></div>' +
    '<div class="jd-meta-item"><span class="jd-meta-icon" style="display:none"></span><div><div class="jd-meta-key">Posted</div><div class="jd-meta-val">' + posted + '</div></div></div>';

  // Description
  var descEl = document.getElementById("jdDescription");
  if (j.description && j.description.trim()) {
    descEl.className = "jd-description";
    descEl.textContent = j.description;
  } else {
    descEl.className = "jd-no-desc";
    descEl.textContent = "No description provided for this position.";
  }

  document.getElementById("jdSalary").textContent = j.salary || "Negotiable";

  // Individual safety warning
  const indivCats=new Set(["freelance","errand","homeservice","repair","caregiving","event"]);
  document.getElementById("jdSafetyBox").style.display = indivCats.has(j.category) ? "block" : "none";

  // Transparency trust row
  const postedDays = j.created_at ? Math.floor((Date.now()-new Date(j.created_at))/86400000) : null;
  const postedLabel = postedDays===null?"—":postedDays===0?"Today":postedDays===1?"Yesterday":postedDays+" days ago";
  document.getElementById("jdTrustBox").innerHTML =
    '<div class="trust-row"><span>👥</span><span style="flex:1;">Applicants</span><span class="tr-val">'+(j.applicant_count||0)+(j.max_applicants?" / "+j.max_applicants+" slots":"")+'</span></div>'+
    '<div class="trust-row"><span>👁</span><span style="flex:1;">Views</span><span class="tr-val">'+(j.view_count||0)+'</span></div>'+
    (postedDays!==null?'<div class="trust-row"><span>🕐</span><span style="flex:1;">Posted</span><span class="tr-val">'+postedLabel+'</span></div>':"");

  var applyBtn = document.getElementById("jdApplyBtn");
  if (closed) {
    applyBtn.textContent = j.status === "full" ? "Slots Full" : "Position Closed";
    applyBtn.disabled = true; applyBtn.style.opacity = "0.4"; applyBtn.style.cursor = "not-allowed";
  } else {
    applyBtn.textContent = "Apply Now →";
    applyBtn.disabled = false; applyBtn.style.opacity = ""; applyBtn.style.cursor = "";
  }

  document.getElementById("jobDetailModal").classList.add("open");
}

function closeDetailModal() {
  document.getElementById("jobDetailModal").classList.remove("open");
}

function applyFromDetail() {
  closeDetailModal();
  if (!getUser()) { window.location.href = "login.html"; return; }
  openModal(selectedJob);
}

function copyJobLink() {
  var url = window.location.href.split("?")[0] + (selectedJob ? "?job=" + selectedJob.id : "");
  navigator.clipboard.writeText(url).then(function() {
    var btn = document.getElementById("jdShareBtn");
    var orig = btn.textContent;
    btn.textContent = "✓ Copied!";
    setTimeout(function(){ btn.textContent = orig; }, 2000);
  }).catch(function(){ prompt("Copy this link:", url); });
}

document.getElementById("jobDetailModal").addEventListener("click", function(e) {
  if (e.target === document.getElementById("jobDetailModal")) closeDetailModal();
});
document.getElementById("safetyModal").addEventListener("click",function(e){if(e.target===document.getElementById("safetyModal"))document.getElementById("safetyModal").classList.remove("open");});
document.getElementById("reportModal").addEventListener("click",function(e){if(e.target===document.getElementById("reportModal"))closeReportModal();});

function openReportModal(){
  if(!selectedJob)return;
  document.getElementById("reportJobTitle").textContent="Report: "+selectedJob.title;
  document.getElementById("reportReason").value="";
  document.getElementById("reportDetails").value="";
  document.getElementById("reportAlert").className="alert";
  document.getElementById("reportAlert").innerHTML="";
  document.getElementById("reportModal").classList.add("open");
}
function closeReportModal(){document.getElementById("reportModal").classList.remove("open");}

async function submitReport(){
  const reason=document.getElementById("reportReason").value;
  if(!reason){showAlert("reportAlert","Please select a reason.","error");return;}
  const details=document.getElementById("reportDetails").value.trim();
  try{
    await api("/admin/reports","POST",{job_id:selectedJob.id,reason,details:details||null});
    showAlert("reportAlert","✓ Report submitted. Thank you for keeping JobTrack safe.","success");
    setTimeout(()=>closeReportModal(),2000);
  }catch(e){showAlert("reportAlert",e.message||"Failed to submit report.","error");}
}


// ══ USER PROFILE AUTO-FILL ════════════════════════════
async function loadUserProfileForAutofill() {
  const u = getUser(); if (!u) return;
  try { window._userProfile = await api(`/users/${u.id}`); }
  catch(e) { window._userProfile = {}; }
}

// ══ TOAST ════════════════════════════════════════════
function showToast(msg, type="success") {
  let t = document.getElementById("_jt_toast");
  if (!t) {
    t = document.createElement("div");
    t.id = "_jt_toast";
    t.style.cssText = "position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:10px 18px;font-size:13px;color:var(--ink);box-shadow:0 8px 28px rgba(0,0,0,0.2);z-index:9999;transition:opacity 0.3s,transform 0.3s;white-space:nowrap;font-family:var(--font);pointer-events:none;";
    document.body.appendChild(t);
  }
  t.style.color = type === "error" ? "var(--red)" : "var(--ink)";
  t.textContent = msg;
  t.style.opacity = "1";
  t.style.transform = "translateX(-50%) translateY(0)";
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.opacity="0"; t.style.transform="translateX(-50%) translateY(8px)"; }, 2800);
}

// ══ INIT FOR LOGGED-IN USERS ════════════════════════
if (getUser()) {
  document.getElementById("notifBellWrap").style.display = "block";
  loadNotifCount();
  loadUserProfileForAutofill();
  setInterval(loadNotifCount, 30000);
}

loadJobs();
