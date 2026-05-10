"""
Public Profile route — JobTrack
Mounted at /profile in main.py

Provides public shareable profile pages for both applicants and employers.
No authentication required to view.
"""
from fastapi import APIRouter, HTTPException, Request
from app.database import supabase

router = APIRouter()


@router.get("/{user_id}")
def get_public_profile(user_id: int):
    """
    Get a user's public profile. Available to anyone (no auth).
    Excludes sensitive info like email, password, etc.
    """
    result = supabase.table("users").select(
        "id, name, role, profile_pic, banner_url, about_me, "
        "instagram, facebook, website, is_verified, created_at"
    ).eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")

    user = result.data[0]

    # For employers: include their job postings
    jobs = []
    if user.get("role") == "employer":
        jobs_result = (
            supabase.table("jobs")
            .select("id, title, company, location, type, category, salary, status, created_at, image_url")
            .eq("employer_id", user_id)
            .eq("status", "open")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        jobs = jobs_result.data or []

    # Profile completeness
    completeness = calculate_completeness(user)

    return {
        **user,
        "jobs": jobs,
        "completeness": completeness,
    }


@router.get("/{user_id}/completeness")
def get_profile_completeness(user_id: int, request: Request):
    """Get profile completeness for a specific user (auth required for own profile)."""
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    payload = verify_token(token)

    if int(payload["sub"]) != user_id:
        raise HTTPException(status_code=403, detail="You can only check your own completeness.")

    result = supabase.table("users").select(
        "id, name, role, profile_pic, banner_url, about_me, "
        "instagram, facebook, website, phone, default_resume, default_cover"
    ).eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")

    return calculate_completeness(result.data[0])


def calculate_completeness(user: dict) -> dict:
    """Calculate profile completeness percentage and missing fields."""
    role = user.get("role", "applicant")

    if role == "employer":
        fields = {
            "Profile Picture": bool(user.get("profile_pic")),
            "Banner Photo": bool(user.get("banner_url")),
            "Company Description": bool(user.get("about_me")),
            "Instagram": bool(user.get("instagram")),
            "Facebook": bool(user.get("facebook")),
            "Website": bool(user.get("website")),
            "Phone": bool(user.get("phone")),
        }
    else:
        fields = {
            "Profile Picture": bool(user.get("profile_pic")),
            "About Me": bool(user.get("about_me")),
            "Instagram": bool(user.get("instagram")),
            "Facebook": bool(user.get("facebook")),
            "Default Resume": bool(user.get("default_resume")),
            "Default Cover Letter": bool(user.get("default_cover")),
        }

    filled = sum(1 for v in fields.values() if v)
    total = len(fields)
    percentage = round((filled / total) * 100) if total > 0 else 0

    missing = [k for k, v in fields.items() if not v]

    return {
        "percentage": percentage,
        "filled": filled,
        "total": total,
        "missing": missing,
        "fields": fields,
    }
