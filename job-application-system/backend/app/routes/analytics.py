"""
Job analytics route — returns view count, application rate over time, acceptance rate.
Mounted at /analytics in main.py
"""
from fastapi import APIRouter, HTTPException, Request
from app.database import supabase
from datetime import datetime, timedelta
from collections import defaultdict

router = APIRouter()


def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


@router.get("/jobs/{job_id}")
def get_job_analytics(job_id: int, request: Request):
    """
    Returns analytics for a specific job posting.
    Only accessible by the employer who owns the job.
    """
    payload = get_user_from_request(request)
    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Only employers can view analytics.")

    # Verify ownership
    job_result = supabase.table("jobs").select(
        "id, title, employer_id, view_count, created_at, max_applicants, deadline, status"
    ).eq("id", job_id).execute()

    if not job_result.data:
        raise HTTPException(status_code=404, detail="Job not found.")
    job = job_result.data[0]
    if job["employer_id"] != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="Access denied.")

    # Fetch all applications for this job
    apps_result = supabase.table("applications").select(
        "id, status, created_at"
    ).eq("job_id", job_id).order("created_at").execute()

    apps = apps_result.data or []

    # ── Status breakdown ──────────────────────────────────
    status_counts = defaultdict(int)
    for a in apps:
        status_counts[a["status"]] += 1

    total       = len(apps)
    accepted    = status_counts["accepted"]
    rejected    = status_counts["rejected"]
    pending     = status_counts["pending"]
    reviewed    = status_counts["reviewed"]
    accept_rate = round((accepted / total * 100), 1) if total > 0 else 0

    # ── Applications per day (last 30 days) ──────────────
    today     = datetime.utcnow().date()
    day_range = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
    daily     = defaultdict(int)

    for a in apps:
        try:
            day = datetime.fromisoformat(a["created_at"].replace("Z", "+00:00")).date()
            daily[day] += 1
        except Exception:
            pass

    timeline = [
        {"date": str(d), "applications": daily.get(d, 0)}
        for d in day_range
    ]

    # ── Slots fill rate ───────────────────────────────────
    max_slots  = job.get("max_applicants")
    fill_rate  = round((total / max_slots * 100), 1) if max_slots and max_slots > 0 else None

    # ── Days since posted ─────────────────────────────────
    try:
        posted_date = datetime.fromisoformat(job["created_at"].replace("Z", "+00:00")).date()
        days_active = (today - posted_date).days
    except Exception:
        days_active = 0

    # ── Deadline urgency ──────────────────────────────────
    days_until_deadline = None
    if job.get("deadline"):
        try:
            dl = datetime.strptime(job["deadline"], "%Y-%m-%d").date()
            days_until_deadline = (dl - today).days
        except Exception:
            pass

    return {
        "job_id":    job_id,
        "job_title": job["title"],
        "status":    job["status"],

        # Summary stats
        "total_applications":  total,
        "accepted":            accepted,
        "rejected":            rejected,
        "pending":             pending,
        "reviewed":            reviewed,
        "acceptance_rate":     accept_rate,
        "view_count":          job.get("view_count", 0),

        # Slot info
        "max_applicants":      max_slots,
        "fill_rate":           fill_rate,

        # Time info
        "days_active":         days_active,
        "days_until_deadline": days_until_deadline,

        # Chart data
        "timeline": timeline,
        "status_breakdown": [
            {"label": "Pending",  "value": pending,  "color": "#ffcc44"},
            {"label": "Reviewed", "value": reviewed, "color": "#4d9fff"},
            {"label": "Accepted", "value": accepted, "color": "#44dd88"},
            {"label": "Rejected", "value": rejected, "color": "#ff4444"},
        ],
    }


@router.post("/jobs/{job_id}/view")
def record_job_view(job_id: int):
    """Increment view counter for a job. No auth required."""
    try:
        cur = supabase.table("jobs").select("view_count").eq("id", job_id).execute()
        if cur.data:
            new_count = (cur.data[0].get("view_count") or 0) + 1
            supabase.table("jobs").update({"view_count": new_count}).eq("id", job_id).execute()
            return {"message": "View recorded.", "view_count": new_count}
    except Exception:
        pass
    return {"message": "View recorded."}


