# AEGIS Operations & Demo Runbook

Compliant with Section 25 of the Master Specification.

## 1. Prerequisites
- Windows 10/11 with PowerShell 7+
- Python 3.12 (`.venv` virtual environment)
- Docker Desktop 4.30+ (Linux containers enabled)

## 2. Quickstart Commands

### Step 1: Generate mTLS Certificates
```powershell
.\scripts\generate-certs.ps1
```
Generates CA, Gateway server certs, and client certificates in `infrastructure/certificates/`.

### Step 2: Start the System
```powershell
.\scripts\dev-up.ps1
```
Or start in local standalone mode:
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 3: Run Automated Verification Tests
```powershell
.\scripts\verify-stack.ps1
```
Executes all 36 unit, integration, and security negative tests across the test suite.

### Step 4: Access Interfaces
- **Command Deck Dashboard**: `http://127.0.0.1:8000/dashboard`
- **Swagger REST API**: `http://127.0.0.1:8000/docs`
- **HAProxy Ingress**: `https://127.0.0.1:8443`
- **HAProxy Stats**: `http://127.0.0.1:8088/stats`

## 3. Demo Runbook (Vertical Slice)

1. Open the **Command Deck Dashboard** at `http://127.0.0.1:8000/dashboard`.
2. Observe system health in the `NORMAL` defense state.
3. Click **"Run T1110 Adaptive Test"** or execute via API:
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/metrics/compare?scenario_id=brute_force"
   ```
4. Observe the live stream:
   - Ingested authentication failure events.
   - Independent detection of `T1110 - Brute Force`.
   - Structured Gemma incident analysis and recommendation.
   - Deterministic policy engine validation against invariants ($\Omega$).
   - Gateway ACL block applied to test source `172.31.10.15`.
   - Defense state transitions to `MITIGATING` $\to$ `CONTAINED`.
5. Click **"Emergency Stop"** or test rollback:
   - System unblocks the source IP and safely returns to `NORMAL` state.

