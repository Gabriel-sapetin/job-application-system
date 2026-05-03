import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def main() -> int:
    backend_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_root))

    # Force a tiny memory limit for deterministic smoke testing.
    os.environ["RATE_LIMIT_BACKEND"] = "memory"
    os.environ["RATE_LIMIT_GLOBAL_LIMIT"] = "3"
    os.environ["RATE_LIMIT_GLOBAL_WINDOW"] = "60"

    from app.main import app  # Import only after env vars are set.

    client = TestClient(app)

    statuses = []
    for i in range(1, 6):
        resp = client.get("/health")
        statuses.append(resp.status_code)
        print(f"request {i}: status={resp.status_code}")

    if 429 not in statuses:
        print("FAIL: expected at least one 429 Too Many Requests.")
        return 1

    first_429 = statuses.index(429) + 1
    print(f"PASS: got 429 on request #{first_429}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
