from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import auth, jobs, applications, users
from app.routes.upload        import router as upload_router
from app.routes.analytics     import router as analytics_router
from app.routes.chat          import router as chat_router
from app.routes.admin         import router as admin_router
from app.routes.saved_jobs    import router as saved_jobs_router
from app.routes.notifications import router as notifications_router
from app.routes.activity_log  import router as activity_log_router
from app.routes.reactions      import router as reactions_router
from app.routes.public_profile import router as public_profile_router
from app.routes.attachments    import router as attachments_router
from app.routes.websocket_chat import router as ws_router
from app.routes.oauth          import router as oauth_router
from app.routes.dashboard_init  import router as dash_init_router
from app.rate_limit import extract_client_key, get_rate_limiter
from app.middleware.security import security_headers_middleware
import time
import os
import logging
import threading
import requests as _requests

def _keep_alive():
    """Ping self every 14 minutes to prevent Render free-tier spin-down."""
    import time as _time
    _time.sleep(30)  # wait for server to fully start first
    self_url = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
    if not self_url:
        return  # not on Render, skip
    while True:
        try:
            _requests.get(f"{self_url}/health", timeout=10)
            logger.info("[KeepAlive] Pinged self.")
        except Exception as e:
            logger.warning(f"[KeepAlive] Ping failed: {e}")
        _time.sleep(13 * 60)  # 14 minutes

threading.Thread(target=_keep_alive, daemon=True).start()

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("jobtrack")

app = FastAPI(title="JobTrack API", version="2.2.0",
    description="Job application system — Information Management Final Project")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000,"
    "http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,"
    "http://localhost:8080,http://127.0.0.1:8080"
).split(",")

# Strip whitespace from each origin
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

@app.middleware("http")
async def csrf_origin_check(request: Request, call_next):
    if request.method not in CSRF_SAFE_METHODS:
        origin  = request.headers.get("origin", "")
        is_dev  = os.getenv("ENV", "development") == "development"
        if origin and origin not in ALLOWED_ORIGINS:
            logger.warning(f"CSRF block: origin={origin} method={request.method} path={request.url.path}")
            return JSONResponse(status_code=403, content={"detail": "Forbidden: origin not allowed."})
        if not origin and not is_dev:
            return JSONResponse(status_code=403, content={"detail": "Forbidden: origin header required."})
    return await call_next(request)

_limiter = get_rate_limiter()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    key = extract_client_key(request)
    allowed, detail = await _limiter.check(key)
    if not allowed:
        logger.warning(f"Rate limit hit: key={key} path={request.url.path}")
        return JSONResponse(status_code=429, content={"detail": detail})
    return await call_next(request)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start    = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


# Outermost (registered last via insert-at-head): attaches to ALL responses incl. CSR / rate-limit JSON.
@app.middleware("http")
async def security_headers_dispatch(request: Request, call_next):
    return await security_headers_middleware(request, call_next)


# ── Routers ──────────────────────────────────────────────
app.include_router(auth.router,             prefix="/auth",           tags=["Auth"])
app.include_router(jobs.router,             prefix="/jobs",           tags=["Jobs"])
app.include_router(applications.router,     prefix="/applications",   tags=["Applications"])
app.include_router(users.router,            prefix="/users",          tags=["Users"])
app.include_router(upload_router,           prefix="/upload",         tags=["Upload"])
app.include_router(analytics_router,        prefix="/analytics",      tags=["Analytics"])
app.include_router(chat_router,             prefix="/chat",           tags=["Chat"])
app.include_router(admin_router,            prefix="/admin",          tags=["Admin"])
app.include_router(saved_jobs_router,       prefix="/saved-jobs",     tags=["Saved Jobs"])
app.include_router(notifications_router,    prefix="/notifications",  tags=["Notifications"])
app.include_router(activity_log_router,     prefix="/activity-log",   tags=["Activity Log"])
app.include_router(reactions_router,        prefix="/reactions",      tags=["Reactions"])
app.include_router(public_profile_router,   prefix="/profile",        tags=["Public Profile"])
app.include_router(attachments_router,      prefix="/attachments",    tags=["Attachments"])
app.include_router(ws_router,               prefix="/ws",             tags=["WebSocket"])
app.include_router(oauth_router,            prefix="/oauth",          tags=["OAuth"])
app.include_router(dash_init_router,        prefix="/dashboard-init", tags=["Dashboard Init"])

@app.get("/", tags=["Health"])
def root():
    return {"message": "JobTrack API v2.2 running 🚀", "status": "ok"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "timestamp": int(time.time())}