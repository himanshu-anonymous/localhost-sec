"""
Ephemeral Runtime Graph Manager (Neo4j 5) for localhost (BASTION X).
Manages run-scoped graph lifecycles:
1. Hydration from baseline topology template
2. Dynamic edge mutation (ALLOWS_TRAFFIC_TO -> DENIES_TRAFFIC_TO)
3. Incident marking (ActiveIncident -> TARGETS_NODE)
4. Dynamic blast radius fraction calculation
5. Full graph snapshot and automatic DETACH DELETE teardown
"""

import os
import socket
from urllib.parse import urlparse
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jpassword")


class EphemeralGraphManager:
    """Run-scoped ephemeral graph manager interfacing with Neo4j 5."""

    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None
        self._driver_checked = False
        self._in_memory_fallback: Dict[str, Dict[str, Any]] = {}

    def _get_driver(self):
        if not self._driver_checked:
            self._driver_checked = True
            try:
                parsed = urlparse(self.uri)
                host = parsed.hostname or "localhost"
                port = parsed.port or 7687

                # Fast socket connection check avoids 30s TCP timeouts when Neo4j is offline
                with socket.create_connection((host, port), timeout=0.15):
                    pass

                from neo4j import AsyncGraphDatabase
                self._driver = AsyncGraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    connection_timeout=0.5,
                    max_connection_lifetime=30
                )
            except Exception:
                self._driver = None
        return self._driver

    async def close(self):
        if self._driver:
            await self._driver.close()
            self._driver = None
            self._driver_checked = False

    async def init_constraints(self):
        """Initialises unique constraints and lookup indexes."""
        driver = self._get_driver()
        if not driver:
            return
        try:
            async with driver.session() as session:
                await session.run("""
                    CREATE CONSTRAINT container_run_unique IF NOT EXISTS
                    FOR (n:ContainerNode) REQUIRE (n.run_id, n.environment_id, n.node_id) IS UNIQUE;
                """)
                await session.run("""
                    CREATE INDEX container_lookup_idx IF NOT EXISTS
                    FOR (n:ContainerNode) ON (n.run_id, n.environment_id);
                """)
        except Exception:
            pass

    async def hydrate_environment(self, run_id: str, env_id: str, topology_template: dict) -> None:
        """Hydrates virtual network topology into Neo4j for the active run."""
        driver = self._get_driver()
        nodes = topology_template.get("nodes", [])
        edges = topology_template.get("edges", [])

        if driver:
            try:
                async with driver.session() as session:
                    await session.run(
                        """
                        UNWIND $nodes AS node
                        MERGE (c:ContainerNode {
                            run_id: $run_id, environment_id: $env_id, node_id: node.node_id
                        })
                        SET c.name = node.name,
                            c.role = node.role,
                            c.zone = node.zone,
                            c.status = 'healthy',
                            c.compromised = false,
                            c.created_at = datetime()
                        """,
                        run_id=run_id,
                        env_id=env_id,
                        nodes=nodes,
                    )
                    await session.run(
                        """
                        UNWIND $edges AS edge
                        MATCH (s:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: edge.source})
                        MATCH (d:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: edge.target})
                        MERGE (s)-[r:ALLOWS_TRAFFIC_TO {run_id: $run_id}]->(d)
                        SET r.port = edge.port,
                            r.rate_limit_rps = edge.rate_limit_rps,
                            r.policy_version = 'baseline-v1'
                        """,
                        run_id=run_id,
                        env_id=env_id,
                        edges=edges,
                    )
                return
            except Exception:
                pass

        # In-memory fallback representation
        self._in_memory_fallback[run_id] = {
            "env_id": env_id,
            "nodes": {n["node_id"]: {**n, "status": "healthy", "compromised": False} for n in nodes},
            "edges": [
                {"source": e["source"], "target": e["target"], "type": "ALLOWS_TRAFFIC_TO", "props": e}
                for e in edges
            ],
            "incidents": [],
        }

    async def record_active_incident(
        self, run_id: str, env_id: str, target_node: str, detection_id: str, technique_id: str, confidence: float
    ) -> None:
        """Attaches an ActiveIncident marker to a target ContainerNode."""
        driver = self._get_driver()
        if driver:
            try:
                async with driver.session() as session:
                    await session.run(
                        """
                        MATCH (target:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: $target_node})
                        MERGE (inc:ActiveIncident {run_id: $run_id, detection_id: $detection_id})
                        SET inc.inferred_technique_id = $technique_id,
                            inc.confidence = $confidence,
                            inc.detected_at = datetime()
                        MERGE (inc)-[:TARGETS_NODE {run_id: $run_id}]->(target)
                        """,
                        run_id=run_id,
                        env_id=env_id,
                        target_node=target_node,
                        detection_id=detection_id,
                        technique_id=technique_id,
                        confidence=confidence,
                    )
                return
            except Exception:
                pass

        if run_id in self._in_memory_fallback:
            self._in_memory_fallback[run_id]["incidents"].append({
                "detection_id": detection_id,
                "target_node": target_node,
                "technique_id": technique_id,
                "confidence": confidence,
            })

    async def mutate_traffic_policy(
        self, run_id: str, env_id: str, source_node: str, target_node: str, action_id: str, technique_id: str
    ) -> None:
        """Mutates graph edges when DDPS approves a defensive action (ALLOWS_TRAFFIC_TO -> DENIES_TRAFFIC_TO)."""
        driver = self._get_driver()
        if driver:
            try:
                async with driver.session() as session:
                    await session.run(
                        """
                        MATCH (src:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: $source_node})
                              -[allow:ALLOWS_TRAFFIC_TO {run_id: $run_id}]->
                              (dst:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: $target_node})
                        DELETE allow
                        MERGE (src)-[deny:DENIES_TRAFFIC_TO {run_id: $run_id}]->(dst)
                        SET deny.action_id = $action_id,
                            deny.reason = $technique_id,
                            deny.applied_at = datetime()
                        """,
                        run_id=run_id,
                        env_id=env_id,
                        source_node=source_node,
                        target_node=target_node,
                        action_id=action_id,
                        technique_id=technique_id,
                    )
                return
            except Exception:
                pass

        if run_id in self._in_memory_fallback:
            updated_edges = []
            for edge in self._in_memory_fallback[run_id]["edges"]:
                if edge["source"] == source_node and edge["target"] == target_node and edge["type"] == "ALLOWS_TRAFFIC_TO":
                    updated_edges.append({
                        "source": source_node,
                        "target": target_node,
                        "type": "DENIES_TRAFFIC_TO",
                        "props": {"action_id": action_id, "reason": technique_id},
                    })
                else:
                    updated_edges.append(edge)
            self._in_memory_fallback[run_id]["edges"] = updated_edges

    async def compute_blast_radius(self, run_id: str, env_id: str, attacked_node_id: str) -> dict:
        """Evaluates graph reachability from attacked node to compute live blast radius fraction."""
        driver = self._get_driver()
        if driver:
            try:
                async with driver.session() as session:
                    result = await session.run(
                        """
                        MATCH (target:ContainerNode {run_id: $run_id, environment_id: $env_id, node_id: $attacked_node_id})
                        OPTIONAL MATCH path = (target)-[:ALLOWS_TRAFFIC_TO*1..4 {run_id: $run_id}]->(reachable:ContainerNode)
                        WITH target, collect(DISTINCT reachable.node_id) AS exposed_nodes
                        MATCH (all_nodes:ContainerNode {run_id: $run_id, environment_id: $env_id})
                        RETURN size(exposed_nodes) AS exposed_count,
                               count(all_nodes) AS total_nodes,
                               toFloat(size(exposed_nodes)) / count(all_nodes) AS blast_radius_fraction,
                               exposed_nodes
                        """,
                        run_id=run_id,
                        env_id=env_id,
                        attacked_node_id=attacked_node_id,
                    )
                    rec = await result.single()
                    if rec:
                        return {
                            "exposed_count": rec["exposed_count"],
                            "total_nodes": rec["total_nodes"],
                            "blast_radius_fraction": rec["blast_radius_fraction"] or 0.0,
                            "exposed_nodes": rec["exposed_nodes"] or [],
                        }
            except Exception:
                pass

        # In-memory BFS reachability calculation
        if run_id in self._in_memory_fallback:
            g = self._in_memory_fallback[run_id]
            total_nodes = len(g["nodes"])
            allowed_adj = {}
            for e in g["edges"]:
                if e["type"] == "ALLOWS_TRAFFIC_TO":
                    allowed_adj.setdefault(e["source"], []).append(e["target"])

            visited = set()
            queue = [attacked_node_id]
            while queue:
                curr = queue.pop(0)
                for nxt in allowed_adj.get(curr, []):
                    if nxt not in visited and nxt != attacked_node_id:
                        visited.add(nxt)
                        queue.append(nxt)

            fraction = len(visited) / total_nodes if total_nodes > 0 else 0.0
            return {
                "exposed_count": len(visited),
                "total_nodes": total_nodes,
                "blast_radius_fraction": round(fraction, 4),
                "exposed_nodes": list(visited),
            }

        return {"exposed_count": 0, "total_nodes": 0, "blast_radius_fraction": 0.0, "exposed_nodes": []}

    async def snapshot_and_teardown(self, run_id: str) -> dict:
        """Captures final graph topology snapshot and purges ephemeral nodes from Neo4j."""
        driver = self._get_driver()
        snapshot = {"nodes": [], "edges": []}
        if driver:
            try:
                async with driver.session() as session:
                    result = await session.run(
                        """
                        MATCH (n:ContainerNode {run_id: $run_id})
                        OPTIONAL MATCH (n)-[r]->(m:ContainerNode {run_id: $run_id})
                        RETURN collect(DISTINCT properties(n)) AS nodes,
                               collect(DISTINCT {
                                   source: n.node_id,
                                   type: type(r),
                                   target: m.node_id,
                                   props: properties(r)
                               }) AS edges
                        """,
                        run_id=run_id,
                    )
                    record = await result.single()
                    if record:
                        snapshot = {
                            "nodes": record["nodes"] or [],
                            "edges": record["edges"] or [],
                        }
                    await session.run("MATCH (n {run_id: $run_id}) DETACH DELETE n", run_id=run_id)
                return self._sanitize_for_json(snapshot)
            except Exception:
                pass

        if run_id in self._in_memory_fallback:
            g = self._in_memory_fallback.pop(run_id)
            snapshot = {
                "nodes": list(g["nodes"].values()),
                "edges": g["edges"],
            }
        return self._sanitize_for_json(snapshot)

    @staticmethod
    def _sanitize_for_json(val):
        if isinstance(val, dict):
            return {k: EphemeralGraphManager._sanitize_for_json(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [EphemeralGraphManager._sanitize_for_json(v) for v in val]
        elif hasattr(val, "isoformat"):
            return val.isoformat()
        elif hasattr(val, "__str__") and type(val).__name__ in ("DateTime", "Date", "Time"):
            return str(val)
        return val

    @asynccontextmanager
    async def simulation_graph_scope(self, run_id: str, env_id: str, topology_template: dict):
        """Asynchronous context manager governing the ephemeral lifecycle of a run."""
        await self.hydrate_environment(run_id, env_id, topology_template)
        try:
            yield self
        finally:
            await self.snapshot_and_teardown(run_id)


# Global singleton instance
ephemeral_neo4j = EphemeralGraphManager()
