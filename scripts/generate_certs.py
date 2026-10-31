"""
AEGIS Local Development Certificate Generator.
Generates local development CA, Gateway server certificate (with serverAuth EKU & SANs),
and Client certificates (with clientAuth EKU) for mTLS authentication.
Compliant with Section 6.2 of AEGIS Master Implementation Spec.
"""

import datetime
import ipaddress
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

CERTS_DIR = Path(__file__).resolve().parent.parent / "infrastructure" / "certificates"


def generate_rsa_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


def save_key(key: rsa.RSAPrivateKey, path: Path):
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )


def save_cert(cert: x509.Certificate, path: Path):
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def generate_all_certificates(out_dir: Path = CERTS_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc)
    one_year = now + datetime.timedelta(days=365)

    print(f"[*] Generating AEGIS Development CA and mTLS Certificates in {out_dir}...")

    # 1. ROOT CA
    ca_key = generate_rsa_key()
    ca_name = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AEGIS Security Lab"),
        x509.NameAttribute(NameOID.COMMON_NAME, "AEGIS Root CA"),
    ])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    save_key(ca_key, out_dir / "ca.key")
    save_cert(ca_cert, out_dir / "ca.crt")
    print("  [+] CA generated: ca.crt, ca.key")

    # 2. GATEWAY SERVER CERT (serverAuth EKU + SANs)
    gw_key = generate_rsa_key()
    gw_name = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AEGIS Security Lab"),
        x509.NameAttribute(NameOID.COMMON_NAME, "aegis-gateway"),
    ])
    gw_sans = [
        x509.DNSName("aegis-gateway"),
        x509.DNSName("gateway"),
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        x509.IPAddress(ipaddress.IPv4Address("172.31.10.2")),
    ]
    gw_cert = (
        x509.CertificateBuilder()
        .subject_name(gw_name)
        .issuer_name(ca_name)
        .public_key(gw_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(one_year)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.SubjectAlternativeName(gw_sans), critical=False)
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )
    save_key(gw_key, out_dir / "gateway.key")
    save_cert(gw_cert, out_dir / "gateway.crt")
    # HAProxy bundle (cert + key)
    (out_dir / "gateway.pem").write_bytes(
        (out_dir / "gateway.crt").read_bytes() + b"\n" + (out_dir / "gateway.key").read_bytes()
    )
    print("  [+] Gateway server cert generated: gateway.crt, gateway.key, gateway.pem")

    # 3. BACKEND CLIENT CERT (clientAuth EKU)
    be_key = generate_rsa_key()
    be_name = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AEGIS Security Lab"),
        x509.NameAttribute(NameOID.COMMON_NAME, "aegis-backend-client"),
    ])
    be_cert = (
        x509.CertificateBuilder()
        .subject_name(be_name)
        .issuer_name(ca_name)
        .public_key(be_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(one_year)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )
    save_key(be_key, out_dir / "backend-client.key")
    save_cert(be_cert, out_dir / "backend-client.crt")
    print("  [+] Backend client cert generated: backend-client.crt, backend-client.key")

    # 4. ATTACKER LAB CLIENT CERT (clientAuth EKU)
    att_key = generate_rsa_key()
    att_name = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AEGIS Security Lab"),
        x509.NameAttribute(NameOID.COMMON_NAME, "aegis-attacker-client"),
    ])
    att_cert = (
        x509.CertificateBuilder()
        .subject_name(att_name)
        .issuer_name(ca_name)
        .public_key(att_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(one_year)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )
    save_key(att_key, out_dir / "attacker-client.key")
    save_cert(att_cert, out_dir / "attacker-client.crt")
    print("  [+] Attacker client cert generated: attacker-client.crt, attacker-client.key")

    # 5. UNTRUSTED CERT (signed by a rogue CA for negative-security testing)
    rogue_ca_key = generate_rsa_key()
    rogue_ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Rogue Untrusted CA")])
    rogue_ca_cert = (
        x509.CertificateBuilder()
        .subject_name(rogue_ca_name)
        .issuer_name(rogue_ca_name)
        .public_key(rogue_ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(one_year)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(rogue_ca_key, hashes.SHA256())
    )
    untrusted_key = generate_rsa_key()
    untrusted_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "untrusted-client")])
    untrusted_cert = (
        x509.CertificateBuilder()
        .subject_name(untrusted_name)
        .issuer_name(rogue_ca_name)
        .public_key(untrusted_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(one_year)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]), critical=True)
        .sign(rogue_ca_key, hashes.SHA256())
    )
    save_key(untrusted_key, out_dir / "untrusted-client.key")
    save_cert(untrusted_cert, out_dir / "untrusted-client.crt")
    print("  [+] Untrusted test cert generated: untrusted-client.crt, untrusted-client.key")

    # Write README
    readme_content = """# AEGIS Certificate Store

Generated for local development and test simulation environments.
Contains:
- `ca.crt`, `ca.key`: Local Root Certificate Authority.
- `gateway.crt`, `gateway.key`, `gateway.pem`: HAProxy Gateway TLS 1.3 server credentials.
- `backend-client.crt`, `backend-client.key`: Backend mTLS client certificate.
- `attacker-client.crt`, `attacker-client.key`: Attacker lab mTLS client certificate.
- `untrusted-client.crt`, `untrusted-client.key`: Untrusted certificate used for negative security testing.

To regenerate at any time:
```powershell
.\\scripts\\generate-certs.ps1
```
"""
    (out_dir / "README.md").write_text(readme_content, encoding="utf-8")
    print("[*] Certificate generation complete.")


if __name__ == "__main__":
    generate_all_certificates()

