from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import auth, jobs, applications, users
from app.routes.upload    import router as upload_router
from app.routes.analytics import router as analytics_router
from collections import defaultdict
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("jobtrack")

app = FastAPI(title="JobTrack API", version="2.1.0",
    description="Job application system — Information Management Final Project")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ── Global rate limiter ──────────────────────────────────
_request_log: dict = defaultdict(list)
GLOBAL_LIMIT  = 100
GLOBAL_WINDOW = 60

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip  = request.client.host if request.client else "unknown"
    now = time.time()
    _request_log[ip] = [t for t in _request_log[ip] if now - t < GLOBAL_WINDOW]
    if len(_request_log[ip]) >= GLOBAL_LIMIT:
        logger.warning(f"Rate limit hit: {ip} on {request.url.path}")
        return JSONResponse(status_code=429,
            content={"detail": f"Too many requests. Limit is {GLOBAL_LIMIT} per {GLOBAL_WINDOW}s."})
    _request_log[ip].append(now)
    return await call_next(request)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start    = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response

# ── Routers ──────────────────────────────────────────────
app.include_router(auth.router,         prefix="/auth",         tags=["Auth"])
app.include_router(jobs.router,         prefix="/jobs",         tags=["Jobs"])
app.include_router(applications.router, prefix="/applications", tags=["Applications"])
app.include_router(users.router,        prefix="/users",        tags=["Users"])
app.include_router(upload_router,       prefix="/upload",       tags=["Upload"])       # NEW
app.include_router(analytics_router,    prefix="/analytics",    tags=["Analytics"])    # NEW

@app.get("/", tags=["Health"])
def root():
    return {"message": "JobTrack API v2.1 running 🚀", "status": "ok"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "timestamp": int(time.time())}
