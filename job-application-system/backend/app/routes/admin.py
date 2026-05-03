"""
Admin route — JobTrack
Mounted at /admin in main.py
Requires role == 'admin' for all endpoints.
"""
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from app.database import supabase
from app.models import ReportCreate, ReportStatusUpdate, UserReportCreate, UserReportStatusUpdate
from typing import Optional

router = APIRouter()


def get_admin(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    payload = verify_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access only.")
    return payload


# ══════════════════════════════════════════════════════
#  STATS
# ══════════════════════════════════════════════════════

@router.get("/stats")
def get_stats(request: Request):
    get_admin(request)
    users  = supabase.table("users").select("id, role").execute().data or []
    jobs   = supabase.table("jobs").select("id, status").execute().data or []
    apps   = supabase.table("applications").select("id, status").execute().data or []
    reps   = supabase.table("reports").select("id, status").execute().data or []
    ureps  = supabase.table("user_reports").select("id, status").execute().data or []
    return {
        "users": {
            "total":      len(users),
            "applicants": sum(1 for u in users if u["role"] == "applicant"),
            "employers":  sum(1 for u in users if u["role"] == "employer"),
            "admins":     sum(1 for u in users if u["role"] == "admin"),
        },
        "jobs": {
            "total":  len(jobs),
            "open":   sum(1 for j in jobs if j["status"] == "open"),
            "closed": sum(1 for j in jobs if j["status"] == "closed"),
            "full":   sum(1 for j in jobs if j["status"] == "full"),
        },
        "applications": {
            "total":    len(apps),
            "pending":  sum(1 for a in apps if a["status"] == "pending"),
            "accepted": sum(1 for a in apps if a["status"] == "accepted"),
            "rejected": sum(1 for a in apps if a["status"] == "rejected"),
            "reviewed": sum(1 for a in apps if a["status"] == "reviewed"),
        },
        "reports": {
            "total":    len(reps),
            "pending":  sum(1 for r in reps if r["status"] == "pending"),
            "actioned": sum(1 for r in reps if r["status"] == "actioned"),
        },
        "user_reports": {
            "total":    len(ureps),
            "pending":  sum(1 for r in ureps if r["status"] == "pending"),
        },
    }


# ══════════════════════════════════════════════════════
#  JOB REPORTS
# ══════════════════════════════════════════════════════

@router.get("/reports")
def get_reports(request: Request, status: Optional[str] = None):
    get_admin(request)
    q = supabase.table("reports").select(
        "*, jobs(id, title, company, status), users(id, name, email)"
    ).order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    return q.execute().data or []


@router.post("/reports")
def create_report(report: ReportCreate, request: Request):
    """Any authenticated user can file a report."""
    from app.routes.auth import get_token_from_request, verify_token
    reporter_id = None
    try:
        payload = verify_token(get_token_from_request(request))
        reporter_id = int(payload["sub"])
    except Exception:
        pass
    result = supabase.table("reports").insert({
        "job_id":      report.job_id,
        "reporter_id": reporter_id,
        "reason":      report.reason,
        "details":     report.details,
        "status":      "pending",
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to submit report.")
    return result.data[0]


@router.patch("/reports/{report_id}")
def update_report(report_id: int, update: ReportStatusUpdate, request: Request):
    get_admin(request)
    result = supabase.table("reports").update({
        "status":      update.status,
        "admin_notes": update.admin_notes,
    }).eq("id", report_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Report not found.")
    return result.data[0]


@router.delete("/reports/{report_id}")
def delete_report(report_id: int, request: Request):
    get_admin(request)
    supabase.table("reports").delete().eq("id", report_id).execute()
    return {"message": "Report deleted."}


# ══════════════════════════════════════════════════════
#  USER REPORTS
# ══════════════════════════════════════════════════════

@router.get("/user-reports")
def get_user_reports(request: Request, status: Optional[str] = None):
    get_admin(request)
    q = supabase.table("user_reports").select(
        "*, reported:reported_id(id, name, email, role, profile_pic), reporter:reporter_id(id, name, email, profile_pic)"
    ).order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    return q.execute().data or []


@router.post("/user-reports")
def create_user_report(report: UserReportCreate, request: Request):
    """Any authenticated user can report another user."""
    from app.routes.auth import get_token_from_request, verify_token
    reporter_id = None
    try:
        payload = verify_token(get_token_from_request(request))
        reporter_id = int(payload["sub"])
    except Exception:
        pass
    result = supabase.table("user_reports").insert({
        "reported_id": report.reported_id,
        "reporter_id": reporter_id,
        "reason":      report.reason,
        "details":     report.details,
        "status":      "pending",
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to submit report.")
    return result.data[0]


@router.patch("/user-reports/{report_id}")
def update_user_report(report_id: int, update: UserReportStatusUpdate, request: Request):
    get_admin(request)
    result = supabase.table("user_reports").update({
        "status":      update.status,
        "admin_notes": update.admin_notes,
    }).eq("id", report_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Report not found.")
    return result.data[0]


@router.delete("/user-reports/{report_id}")
def delete_user_report(report_id: int, request: Request):
    get_admin(request)
    supabase.table("user_reports").delete().eq("id", report_id).execute()
    return {"message": "Report deleted."}


# ══════════════════════════════════════════════════════
#  JOBS (Admin)
# ══════════════════════════════════════════════════════

@router.get("/jobs")
def get_all_jobs(request: Request):
    get_admin(request)
    jobs = supabase.table("jobs").select("*").order("created_at", desc=True).execute().data or []
    if jobs:
        from collections import Counter
        job_ids = [j["id"] for j in jobs]
        counts = supabase.table("applications").select("job_id").in_("job_id", job_ids).execute().data or []
        count_map = Counter(row["job_id"] for row in counts)
        for j in jobs:
            j["applicant_count"] = count_map.get(j["id"], 0)
    return jobs


@router.patch("/jobs/{job_id}/status")
def set_job_status(job_id: int, status: str, request: Request):
    get_admin(request)
    if status not in ("open", "closed", "full"):
        raise HTTPException(status_code=400, detail="Invalid status.")
    result = supabase.table("jobs").update({"status": status}).eq("id", job_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found.")
    return result.data[0]


@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, request: Request):
    get_admin(request)
    supabase.table("jobs").delete().eq("id", job_id).execute()
    return {"message": "Job deleted."}


# ══════════════════════════════════════════════════════
#  USERS (Admin)
# ══════════════════════════════════════════════════════

@router.get("/users")
def get_all_users(request: Request):
    get_admin(request)
    return supabase.table("users").select(
        "id, name, email, role, profile_pic, is_verified, created_at"
    ).order("created_at", desc=True).execute().data or []


@router.get("/users/{user_id}")
def get_user(user_id: int, request: Request):
    get_admin(request)
    result = supabase.table("users").select(
        "id, name, email, role, profile_pic, banner_url, about_me, instagram, facebook, phone, website, is_verified, created_at"
    ).eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")
    return result.data[0]


@router.delete("/users/{user_id}")
def delete_user(user_id: int, request: Request):
    payload = get_admin(request)
    if int(payload["sub"]) == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account.")
    supabase.table("users").delete().eq("id", user_id).execute()
    return {"message": "User deleted."}


# ══════════════════════════════════════════════════════
#  EMPLOYER VERIFICATION  ← NEW
# ══════════════════════════════════════════════════════

@router.patch("/users/{user_id}/verify")
def verify_employer(user_id: int, request: Request):
    """Grant verified badge to an employer account."""
    get_admin(request)
    result = supabase.table("users").select("role").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")
    if result.data[0]["role"] not in ("employer", "admin"):
        raise HTTPException(status_code=400, detail="Only employer accounts can be verified.")
    updated = supabase.table("users").update({"is_verified": True}).eq("id", user_id).execute()
    return {"message": "Employer verified.", "user": updated.data[0] if updated.data else {}}


@router.patch("/users/{user_id}/unverify")
def unverify_employer(user_id: int, request: Request):
    """Revoke verified badge."""
    get_admin(request)
    result = supabase.table("users").select("id").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")
    updated = supabase.table("users").update({"is_verified": False}).eq("id", user_id).execute()
    return {"message": "Verification revoked.", "user": updated.data[0] if updated.data else {}}

# ══════════════════════════════════════════════════════
#  ID VERIFICATIONS
# ══════════════════════════════════════════════════════

class IdVerifUpdate(BaseModel):
    status:      str
    admin_notes: Optional[str] = None

@router.get("/id-verifications")
def get_id_verifications(request: Request, status: Optional[str] = None):
    get_admin(request)
    q = supabase.table("id_verifications").select(
        "*, users(id, name, email, role, profile_pic, is_verified)"
    ).order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    return q.execute().data or []


@router.patch("/id-verifications/{verif_id}")
def update_id_verification(verif_id: int, update: IdVerifUpdate, request: Request):
    get_admin(request)
    result = supabase.table("id_verifications").update({
        "status":      update.status,
        "admin_notes": update.admin_notes,
    }).eq("id", verif_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Verification record not found.")
    return result.data[0]