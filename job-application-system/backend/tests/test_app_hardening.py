import importlib
import sys
from typing import Dict

from fastapi.testclient import TestClient


def _load_app_with_env(env: Dict[str, str]):
    relevant = [
        "RATE_LIMIT_BACKEND",
        "RATE_LIMIT_GLOBAL_LIMIT",
        "RATE_LIMIT_GLOBAL_WINDOW",
        "REDIS_URL",
        "RATE_LIMIT_REDIS_FALLBACK_TO_MEMORY",
        "SECURITY_HEADERS_ENABLED",
        "CSP_ENABLE",
        "X_FRAME_OPTIONS",
        "TRUST_PROXY",
    ]

    import os

    for key in relevant:
        os.environ.pop(key, None)
    for key, value in env.items():
        os.environ[key] = value

    factory_mod = sys.modules.get("app.rate_limit.factory")
    if factory_mod and hasattr(factory_mod, "_build_limiter"):
        factory_mod._build_limiter.cache_clear()

    if "app.main" in sys.modules:
        del sys.modules["app.main"]
    importlib.invalidate_caches()
    app_main = importlib.import_module("app.main")
    return app_main


def test_security_headers_on_health():
    app_main = _load_app_with_env(
        {
            "RATE_LIMIT_BACKEND": "memory",
            "RATE_LIMIT_GLOBAL_LIMIT": "100",
            "RATE_LIMIT_GLOBAL_WINDOW": "60",
            "SECURITY_HEADERS_ENABLED": "true",
            "CSP_ENABLE": "true",
            "X_FRAME_OPTIONS": "DENY",
        }
    )
    client = TestClient(app_main.app)
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.headers.get("x-frame-options") == "DENY"
    assert "content-security-policy" in resp.headers


def test_rate_limiting_hits_429_after_limit():
    app_main = _load_app_with_env(
        {
            "RATE_LIMIT_BACKEND": "memory",
            "RATE_LIMIT_GLOBAL_LIMIT": "3",
            "RATE_LIMIT_GLOBAL_WINDOW": "60",
            "SECURITY_HEADERS_ENABLED": "true",
        }
    )
    client = TestClient(app_main.app)

    statuses = [client.get("/health").status_code for _ in range(5)]
    assert statuses[:3] == [200, 200, 200]
    assert statuses[3] == 429
    assert statuses[4] == 429


def test_redis_backend_missing_url_falls_back_to_memory_and_stays_healthy():
    app_main = _load_app_with_env(
        {
            "RATE_LIMIT_BACKEND": "redis",
            "REDIS_URL": "",
            "RATE_LIMIT_REDIS_FALLBACK_TO_MEMORY": "true",
            "RATE_LIMIT_GLOBAL_LIMIT": "100",
            "RATE_LIMIT_GLOBAL_WINDOW": "60",
            "SECURITY_HEADERS_ENABLED": "true",
        }
    )
    client = TestClient(app_main.app)
    resp = client.get("/health")

    assert resp.status_code == 200
    assert type(app_main._limiter).__name__ == "MemoryRateLimiter"
