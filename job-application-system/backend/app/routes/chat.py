"""
Chat / Messaging route — JobTrack
Mounted at /chat in main.py
"""
from fastapi import APIRouter, HTTPException, Request
from app.database import supabase
from pydantic import BaseModel

router = APIRouter()


def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


class MessageCreate(BaseModel):
    body:        str
    reply_to_id: int | None = None
    image_url:   str | None = None


def _assert_participant(application_id: int, user_id: int):
    """Ensure the user is either the applicant or the employer of this application."""
    app_result = supabase.table("applications").select(
        "user_id, jobs(employer_id)"
    ).eq("id", application_id).execute()

    if not app_result.data:
        raise HTTPException(status_code=404, detail="Application not found.")

    app = app_result.data[0]
    applicant_id = app["user_id"]
    employer_id  = (app.get("jobs") or {}).get("employer_id")

    if user_id not in (applicant_id, employer_id):
        raise HTTPException(status_code=403, detail="Access denied.")

    return app


@router.get("/application/{application_id}")
def get_messages(application_id: int, request: Request):
    """Fetch all messages for an application thread."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    _assert_participant(application_id, user_id)

    # Mark unread messages (sent by the other party) as read
    supabase.table("messages").update({"is_read": True}).eq(
        "application_id", application_id
    ).neq("sender_id", user_id).eq("is_read", False).execute()

    result = (
        supabase.table("messages")
        .select("*, users(id, name, profile_pic), reply:reply_to_id(id, body, image_url, users(name))")
        .eq("application_id", application_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


@router.post("/application/{application_id}")
def send_message(application_id: int, msg: MessageCreate, request: Request):
    """Send a message in an application thread."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    if not msg.body.strip() and not msg.image_url:
        raise HTTPException(status_code=400, detail="Message body cannot be empty.")

    _assert_participant(application_id, user_id)

    result = supabase.table("messages").insert({
        "application_id": application_id,
        "sender_id":      user_id,
        "body":           msg.body.strip(),
        "reply_to_id":    msg.reply_to_id,
        "image_url":      msg.image_url,
        "is_read":        False,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to send message.")

    return result.data[0]


@router.get("/unread-counts")
def get_unread_counts(request: Request):
    """
    Returns a dict of {application_id: unread_count} for messages
    sent by the OTHER party (not the current user) that are unread.
    Only counts messages from applications the user is a participant in.
    """
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    # Collect all application IDs the user participates in
    applicant_apps = (
        supabase.table("applications")
        .select("id")
        .eq("user_id", user_id)
        .execute()
    )
    employer_jobs = (
        supabase.table("jobs")
        .select("id")
        .eq("employer_id", user_id)
        .execute()
    )
    job_ids = [j["id"] for j in (employer_jobs.data or [])]
    employer_apps = []
    if job_ids:
        employer_apps_result = (
            supabase.table("applications")
            .select("id")
            .in_("job_id", job_ids)
            .execute()
        )
        employer_apps = employer_apps_result.data or []

    all_app_ids = list(set(
        [a["id"] for a in (applicant_apps.data or [])] +
        [a["id"] for a in employer_apps]
    ))

    if not all_app_ids:
        return {}

    # Only count unread messages from conversations the user is part of
    result = (
        supabase.table("messages")
        .select("application_id")
        .in_("application_id", all_app_ids)
        .neq("sender_id", user_id)
        .eq("is_read", False)
        .execute()
    )

    counts: dict = {}
    for row in (result.data or []):
        app_id = row["application_id"]
        counts[app_id] = counts.get(app_id, 0) + 1

    return counts


@router.get("/conversation-previews")
def get_conversation_previews(request: Request):
    """
    Returns a dict of {application_id: last_message_preview} for
    all conversations the user is part of. Used for the Instagram-style
    message list.
    """
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    # Get all application IDs the user is part of (as applicant or employer)
    # First, get apps where user is the applicant
    applicant_apps = (
        supabase.table("applications")
        .select("id")
        .eq("user_id", user_id)
        .execute()
    )
    # Then, get apps where user is the employer
    employer_jobs = (
        supabase.table("jobs")
        .select("id")
        .eq("employer_id", user_id)
        .execute()
    )
    job_ids = [j["id"] for j in (employer_jobs.data or [])]
    employer_apps = []
    if job_ids:
        employer_apps_result = (
            supabase.table("applications")
            .select("id")
            .in_("job_id", job_ids)
            .execute()
        )
        employer_apps = employer_apps_result.data or []

    all_app_ids = list(set(
        [a["id"] for a in (applicant_apps.data or [])] +
        [a["id"] for a in employer_apps]
    ))

    if not all_app_ids:
        return {}

    # Get latest message for each application
    previews: dict = {}
    for app_id in all_app_ids:
        result = (
            supabase.table("messages")
            .select("body, sender_id, created_at, image_url, users(name)")
            .eq("application_id", app_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            msg = result.data[0]
            previews[app_id] = {
                "body": msg.get("body", ""),
                "sender_id": msg["sender_id"],
                "sender_name": (msg.get("users") or {}).get("name", "Unknown"),
                "created_at": msg.get("created_at"),
                "image_url": msg.get("image_url"),
            }

    return previews