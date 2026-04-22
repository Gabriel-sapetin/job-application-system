from fastapi import APIRouter, HTTPException, Request
from app.models import UserRegister, UserLogin
from app.database import supabase
import bcrypt
import jwt
import time
from collections import defaultdict

router = APIRouter()

# ── JWT config ──────────────────────────────────────────
SECRET_KEY  = "jobtrack-secret-change-in-production"   # move to .env in production
ALGORITHM   = "HS256"
TOKEN_TTL   = 60 * 60 * 24 * 7  # 7 days in seconds

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

# ── Login rate limiter ───────────────────────────────────
# Tracks failed attempts per IP: {ip: [timestamp, ...]}
_failed_attempts: dict = defaultdict(list)
MAX_ATTEMPTS   = 5
LOCKOUT_WINDOW = 60 * 5  # 5 minutes

def check_rate_limit(ip: str):
    now = time.time()
    # Clear old attempts outside the window
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

# ── Input validation helpers ─────────────────────────────
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

# ── Routes ───────────────────────────────────────────────

@router.post("/register")
def register(user: UserRegister):
    # Validate inputs
    name = validate_name(user.name)
    validate_password(user.password)

    # Check duplicate email
    existing = supabase.table("users").select("id").eq("email", user.email.lower()).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Hash password with bcrypt (cost factor 12)
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
def login(credentials: UserLogin, request: Request):
    # Get client IP for rate limiting
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

    # Login successful — clear failure history, issue JWT
    clear_failures(client_ip)
    token = create_token(db_user["id"], db_user["role"])

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":          db_user["id"],
            "name":        db_user["name"],
            "email":       db_user["email"],
            "role":        db_user["role"],
            "profile_pic": db_user.get("profile_pic"),
        }
    }


@router.get("/me")
def get_current_user(request: Request):
    """Validate token and return current user. Useful for session restore."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    token = auth_header[7:]
    payload = verify_token(token)
    user_id = int(payload["sub"])
    result = supabase.table("users").select(
        "id, name, email, role, profile_pic, about_me, instagram, facebook"
    ).eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")
    return result.data[0]