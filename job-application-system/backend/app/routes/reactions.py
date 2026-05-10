"""
Message Reactions route — JobTrack
Mounted at /reactions in main.py

Allows users to add/remove emoji reactions on chat messages.
"""
from fastapi import APIRouter, HTTPException, Request
from app.database import supabase
from pydantic import BaseModel

router = APIRouter()


def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


class ReactionCreate(BaseModel):
    emoji: str  # e.g. "👍", "❤️", "😂", "🎉", "😢", "🔥"


ALLOWED_EMOJIS = {"👍", "❤️", "😂", "🎉", "😢", "🔥", "👏", "💯", "✅", "👀"}


@router.post("/message/{message_id}")
def toggle_reaction(message_id: int, reaction: ReactionCreate, request: Request):
    """Toggle a reaction on a message. If already reacted with same emoji, remove it."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    if reaction.emoji not in ALLOWED_EMOJIS:
        raise HTTPException(status_code=400, detail=f"Emoji not allowed. Use one of: {', '.join(ALLOWED_EMOJIS)}")

    # Check if user already reacted with this emoji
    existing = (
        supabase.table("message_reactions")
        .select("id")
        .eq("message_id", message_id)
        .eq("user_id", user_id)
        .eq("emoji", reaction.emoji)
        .execute()
    )

    if existing.data:
        # Remove reaction (toggle off)
        supabase.table("message_reactions").delete().eq("id", existing.data[0]["id"]).execute()
        return {"action": "removed", "emoji": reaction.emoji}
    else:
        # Add reaction
        result = supabase.table("message_reactions").insert({
            "message_id": message_id,
            "user_id":    user_id,
            "emoji":      reaction.emoji,
        }).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to add reaction.")
        return {"action": "added", "emoji": reaction.emoji, "id": result.data[0]["id"]}


@router.get("/message/{message_id}")
def get_reactions(message_id: int, request: Request):
    """Get all reactions for a message."""
    get_user_from_request(request)  # auth check
    result = (
        supabase.table("message_reactions")
        .select("id, emoji, user_id, users(name)")
        .eq("message_id", message_id)
        .execute()
    )
    return result.data or []


@router.get("/messages/batch")
def get_batch_reactions(request: Request, message_ids: str = ""):
    """Get reactions for multiple messages. Pass comma-separated IDs."""
    get_user_from_request(request)
    if not message_ids:
        return {}
    ids = [int(i) for i in message_ids.split(",") if i.strip().isdigit()]
    if not ids:
        return {}
    result = (
        supabase.table("message_reactions")
        .select("id, message_id, emoji, user_id, users(name)")
        .in_("message_id", ids)
        .execute()
    )
    # Group by message_id
    grouped = {}
    for r in (result.data or []):
        mid = r["message_id"]
        if mid not in grouped:
            grouped[mid] = []
        grouped[mid].append(r)
    return grouped
