from fastapi import APIRouter, HTTPException, Request
from app.models import ApplicationCreate, ApplicationStatusUpdate, ApplicationNotesUpdate
from app.database import supabase
import asyncio

router = APIRouter()

def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


@router.get("/public")
def get_public_stats():
    result = supabase.table("applications").select("id, status", count="exact").execute()
    data   = result.data or []
    return {
        "total":    result.count or 0,
        "accepted": sum(1 for a in data if a.get("status") == "accepted"),
        "pending":  sum(1 for a in data if a.get("status") == "pending"),
    }


@router.get("/me")
def get_my_applications(request: Request):
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    result = (
        supabase.table("applications")
        .select("*, jobs(title, company, status, deadline, max_applicants)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/employer")
def get_employer_applications(request: Request):
    payload = get_user_from_request(request)
    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Only employers can access this endpoint.")
    user_id = int(payload["sub"])
    jobs_result = supabase.table("jobs").select("id").eq("employer_id", user_id).execute()
    job_ids = [j["id"] for j in jobs_result.data]
    if not job_ids:
        return []
    result = (
        supabase.table("applications")
        .select("*, employer_notes, jobs(title, company), users(name, email, profile_pic, about_me, instagram, facebook)")
        .in_("job_id", job_ids)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/count/{job_id}")
def get_job_application_count(job_id: int):
    result = supabase.table("applications").select("id", count="exact").eq("job_id", job_id).execute()
    return {"count": result.count or 0}


@router.post("/")
def submit_application(app: ApplicationCreate, request: Request):
    payload = get_user_from_request(request)
    authenticated_user_id = int(payload["sub"])

    if app.user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="Cannot submit application on behalf of another user.")
    if payload.get("role") == "employer":
        raise HTTPException(status_code=403, detail="Employers cannot submit job applications.")
    if app.resume_url and not app.resume_url.startswith("http"):
        raise HTTPException(status_code=400, detail="Resume URL must be a valid http(s) link.")

    job = supabase.table("jobs").select("*").eq("id", app.job_id).execute()
    if not job.data:
        raise HTTPException(status_code=404, detail="Job not found.")
    job_data = job.data[0]
    if job_data.get("status") != "open":
        raise HTTPException(status_code=400, detail="This job is no longer accepting applications.")

    # ── Deadline enforcement ──────────────────────────
    import datetime
    if job_data.get("deadline"):
        try:
            dl = datetime.date.fromisoformat(str(job_data["deadline"]))
            if datetime.date.today() > dl:
                raise HTTPException(status_code=400, detail="The application deadline for this job has passed.")
        except HTTPException:
            raise
        except Exception:
            pass  # malformed deadline — don't block

    if job_data.get("max_applicants"):
        count = supabase.table("applications").select("id", count="exact").eq("job_id", app.job_id).execute()
        if (count.count or 0) >= job_data["max_applicants"]:
            supabase.table("jobs").update({"status": "full"}).eq("id", app.job_id).execute()
            raise HTTPException(status_code=400, detail="Application slots are full.")

    existing = supabase.table("applications").select("id").eq("job_id", app.job_id).eq("user_id", app.user_id).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="You have already applied for this job.")

    result = supabase.table("applications").insert({**app.dict(), "status": "pending"}).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to submit application.")

    if job_data.get("max_applicants"):
        count = supabase.table("applications").select("id", count="exact").eq("job_id", app.job_id).execute()
        if (count.count or 0) >= job_data["max_applicants"]:
            supabase.table("jobs").update({"status": "full"}).eq("id", app.job_id).execute()

    # ── Notify employer of new application ──────────────
    try:
        from app.routes.notifications import create_notification
        employer_id = job_data.get("employer_id")
        if employer_id:
            create_notification(
                user_id=employer_id,
                notif_type="application",
                title=f"New application: {job_data['title']}",
                body=f"{app.name} applied for your listing.",
                link="/pages/dashboard.html",
            )
    except Exception as e:
        print(f"[Notif] Non-critical: {e}")

    return result.data[0]


@router.patch("/{app_id}")
async def update_status(app_id: int, update: ApplicationStatusUpdate, request: Request):
    """Update status + send email notification + in-app notification."""
    payload = get_user_from_request(request)
    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Only employers can update application status.")

    app_result = supabase.table("applications").select(
        "job_id, user_id, name, email"
    ).eq("id", app_id).execute()
    if not app_result.data:
        raise HTTPException(status_code=404, detail="Application not found.")

    app_data = app_result.data[0]
    job_result = supabase.table("jobs").select("employer_id, title, company").eq("id", app_data["job_id"]).execute()
    if not job_result.data or job_result.data[0]["employer_id"] != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="Permission denied.")

    result = supabase.table("applications").update({"status": update.status}).eq("id", app_id).execute()

    # Email notification
    if update.status in ("accepted", "rejected", "reviewed"):
        try:
            from app.email import send_status_email
            job_info = job_result.data[0]
            asyncio.create_task(send_status_email(
                to_email       = app_data.get("email", ""),
                applicant_name = app_data.get("name", "Applicant"),
                job_title      = job_info.get("title", ""),
                company        = job_info.get("company", ""),
                new_status     = update.status,
            ))
        except Exception as e:
            print(f"[Email] Non-critical: {e}")

        # ── In-app notification for applicant ────────────
        try:
            from app.routes.notifications import create_notification
            job_info = job_result.data[0]
            status_msgs = {
                "accepted": ("🎉 Application Accepted!", f"You've been accepted for {job_info['title']} at {job_info['company']}."),
                "rejected": ("Application Update", f"Your application for {job_info['title']} was not successful."),
                "reviewed": ("Application Under Review", f"Your application for {job_info['title']} is being reviewed."),
            }
            title, body = status_msgs.get(update.status, ("Application Update", ""))
            create_notification(
                user_id=app_data["user_id"],
                notif_type="status_change",
                title=title,
                body=body,
                link="/pages/dashboard.html",
            )
        except Exception as e:
            print(f"[Notif] Non-critical: {e}")

    return result.data[0]


@router.patch("/{app_id}/notes")
def update_employer_notes(app_id: int, notes_update: ApplicationNotesUpdate, request: Request):
    """Employer saves private notes on an applicant."""
    payload = get_user_from_request(request)
    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Only employers can add notes.")

    app_result = supabase.table("applications").select("job_id").eq("id", app_id).execute()
    if not app_result.data:
        raise HTTPException(status_code=404, detail="Application not found.")

    job_result = supabase.table("jobs").select("employer_id").eq("id", app_result.data[0]["job_id"]).execute()
    if not job_result.data or job_result.data[0]["employer_id"] != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="Access denied.")

    result = supabase.table("applications").update(
        {"employer_notes": notes_update.notes}
    ).eq("id", app_id).execute()
    return result.data[0]


@router.delete("/{app_id}")
def withdraw_application(app_id: int, request: Request):
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    existing = supabase.table("applications").select("user_id").eq("id", app_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Application not found.")
    if existing.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You can only withdraw your own applications.")
    supabase.table("applications").delete().eq("id", app_id).execute()
    return {"message": "Application withdrawn."}