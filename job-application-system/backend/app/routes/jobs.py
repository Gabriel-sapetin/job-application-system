from fastapi import APIRouter, HTTPException, Request, Query
from app.models import JobCreate, JobUpdate
from app.database import supabase
from typing import Optional

router = APIRouter()

def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


@router.get("/")
def get_jobs(
    type:        Optional[str] = None,
    location:    Optional[str] = None,
    employer_id: Optional[int] = None,
    category:    Optional[str] = None,
    status:      Optional[str] = None,
    search:      Optional[str] = None,
    page:        int = Query(1, ge=1),
    limit:       int = Query(50, ge=1, le=100),
):
    query = supabase.table("jobs").select("*").order("created_at", desc=True)
    if employer_id: query = query.eq("employer_id", employer_id)
    if type:        query = query.eq("type", type)
    if location:    query = query.ilike("location", f"%{location}%")
    if category:    query = query.eq("category", category)
    if status:      query = query.eq("status", status)

    # ── Improvement 2: Full-text search across title + company + description ──
    if search:
        search_clean = search.strip()
        # Supabase textSearch uses PostgreSQL tsvector — searches title, company, description
        try:
            result = (
                supabase.table("jobs")
                .select("*")
                .text_search("title", search_clean, config="english")
                .order("created_at", desc=True)
                .execute()
            )
            # Fallback: also ilike search company
            ilike_result = supabase.table("jobs").select("*").ilike("company", f"%{search_clean}%").execute()
            # Merge + deduplicate
            seen_ids = set()
            merged   = []
            for row in (result.data or []) + (ilike_result.data or []):
                if row["id"] not in seen_ids:
                    seen_ids.add(row["id"])
                    merged.append(row)
            # Attach applicant_count to merged search results
            if merged:
                from collections import Counter
                s_ids = [j["id"] for j in merged]
                s_counts = supabase.table("applications").select("job_id", count="exact").in_("job_id", s_ids).execute()
                s_map = Counter(row["job_id"] for row in (s_counts.data or []))
                for j in merged:
                    j["applicant_count"] = s_map.get(j["id"], 0)
            return merged
        except Exception:
            # Graceful fallback to ilike
            query = supabase.table("jobs").select("*").ilike("title", f"%{search}%").order("created_at", desc=True)

    offset = (page - 1) * limit
    query  = query.range(offset, offset + limit - 1)
    jobs = query.execute().data

    # Attach applicant_count to each job
    if jobs:
        job_ids = [j["id"] for j in jobs]
        counts_result = supabase.table("applications").select("job_id", count="exact").in_("job_id", job_ids).execute()
        # count per job_id
        from collections import Counter
        count_map = Counter(row["job_id"] for row in (counts_result.data or []))
        for j in jobs:
            j["applicant_count"] = count_map.get(j["id"], 0)
    return jobs


@router.get("/stats")
def get_job_stats():
    jobs      = supabase.table("jobs").select("id", count="exact").execute()
    open_jobs = supabase.table("jobs").select("id", count="exact").eq("status", "open").execute()
    return {"job_count": jobs.count or 0, "open_job_count": open_jobs.count or 0}


@router.get("/{job_id}")
def get_job(job_id: int):
    # ── Increment view count ──
    try:
        cur = supabase.table("jobs").select("view_count").eq("id", job_id).execute()
        if cur.data:
            new_views = (cur.data[0].get("view_count") or 0) + 1
            supabase.table("jobs").update({"view_count": new_views}).eq("id", job_id).execute()
    except Exception:
        pass

    result = supabase.table("jobs").select("*").eq("id", job_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found.")
    return result.data[0]


@router.post("/")
def create_job(job: JobCreate, request: Request):
    payload = get_user_from_request(request)
    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Only employers can post jobs.")
    if job.deadline:
        import datetime
        try:
            datetime.date.fromisoformat(job.deadline)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline format. Use YYYY-MM-DD.")
    job_data = job.dict()
    job_data["employer_id"] = int(payload["sub"])
    result = supabase.table("jobs").insert(job_data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create job.")
    return result.data[0]


@router.patch("/{job_id}")
def update_job(job_id: int, job: JobUpdate, request: Request):
    payload  = get_user_from_request(request)
    existing = supabase.table("jobs").select("employer_id").eq("id", job_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Job not found.")
    if existing.data[0]["employer_id"] != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="You do not own this job posting.")
    updates = {k: v for k, v in job.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update.")
    result = supabase.table("jobs").update(updates).eq("id", job_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found.")
    return result.data[0]


@router.delete("/{job_id}")
def delete_job(job_id: int, request: Request):
    payload  = get_user_from_request(request)
    existing = supabase.table("jobs").select("employer_id").eq("id", job_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Job not found.")
    if existing.data[0]["employer_id"] != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="You do not own this job posting.")
    supabase.table("jobs").delete().eq("id", job_id).execute()
    return {"message": "Job deleted."}