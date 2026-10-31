"""
Central Training Service & Background Orchestrator.
Compliant with Section 6 & 10 of Master Execution Specification.
Executes the Shared PPO training loop across the 4 environments without blocking FastAPI.
"""

import os
import time
import threading
import logging
from typing import Dict, Any, Optional, List
import numpy as np

from backend.app.environments.vector_manager import ParallelEnvironmentManager
from backend.app.environments.remote_worker_adapter import RemoteWorkerEnv
from backend.app.rl.ppo_agent import PPOAgent
from backend.app.telemetry.redis_broker import broker

logger = logging.getLogger("localhost.trainer")


class CentralTrainingService:
    """
    Central PPO Trainer coordinating 4 isolated simulation workers.
    Runs asynchronously in a background thread.
    """

    def __init__(self):
        self.agent = PPOAgent(obs_dim=14, num_actions=8, action_levels=3)
        self.manager: Optional[ParallelEnvironmentManager] = None
        self.remote_workers: Dict[str, RemoteWorkerEnv] = {}

        self.is_running = False
        self.is_paused = False
        self.current_step = 0
        self.current_episode = 0
        self.total_timesteps = 0
        self.active_experiment_id = "exp-default"
        self.worker_mode = "in_process"  # "in_process" or "docker_remote"
        
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Metrics history
        self.metrics_history: List[Dict[str, Any]] = []

    def start_training(
        self,
        experiment_id: str = "exp-001",
        scenario_name: str = "black_sky",
        max_episodes: int = 5,
        steps_per_episode: int = 100,
        worker_urls: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Starts asynchronous training loop in background."""
        with self._lock:
            if self.is_running:
                return {"status": "already_running", "experiment_id": self.active_experiment_id}

            self.active_experiment_id = experiment_id
            self.is_running = True
            self.is_paused = False
            self._stop_event.clear()

            if worker_urls and len(worker_urls) == 4:
                # Docker Remote Workers mode
                self.worker_mode = "docker_remote"
                self.remote_workers = {
                    env_id: RemoteWorkerEnv(url, env_id)
                    for env_id, url in worker_urls.items()
                }
            else:
                # In-process Parallel Manager mode
                self.worker_mode = "in_process"
                self.manager = ParallelEnvironmentManager(
                    scenario_name=scenario_name,
                    max_steps=steps_per_episode
                )

            self._thread = threading.Thread(
                target=self._training_loop,
                args=(max_episodes, steps_per_episode),
                daemon=True
            )
            self._thread.start()

            return {
                "status": "started",
                "experiment_id": self.active_experiment_id,
                "worker_mode": self.worker_mode,
                "max_episodes": max_episodes
            }

    def pause_training(self) -> Dict[str, Any]:
        with self._lock:
            self.is_paused = True
            return {"status": "paused", "experiment_id": self.active_experiment_id}

    def resume_training(self) -> Dict[str, Any]:
        with self._lock:
            self.is_paused = False
            return {"status": "resumed", "experiment_id": self.active_experiment_id}

    def stop_training(self) -> Dict[str, Any]:
        with self._lock:
            self._stop_event.set()
            self.is_running = False
            self.is_paused = False
            return {"status": "stopped", "experiment_id": self.active_experiment_id}

    def get_status(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.active_experiment_id,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "worker_mode": self.worker_mode,
            "current_episode": self.current_episode,
            "current_step": self.current_step,
            "total_timesteps": self.total_timesteps,
            "checkpoint_available": os.path.exists("models/checkpoints/m1_ppo_policy.pt")
        }

    def get_metrics(self) -> List[Dict[str, Any]]:
        return self.metrics_history

    def _training_loop(self, max_episodes: int, steps_per_episode: int):
        logger.info(f"Central PPO training loop started: {max_episodes} episodes, mode={self.worker_mode}")

        for ep in range(1, max_episodes + 1):
            if self._stop_event.is_set():
                break

            self.current_episode = ep
            self.current_step = 0

            # Reset environments
            if self.worker_mode == "docker_remote":
                obs_dict = {}
                for env_id, w in self.remote_workers.items():
                    obs, _ = w.reset()
                    obs_dict[env_id] = obs
            else:
                assert self.manager is not None
                obs_dict, _ = self.manager.reset()

            episode_rewards = {env_id: 0.0 for env_id in obs_dict}

            for step in range(1, steps_per_episode + 1):
                if self._stop_event.is_set():
                    break

                # Handle pause
                while self.is_paused and not self._stop_event.is_set():
                    time.sleep(0.1)

                self.current_step = step
                self.total_timesteps += 1

                actions_dict = {}
                transition_data = {}

                # 1. PPO Policy Inference across all workers
                for env_id, obs in obs_dict.items():
                    action, log_prob, val = self.agent.select_action(obs)
                    actions_dict[env_id] = action
                    transition_data[env_id] = (obs, action, log_prob, val)

                # 2. Step Environments
                if self.worker_mode == "docker_remote":
                    next_obs_dict = {}
                    reward_dict = {}
                    done_dict = {}
                    info_dict = {}
                    for env_id, w in self.remote_workers.items():
                        o, r, term, trunc, inf = w.step(actions_dict[env_id])
                        next_obs_dict[env_id] = o
                        reward_dict[env_id] = r
                        done_dict[env_id] = term or trunc
                        info_dict[env_id] = inf
                else:
                    assert self.manager is not None
                    next_obs_dict, reward_dict, done_dict, info_dict = self.manager.step(actions_dict)

                # 3. Record Rollout Transitions for adaptive environments
                for env_id in ["env_b_adaptive", "env_d_experimental"]:
                    if env_id in transition_data:
                        obs, act, lp, val = transition_data[env_id]
                        r = reward_dict[env_id]
                        d = done_dict[env_id]
                        self.agent.record_transition(obs, act, lp, r, d, val)

                for env_id, r in reward_dict.items():
                    episode_rewards[env_id] += r

                obs_dict = next_obs_dict

                # 4. Broadcast Telemetry Event to Redis & WebSockets
                telemetry_payload = {
                    "event_type": "environment.telemetry",
                    "experiment_id": self.active_experiment_id,
                    "episode": ep,
                    "step": step,
                    "timestamp": time.time(),
                    "workers": {
                        env_id: {
                            "reward": reward_dict[env_id],
                            "metrics": info_dict[env_id]["metrics"],
                            "enforced_policy": info_dict[env_id]["enforced_policy"]
                        }
                        for env_id in obs_dict
                    }
                }
                broker.publish_event("environment.telemetry", telemetry_payload)

                # Regulate rate (10-20Hz)
                time.sleep(0.02)

            # End of Episode: PPO Policy Update
            ppo_stats = self.agent.update(ppo_epochs=2, batch_size=32)

            # Record Episode Metrics
            metric_entry = {
                "episode": ep,
                "timestamp": time.time(),
                "rewards": episode_rewards,
                "ppo_loss": ppo_stats.get("policy_loss", 0.0),
                "value_loss": ppo_stats.get("value_loss", 0.0),
                "entropy": ppo_stats.get("mean_entropy", 0.0)
            }
            self.metrics_history.append(metric_entry)

            # Save checkpoint
            ckpt_path = "models/checkpoints/m1_ppo_policy.pt"
            self.agent.save_checkpoint(ckpt_path)

            # Publish PPO Metrics Event
            broker.publish_event("rl.training_metrics", {
                "event_type": "rl.training_metrics",
                "experiment_id": self.active_experiment_id,
                "episode": ep,
                "metrics": metric_entry
            })

            logger.info(f"Episode {ep}/{max_episodes} complete. PPO Loss: {ppo_stats.get('policy_loss', 0.0):.4f}")

        self.is_running = False
        broker.publish_event("experiment.completed", {
            "event_type": "experiment.completed",
            "experiment_id": self.active_experiment_id,
            "total_episodes": max_episodes
        })
        logger.info("Central training process finished.")


# Global Singleton Service
trainer_service = CentralTrainingService()
