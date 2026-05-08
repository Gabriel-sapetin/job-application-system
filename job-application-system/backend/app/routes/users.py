from fastapi import APIRouter, HTTPException, Request
from app.models import UserProfileUpdate
from app.database import supabase

router = APIRouter()

def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


@router.get("/{user_id}")
def get_user(user_id: int, request: Request):
    payload = get_user_from_request(request)
    requester_id   = int(payload["sub"])
    requester_role = payload.get("role")

    if requester_role == "applicant" and requester_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    result = supabase.table("users").select(
        "id, name, email, role, profile_pic, banner_url, about_me, "
        "instagram, facebook, phone, website, is_verified, created_at"
    ).eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")
    return result.data[0]


@router.patch("/{user_id}")
def update_profile(user_id: int, profile: UserProfileUpdate, request: Request):
    payload = get_user_from_request(request)
    if int(payload["sub"]) != user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own profile.")

    if profile.instagram:
        handle = profile.instagram.lstrip("@").strip()
        if " " in handle or len(handle) > 30:
            raise HTTPException(status_code=400, detail="Invalid Instagram username.")
        profile = profile.copy(update={"instagram": handle})

    updates = profile.dict()
    result = supabase.table("users").update(updates).eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")

    u = result.data[0]
    u.pop("password", None)
    return u