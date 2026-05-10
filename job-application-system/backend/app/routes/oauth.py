"""
OAuth Login route — JobTrack
Mounted at /oauth in main.py
"""
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from app.database import supabase
from app.routes.auth import create_token, TOKEN_TTL
import os
import httpx
import logging

router = APIRouter()
logger = logging.getLogger("jobtrack.oauth")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500/job-application-system/frontend")
BACKEND_URL  = os.getenv("BACKEND_URL",  "http://localhost:8000")

# ── Google OAuth ─────────────────────────────────────────
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_AUTH_URL      = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL     = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL  = "https://www.googleapis.com/oauth2/v2/userinfo"

# ── GitHub OAuth ─────────────────────────────────────────
GITHUB_CLIENT_ID     = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_AUTH_URL      = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL     = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL      = "https://api.github.com/user"
GITHUB_EMAIL_URL     = "https://api.github.com/user/emails"


def _find_user(email: str, profile_pic: str = None) -> dict:
    """Find existing user by email. Returns None if not found."""
    result = supabase.table("users").select("*").eq("email", email.lower()).execute()
    if not result.data:
        return None
    user = result.data[0]
    if profile_pic and not user.get("profile_pic"):
        supabase.table("users").update({"profile_pic": profile_pic}).eq("id", user["id"]).execute()
        user["profile_pic"] = profile_pic
    return user


def _build_login_redirect(user: dict) -> str:
    token = create_token(user["id"], user["role"])
    try:
        from app.routes.activity_log import log_activity
        log_activity(user_id=user["id"], action="login", details="OAuth login")
    except Exception:
        pass
    from urllib.parse import quote
    redirect_url = (
        f"{FRONTEND_URL}/pages/login.html"
        f"?oauth_token={token}"
        f"&user_id={user['id']}"
        f"&user_name={quote(user['name'])}"
        f"&user_email={quote(user['email'])}"
        f"&user_role={user['role']}"
    )
    if user.get("profile_pic"):
        redirect_url += f"&user_pic={quote(user['profile_pic'], safe=':/?=&')}"
    return redirect_url


@router.get("/google/login")
def google_login():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars.")
    redirect_uri = f"{BACKEND_URL}/oauth/google/callback"
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  redirect_uri,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    url = f"{GOOGLE_AUTH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str = None, error: str = None):
    if error or not code:
        return RedirectResponse(f"{FRONTEND_URL}/pages/login.html?oauth_error=Google login cancelled")
    redirect_uri = f"{BACKEND_URL}/oauth/google/callback"
    try:
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(GOOGLE_TOKEN_URL, data={
                "code":          code,
                "client_id":     GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri":  redirect_uri,
                "grant_type":    "authorization_code",
            })
            token_data = token_resp.json()
            if "access_token" not in token_data:
                logger.error(f"Google token error: {token_data}")
                return RedirectResponse(f"{FRONTEND_URL}/pages/login.html?oauth_error=Failed to authenticate with Google")
            userinfo_resp = await client.get(GOOGLE_USERINFO_URL, headers={
                "Authorization": f"Bearer {token_data['access_token']}"
            })
            userinfo = userinfo_resp.json()
        email = userinfo.get("email")
        if not email:
            return RedirectResponse(f"{FRONTEND_URL}/pages/login.html?oauth_error=No email returned from Google")
        user = _find_user(email=email, profile_pic=userinfo.get("picture", ""))
        if not user:
            from urllib.parse import quote
            return RedirectResponse(
                f"{FRONTEND_URL}/pages/login.html?oauth_error="
                f"No account found for {quote(email)}. Please register first."
            )
        return RedirectResponse(_build_login_redirect(user))
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        return RedirectResponse(f"{FRONTEND_URL}/pages/login.html?oauth_error=OAuth error: {str(e)}")


@router.get("/github/login")
def github_login():
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=501, detail="GitHub OAuth not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET env vars.")
    redirect_uri = f"{BACKEND_URL}/oauth/github/callback"
    params = {
        "client_id":    GITHUB_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope":        "user:email",
    }
    url = f"{GITHUB_AUTH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url)


@router.get("/github/callback")
async def github_callback(code: str = None, error: str = None):
    if error or not code:
        return RedirectResponse(f"{FRONTEND_URL}/pages/login.html?oauth_error=GitHub login cancelled")
    try:
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(GITHUB_TOKEN_URL, data={
                "client_id":     GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code":          code,
            }, headers={"Accept": "application/json"})
            token_data = token_resp.json()
            if "access_token" not in token_data:
                logger.error(f"GitHub token error: {token_data}")
                return RedirectResponse(f"{FRONTEND_URL}/pages/login.html?oauth_error=Failed to authenticate with GitHub")
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "Accept":        "application/json",
            }
            user_resp = await client.get(GITHUB_USER_URL, headers=headers)
            user_data = user_resp.json()
            email = user_data.get("email")
            if not email:
                email_resp = await client.get(GITHUB_EMAIL_URL, headers=headers)
                emails = email_resp.json()
                if isinstance(emails, list):
                    primary = next((e for e in emails if e.get("primary")), None)
                    email = primary["email"] if primary else (emails[0]["email"] if emails else None)
            if not email:
                return RedirectResponse(f"{FRONTEND_URL}/pages/login.html?oauth_error=No email returned from GitHub")
        user = _find_user(email=email, profile_pic=user_data.get("avatar_url", ""))
        if not user:
            from urllib.parse import quote
            return RedirectResponse(
                f"{FRONTEND_URL}/pages/login.html?oauth_error="
                f"No account found for {quote(email)}. Please register first."
            )
        return RedirectResponse(_build_login_redirect(user))
    except Exception as e:
        logger.error(f"GitHub OAuth error: {e}")
        return RedirectResponse(f"{FRONTEND_URL}/pages/login.html?oauth_error=OAuth error: {str(e)}")


@router.get("/providers")
def get_oauth_providers():
    return {
        "google": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
        "github": bool(GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET),
    }