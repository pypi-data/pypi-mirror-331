# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""
TakWorker for Mesh (udp) "connections"

Although udp is connectionless, this worker *models* a connection.
It handles tx to the configured peer endpoint or to a dynamically
specified endpoint depending on whether the tx queue delivers a
msg or a (msg, endpoint) tuple, respectively. So any MeshWorker
can also be used as a udp-direct worker as well.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, NamedTuple
from ..takproto import deserialize, serialize, serialize_takc, MAX_PROTO_VERSION, TakMessage
from .conf import TAG_BCAST, TAG_NOBCAST, WorkerContext, WorkerConf
from .io.udp import get_io
from .io.net import resolve_local_ip
from .tak_worker import TakWorker


logger = logging.getLogger(__name__)

class MeshDeviceProto(NamedTuple):
    uid: str
    min: int = 0
    max: int = 0
    ts: datetime = None

class MeshWorker(TakWorker):

    @classmethod
    async def create(cls, wc: WorkerConf, uid: str = ""):
        """Create a worker to handle tak mesh protocol"""

        iface = resolve_local_ip(wc.local_net)
        url = wc.url.replace("0.0.0.0", iface.ip).replace("*", iface.ip)

        reader, writer = await get_io(url, iface, wc.mesh_mode, wc.mesh_ttl)

        conf = WorkerContext(
            reader, writer,
            url=url,
            uid=uid,
            delay=wc.tx_delay,
            force_legacy=wc.force_legacy,
            force_takp=wc.force_takp,
            local_ip=iface.ip,
            tags=wc.tags
        )

        return cls(conf)

    def __init__(self, ctx: WorkerContext):
        """initialize worker"""

        super().__init__(ctx)
        self.takc: Dict[str, MeshDeviceProto] = {}
        if self.ctx.writer and not self.has_tag(TAG_NOBCAST):
            self.tags.add(TAG_BCAST)

    async def run(self):
        """run worker tasks"""

        await super().run(
            self._takc_loop()
        )

    async def _tx(self, msg):
        """transmit data"""

        msg, endpoint = msg if isinstance(msg, tuple) else (msg, None)

        if self.ctx.writer and not endpoint:
            data = bytes([0xbf, self.proto_version, 0xbf]) if self.proto_version else b''
            data += serialize(msg, self.proto_version)
            await self.ctx.writer.send(data)
            logger.debug(f"--TX--> {self.ctx.url} {data}")

        # for udp a reader also serves as a direct writer
        elif self.ctx.reader and ":udp" in endpoint:
            host, port = endpoint.split(":", 2)
            await self.ctx.reader.send(msg, (host, int(port)))
            logger.debug(f"--TX--> {self.ctx.url} --> udp://{host}:{port} {msg}")


    async def _rx(self) -> TakMessage:
        """receive data"""

        data, _ = await self.ctx.reader.recv()
        v = int(data[1]) if data[0] == b'\xbf' else 0
        msg = deserialize(data)

        if not self.forced_proto:
            changed = self.negotiate_mesh_proto(msg, v)
            if changed:
                await self.send_takc()

        logger.debug(f"<--RX-- {self.ctx.url} {data}")
        logger.debug(f"<--RX-- {self.ctx.url} {msg}")

        return msg

    async def send_takc(self):
        """send mesh takc message directly"""

        if self.ctx.writer:
            await self.ctx.writer.send(
                serialize_takc(self.ctx.uid)
            )

    async def _takc_loop(self):
        """periodically send takc message for mesh proto negotation"""

        if self.ctx.writer and not self.ctx.force_legacy:
            while not self.closing:
                await self.send_takc()
                await asyncio.sleep(60)

    def negotiate_mesh_proto(self, msg: TakMessage, v: int) -> bool:
        """set proto version based on tracked device versions (mesh negotiation)"""

        if not msg.takControl and not msg.cotEvent.detail.takv.device:
            return

        changed = False
        takc = None
        now = datetime.now()

        if msg.takControl:
            takc = MeshDeviceProto(
                msg.takControl.contactUid or msg.cotEvent.uid,
                msg.takControl.minProtoVersion or 1,
                msg.takControl.maxProtoVersion or 1,
                now
            )

        elif msg.cotEvent.detail.takv.device:
            takc = MeshDeviceProto(
                msg.cotEvent.uid,
                v,
                v,
                now
            )

        if takc and takc.uid:
            self.takc[takc.uid] = takc
            proto = 0

            for p in range(MAX_PROTO_VERSION, 0, -1):
                unsupported = [c for c in self.takc.values() if c.ts + timedelta(minutes=2) > now and c.max < p]

                if not len(unsupported):
                    proto = p
                    break

            if proto != self.proto_version:
                self.proto_version = proto
                changed = True
                logger.info(f"TAK PROTO = {self.proto_version}")

        return changed
