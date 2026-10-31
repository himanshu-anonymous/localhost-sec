"""
Docker Environment Manager.
Compliant with Section 4 of Master Execution Specification.
Manages lifecycle, isolated Docker bridge networks, resource limits, and health checks.
"""

import os
import subprocess
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger("localhost.docker")


class DockerEnvironmentManager:
    """
    Manages the 4 containerized simulation workers and Redis via Docker Compose.
    - Isolated Docker network (`localhost-net`)
    - CPU limit: 1.0 core, Memory limit: 512MB per worker
    - Health checks against /health endpoints
    """

    WORKER_PORTS = {
        "env_a_baseline": 8001,
        "env_b_adaptive": 8002,
        "env_c_hardened": 8003,
        "env_d_experimental": 8004
    }

    def __init__(self, compose_file: str = "docker-compose.yml"):
        self.compose_file = compose_file

    def get_worker_urls(self, host: str = "http://localhost") -> Dict[str, str]:
        return {
            env_id: f"{host}:{port}"
            for env_id, port in self.WORKER_PORTS.items()
        }

    def start_all(self) -> Dict[str, Any]:
        """Runs docker compose up -d."""
        try:
            cmd = ["docker", "compose", "-f", self.compose_file, "up", "-d"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Docker environment workers successfully started.")
            return {"status": "success", "output": res.stdout}
        except Exception as e:
            logger.error(f"Failed to start Docker environments: {e}")
            return {"status": "error", "error": str(e)}

    def stop_all(self) -> Dict[str, Any]:
        """Runs docker compose down."""
        try:
            cmd = ["docker", "compose", "-f", self.compose_file, "down"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Docker environments stopped.")
            return {"status": "success", "output": res.stdout}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_worker_health(self) -> Dict[str, bool]:
        """Queries health status of all 4 workers over HTTP with rapid timeout."""
        health_status = {}
        for env_id, url in self.get_worker_urls().items():
            try:
                with httpx.Client(timeout=0.15) as client:
                    resp = client.get(f"{url}/health")
                    health_status[env_id] = resp.status_code == 200 and resp.json().get("status") == "healthy"
            except Exception:
                health_status[env_id] = False
        return health_status


# Global manager instance
docker_manager = DockerEnvironmentManager()
