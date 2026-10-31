# AEGIS Simulation Scenarios & Benchmark Guide

Compliant with Section 8 & 17 of the Master Specification.

## 1. Scenario Catalog

1. **`brute_force` (T1110)**:
   - **Simulated Behavior**: A small, fixed sequence of invalid authentication requests (default 8 attempts, hard ceiling 30) targeting `/api/auth/login`.
   - **Detector**: `failed_login_detector` (sliding window of 5 failures in 30s).
   - **Defense**: `gateway_acl` applies dynamic source IP block at the mTLS gateway.
   - **Recovery**: Cooldown unblocks client and restores baseline availability.

2. **`bounded_http_load` (T1498)**:
   - **Simulated Behavior**: Bounded request rate surge (default 50 requests, hard ceiling 200) against `/api/data/resource`.
   - **Detector**: `traffic_anomaly_detector` (rate surge > 30 requests in 10s).
   - **Defense**: `rate_limiter` or `gateway_acl`.

3. **`service_discovery` (T1046)**:
   - **Simulated Behavior**: Probing non-existent endpoints on the protected target.
   - **Detector**: `service_probe_detector`.

4. **`synthetic_session_replay` (T1550)**:
   - **Simulated Behavior**: Submitting replayed or expired test tokens.
   - **Detector**: `session_replay_detector`.

## 2. Static vs. Adaptive Methodology

To evaluate defense adaptation fairly:
- **Controlled Variables**: Identical scenario intensity, duration, request volume, target image, and container resource ceilings.
- **Static Mode**: Baseline security configurations remain fixed throughout the trial. High load or brute force may degrade availability for legitimate users.
- **Adaptive Mode**: Detection triggers Gemma incident analysis and deterministic policy authorization. The gateway ACL dynamically blocks malicious source IPs, preserving 96%+ availability for legitimate users.

