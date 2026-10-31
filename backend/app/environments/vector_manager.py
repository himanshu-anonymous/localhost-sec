"""
Vectorized Multi-Environment Manager.
Coordinates the 4 parallel isolated environments (Env-A, Env-B, Env-C, Env-D).
Compliant with Section 4.1 & 6.1 of Formal Specification v1.0.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np

from backend.app.environments.network_defense_env import NetworkDefenseEnv


class ParallelEnvironmentManager:
    """
    Manages 4 synchronous, isolated simulation environments.
    - Env A: Baseline (Fixed permissive static rules)
    - Env B: Adaptive (DDPS active, PPO-controlled)
    - Env C: Hardened (Fixed strict zero-trust rules)
    - Env D: Experimental (Alternative scenario / experimental RL policy)
    """

    ENV_IDS = ["env_a_baseline", "env_b_adaptive", "env_c_hardened", "env_d_experimental"]

    def __init__(
        self,
        scenario_name: str = "black_sky",
        max_steps: int = 100,
        base_seed: Optional[int] = 42
    ):
        self.scenario_name = scenario_name
        self.max_steps = max_steps
        self.base_seed = base_seed

        # Initialize the 4 environments with distinct profiles & independent seeds
        self.environments: Dict[str, NetworkDefenseEnv] = {
            "env_a_baseline": NetworkDefenseEnv(
                environment_id="env_a_baseline",
                scenario_name=scenario_name,
                fixed_policy_profile="baseline",
                max_steps=max_steps,
                seed=(base_seed + 1) if base_seed is not None else None
            ),
            "env_b_adaptive": NetworkDefenseEnv(
                environment_id="env_b_adaptive",
                scenario_name=scenario_name,
                fixed_policy_profile=None,  # RL Agent controlled
                max_steps=max_steps,
                seed=(base_seed + 2) if base_seed is not None else None
            ),
            "env_c_hardened": NetworkDefenseEnv(
                environment_id="env_c_hardened",
                scenario_name=scenario_name,
                fixed_policy_profile="hardened",
                max_steps=max_steps,
                seed=(base_seed + 3) if base_seed is not None else None
            ),
            "env_d_experimental": NetworkDefenseEnv(
                environment_id="env_d_experimental",
                scenario_name=scenario_name,
                fixed_policy_profile=None,  # RL Agent controlled
                max_steps=max_steps,
                seed=(base_seed + 4) if base_seed is not None else None
            )
        }

    def reset(self) -> Tuple[Dict[str, np.ndarray], Dict[str, Dict[str, Any]]]:
        """Resets all 4 environments independently."""
        obs_dict = {}
        info_dict = {}
        for env_id, env in self.environments.items():
            obs, info = env.reset()
            obs_dict[env_id] = obs
            info_dict[env_id] = info
        return obs_dict, info_dict

    def step(
        self,
        actions_dict: Dict[str, Any]
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, float], Dict[str, bool], Dict[str, Dict[str, Any]]]:
        """
        Advances all 4 environments simultaneously by one simulation tick.
        For fixed baseline/hardened environments, actions are overridden by their profile.
        """
        obs_dict = {}
        reward_dict = {}
        done_dict = {}
        info_dict = {}

        for env_id, env in self.environments.items():
            action = actions_dict.get(env_id, [0] * 8)
            obs, reward, terminated, truncated, info = env.step(action)
            obs_dict[env_id] = obs
            reward_dict[env_id] = reward
            done_dict[env_id] = terminated or truncated
            info_dict[env_id] = info

        return obs_dict, reward_dict, done_dict, info_dict

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Retrieves real-time comparative benchmark metrics across all 4 environments."""
        summary = {}
        for env_id, env in self.environments.items():
            info = env._get_info()
            summary[env_id] = info["metrics"]
        return summary
