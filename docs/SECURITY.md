# AEGIS Security Requirements & Threat Model

Compliant with Section 18 of the Master Specification.

## 1. Boundary Defense & Invariants ($\Omega$)

- **Deterministic Authorization**: Gemma is an analyst and advisor only. Gemma cannot execute commands or modify firewall/gateway configurations directly.
- **Subnet Restriction**: The Policy Agent will only accept IP addresses residing in the configured lab subnet (`172.31.10.0/24`). Out-of-scope, loopback (`127.0.0.0/8`), multicast, or host-adjacent router IPs are rejected.
- **Control Plane Immutability**: The Policy Agent and backend IPs cannot be blocked.
- **mTLS Enforcement**: The HAProxy gateway enforces client certificate verification with TLS 1.3 minimum. Connections without valid certificates signed by the lab CA are rejected at the TLS handshake.
- **Network Isolation**: The `aegis_target` network is configured with `internal: true`. The Attacker container cannot directly ping or establish TCP connections to protected targets.
- **Least Privilege Containers**: Containers drop all Linux capabilities (`cap_drop: [ALL]`), run as unprivileged users (`1000:1000`), enforce `no-new-privileges:true`, and set hard memory/CPU limits.
- **Docker Socket Isolation**: The Docker socket (`/var/run/docker.sock`) is never mounted into attack, AI, or backend containers.
- **Prompt Injection Defense**: Event logs fed to Gemma are treated as untrusted data, sanitized, truncated, and strictly validated against Pydantic models.

