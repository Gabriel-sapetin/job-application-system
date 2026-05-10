"""
Application Attachments route — JobTrack
Mounted at /attachments in main.py

Allows applicants to upload portfolio items, certificates, and other
documents to attach to their applications.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from app.database import supabase
import requests as _requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SUPABASE_URL   = os.getenv("SUPABASE_URL", "")
SERVICE_KEY    = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB per file
MAX_FILES      = 5  # max attachments per application
ALLOWED_TYPES  = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def get_user_from_request(request: Request) -> dict:
    from app.routes.auth import get_token_from_request, verify_token
    token = get_token_from_request(request)
    return verify_token(token)


def _upload_to_storage(bucket: str, filename: str, contents: bytes, content_type: str) -> str:
    """Upload to Supabase Storage. Returns public CDN URL."""
    headers = {
        "Authorization": f"Bearer {SERVICE_KEY}",
        "apikey":        SERVICE_KEY,
        "Content-Type":  content_type,
        "x-upsert":      "true",
    }
    url  = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    resp = _requests.post(url, headers=headers, data=contents, timeout=30)
    if resp.status_code in (400, 409):
        headers["x-upsert"] = "true"
        resp = _requests.put(url, headers=headers, data=contents, timeout=30)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=500, detail=f"Upload failed: {resp.text}")
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"


@router.post("/upload")
async def upload_attachment(
    request: Request,
    file: UploadFile = File(...),
    application_id: int = Form(...),
    label: str = Form("Document"),
):
    """Upload an attachment for an application."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    # Verify the application belongs to this user
    app_result = supabase.table("applications").select("user_id").eq("id", application_id).execute()
    if not app_result.data or app_result.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    # Check existing attachment count
    count_result = supabase.table("application_attachments").select("id", count="exact").eq("application_id", application_id).execute()
    if (count_result.count or 0) >= MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_FILES} attachments per application.")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed. Use PDF, DOC, DOCX, or images.")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "pdf"
    filename = f"attachments/{user_id}/{application_id}/{uuid.uuid4().hex}.{ext}"

    cdn_url = _upload_to_storage("job-images", filename, contents, file.content_type)

    result = supabase.table("application_attachments").insert({
        "application_id": application_id,
        "user_id":        user_id,
        "file_url":       cdn_url,
        "file_name":      file.filename,
        "file_type":      file.content_type,
        "file_size":      len(contents),
        "label":          label[:100],
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save attachment record.")

    return result.data[0]


@router.get("/application/{application_id}")
def get_attachments(application_id: int, request: Request):
    """Get all attachments for an application."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])
    role = payload.get("role")

    # Verify access
    app_result = supabase.table("applications").select("user_id, job_id").eq("id", application_id).execute()
    if not app_result.data:
        raise HTTPException(status_code=404, detail="Application not found.")

    app_data = app_result.data[0]
    if role == "applicant" and app_data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")
    if role == "employer":
        job_result = supabase.table("jobs").select("employer_id").eq("id", app_data["job_id"]).execute()
        if not job_result.data or job_result.data[0]["employer_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied.")

    result = (
        supabase.table("application_attachments")
        .select("*")
        .eq("application_id", application_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


@router.delete("/{attachment_id}")
def delete_attachment(attachment_id: int, request: Request):
    """Delete an attachment. Only the owner can delete."""
    payload = get_user_from_request(request)
    user_id = int(payload["sub"])

    existing = supabase.table("application_attachments").select("user_id").eq("id", attachment_id).execute()
    if not existing.data or existing.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    supabase.table("application_attachments").delete().eq("id", attachment_id).execute()
    return {"message": "Attachment deleted."}
