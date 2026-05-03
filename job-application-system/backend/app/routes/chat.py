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
    """
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    result = (
        supabase.table("messages")
        .select("application_id")
        .neq("sender_id", user_id)
        .eq("is_read", False)
        .execute()
    )

    counts: dict = {}
    for row in (result.data or []):
        app_id = row["application_id"]
        counts[app_id] = counts.get(app_id, 0) + 1

    return counts