"""
Saved Jobs (Bookmarks) route — JobTrack
Mounted at /saved-jobs in main.py
"""
from fastapi import APIRouter, HTTPException, Request
from app.database import supabase

router = APIRouter()


def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


@router.get("/")
def get_saved_jobs(request: Request):
    """Return all saved job IDs + full job data for the current user."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    result = (
        supabase.table("saved_jobs")
        .select("id, job_id, created_at, jobs(*)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


@router.get("/ids")
def get_saved_job_ids(request: Request):
    """Return only saved job_ids — fast check for bookmark state."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    result = supabase.table("saved_jobs").select("job_id").eq("user_id", user_id).execute()
    return [row["job_id"] for row in (result.data or [])]


@router.post("/{job_id}")
def save_job(job_id: int, request: Request):
    """Bookmark a job. Idempotent — no error if already saved."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    # Verify job exists
    job = supabase.table("jobs").select("id").eq("id", job_id).execute()
    if not job.data:
        raise HTTPException(status_code=404, detail="Job not found.")

    existing = supabase.table("saved_jobs").select("id").eq("user_id", user_id).eq("job_id", job_id).execute()
    if existing.data:
        return {"saved": True, "message": "Already saved."}

    supabase.table("saved_jobs").insert({"user_id": user_id, "job_id": job_id}).execute()
    return {"saved": True, "message": "Job bookmarked."}


@router.delete("/{job_id}")
def unsave_job(job_id: int, request: Request):
    """Remove a bookmark."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    supabase.table("saved_jobs").delete().eq("user_id", user_id).eq("job_id", job_id).execute()
    return {"saved": False, "message": "Bookmark removed."}