# AEGIS Certificate Store

Generated for local development and test simulation environments.
Contains:
- `ca.crt`, `ca.key`: Local Root Certificate Authority.
- `gateway.crt`, `gateway.key`, `gateway.pem`: HAProxy Gateway TLS 1.3 server credentials.
- `backend-client.crt`, `backend-client.key`: Backend mTLS client certificate.
- `attacker-client.crt`, `attacker-client.key`: Attacker lab mTLS client certificate.
- `untrusted-client.crt`, `untrusted-client.key`: Untrusted certificate used for negative security testing.

To regenerate at any time:
```powershell
.\scripts\generate-certs.ps1
```
