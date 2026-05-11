"""
User Activity Log route — JobTrack
Mounted at /activity-log in main.py

Tracks login history, profile updates, application submissions, etc.
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


# ── Public helper: log an activity (called internally) ──
def log_activity(
    user_id: int,
    action: str,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Fire-and-forget activity insert. Never raises."""
    try:
        supabase.table("activity_log").insert({
            "user_id":    user_id,
            "action":     action,
            "details":    details,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }).execute()
    except Exception as e:
        print(f"[ActivityLog] Failed to log for user {user_id}: {e}")


# ── Routes ───────────────────────────────────────────────

@router.get("/")
def get_activity_log(request: Request, limit: int = 50):
    """Return recent activity for the current user."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    try:
        result = (
            supabase.table("activity_log")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[ActivityLog] Query failed for user {user_id}: {e}")
        return []


@router.delete("/clear")
def clear_activity_log(request: Request):
    """Clear all activity logs for current user."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    supabase.table("activity_log").delete().eq("user_id", user_id).execute()
    return {"message": "Activity log cleared."}


@router.post("/session")
def log_session_resumed(request: Request):
    """
    Log a 'session resumed' event when the user opens the dashboard
    with an existing valid token (not a fresh login).
    Deduplicates within a 5-minute window to avoid spam from refreshes.
    """
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    # Check if there's already a login/session_resumed entry in the last 5 minutes
    from datetime import datetime, timedelta, timezone
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    try:
        recent = (
            supabase.table("activity_log")
            .select("id")
            .eq("user_id", user_id)
            .in_("action", ["login", "session_resumed"])
            .gte("created_at", cutoff)
            .limit(1)
            .execute()
        )
        if recent.data:
            return {"message": "Already logged recently."}
    except Exception:
        pass

    log_activity(
        user_id=user_id,
        action="login",
        details="Dashboard opened",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:200],
    )
    return {"message": "Session logged."}

