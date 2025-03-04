# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Base TakWorker"""
import abc
import asyncio
import logging
import random
from typing import List
from ..takproto import MAX_PROTO_VERSION
from ..workers.conf import WorkerContext


logger = logging.getLogger(__name__)

class TakWorker:
    def __init__(self, ctx: WorkerContext):
        """initialize TakWorker"""

        self.ctx = ctx
        self.rxq = asyncio.Queue(100)
        self.txq = asyncio.Queue(100)
        self.forced_proto = self.ctx.force_legacy or self.ctx.force_takp
        self.proto_version = MAX_PROTO_VERSION if self.ctx.force_takp else 0
        self.tags = set(self.ctx.tags or [])
        self.closing = False
        logger.info(f"{self.__class__.__name__} created with {self.ctx.url}")

    async def run(self, *additional_tasks):
        """run worker tasks"""

        await asyncio.gather(
            self._tx_loop(),
            self._rx_loop(),
            *additional_tasks
        )

    def has_tag(self, tag: str|List[str], all: bool = False) -> bool:
        """check existence of tags"""

        if not isinstance(tag, list):
            tag = tag.split()

        s = self.tags
        t = set(tag)
        r = len(t - s) == 0 if all else len(s & t) > 0
        return r

    def close(self):
        """graceful exit"""

        self.closing = True

        if self.ctx.reader and hasattr(self.ctx.reader, "close"):
            self.ctx.reader.close()

        if self.ctx.writer and hasattr(self.ctx.writer, "close"):
            self.ctx.writer.close()

    async def send_cot(self, msg):
        """enqueue outbound messages"""

        if not msg:
            return

        if not isinstance(msg, list):
            msg = [msg]

        await asyncio.gather(
            *[self.txq.put(m) for m in msg]
        )

    @abc.abstractmethod
    async def _tx(self, data):
        """transmit data (override this)"""
        pass

    @abc.abstractmethod
    async def _rx(self):
        """receive data (override this)"""
        return None

    async def _tx_loop(self):
        """Dequeue messages to transport"""

        q = self.txq

        while not self.closing:

            data = await q.get()

            if not data:
                continue

            await self._tx(data)

            await asyncio.sleep(
                -self.ctx.delay * random.random() if self.ctx.delay < 0 else self.ctx.delay
            )


    async def _rx_loop(self):
        """Enqueue messages from transport"""

        while self.ctx.reader and not self.closing:

            msg = await self._rx()

            if not msg:
                continue

            if msg.cotEvent.uid == self.ctx.uid or (msg.takControl.contactUid and msg.takControl.contactUid == self.ctx.uid):
                continue

            logger.info(f"<--RX {self.ctx.url} {msg.cotEvent.uid} {msg.cotEvent.detail.group.name} {msg.cotEvent.detail.contact.callsign}")

            if self.rxq.full():
                await self.rxq.get()

            await self.rxq.put((msg, self.ctx.url))
