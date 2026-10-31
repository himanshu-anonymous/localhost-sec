"""
Network Topology and Service Graph Model.
Compliant with Section 4.2 of Formal Specification v1.0.
"""

from typing import Dict, Set, Tuple, List
from backend.app.schemas.models import NodeState


class NetworkTopology:
    """
    Logical network graph G = (V, E) representing the private enterprise infrastructure.
    Enforces deny-by-default communication policies across layers.
    """
    
    # 8 Canonical Node IDs
    EDGE_GW = "edge_gateway"
    AUTH_SVC = "auth_service"
    APP_GW = "app_gateway"
    APP_SVC = "application_service"
    CI_RUNNER = "ci_runner"
    INTERNAL_SVC = "internal_service"
    DATABASE = "database"
    ADMIN_SVC = "admin_service"

    def __init__(self):
        self.nodes: Dict[str, NodeState] = {}
        self.permitted_edges: Set[Tuple[str, str]] = set()
        self.reset()

    def reset(self):
        """Initializes canonical nodes and permitted communication edges."""
        self.nodes = {
            self.EDGE_GW: NodeState(id=self.EDGE_GW, name="Edge Gateway", layer=1, status="HEALTHY"),
            self.APP_GW: NodeState(id=self.APP_GW, name="Application Gateway (WAF)", layer=3, status="HEALTHY"),
            self.AUTH_SVC: NodeState(id=self.AUTH_SVC, name="Identity & Auth Service", layer=4, status="HEALTHY"),
            self.APP_SVC: NodeState(id=self.APP_SVC, name="Application Microservice", layer=5, status="HEALTHY"),
            self.CI_RUNNER: NodeState(id=self.CI_RUNNER, name="CI/CD Runner Pool", layer=5, status="HEALTHY"),
            self.INTERNAL_SVC: NodeState(id=self.INTERNAL_SVC, name="Internal Service Bus", layer=6, status="HEALTHY"),
            self.DATABASE: NodeState(id=self.DATABASE, name="Protected Database (L7)", layer=7, status="HEALTHY"),
            self.ADMIN_SVC: NodeState(id=self.ADMIN_SVC, name="Admin Control Plane", layer=4, status="HEALTHY"),
        }

        # Strict allowlist of communication channels
        self.permitted_edges = {
            (self.EDGE_GW, self.APP_GW),
            (self.APP_GW, self.AUTH_SVC),
            (self.APP_GW, self.APP_SVC),
            (self.APP_SVC, self.DATABASE),
            (self.CI_RUNNER, self.INTERNAL_SVC),
            (self.ADMIN_SVC, self.AUTH_SVC),
            (self.ADMIN_SVC, self.DATABASE),
            (self.INTERNAL_SVC, self.APP_SVC),
        }

    def is_communication_allowed(self, source_id: str, dest_id: str) -> bool:
        """Deny-by-default network policy checker."""
        if source_id not in self.nodes or dest_id not in self.nodes:
            return False
        if self.nodes[source_id].is_isolated or self.nodes[dest_id].is_isolated:
            return False
        return (source_id, dest_id) in self.permitted_edges

    def get_node(self, node_id: str) -> NodeState:
        return self.nodes[node_id]

    def get_all_nodes(self) -> Dict[str, NodeState]:
        return self.nodes

    def isolate_node(self, node_id: str, isolated: bool = True):
        if node_id in self.nodes:
            self.nodes[node_id].is_isolated = isolated

    def mark_compromised(self, node_id: str, compromised: bool = True):
        if node_id in self.nodes:
            self.nodes[node_id].is_compromised = compromised
            if compromised:
                self.nodes[node_id].status = "COMPROMISED"
                self.nodes[node_id].health_index = min(self.nodes[node_id].health_index, 0.2)
