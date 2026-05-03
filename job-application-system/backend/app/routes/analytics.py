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
    supabase.table("jobs").update(
        {"view_count": supabase.raw("view_count + 1")}
    ).eq("id", job_id).execute()
    return {"message": "View recorded."}
