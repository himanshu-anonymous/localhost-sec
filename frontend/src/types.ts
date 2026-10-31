export interface EnvironmentMetric {
  effective_availability_pct: number;
  mean_time_to_containment_s: number | null;
  blast_radius_factor: number;
  resilience_degradation_index: number;
  security_invariant_violations: number;
  policy_churn_count: number;
  total_legitimate_requests: number;
  successful_legitimate_requests: number;
}

export interface EnforcedPolicy {
  edge_rate_limit_level: number;
  connection_limit_level: number;
  app_quota_level: number;
  auth_throttle_level: number;
  app_concurrency_level: number;
  segmentation_mode: number;
  egress_limit_level: number;
  workload_priority_level: number;
}

export interface WorkerTelemetry {
  reward: number;
  metrics: EnvironmentMetric;
  enforced_policy: EnforcedPolicy;
}

export interface LiveTelemetryMessage {
  event_type: 'environment.telemetry' | 'rl.training_metrics' | 'ddps.actions' | 'experiment.completed';
  experiment_id: string;
  episode: number;
  step: number;
  timestamp: number;
  workers?: {
    env_a_baseline: WorkerTelemetry;
    env_b_adaptive: WorkerTelemetry;
    env_c_hardened: WorkerTelemetry;
    env_d_experimental: WorkerTelemetry;
  };
}

export interface GemmaAIExplanation {
  environment_id: string;
  incident_summary: string;
  observed_degradation: string;
  defensive_action_explanation: string;
  policy_outcome: string;
  invariant_status: string;
  potential_weaknesses: string[];
  recommendations: string[];
  confidence_score: number;
}

export interface ExperimentReport {
  experiment_id: string;
  status: 'completed' | 'in_progress';
  benchmark_summary: {
    env_a_baseline: { availability: string; blast_radius: number; mttc: string };
    env_b_adaptive: { availability: string; blast_radius: number; mttc: string };
    env_c_hardened: { availability: string; blast_radius: number; mttc: string };
    env_d_experimental: { availability: string; blast_radius: number; mttc: string };
  };
  latest_training_metric?: any;
  gemma_ai_explanation: GemmaAIExplanation;
}

export interface TrainingStatus {
  experiment_id: string;
  is_running: boolean;
  is_paused: boolean;
  worker_mode: string;
  current_episode: number;
  current_step: number;
  total_timesteps: number;
  checkpoint_available: boolean;
}

export interface NodeState {
  id: string;
  name: string;
  layer: number;
  status: 'HEALTHY' | 'OPERATIONAL' | 'DEGRADED' | 'SEVERELY_DEGRADED' | 'UNAVAILABLE' | 'COMPROMISED';
  cpu_utilization: number;
  memory_utilization: number;
  connection_utilization: number;
  request_rate: number;
  response_latency_ms: number;
  error_rate: number;
  health_index: number;
  is_compromised: boolean;
  is_isolated: boolean;
}

