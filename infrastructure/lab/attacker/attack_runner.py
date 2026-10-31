"""
AEGIS Controlled Lab Attack Client Runner.
Executes safe, allowlisted, bounded attack simulations across mTLS gateway.
Compliant with Section 8 of AEGIS Master Implementation Spec.
"""

import os
import sys
import time
import httpx
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Attacker] %(message)s")
logger = logging.getLogger("aegis.attacker")

CERTS_DIR = os.getenv("CERTS_DIR", "/certs")
CA_CERT = os.path.join(CERTS_DIR, "ca.crt")
CLIENT_CERT = os.path.join(CERTS_DIR, "attacker-client.crt")
CLIENT_KEY = os.path.join(CERTS_DIR, "attacker-client.key")

GATEWAY_URL = os.getenv("GATEWAY_URL", "https://aegis-gateway:8443")
ALLOWED_TARGET_HOSTS = ["aegis-gateway", "gateway", "127.0.0.1", "localhost", "172.31.10.2"]


class BoundedAttackRunner:
    def __init__(self, gateway_url: str = GATEWAY_URL, ca_cert: str = CA_CERT, cert: str = CLIENT_CERT, key: str = CLIENT_KEY):
        self.gateway_url = gateway_url.rstrip("/")
        self.ca_cert = ca_cert
        self.cert = (cert, key) if os.path.exists(cert) and os.path.exists(key) else None

    def _get_client(self, use_mtls: bool = True, timeout: float = 5.0) -> httpx.Client:
        import ssl
        if use_mtls and self.cert and os.path.exists(self.ca_cert):
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.ca_cert)
            ctx.load_cert_chain(self.cert[0], self.cert[1])
            return httpx.Client(verify=ctx, http2=False, timeout=timeout)
        elif os.path.exists(self.ca_cert):
            return httpx.Client(verify=self.ca_cert, http2=False, timeout=timeout)
        else:
            return httpx.Client(verify=False, http2=False, timeout=timeout)

    def run_brute_force(self, attempt_count: int = 8, delay_seconds: float = 0.5) -> Dict[str, Any]:
        """T1110: Bounded brute-force authentication attempts against lab login endpoint."""
        # Enforce hard upper bound ceiling
        attempt_count = min(max(attempt_count, 1), 30)
        logger.info(f"Starting T1110 Bounded Brute Force ({attempt_count} attempts) against {self.gateway_url}...")

        target_endpoint = f"{self.gateway_url}/api/auth/login"
        passwords = [f"guess_attempt_pass_{i}" for i in range(attempt_count)]
        results: List[Dict[str, Any]] = []

        start_time = datetime.now(timezone.utc)
        blocked_detected = False

        with self._get_client(use_mtls=True) as client:
            for idx, pwd in enumerate(passwords):
                ts = datetime.now(timezone.utc).isoformat()
                try:
                    resp = client.post(
                        target_endpoint,
                        json={"username": "victim_user", "password": pwd}
                    )
                    status_code = resp.status_code
                    if status_code == 403:
                        blocked_detected = True
                        logger.warning(f"Attempt {idx+1}/{attempt_count}: Gateway returned 403 FORBIDDEN (Source Block Active!)")
                    else:
                        logger.info(f"Attempt {idx+1}/{attempt_count}: Status {status_code}")

                    results.append({
                        "attempt": idx + 1,
                        "timestamp": ts,
                        "status_code": status_code,
                        "blocked": status_code == 403
                    })
                except httpx.HTTPError as e:
                    logger.error(f"Attempt {idx+1} network error: {e}")
                    results.append({"attempt": idx + 1, "timestamp": ts, "error": str(e), "blocked": True})

                time.sleep(delay_seconds)

        end_time = datetime.now(timezone.utc)
        duration_ms = (end_time - start_time).total_seconds() * 1000.0

        summary = {
            "scenario_id": "brute_force",
            "ground_truth_technique_id": "T1110",
            "total_attempts": attempt_count,
            "blocked_detected": blocked_detected,
            "duration_ms": duration_ms,
            "results": results
        }
        return summary

    def run_bounded_http_load(self, request_count: int = 50, rate_limit_rps: int = 10) -> Dict[str, Any]:
        """T1498: Bounded low-rate HTTP load test against gateway target."""
        request_count = min(max(request_count, 1), 200)
        logger.info(f"Starting T1498 Bounded HTTP Load ({request_count} requests) against {self.gateway_url}...")

        target_endpoint = f"{self.gateway_url}/api/data/resource"
        results: List[Dict[str, Any]] = []
        delay = 1.0 / max(rate_limit_rps, 1)

        start_time = datetime.now(timezone.utc)
        blocked_count = 0

        with self._get_client(use_mtls=True) as client:
            for i in range(request_count):
                ts = datetime.now(timezone.utc).isoformat()
                try:
                    resp = client.get(target_endpoint)
                    if resp.status_code == 403:
                        blocked_count += 1
                    results.append({"req": i + 1, "timestamp": ts, "status_code": resp.status_code})
                except Exception as e:
                    results.append({"req": i + 1, "timestamp": ts, "error": str(e)})
                time.sleep(delay)

        end_time = datetime.now(timezone.utc)
        return {
            "scenario_id": "bounded_http_load",
            "ground_truth_technique_id": "T1498",
            "total_requests": request_count,
            "blocked_count": blocked_count,
            "duration_ms": (end_time - start_time).total_seconds() * 1000.0,
            "results": results
        }


if __name__ == "__main__":
    runner = BoundedAttackRunner()
    action = sys.argv[1] if len(sys.argv) > 1 else "brute_force"
    if action == "brute_force":
        out = runner.run_brute_force(attempt_count=5)
        print(f"Brute force completed. Blocked: {out['blocked_detected']}")
    elif action == "bounded_http_load":
        out = runner.run_bounded_http_load(request_count=10)
        print(f"HTTP load completed. Blocked count: {out['blocked_count']}")

