from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import re
from homelink.settings import (
    MQTT_ROOT_CA,
    MQTT_ROOT_CA_REPOSITORY,
    MQTT_PRIVATE_KEY_SIZE,
)
from aiohttp import ClientTimeout, request


def format_csr(csr_pem):
    return (
        re.search(
            r"-+BEGIN CERTIFICATE REQUEST-+\s+(.*?)\s+-+END CERTIFICATE REQUEST-+",
            csr_pem,
            flags=re.DOTALL,
        )
        .group(1)
        .strip()
        .replace("\n", "")
    )


async def generate_csr():
    url = f"{MQTT_ROOT_CA_REPOSITORY}/{MQTT_ROOT_CA}"
    client_timeout = ClientTimeout(total=60)
    async with request("GET", url=url, timeout=client_timeout) as response:
        cert_data = await response.text()
        if response.status != 200 or "error" in cert_data:
            raise Exception("Failed to get root certificate")
    key = rsa.generate_private_key(public_exponent=65537, key_size=MQTT_PRIVATE_KEY_SIZE)
    bytes_private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "gentex")]))
        .sign(key, hashes.SHA512())
    )

    csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode(encoding="utf-8")

    return bytes_private_key, format_csr(csr_pem)
