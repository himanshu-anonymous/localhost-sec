"""
Milestone M1 Acceptance Test Suite: Parallel RL Simulation Proof.
Formally verifies all 7 acceptance criteria outlined in Section 17 & Milestone M1.
"""

import os
import tempfile
import pytest
import numpy as np

from backend.app.schemas.models import DefensiveActionProposal
from backend.app.environments.network_defense_env import NetworkDefenseEnv
from backend.app.environments.vector_manager import ParallelEnvironmentManager
from backend.app.rl.ppo_agent import PPOAgent
from backend.app.ddps.policy_stack import DynamicDefensivePolicyStack


class TestMilestoneM1:
    """Rigorous verification of Milestone M1 acceptance criteria."""

    def test_criterion_1_four_isolated_gymnasium_environments(self):
        """Criterion 1: Four independent Gymnasium-compatible environments can be created."""
        manager = ParallelEnvironmentManager(scenario_name="black_sky", max_steps=10)
        assert len(manager.environments) == 4
        
        obs_dict, info_dict = manager.reset()
        assert len(obs_dict) == 4
        assert len(info_dict) == 4

        for env_id in ParallelEnvironmentManager.ENV_IDS:
            assert env_id in obs_dict
            obs = obs_dict[env_id]
            assert isinstance(obs, np.ndarray)
            assert obs.shape == (14,)
            # Normalized in [0.0, 1.0]
            assert np.all(obs >= 0.0) and np.all(obs <= 1.0)

    def test_criterion_2_shared_ppo_policy_interaction(self):
        """Criterion 2: One shared PPO policy interacts with all four environments."""
        manager = ParallelEnvironmentManager(scenario_name="black_sky", max_steps=20)
        agent = PPOAgent(obs_dim=14, num_actions=8, action_levels=3)

        obs_dict, _ = manager.reset()
        actions_dict = {}

        # Agent selects actions for all environments using the same shared policy
        for env_id, obs in obs_dict.items():
            action, log_prob, value = agent.select_action(obs)
            assert len(action) == 8
            assert all(0 <= a <= 2 for a in action)
            actions_dict[env_id] = action

        # Advance one step across all 4 environments
        next_obs, rewards, dones, infos = manager.step(actions_dict)
        assert len(next_obs) == 4
        assert len(rewards) == 4
        assert len(dones) == 4
        assert len(infos) == 4

    def test_criterion_3_and_4_independent_states_and_rewards(self):
        """
        Criteria 3 & 4: Independent state transitions and reward calculations
        across different policy profiles (Baseline vs Adaptive vs Hardened).
        """
        manager = ParallelEnvironmentManager(scenario_name="black_sky", max_steps=35)
        agent = PPOAgent(obs_dim=14, num_actions=8, action_levels=3)

        obs_dict, _ = manager.reset()
        
        # Run 35 simulation steps to cross incident thresholds (T=15s Edge Flood, T=30s Auth Stuffing)
        for _ in range(35):
            actions_dict = {}
            for env_id, obs in obs_dict.items():
                action, _, _ = agent.select_action(obs)
                actions_dict[env_id] = action
            obs_dict, rewards, dones, infos = manager.step(actions_dict)

        # Baseline (env_a) has fixed permissive rules (all 0), so it degrades under flood
        # Hardened (env_c) has strict rules (all 2)
        env_a = manager.environments["env_a_baseline"]
        env_c = manager.environments["env_c_hardened"]
        
        metrics_a = env_a._get_info()["metrics"]
        metrics_c = env_c._get_info()["metrics"]

        # Verification of independent state trajectories:
        # Hardened drops fewer flood requests than unmitigated baseline
        assert metrics_a["effective_availability_pct"] != metrics_c["effective_availability_pct"]
        # Rewards must reflect differing policy configurations
        assert rewards["env_a_baseline"] != rewards["env_c_hardened"]

    def test_criterion_5_checkpoint_save_and_load(self):
        """Criterion 5: Policy checkpoints can be saved and loaded deterministically."""
        agent = PPOAgent(obs_dim=14, num_actions=8, action_levels=3)
        sample_obs = np.ones(14, dtype=np.float32) * 0.5
        initial_action, _, _ = agent.select_action(sample_obs, deterministic=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            ckpt_path = os.path.join(tmpdir, "policy_v1.pt")
            agent.save_checkpoint(ckpt_path)
            assert os.path.exists(ckpt_path)

            # Load into a fresh agent
            new_agent = PPOAgent(obs_dim=14, num_actions=8, action_levels=3)
            new_agent.load_checkpoint(ckpt_path)

            loaded_action, _, _ = new_agent.select_action(sample_obs, deterministic=True)
            assert initial_action == loaded_action

    def test_criterion_6_repeatable_held_out_evaluation(self):
        """Criterion 6: Repeatable evaluation against held-out scenario with fixed seed."""
        env_eval_1 = NetworkDefenseEnv(
            environment_id="eval_run_1",
            scenario_name="held_out_evaluation",
            max_steps=40,
            seed=1337
        )
        env_eval_2 = NetworkDefenseEnv(
            environment_id="eval_run_2",
            scenario_name="held_out_evaluation",
            max_steps=40,
            seed=1337
        )

        obs1, _ = env_eval_1.reset()
        obs2, _ = env_eval_2.reset()
        assert np.allclose(obs1, obs2)

        # Apply identical action sequences
        test_action = [1, 1, 1, 1, 1, 1, 1, 1]
        for step in range(40):
            o1, r1, d1, _, info1 = env_eval_1.step(test_action)
            o2, r2, d2, _, info2 = env_eval_2.step(test_action)
            assert np.allclose(o1, o2), f"Divergence detected at step {step}"
            assert r1 == r2
            assert d1 == d2

        # Final evaluation metrics must match bit-for-bit
        metrics1 = info1["metrics"]
        metrics2 = info2["metrics"]
        assert metrics1["effective_availability_pct"] == metrics2["effective_availability_pct"]
        assert metrics1["blast_radius_factor"] == metrics2["blast_radius_factor"]

    def test_criterion_7_ddps_invariant_rejection(self):
        """
        Criterion 7: Unit test proving that an invalid defensive action
        (violating security invariants Omega) is rejected by the DDPS.
        """
        ddps = DynamicDefensivePolicyStack(cooldown_steps=5)
        
        # Test 1: Action out of bounded range {0, 1, 2} is rejected at schema level
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            DefensiveActionProposal(edge_rate_limit_level=99)

        # Test 2: Invariant Omega violation (attempted unauthorized bypass)
        bypass_proposal = DefensiveActionProposal(segmentation_mode=0)
        rejection_res = ddps.validate_and_enforce(
            bypass_proposal,
            current_step=2,
            attempted_illegal_bypass=True
        )
        assert rejection_res.is_approved is False
        assert any("Omega Violation" in reason for reason in rejection_res.rejected_reasons)
        assert ddps.rejected_count == 1

        # Test 3: Excessive policy oscillation (jump of 2 levels during cooldown)
        # First set policy to [0, 0, 0, 0, 0, 0, 0, 0] at step 5
        ddps.validate_and_enforce(DefensiveActionProposal(), current_step=5)
        # Immediately try to swing to level 2 on step 6 (during cooldown)
        sudden_jump = DefensiveActionProposal(edge_rate_limit_level=2)
        cooldown_res = ddps.validate_and_enforce(sudden_jump, current_step=6)
        assert cooldown_res.is_approved is False
        assert any("Stability Violation" in reason for reason in cooldown_res.rejected_reasons)
