# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Utility functions for TCP/TLS connections"""
import asyncio
import logging
import ssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from pathlib import Path
from typing import Tuple, NamedTuple
from urllib.parse import urlparse


logger = logging.getLogger(__name__)

class TLSConf(NamedTuple):
    hostname: str = ""
    ciphers: str = ""
    p12_path: str = ""
    p12_password: str = "atakatak"
    skip_verification: bool = False

async def get_io(url: str, tls: TLSConf = TLSConf()) -> Tuple[
    asyncio.StreamReader,
    asyncio.StreamWriter
]:
    """Create a tcp or tls connection."""

    url = urlparse(url)
    sslctx = pkcs12_to_sslctx(tls) if url.scheme in ["tls", "ssl"] else None
    hostname = tls.hostname if sslctx else None

    # TODO: wrap with shorter timeout

    return await asyncio.open_connection(
        url.hostname, url.port,
        ssl=sslctx, server_hostname=hostname
    )

def pkcs12_to_sslctx(conf: TLSConf) -> ssl.SSLContext:
    """Configure a TLS socket context from pkcs12 file."""

    # SSL Context
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.options |= ssl.OP_NO_TLSv1
    ctx.options |= ssl.OP_NO_TLSv1_1
    ctx.set_ciphers(conf.ciphers or "ALL")
    ctx.check_hostname = not conf.skip_verification
    ctx.verify_mode = ssl.VerifyMode.CERT_NONE if conf.skip_verification else ssl.VerifyMode.CERT_REQUIRED

    if not conf.p12_path or not Path(conf.p12_path).exists():
        raise Exception(f"Missing client certificate (pkcs12) [{conf.p12_path}]")

    with open(conf.p12_path, "rb") as fh:
        p12_data = fh.read()

    key, cert, certs = pkcs12.load_key_and_certificates(
        p12_data,
        str.encode(conf.p12_password)
    )

    cert_path = Path(conf.p12_path).with_suffix('.pem')
    with open(cert_path, "wb") as fh:
        fh.write(cert.public_bytes(serialization.Encoding.PEM))

    key_path = Path(conf.p12_path).with_suffix('.key')
    with open(key_path, "wb") as fh:
        fh.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
        ))

    ctx.load_cert_chain(cert_path, key_path, conf.p12_password)
    cert_path.unlink()
    key_path.unlink()

    if certs and len(certs):
        cadata = certs[0].public_bytes(serialization.Encoding.PEM).decode()
        ctx.load_verify_locations(cadata=cadata)
    else:
        logger.warning("PKCS12 file missing CA file. Assuming CA is already trusted on host.")

    if conf.skip_verification:
        logger.warning("Disabled TLS Server Certificate Verification. Do this for testing only!")

    return ctx
