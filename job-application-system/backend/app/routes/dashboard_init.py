"""
Dashboard Init — Single-shot combined endpoint
Replaces 4-6 sequential frontend calls with ONE request.
"""
from fastapi import APIRouter, HTTPException, Request
from app.database import supabase
import time, threading

router = APIRouter()

# ── In-memory micro-cache (TTL-based) ────────────────────
_cache = {}
_cache_lock = threading.Lock()

def _cached(key: str, ttl: int = 15):
    """Return cached value or None if expired/missing."""
    with _cache_lock:
        entry = _cache.get(key)
        if entry and time.time() - entry["t"] < ttl:
            return entry["v"]
    return None

def _set_cache(key: str, val):
    with _cache_lock:
        _cache[key] = {"v": val, "t": time.time()}


def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    return verify_token(get_token_from_request(request))


@router.get("/applicant")
def applicant_init(request: Request):
    """
    Combined init for applicant dashboard.
    Returns: profile, applications, stats, notification count, completeness.
    Replaces: GET /users/:id + GET /applications/me + GET /notifications/unread-count + GET /profile/:id/completeness
    """
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    # Profile
    profile = supabase.table("users").select(
        "id, name, email, role, profile_pic, banner_url, about_me, "
        "instagram, facebook, phone, website, is_verified, default_resume, default_cover"
    ).eq("id", user_id).single().execute().data

    # Applications with job info (single query with join)
    apps = (
        supabase.table("applications")
        .select("id, job_id, user_id, name, email, cover_letter, resume_url, status, created_at, "
                "jobs(title, company, status, deadline, max_applicants)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []

    # Stats from apps (no extra query needed)
    stats = {
        "total": len(apps),
        "pending": sum(1 for a in apps if a.get("status") == "pending"),
        "accepted": sum(1 for a in apps if a.get("status") == "accepted"),
        "rejected": sum(1 for a in apps if a.get("status") == "rejected"),
    }

    # Unread notification count
    notif = supabase.table("notifications").select("id", count="exact").eq("user_id", user_id).eq("is_read", False).execute()
    unread_count = notif.count or 0

    # Profile completeness (compute in-memory, no extra query)
    from app.routes.public_profile import calculate_completeness
    completeness = calculate_completeness(profile)

    return {
        "profile": profile,
        "applications": apps,
        "stats": stats,
        "unread_notifications": unread_count,
        "completeness": completeness,
    }


@router.get("/employer")
def employer_init(request: Request):
    """
    Combined init for employer dashboard.
    Returns: profile, apps received, my jobs, stats, notification count.
    Replaces: GET /users/:id + GET /applications/employer + GET /jobs?employer_id=X + GET /notifications/unread-count
    """
    payload = get_user_from_request(request)
    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Employer only.")
    user_id = int(payload["sub"])

    # Profile
    profile = supabase.table("users").select(
        "id, name, email, role, profile_pic, banner_url, about_me, "
        "instagram, facebook, phone, website, is_verified"
    ).eq("id", user_id).single().execute().data

    # My jobs
    jobs = (
        supabase.table("jobs")
        .select("id, title, company, location, type, category, salary, status, "
                "description, image_url, max_applicants, deadline, created_at, view_count")
        .eq("employer_id", user_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []

    job_ids = [j["id"] for j in jobs]

    # Applications received (single query)
    apps = []
    if job_ids:
        apps = (
            supabase.table("applications")
            .select("id, job_id, user_id, name, email, cover_letter, resume_url, status, "
                    "employer_notes, created_at, "
                    "jobs(title, company), users(name, email, profile_pic, about_me, instagram, facebook)")
            .in_("job_id", job_ids)
            .order("created_at", desc=True)
            .execute()
        ).data or []

    # Stats
    stats = {
        "total": len(apps),
        "pending": sum(1 for a in apps if a.get("status") == "pending"),
        "accepted": sum(1 for a in apps if a.get("status") == "accepted"),
        "rejected": sum(1 for a in apps if a.get("status") == "rejected"),
    }

    # Unread notifications
    notif = supabase.table("notifications").select("id", count="exact").eq("user_id", user_id).eq("is_read", False).execute()
    unread_count = notif.count or 0

    return {
        "profile": profile,
        "applications": apps,
        "jobs": jobs,
        "stats": stats,
        "unread_notifications": unread_count,
    }
