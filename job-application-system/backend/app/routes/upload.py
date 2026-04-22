"""
Upload endpoint — Supabase Storage
Accepts image files, uploads to Supabase Storage bucket, returns CDN URL.

Setup in Supabase:
  1. Storage → New bucket → Name: "profile-pics" → Public: ON
  2. Storage → New bucket → Name: "job-images"   → Public: ON
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.database import supabase
import uuid
import time

router = APIRouter()

# Max file size: 2MB
MAX_SIZE_BYTES = 2 * 1024 * 1024
ALLOWED_TYPES  = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import verify_token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return verify_token(auth_header[7:])


@router.post("/profile-pic")
async def upload_profile_pic(
    request: Request,
    file: UploadFile = File(...),
):
    """Upload profile picture → returns CDN URL."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Use: {', '.join(ALLOWED_TYPES)}")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 2MB.")

    # Unique filename per user (overwrites old pic)
    ext      = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"user_{user_id}/profile.{ext}"

    try:
        # Upload to Supabase Storage bucket "profile-pics"
        supabase.storage.from_("profile-pics").upload(
            path       = filename,
            file       = contents,
            file_options= {"content-type": file.content_type, "upsert": "true"},
        )
        # Get public CDN URL
        url_data = supabase.storage.from_("profile-pics").get_public_url(filename)
        cdn_url  = url_data if isinstance(url_data, str) else url_data.get("publicUrl", "")

        # Update user record
        supabase.table("users").update({"profile_pic": cdn_url}).eq("id", user_id).execute()

        return {"url": cdn_url, "message": "Profile picture updated."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/job-image")
async def upload_job_image(
    request: Request,
    file: UploadFile = File(...),
):
    """Upload job banner/cover image → returns CDN URL."""
    payload = get_user_from_request(request)

    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Only employers can upload job images.")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed.")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 2MB.")

    ext      = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"jobs/{uuid.uuid4().hex}.{ext}"

    try:
        supabase.storage.from_("job-images").upload(
            path        = filename,
            file        = contents,
            file_options= {"content-type": file.content_type},
        )
        url_data = supabase.storage.from_("job-images").get_public_url(filename)
        cdn_url  = url_data if isinstance(url_data, str) else url_data.get("publicUrl", "")

        return {"url": cdn_url, "message": "Job image uploaded."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
