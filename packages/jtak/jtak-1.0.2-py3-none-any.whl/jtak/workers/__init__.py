# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

from .conf import WorkerConf, TAG_BCAST, TAG_GLOBALCHAT, TAG_MARTI, TAG_NOBCAST
from .direct_worker import DirectWorker
from .mesh_worker import MeshWorker
from .stream_worker import StreamWorker
from .tak_worker import TakWorker
from .io.tcp import TLSConf
from .io.net import NetworkInterface, resolve_local_ip



async def create_worker( wc: WorkerConf, uid: str = "") -> TakWorker:
    """Create a worker from a worker config"""

    from urllib.parse import urlparse
    url = urlparse(wc.url)

    type = MeshWorker
    type = StreamWorker if url.scheme in ["tls", "ssl", "stcp"] else type
    type = DirectWorker if url.scheme in ["tcp"] else type
    return await type.create(wc, uid)
