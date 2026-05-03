"""
In-app Notifications route — JobTrack
Mounted at /notifications in main.py

Notification types:
  status_change  — application accepted/rejected/reviewed
  new_message    — unread chat message
  application    — employer: new application received
  system         — platform-wide announcements
"""
from fastapi import APIRouter, HTTPException, Request
from app.database import supabase
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


# ── Public helper: create a notification (called internally) ──
def create_notification(
    user_id: int,
    notif_type: str,
    title: str,
    body: Optional[str] = None,
    link: Optional[str] = None,
) -> None:
    """Fire-and-forget notification insert. Never raises — always logs."""
    try:
        supabase.table("notifications").insert({
            "user_id": user_id,
            "type":    notif_type,
            "title":   title,
            "body":    body,
            "link":    link,
        }).execute()
    except Exception as e:
        print(f"[Notif] Failed to create notification for user {user_id}: {e}")


# ── Routes ───────────────────────────────────────────────

@router.get("/")
def get_notifications(request: Request, limit: int = 30):
    """Return recent notifications for the current user."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    result = (
        supabase.table("notifications")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


@router.get("/unread-count")
def get_unread_count(request: Request):
    """Return unread notification count — used for the bell badge."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    result = (
        supabase.table("notifications")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("is_read", False)
        .execute()
    )
    return {"count": result.count or 0}


@router.patch("/read-all")
def mark_all_read(request: Request):
    """Mark all notifications as read."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    supabase.table("notifications").update({"is_read": True}).eq("user_id", user_id).eq("is_read", False).execute()
    return {"message": "All notifications marked as read."}


@router.patch("/{notif_id}/read")
def mark_one_read(notif_id: int, request: Request):
    """Mark a single notification as read."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    result = supabase.table("notifications").select("user_id").eq("id", notif_id).execute()
    if not result.data or result.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Notification not found.")
    supabase.table("notifications").update({"is_read": True}).eq("id", notif_id).execute()
    return {"message": "Marked as read."}


@router.delete("/{notif_id}")
def delete_notification(notif_id: int, request: Request):
    """Delete a single notification."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    result = supabase.table("notifications").select("user_id").eq("id", notif_id).execute()
    if not result.data or result.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Notification not found.")
    supabase.table("notifications").delete().eq("id", notif_id).execute()
    return {"message": "Notification deleted."}
