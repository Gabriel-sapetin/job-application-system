from fastapi import APIRouter, HTTPException, Request, Response
from app.models import UserRegister, UserLogin
from app.database import supabase
import bcrypt
import jwt
import time
import os
import secrets
from collections import defaultdict
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr

load_dotenv()

router = APIRouter()

# ── JWT config ──────────────────────────────────────────
SECRET_KEY  = os.getenv("SECRET_KEY", "jobtrack-secret-change-in-production")
ALGORITHM   = "HS256"
TOKEN_TTL   = 60 * 60 * 24 * 7  # 7 days

def create_token(user_id: int, role: str) -> str:
    payload = {
        "sub":  str(user_id),
        "role": role,
        "iat":  int(time.time()),
        "exp":  int(time.time()) + TOKEN_TTL,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")


def get_token_from_request(request: Request) -> str:
    """Read JWT from Authorization header first, then secure auth cookie."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        header_token = auth_header[7:].strip()
        if header_token and header_token.lower() not in ("null", "undefined"):
            return header_token

    cookie_token = (request.cookies.get("access_token") or "").strip()
    if cookie_token and cookie_token.lower() not in ("null", "undefined"):
        return cookie_token

    raise HTTPException(status_code=401, detail="Not authenticated.")

# ── Login rate limiter ───────────────────────────────────
_failed_attempts: dict = defaultdict(list)
MAX_ATTEMPTS   = 5
LOCKOUT_WINDOW = 60 * 5

def check_rate_limit(ip: str):
    now = time.time()
    _failed_attempts[ip] = [t for t in _failed_attempts[ip] if now - t < LOCKOUT_WINDOW]
    if len(_failed_attempts[ip]) >= MAX_ATTEMPTS:
        wait = int(LOCKOUT_WINDOW - (now - _failed_attempts[ip][0]))
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed attempts. Try again in {wait // 60}m {wait % 60}s."
        )

def record_failure(ip: str):
    _failed_attempts[ip].append(time.time())

def clear_failures(ip: str):
    _failed_attempts.pop(ip, None)

# ── In-memory reset token store ──────────────────────────
_reset_tokens: dict = {}
RESET_TTL = 60 * 30  # 30 minutes

# ── Input validation ─────────────────────────────────────
def validate_name(name: str):
    name = name.strip()
    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters.")
    if len(name) > 80:
        raise HTTPException(status_code=400, detail="Name must be 80 characters or fewer.")
    return name

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    if len(password) > 128:
        raise HTTPException(status_code=400, detail="Password too long.")

# ── Pydantic models for password reset ───────────────────
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# ── Routes ───────────────────────────────────────────────

@router.post("/register")
def register(user: UserRegister):
    name = validate_name(user.name)
    validate_password(user.password)

    existing = supabase.table("users").select("id").eq("email", user.email.lower()).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt(rounds=12)).decode()

    result = supabase.table("users").insert({
        "name":     name,
        "email":    user.email.lower(),
        "password": hashed,
        "role":     user.role,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create account.")

    return {"message": "Account created successfully."}


@router.post("/login")
def login(credentials: UserLogin, request: Request, response: Response):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    result = supabase.table("users").select("*").eq("email", credentials.email.lower()).execute()

    if not result.data:
        record_failure(client_ip)
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    db_user = result.data[0]

    if not bcrypt.checkpw(credentials.password.encode(), db_user["password"].encode()):
        record_failure(client_ip)
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    clear_failures(client_ip)
    token = create_token(db_user["id"], db_user["role"])

    # Use secure=False in development (http), secure=True in production (https)
    is_production = os.getenv("ENV", "development") == "production"

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=TOKEN_TTL,
        path="/",
    )

    return {
        "access_token": token,
        "user": {
            "id":          db_user["id"],
            "name":        db_user["name"],
            "email":       db_user["email"],
            "role":        db_user["role"],
            "profile_pic": db_user.get("profile_pic"),
        },
    }


@router.get("/me")
def get_current_user(request: Request):
    token = get_token_from_request(request)
    payload = verify_token(token)
    user_id = int(payload["sub"])
    result = supabase.table("users").select(
        "id, name, email, role, profile_pic, about_me, instagram, facebook"
    ).eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")
    return result.data[0]


# ── Password Reset ────────────────────────────────────────

@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    """Generate a reset token and email it. Always returns 200 to prevent email enumeration."""
    result = supabase.table("users").select("id, name, email").eq("email", body.email.lower()).execute()

    if result.data:
        user_row = result.data[0]
        token = secrets.token_urlsafe(32)
        _reset_tokens[token] = {
            "user_id": user_row["id"],
            "expires": time.time() + RESET_TTL,
        }

        base_url   = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500/job-application-system/frontend")
        reset_link = f"{base_url}/pages/reset-password.html?token={token}"

        print(f"\n{'='*60}")
        print(f"[Auth] Password reset requested for: {body.email}")
        print(f"[Auth] Reset link: {reset_link}")
        print(f"{'='*60}\n")

        mail_user = os.getenv("MAIL_USERNAME", "")
        mail_pass = os.getenv("MAIL_PASSWORD", "")
        mail_from = os.getenv("MAIL_FROM", mail_user)

        if mail_user and mail_pass and mail_pass not in ("your_app_password", "your_gmail_app_password", ""):
            try:
                from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

                config = ConnectionConfig(
                    MAIL_USERNAME   = mail_user,
                    MAIL_PASSWORD   = mail_pass,
                    MAIL_FROM       = mail_from,
                    MAIL_PORT       = int(os.getenv("MAIL_PORT", "587")),
                    MAIL_SERVER     = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
                    MAIL_STARTTLS   = True,
                    MAIL_SSL_TLS    = False,
                    USE_CREDENTIALS = True,
                    VALIDATE_CERTS  = True,
                )

                html = f"""
                <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#0a0a0a;color:#f2f2f2;border-radius:12px;overflow:hidden;">
                  <div style="background:#111;padding:24px;border-bottom:1px solid #222;">
                    <span style="font-size:18px;font-weight:700;">Job<span style="color:#7fff00;">Track</span></span>
                  </div>
                  <div style="padding:32px;">
                    <h2 style="margin:0 0 12px;">Reset Your Password</h2>
                    <p style="color:#a0a0a0;line-height:1.7;">
                      Hi {user_row['name']}, click the button below to reset your password.
                      This link expires in <strong style="color:#f2f2f2;">30 minutes</strong>.
                    </p>
                    <a href="{reset_link}"
                       style="display:inline-block;margin-top:20px;padding:12px 24px;
                              background:#7fff00;color:#000;border-radius:8px;
                              text-decoration:none;font-weight:700;">
                      Reset Password →
                    </a>
                    <p style="color:#555;font-size:12px;margin-top:20px;">
                      If you didn't request this, you can safely ignore this email.
                    </p>
                  </div>
                  <div style="padding:16px 32px;border-top:1px solid #222;font-size:11px;color:#555;">
                    JobTrack — sent from {mail_from}
                  </div>
                </div>
                """

                message = MessageSchema(
                    subject    = "Reset your JobTrack password",
                    recipients = [body.email],
                    body       = html,
                    subtype    = MessageType.html,
                )
                fm = FastMail(config)
                await fm.send_message(message)
                print(f"[Auth] ✓ Reset email sent to {body.email}")

            except Exception as e:
                import traceback
                print(f"[Auth] ✗ Email send failed: {type(e).__name__}: {e}")
                print(traceback.format_exc())
        else:
            print(f"[Auth] Mail not configured — skipping email send. Use the link above.")

    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest):
    """Validate reset token and update password."""
    entry = _reset_tokens.get(body.token)
    if not entry:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    if time.time() > entry["expires"]:
        del _reset_tokens[body.token]
        raise HTTPException(status_code=400, detail="Reset token has expired. Please request a new one.")

    validate_password(body.new_password)
    hashed = bcrypt.hashpw(body.new_password.encode(), bcrypt.gensalt(rounds=12)).decode()

    supabase.table("users").update({"password": hashed}).eq("id", entry["user_id"]).execute()

    del _reset_tokens[body.token]

    return {"message": "Password updated successfully. You can now log in."}


@router.get("/reset-password/verify")
def verify_reset_token(token: str):
    """Check if a reset token is still valid (for frontend page load)."""
    entry = _reset_tokens.get(token)
    if not entry or time.time() > entry["expires"]:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    return {"valid": True}