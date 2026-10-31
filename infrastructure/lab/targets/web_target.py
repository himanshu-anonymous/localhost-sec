"""
AEGIS Protected Target Web Application.
Runs in isolated aegis_target network behind HAProxy gateway.
Logs all requests and authentication events with real client IP (extracted from X-Forwarded-For).
Compliant with Section 6 & 9 of AEGIS Master Implementation Spec.
"""

import os
import json
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel

LOG_DIR = os.getenv("LOG_DIR", "/var/log/aegis")
LOG_FILE = os.path.join(LOG_DIR, "target_auth.log")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [TargetWeb] %(message)s")
logger = logging.getLogger("aegis.target_web")

app = FastAPI(title="AEGIS Protected Web Target", version="1.0.0")


class LoginRequest(BaseModel):
    username: str
    password: str


def append_security_log(event: dict):
    line = json.dumps(event) + "\n"
    logger.info(f"SECURITY_EVENT: {line.strip()}")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        logger.warning(f"Could not append to {LOG_FILE}: {e}")


def get_verified_client_ip(request: Request) -> str:
    # Gateway strips untrusted headers and sets X-Forwarded-For to %[src]
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@app.get("/healthz")
def healthcheck():
    return {"status": "healthy", "service": "target-web"}


@app.post("/api/auth/login")
def login(req: LoginRequest, request: Request):
    client_ip = get_verified_client_ip(request)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Valid test credential
    if req.username == "secops_admin" and req.password == "AEGIS-Hardened-Pass-2026":
        event = {
            "timestamp": now_iso,
            "source_type": "target_app",
            "source_name": "target-web",
            "event_type": "auth_success",
            "username": req.username,
            "source_ip": client_ip,
            "destination_ip": "172.31.20.10",
            "status_code": 200,
            "severity": "info"
        }
        append_security_log(event)
        return {"status": "authenticated", "token": "aegis-session-token-valid"}

    # Failed login attempt (e.g. T1110 brute force)
    event = {
        "timestamp": now_iso,
        "source_type": "target_app",
        "source_name": "target-web",
        "event_type": "auth_failure",
        "username": req.username,
        "source_ip": client_ip,
        "destination_ip": "172.31.20.10",
        "status_code": 401,
        "severity": "warning"
    }
    append_security_log(event)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")


@app.get("/api/data/resource")
def get_resource(request: Request):
    client_ip = get_verified_client_ip(request)
    now_iso = datetime.now(timezone.utc).isoformat()
    event = {
        "timestamp": now_iso,
        "source_type": "target_app",
        "source_name": "target-web",
        "event_type": "http_request",
        "source_ip": client_ip,
        "destination_ip": "172.31.20.10",
        "path": "/api/data/resource",
        "status_code": 200,
        "severity": "info"
    }
    append_security_log(event)
    return {
        "resource": "Confidential Research Telemetry",
        "classification": "PROTECTED",
        "served_to": client_ip
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_target:app", host="0.0.0.0", port=8080, reload=False)

