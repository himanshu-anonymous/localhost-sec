"""
Main FastAPI Orchestrator Core — localhost (BASTION X).
Compliant with Section 10 of Master Execution Specification & Hybrid Database Architecture.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.api.routes_environments import router as router_environments
from backend.app.api.routes_scenarios import router as router_scenarios
from backend.app.api.routes_training import router as router_training
from backend.app.api.routes_metrics import router as router_metrics
from backend.app.api.websocket_handler import router as router_websocket
from backend.app.api.routes_mitre import router as router_mitre
from backend.app.api.routes_simulations import router as router_simulations
from backend.app.api.routes_policy import router as router_policy
from backend.app.environments.docker_manager import docker_manager
from backend.app.orchestrator.training_service import trainer_service
from backend.db.postgres import init_db
from backend.db.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialises persistent schema and seeds environments & MITRE container techniques."""
    try:
        init_db()
        seed_database()
    except Exception as e:
        print(f"[Warning] Database initialization or seeding deferred: {e}")
    yield


app = FastAPI(
    title="localhost (BASTION X) — Orchestrator API",
    description="Adaptive Multi-Layer Network Defence Simulator Orchestration Core",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(router_environments)
app.include_router(router_scenarios)
app.include_router(router_training)
app.include_router(router_metrics)
app.include_router(router_websocket)
app.include_router(router_mitre)
app.include_router(router_simulations)
app.include_router(router_policy)


@app.get("/")
def root():
    return {
        "project": "localhost (BASTION X)",
        "subtitle": "Adaptive Multi-Layer Network Defence Simulator",
        "status": "online",
        "trainer_status": trainer_service.get_status(),
        "docker_workers": docker_manager.get_worker_urls(),
        "documentation": "/docs",
        "live_dashboard": "/dashboard",
        "mitre_catalog": "/api/mitre/techniques",
        "simulations": "/api/simulations",
        "policy_metadata": "/api/v1/policy/metadata"
    }


@app.get("/dashboard", response_class=HTMLResponse)
def embedded_dashboard():
    """Lightweight real-time visualizer dashboard embedded directly in FastAPI."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>localhost (BASTION X) — Live Command Deck</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: #0b1120; color: #e2e8f0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
        </style>
    </head>
    <body class="p-6">
        <header class="border-b border-slate-700 pb-4 mb-6 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-cyan-400">localhost (BASTION X) Command Centre</h1>
                <p class="text-xs text-slate-400">Adaptive Multi-Layer Network Defence Simulator — Live Telemetry Deck</p>
            </div>
            <div class="flex gap-2">
                <button onclick="startTraining()" class="bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-1.5 rounded text-xs font-semibold">▶ Start RL Training</button>
                <button onclick="stopTraining()" class="bg-rose-700 hover:bg-rose-600 text-white px-3 py-1.5 rounded text-xs font-semibold">⏹ Stop</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <span class="text-xs text-slate-400">Env A (Baseline)</span>
                <div id="env-a-avail" class="text-2xl font-bold text-rose-400 mt-1">--%</div>
                <div class="text-xs text-slate-500 mt-1">Fixed Permissive</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <span class="text-xs text-cyan-400">Env B (Adaptive DDPS)</span>
                <div id="env-b-avail" class="text-2xl font-bold text-emerald-400 mt-1">--%</div>
                <div class="text-xs text-slate-500 mt-1">Shared PPO Active</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <span class="text-xs text-slate-400">Env C (Hardened)</span>
                <div id="env-c-avail" class="text-2xl font-bold text-blue-400 mt-1">--%</div>
                <div class="text-xs text-slate-500 mt-1">Strict Zero-Trust</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <span class="text-xs text-slate-400">Env D (Experimental)</span>
                <div id="env-d-avail" class="text-2xl font-bold text-amber-400 mt-1">--%</div>
                <div class="text-xs text-slate-500 mt-1">Heuristic Policy</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg lg:col-span-2">
                <h3 class="text-sm font-semibold text-slate-300 mb-3">Live Telemetry Feed (WebSocket)</h3>
                <div id="telemetry-log" class="bg-slate-950 p-3 rounded text-xs text-slate-300 h-64 overflow-y-auto space-y-1">
                    Connecting to WebSocket...
                </div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <h3 class="text-sm font-semibold text-slate-300 mb-3">Gemma 4 Reasoning Explanation</h3>
                <div id="gemma-box" class="bg-slate-950 p-3 rounded text-xs text-slate-300 h-64 overflow-y-auto">
                    Waiting for episode evaluation report...
                </div>
            </div>
        </div>

        <script>
            const logBox = document.getElementById("telemetry-log");
            const gemmaBox = document.getElementById("gemma-box");
            
            function connectWS() {
                const ws = new WebSocket(`ws://${location.host}/ws/v1/experiments/exp-live`);
                ws.onopen = () => { logBox.innerHTML = "<div>[WebSocket Connected] Listening for telemetry...</div>"; };
                ws.onmessage = (e) => {
                    const data = JSON.parse(e.data);
                    if (data.event_type === "environment.telemetry") {
                        const w = data.workers;
                        document.getElementById("env-a-avail").innerText = w.env_a_baseline.metrics.effective_availability_pct.toFixed(1) + "%";
                        document.getElementById("env-b-avail").innerText = w.env_b_adaptive.metrics.effective_availability_pct.toFixed(1) + "%";
                        document.getElementById("env-c-avail").innerText = w.env_c_hardened.metrics.effective_availability_pct.toFixed(1) + "%";
                        document.getElementById("env-d-avail").innerText = w.env_d_experimental.metrics.effective_availability_pct.toFixed(1) + "%";
                        
                        const item = document.createElement("div");
                        item.innerText = `[T+${data.step}s] Ep ${data.episode} | Env-B Avail: ${w.env_b_adaptive.metrics.effective_availability_pct.toFixed(1)}% | Blast: ${w.env_b_adaptive.metrics.blast_radius_factor.toFixed(2)}`;
                        logBox.prepend(item);
                    }
                };
            }
            connectWS();

            async function startTraining() {
                await fetch('/api/v1/training/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({experiment_id: 'exp-live', scenario_name: 'black_sky', max_episodes: 3, steps_per_episode: 50})
                });
            }

            async function stopTraining() {
                await fetch('/api/v1/training/exp-live/stop', {method: 'POST'});
            }

            // Fetch initial report
            fetch('/api/v1/experiments/exp-live/report').then(r => r.json()).then(data => {
                const g = data.gemma_ai_explanation;
                gemmaBox.innerHTML = `
                    <p class="font-bold text-cyan-400 mb-1">Diagnosis:</p>
                    <p class="mb-2">${g.incident_summary}</p>
                    <p class="font-bold text-emerald-400 mb-1">Defensive Action:</p>
                    <p class="mb-2">${g.defensive_action_explanation}</p>
                    <p class="font-bold text-amber-400 mb-1">Outcome:</p>
                    <p>${g.policy_outcome}</p>
                `;
            }).catch(() => {});
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
