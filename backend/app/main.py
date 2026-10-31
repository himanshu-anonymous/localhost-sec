"""
Main FastAPI Orchestrator Core — AEGIS / localhost (BASTION X).
Compliant with Section 10 & 15 of AEGIS Master Execution Specification.
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Ensure root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.api.routes_aegis_v1 import router as router_aegis_v1
from backend.app.api.routes_environments import router as router_environments
from backend.app.api.routes_scenarios import router as router_scenarios
from backend.app.api.routes_training import router as router_training
from backend.app.api.routes_metrics import router as router_metrics
from backend.app.api.websocket_handler import router as router_websocket
from backend.app.api.routes_mitre import router as router_mitre
from backend.app.api.routes_simulations import router as router_simulations
from backend.app.environments.docker_manager import docker_manager
from backend.app.orchestrator.training_service import trainer_service
from backend.db.postgres import init_db
from backend.db.seed import seed_database

app = FastAPI(
    title="AEGIS / localhost (BASTION X) — Orchestrator API",
    description="Adaptive Multi-Layer Network Defence Simulator & Dynamic Policy Orchestration Core",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers (routes_aegis_v1 included first to prioritize static paths like /metrics/compare over parameterized /metrics/{id})
app.include_router(router_aegis_v1)
app.include_router(router_environments)
app.include_router(router_scenarios)
app.include_router(router_training)
app.include_router(router_metrics)
app.include_router(router_websocket)
app.include_router(router_mitre)
app.include_router(router_simulations)


@app.on_event("startup")
def on_startup():
    """Initialises persistent schema and seeds environments & MITRE container techniques."""
    try:
        init_db()
        seed_database()
    except Exception as e:
        print(f"[Warning] Database initialization or seeding deferred: {e}")


@app.get("/")
def root():
    return {
        "project": "localhost (BASTION X)",
        "project_name": "AEGIS",
        "subtitle": "Adaptive Multi-Layer Network Defence Simulator",
        "status": "online",
        "trainer_status": trainer_service.get_status(),
        "docker_workers": docker_manager.get_worker_urls(),
        "api_v1_health": "/api/v1/health",
        "mitre_catalog": "/api/mitre/techniques",
        "simulations": "/api/simulations",
        "events": "/api/v1/events",
        "incidents": "/api/v1/incidents",
        "defense_state": "/api/v1/defense/state",
        "metrics_compare": "/api/v1/metrics/compare",
        "documentation": "/docs",
        "live_dashboard": "/dashboard"
    }


@app.get("/dashboard", response_class=HTMLResponse)
def embedded_dashboard():
    """Lightweight real-time visualizer dashboard embedded directly in FastAPI."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AEGIS — Adaptive Security Command Deck</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: #0b1120; color: #e2e8f0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
        </style>
    </head>
    <body class="p-6">
        <header class="border-b border-slate-700 pb-4 mb-6 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-cyan-400">AEGIS Command Centre</h1>
                <p class="text-xs text-slate-400">Adaptive Elastic Guard & Intelligent Security — Real-Time Operations Deck</p>
            </div>
            <div class="flex gap-2">
                <button onclick="runAdaptiveSimulation()" class="bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-1.5 rounded text-xs font-semibold">▶ Run T1110 Adaptive Test</button>
                <button onclick="emergencyStop()" class="bg-rose-700 hover:bg-rose-600 text-white px-3 py-1.5 rounded text-xs font-semibold">⏹ Emergency Stop</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <span class="text-xs text-slate-400">Defense State</span>
                <div id="defense-state" class="text-2xl font-bold text-emerald-400 mt-1">NORMAL</div>
                <div class="text-xs text-slate-500 mt-1">Active Gateway ACL</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <span class="text-xs text-cyan-400">Events Ingested</span>
                <div id="events-count" class="text-2xl font-bold text-cyan-400 mt-1">0</div>
                <div class="text-xs text-slate-500 mt-1">Normalized Stream</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <span class="text-xs text-slate-400">Detections</span>
                <div id="detections-count" class="text-2xl font-bold text-amber-400 mt-1">0</div>
                <div class="text-xs text-slate-500 mt-1">Independent Inferred</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <span class="text-xs text-slate-400">Open Incidents</span>
                <div id="incidents-count" class="text-2xl font-bold text-rose-400 mt-1">0</div>
                <div class="text-xs text-slate-500 mt-1">Triage & Containment</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg lg:col-span-2">
                <h3 class="text-sm font-semibold text-slate-300 mb-3">Live Telemetry & Defense Log</h3>
                <div id="telemetry-log" class="bg-slate-950 p-3 rounded text-xs text-slate-300 h-64 overflow-y-auto space-y-1">
                    System initialized. Ready for simulation.
                </div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
                <h3 class="text-sm font-semibold text-slate-300 mb-3">Gemma AI Security Assessment</h3>
                <div id="gemma-box" class="bg-slate-950 p-3 rounded text-xs text-slate-300 h-64 overflow-y-auto">
                    Waiting for incident trigger...
                </div>
            </div>
        </div>

        <script>
            const logBox = document.getElementById("telemetry-log");
            const gemmaBox = document.getElementById("gemma-box");

            async function updateDashboardMetrics() {
                try {
                    const r = await fetch('/api/v1/metrics/overview');
                    const d = await r.json();
                    document.getElementById("defense-state").innerText = d.current_defense_state;
                    document.getElementById("events-count").innerText = d.total_events_ingested;
                    document.getElementById("detections-count").innerText = d.total_detections;
                    document.getElementById("incidents-count").innerText = d.open_incidents;
                } catch(e) {}
            }
            setInterval(updateDashboardMetrics, 3000);
            updateDashboardMetrics();

            async function runAdaptiveSimulation() {
                logBox.prepend(Object.assign(document.createElement("div"), {
                    innerText: "[SIMULATION] Launching T1110 Bounded Brute Force trial..."
                }));
                for (let i = 1; i <= 6; i++) {
                    await fetch('/api/v1/events/ingest', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            source_type: 'target_app',
                            source_name: 'target-web',
                            event_type: 'auth_failure',
                            source_ip: '172.31.10.15',
                            destination_ip: '172.31.20.10',
                            protocol: 'HTTP',
                            severity: 'warning',
                            metadata: {username: 'admin', attempt: i}
                        })
                    });
                }
                const incs = await (await fetch('/api/v1/incidents')).json();
                if (incs.length > 0) {
                    const lastInc = incs[incs.length - 1];
                    logBox.prepend(Object.assign(document.createElement("div"), {
                        innerText: `[INCIDENT] ${lastInc.incident_id} detected. Requesting Gemma AI analysis...`
                    }));
                    const analysis = await (await fetch(`/api/v1/incidents/${lastInc.incident_id}/analyze`, {method: 'POST'})).json();
                    gemmaBox.innerHTML = `
                        <p class="font-bold text-cyan-400 mb-1">Incident Summary:</p>
                        <p class="mb-2 text-slate-300">${analysis.incident_summary}</p>
                        <p class="font-bold text-amber-400 mb-1">Recommended Action:</p>
                        <p class="mb-2 text-slate-300">${analysis.recommended_actions[0]?.module_id}.${analysis.recommended_actions[0]?.action_id} (${analysis.recommended_actions[0]?.reason})</p>
                    `;
                    const mit = await (await fetch(`/api/v1/incidents/${lastInc.incident_id}/mitigate`, {method: 'POST'})).json();
                    logBox.prepend(Object.assign(document.createElement("div"), {
                        innerText: `[DEFENSE] Mitigation applied: Gateway ACL blocked ${lastInc.source_identities[0]}`
                    }));
                    updateDashboardMetrics();
                }
            }

            async function emergencyStop() {
                await fetch('/api/v1/defense/emergency-stop', {method: 'POST'});
                logBox.prepend(Object.assign(document.createElement("div"), {
                    innerText: "[EMERGENCY STOP] All active blocks revoked. System in EMERGENCY_STOP state."
                }));
                updateDashboardMetrics();
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
