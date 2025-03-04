# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""
TakWorker for Direct TCP connections

Direct comms involve a single message per connection.
Expects a (msg, endpoint) tuple from tx queue if the
worker wasn't created with a remote endpoint.
"""
import asyncio
import logging
from urllib.parse import urlparse
from ..takproto import serialize, deserialize
from .conf import TAG_BCAST, WorkerConf, WorkerContext
from .io.net import resolve_local_ip
from .tak_worker import TakWorker


logger = logging.getLogger(__name__)

class DirectWorker(TakWorker):

    @classmethod
    async def create(cls, wc: WorkerConf, uid: str = ""):
        """Create a worker to handle direct cot messaging"""

        iface = resolve_local_ip(wc.local_net)
        url = wc.url.replace("0.0.0.0", iface.ip).replace("*", iface.ip)

        conf = WorkerContext(
            None, None,
            url=url,
            uid=uid,
            force_legacy=wc.force_legacy,
            force_takp=wc.force_takp,
            local_ip=iface.ip,
            tags=wc.tags
        )

        return cls(conf)

    def __init__(self, ctx: WorkerContext):
        """initialize worker"""

        super().__init__(ctx)
        url = urlparse(self.ctx.url)
        self.local_endpoint: str = f"{self.ctx.local_ip}:{url.port}:tcp"
        self.peer_endpoint: str = None
        if url.hostname != self.ctx.local_ip:
            self.peer_endpoint = f"{url.hostname}:{url.port}:tcp"
            self.tags.add(TAG_BCAST)

    async def run(self):
        """run worker tasks"""

        ip, port, _ = self.local_endpoint.split(":")
        server = await asyncio.start_server(self._rx, ip, port)

        async with server:
            await super().run(
                server.serve_forever()
            )

    async def _rx(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle direct tcp cot reception"""

        data = await reader.read()

        writer.close()
        await writer.wait_closed()

        msg = deserialize(data)

        if self.rxq.full():
            await self.rxq.get()

        logger.debug(f"<--RX-- {self.ctx.url} {data}")
        logger.debug(f"<--RX-- {self.ctx.url} {msg}")

        await self.rxq.put((msg, self.ctx.url))

    async def _tx(self, msg):
        """transmit data direct to tcp endpoint"""

        msg, endpoint = msg if isinstance(msg, tuple) else (msg, self.peer_endpoint)
        if not endpoint:
            return

        try:
            host, port, _ = endpoint.split(":")
            _, writer = await asyncio.open_connection(host, port)

            data = serialize(msg, self.proto_version)

            writer.write(data)
            await writer.drain()
            writer.close()

            logger.debug(f"--TX--> {endpoint} {data}")

        except Exception as ex:
            logger.debug(f"--TX--X failed direct send to {endpoint} {ex}")
