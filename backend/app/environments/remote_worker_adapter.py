"""
Remote Worker Environment Adapter (Domain A & B Hybrid Bridge).
Compliant with Section 5 & 6 of Master Execution Specification.
Provides a Gymnasium-compatible client interface over HTTP to containerized simulation workers.
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import httpx


class RemoteWorkerEnv(gym.Env):
    """
    Gymnasium-compatible client wrapper that communicates with a Docker worker
    running `backend.app.worker_server` over HTTP/REST.
    """

    metadata = {"render_modes": ["human"], "version": "1.0.0"}

    def __init__(
        self,
        worker_url: str,
        environment_id: str,
        timeout_seconds: float = 5.0
    ):
        super().__init__()
        self.worker_url = worker_url.rstrip("/")
        self.environment_id = environment_id
        self.timeout = timeout_seconds

        # Synchronize observation & action spaces
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(14,),
            dtype=np.float32
        )
        self.action_space = spaces.MultiDiscrete([3, 3, 3, 3, 3, 3, 3, 3])

        self.client = httpx.Client(base_url=self.worker_url, timeout=self.timeout)
        self.last_observation: Optional[np.ndarray] = None

    def health_check(self) -> Dict[str, Any]:
        """Queries container worker /health endpoint."""
        resp = self.client.get("/health")
        resp.raise_for_status()
        return resp.json()

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        payload = {"seed": seed} if seed is not None else {}
        resp = self.client.post("/reset", json=payload)
        resp.raise_for_status()
        data = resp.json()
        
        obs = np.array(data["observation"], dtype=np.float32)
        self.last_observation = obs
        return obs, data["info"]

    def step(self, action: Any) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if isinstance(action, np.ndarray):
            act_list = [int(x) for x in action.tolist()]
        elif isinstance(action, (list, tuple)):
            act_list = [int(x) for x in action]
        else:
            act_list = [0] * 8

        resp = self.client.post("/step", json={"action": act_list})
        resp.raise_for_status()
        data = resp.json()

        obs = np.array(data["observation"], dtype=np.float32)
        self.last_observation = obs
        return (
            obs,
            float(data["reward"]),
            bool(data["terminated"]),
            bool(data["truncated"]),
            data["info"]
        )

    def get_status(self) -> Dict[str, Any]:
        resp = self.client.get("/status")
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self.client.close()
