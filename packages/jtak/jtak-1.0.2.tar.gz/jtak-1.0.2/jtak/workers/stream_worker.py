# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""TakWorker for Stream (stcp/tls) connections"""
import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Tuple
from ..cot import cot_base
from ..takproto import (
    MAX_PROTO_VERSION, TakMessage, CotEvent, serialize,
    deserialize_stream_header, serialize_stream_header,
    convert_to_protobuf
)
from .conf import TAG_BCAST, TAG_MARTI, WorkerContext, WorkerConf
from .io.tcp import get_io
from .tak_worker import TakWorker

logger = logging.getLogger(__name__)

class StreamWorker(TakWorker):

    @classmethod
    async def create(cls, wc: WorkerConf, uid: str = ""):
        """Create a worker to handle tak stream protocol"""

        reader, writer = await get_io(wc.url, wc.tls)

        conf = WorkerContext(
            reader, writer,
            url=wc.url,
            uid=uid,
            delay=wc.tx_delay,
            force_legacy=wc.force_legacy,
            force_takp=False,
            tags=wc.tags
        )

        return cls(conf)

    def __init__(self, ctx: WorkerContext):
        super().__init__(ctx)
        self.negotiating = False
        self.negotiation_expiration = None
        self.tags.update([TAG_MARTI, TAG_BCAST])


    async def send_cot(self, msg):
        """enqueue outbound message"""

        # drop messages during negotiation
        if self.negotiating:
            self.negotiating = datetime.now() < self.negotiation_expiration
        else:
            await super().send_cot(msg)

    async def _tx(self, msg):
        """transmit data"""

        data = serialize(msg, self.proto_version)
        hdr = serialize_stream_header(len(data)) if self.proto_version else b''
        self.ctx.writer.write(hdr + data)
        await self.ctx.writer.drain()

        logger.debug(f"--TX--> {self.ctx.url} {hdr + data}")


    async def _rx(self) -> TakMessage:
        """receive data"""

        if self.proto_version:
            _, size = await self.read_takproto_header(self.ctx.reader)
            data = await self.ctx.reader.read(size)
            msg = TakMessage()
            msg.ParseFromString(data)

        else:
            data = await self.ctx.reader.readuntil("</event>".encode())
            msg = convert_to_protobuf(data)
            if not self.ctx.force_legacy:
                await self._negotiate(msg.cotEvent)

        logger.debug(f"<--RX-- {self.ctx.url} {data}")
        logger.debug(f"<--RX-- {self.ctx.url} {msg}")

        return msg

    async def read_takproto_header(self, stream: asyncio.StreamReader) -> Tuple[int, int]:
        """Extract protobuf message size from stream header"""

        hdr: bytes = await stream.read(2)

        while hdr[-1] & 0x80:
            hdr += await stream.read(1)

        return deserialize_stream_header(hdr)

    async def _negotiate(self, cot: CotEvent):
        """Peek at inbound message"""

        # handle proto negotiation
        if cot.type == "t-x-takp-v":
            await self.negotiate_proto(cot)

        # handle proto resolution
        if cot.type == "t-x-takp-r":
            self.resolve_proto(cot)

    async def negotiate_proto(self, takp):
        """Respond to streaming protocol negotation"""

        detail = ET.fromstring(takp.detail.xmlDetail)
        supported = [e.attrib["version"] for e in detail.findall(".//TakProtocolSupport")]

        if str(MAX_PROTO_VERSION) in supported:
            self.negotiating = True
            await asyncio.sleep(0.5)
            await super().send_cot(
                self.generate_takp_cot()
            )

    def resolve_proto(self, takp):
        """Handle stream proto negotiation result"""

        detail = ET.fromstring(takp.detail.xmlDetail)
        ok = bool(detail.find(".//TakResponse").attrib["status"])
        self.proto_version = MAX_PROTO_VERSION if ok else 0
        self.negotiating = False
        logger.info(f"TAK PROTO = {self.proto_version}")

    def generate_takp_cot(self):
        """Generate TAKP stream negotiation cot"""

        cot = cot_base(self.ctx.uid, "t-x-takp-q")
        detail = ET.SubElement(cot, "detail")
        takc = ET.SubElement(detail, "TakControl")
        ET.SubElement(takc, "TakRequest", {"version": str(MAX_PROTO_VERSION)})
        return cot