@router.get("/applicant")
def get_applicant_analytics(request: Request):
    """
    Returns analytics for the current applicant:
    - Total / accepted / pending / rejected counts
    - Acceptance rate
    - Applications per week (last 8 weeks)
    - Most applied categories
    - Status breakdown
    """
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    # Fetch all applications for this user
    apps_result = supabase.table("applications").select(
        "id, status, created_at, jobs(category, type)"
    ).eq("user_id", user_id).order("created_at").execute()

    apps = apps_result.data or []

    # ── Status counts ─────────────────────────────────────
    status_counts = defaultdict(int)
    for a in apps:
        status_counts[a["status"]] += 1

    total    = len(apps)
    accepted = status_counts["accepted"]
    rejected = status_counts["rejected"]
    pending  = status_counts["pending"]
    reviewed = status_counts["reviewed"]
    accept_rate = round((accepted / total * 100), 1) if total > 0 else 0

    # ── Applications per week (last 8 weeks) ──────────────
    today = datetime.utcnow().date()
    weeks = []
    for i in range(7, -1, -1):
        week_start = today - timedelta(days=today.weekday()) - timedelta(weeks=i)
        weeks.append(week_start)

    weekly = defaultdict(int)
    for a in apps:
        try:
            app_date = datetime.fromisoformat(a["created_at"].replace("Z", "+00:00")).date()
            week_start = app_date - timedelta(days=app_date.weekday())
            weekly[week_start] += 1
        except Exception:
            pass

    timeline = [
        {
            "week": str(w),
            "label": w.strftime("%b %d"),
            "applications": weekly.get(w, 0),
        }
        for w in weeks
    ]

    # ── Category breakdown ────────────────────────────────
    cat_counts = defaultdict(int)
    for a in apps:
        job = a.get("jobs") or {}
        cat = job.get("category") or "uncategorized"
        cat_counts[cat] += 1

    # Sort by count descending, take top 8
    sorted_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:8]

    cat_colors = {
        "software": "#4d9fff", "business": "#fbbf24", "design": "#a78bfa",
        "engineering": "#22c55e", "marketing": "#f87171", "finance": "#60a5fa",
        "healthcare": "#34d16f", "education": "#eab308", "arts": "#f472b6",
        "teaching": "#818cf8", "construction": "#fb923c", "hospitality": "#38bdf8",
    }
    default_color = "#6b7280"

    categories = [
        {
            "label": cat.replace("_", " ").title(),
            "value": count,
            "color": cat_colors.get(cat, default_color),
        }
        for cat, count in sorted_cats
    ]

    # ── Job type breakdown ────────────────────────────────
    type_counts = defaultdict(int)
    for a in apps:
        job = a.get("jobs") or {}
        jtype = job.get("type") or "Unknown"
        type_counts[jtype] += 1

    type_colors = {
        "Full-Time": "#22c55e", "Part-Time": "#60a5fa",
        "Internship": "#fbbf24", "Remote": "#a78bfa",
    }
    job_types = [
        {"label": t, "value": c, "color": type_colors.get(t, default_color)}
        for t, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "total_applications": total,
        "accepted":           accepted,
        "rejected":           rejected,
        "pending":            pending,
        "reviewed":           reviewed,
        "acceptance_rate":    accept_rate,
        "timeline":           timeline,
        "categories":         categories,
        "job_types":          job_types,
        "status_breakdown": [
            {"label": "Pending",  "value": pending,  "color": "#ffcc44"},
            {"label": "Reviewed", "value": reviewed, "color": "#4d9fff"},
            {"label": "Accepted", "value": accepted, "color": "#44dd88"},
            {"label": "Rejected", "value": rejected, "color": "#ff4444"},
        ],
    }

