"""
Shared-Policy Proximal Policy Optimization (PPO) Agent.
Compliant with Section 6 of Formal Specification v1.0.
Supports 8-dimensional MultiDiscrete action space and 14-dimensional observation space.
"""

import os
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical


class ActorCriticNetwork(nn.Module):
    """
    Shared Actor-Critic Neural Network for MultiDiscrete actions.
    Observation: R^14
    Actions: 8 heads, each with 3 logits (0=Baseline, 1=Moderate, 2=Strict)
    """

    def __init__(self, obs_dim: int = 14, num_actions: int = 8, action_levels: int = 3):
        super().__init__()
        self.obs_dim = obs_dim
        self.num_actions = num_actions
        self.action_levels = action_levels

        # Shared feature extractor
        self.shared_net = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh()
        )

        # Critic head: V(s) in R
        self.critic_head = nn.Linear(64, 1)

        # Actor heads: 8 discrete categorical heads
        self.actor_heads = nn.ModuleList([
            nn.Linear(64, action_levels) for _ in range(num_actions)
        ])

    def forward(self, x: torch.Tensor) -> Tuple[List[torch.Tensor], torch.Tensor]:
        features = self.shared_net(x)
        value = self.critic_head(features)
        action_logits = [head(features) for head in self.actor_heads]
        return action_logits, value


class PPOAgent:
    """
    Proximal Policy Optimization Agent.
    Interacts with parallel isolated network environments simultaneously.
    """

    def __init__(
        self,
        obs_dim: int = 14,
        num_actions: int = 8,
        action_levels: int = 3,
        lr: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_epsilon: float = 0.2,
        value_coef: float = 0.5,
        entropy_coef: float = 0.01,
        device: Optional[str] = "cpu"
    ):
        self.device = device or "cpu"
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef

        self.policy = ActorCriticNetwork(obs_dim, num_actions, action_levels).to(self.device)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)

        # Rollout storage
        self.reset_rollout()

    def reset_rollout(self):
        self.states: List[torch.Tensor] = []
        self.actions: List[torch.Tensor] = []
        self.log_probs: List[torch.Tensor] = []
        self.rewards: List[float] = []
        self.dones: List[bool] = []
        self.values: List[torch.Tensor] = []

    def select_action(self, state: np.ndarray, deterministic: bool = False) -> Tuple[List[int], float, float]:
        """
        Samples an action given state S_t.
        Returns: (action_list, log_prob_sum, value_estimate)
        """
        state_t = torch.as_tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            action_logits, value = self.policy(state_t)
            actions = []
            log_prob_sum = 0.0
            for logits in action_logits:
                dist = Categorical(logits=logits)
                if deterministic:
                    a = torch.argmax(logits, dim=-1)
                else:
                    a = dist.sample()
                actions.append(int(a.item()))
                log_prob_sum += float(dist.log_prob(a).item())

        return actions, log_prob_sum, float(value.item())

    def record_transition(
        self,
        state: np.ndarray,
        action: List[int],
        log_prob: float,
        reward: float,
        done: bool,
        value: float
    ):
        self.states.append(torch.as_tensor(state, dtype=torch.float32))
        self.actions.append(torch.as_tensor(action, dtype=torch.int64))
        self.log_probs.append(torch.as_tensor(log_prob, dtype=torch.float32))
        self.rewards.append(float(reward))
        self.dones.append(bool(done))
        self.values.append(torch.as_tensor(value, dtype=torch.float32))

    def update(self, next_value: float = 0.0, ppo_epochs: int = 4, batch_size: int = 32) -> Dict[str, float]:
        """Performs PPO clipped policy and value function update."""
        if len(self.states) == 0:
            return {}

        states = torch.stack(self.states).to(self.device)
        actions = torch.stack(self.actions).to(self.device)
        old_log_probs = torch.stack(self.log_probs).to(self.device)
        values = torch.stack(self.values).to(self.device)

        # Generalized Advantage Estimation (GAE)
        rewards = self.rewards
        dones = self.dones
        advantages = []
        gae = 0.0
        val_next = next_value
        for t in reversed(range(len(rewards))):
            non_terminal = 1.0 - float(dones[t])
            delta = rewards[t] + self.gamma * val_next * non_terminal - values[t].item()
            gae = delta + self.gamma * self.gae_lambda * non_terminal * gae
            advantages.insert(0, gae)
            val_next = values[t].item()

        advantages = torch.tensor(advantages, dtype=torch.float32, device=self.device)
        returns = advantages + values
        # Normalize advantages
        if len(advantages) > 1 and advantages.std() > 1e-8:
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        total_policy_loss = 0.0
        total_value_loss = 0.0
        total_entropy = 0.0
        num_updates = 0

        num_samples = len(states)
        for _ in range(ppo_epochs):
            indices = np.random.permutation(num_samples)
            for start in range(0, num_samples, batch_size):
                end = min(start + batch_size, num_samples)
                batch_idx = indices[start:end]

                b_states = states[batch_idx]
                b_actions = actions[batch_idx]
                b_old_log_probs = old_log_probs[batch_idx]
                b_advantages = advantages[batch_idx]
                b_returns = returns[batch_idx]

                action_logits, b_values = self.policy(b_states)
                b_values = b_values.squeeze(-1)

                # Compute new log_probs and entropy across all 8 heads
                b_new_log_probs = torch.zeros(len(batch_idx), device=self.device)
                entropy_sum = torch.zeros(len(batch_idx), device=self.device)
                for h_idx, logits in enumerate(action_logits):
                    dist = Categorical(logits=logits)
                    a_head = b_actions[:, h_idx]
                    b_new_log_probs += dist.log_prob(a_head)
                    entropy_sum += dist.entropy()

                # Ratio
                ratios = torch.exp(b_new_log_probs - b_old_log_probs)

                # Clipped surrogate loss
                surr1 = ratios * b_advantages
                surr2 = torch.clamp(ratios, 1.0 - self.clip_epsilon, 1.0 + self.clip_epsilon) * b_advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                # Value loss
                value_loss = 0.5 * ((b_values - b_returns) ** 2).mean()

                # Entropy loss
                entropy_loss = -self.entropy_coef * entropy_sum.mean()

                total_loss = policy_loss + self.value_coef * value_loss + entropy_loss

                self.optimizer.zero_grad()
                total_loss.backward()
                nn.utils.clip_grad_norm_(self.policy.parameters(), max_norm=0.5)
                self.optimizer.step()

                total_policy_loss += float(policy_loss.item())
                total_value_loss += float(value_loss.item())
                total_entropy += float(entropy_sum.mean().item())
                num_updates += 1

        self.reset_rollout()
        return {
            "policy_loss": total_policy_loss / max(1, num_updates),
            "value_loss": total_value_loss / max(1, num_updates),
            "mean_entropy": total_entropy / max(1, num_updates),
        }

    def save_checkpoint(self, filepath: str):
        """Saves policy checkpoint to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save({
            "policy_state_dict": self.policy.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "hyperparameters": {
                "obs_dim": self.policy.obs_dim,
                "num_actions": self.policy.num_actions,
                "action_levels": self.policy.action_levels,
                "gamma": self.gamma,
                "clip_epsilon": self.clip_epsilon,
            }
        }, filepath)

    def load_checkpoint(self, filepath: str):
        """Loads policy checkpoint from disk."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.policy.load_state_dict(checkpoint["policy_state_dict"])
        if "optimizer_state_dict" in checkpoint:
            self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.policy.eval()
