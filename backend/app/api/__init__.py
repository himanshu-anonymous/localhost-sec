from backend.app.api.routes_environments import router as router_environments
from backend.app.api.routes_scenarios import router as router_scenarios
from backend.app.api.routes_training import router as router_training
from backend.app.api.routes_metrics import router as router_metrics
from backend.app.api.websocket_handler import router as router_websocket

__all__ = [
    "router_environments",
    "router_scenarios",
    "router_training",
    "router_metrics",
    "router_websocket",
]
