"""
Upload endpoint — Supabase Storage via REST API
Uses service_role key to bypass RLS on storage.

.env addition needed:
  SUPABASE_SERVICE_KEY=eyJ...   <- Supabase > Settings > API > service_role key
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.database import supabase
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SUPABASE_URL   = os.getenv("SUPABASE_URL", "")
SERVICE_KEY    = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")
MAX_SIZE_BYTES = 2 * 1024 * 1024
ALLOWED_TYPES  = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


def _upload_to_storage(bucket: str, filename: str, contents: bytes, content_type: str, upsert: bool = False) -> str:
    """Upload to Supabase Storage REST API using service role key. Returns public CDN URL."""
    headers = {
        "Authorization": f"Bearer {SERVICE_KEY}",
        "apikey":        SERVICE_KEY,
        "Content-Type":  content_type,
        "x-upsert":      "true" if upsert else "false",
    }
    url  = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    resp = requests.post(url, headers=headers, data=contents, timeout=30)

    # If file exists (409/400), retry with PUT + upsert
    if resp.status_code in (400, 409):
        headers["x-upsert"] = "true"
        resp = requests.put(url, headers=headers, data=contents, timeout=30)

    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Upload failed: {resp.text}")

    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"


@router.post("/profile-pic")
async def upload_profile_pic(request: Request, file: UploadFile = File(...)):
    """Upload profile picture, save CDN URL to DB, return URL."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed. Use JPEG, PNG, GIF, or WEBP.")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Max 2MB.")

    ext      = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"user_{user_id}/profile.{ext}"

    cdn_url = _upload_to_storage("profile-pics", filename, contents, file.content_type, upsert=True)
    supabase.table("users").update({"profile_pic": cdn_url}).eq("id", user_id).execute()

    return {"url": cdn_url, "message": "Profile picture updated."}


@router.post("/job-image")
async def upload_job_image(request: Request, file: UploadFile = File(...)):
    """Upload job banner image, return CDN URL."""
    payload = get_user_from_request(request)

    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Only employers can upload job images.")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed. Use JPEG, PNG, GIF, or WEBP.")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Max 2MB.")

    ext      = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"jobs/{uuid.uuid4().hex}.{ext}"

    cdn_url = _upload_to_storage("job-images", filename, contents, file.content_type)

    return {"url": cdn_url, "message": "Job image uploaded."}

@router.post("/verification-id")
async def upload_verification_id(request: Request, file: UploadFile = File(...), id_type: str = "other"):
    """Upload employer verification ID for admin review."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    if payload.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Only employers can submit verification IDs.")

    ALLOWED_ID_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    if file.content_type not in ALLOWED_ID_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed. Use JPEG, PNG, or PDF.")

    contents = await file.read()
    MAX_ID_SIZE = 5 * 1024 * 1024
    if len(contents) > MAX_ID_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"verif/{user_id}/{uuid.uuid4().hex}.{ext}"

    cdn_url = _upload_to_storage("job-images", filename, contents, file.content_type)

    # Save to DB
    from app.database import supabase as _sb
    result = _sb.table("id_verifications").insert({
        "user_id": user_id,
        "id_type": id_type,
        "id_url":  cdn_url,
        "status":  "pending",
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save verification record.")

    return {"message": "ID submitted for review.", "id": result.data[0]["id"]}