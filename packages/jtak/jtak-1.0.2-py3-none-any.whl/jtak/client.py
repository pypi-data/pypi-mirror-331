# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Base TakClient"""
import abc
import asyncio
import logging
from dataclasses import dataclass
from typing import Any, List
from urllib.parse import urlparse
from xml.etree.ElementTree import Element as XmlElement
from .chat import GeoChat, chat_detail
from .state import StateContact, TakState
from .takproto import TakMessage, CotEvent
from .user import UserConf, create_user
from .cot import cot_chat, cot_add_marti, cot_sa
from .workers import TakWorker, WorkerConf, create_worker, TAG_BCAST, TAG_GLOBALCHAT, TAG_MARTI
from .workers.conf import TAG_NOBCAST


logger = logging.getLogger(__name__)

@dataclass
class ClientConf():
    user: UserConf = UserConf()
    workers: List[WorkerConf] = None
    sa_interval: float = 30.0

class TakClient:

    @classmethod
    async def create(cls, cc: ClientConf, data_path: str = "."):
        """create instance of TakClient"""

        worker_conf = cc.workers or [
            WorkerConf("udp://239.2.3.1:6969"),
            WorkerConf("udp://224.10.10.1:17012", tags=[TAG_GLOBALCHAT, TAG_NOBCAST]),
            WorkerConf("tcp://0.0.0.0:4242")
        ]

        workers = [
            await create_worker(wc, cc.user.uid)
            for wc in worker_conf if wc.enabled
        ]

        return cls(cc, workers, data_path)

    """State and utilities for a TAK session"""
    def __init__(self, conf: ClientConf, workers: List[TakWorker], data_path: str = "."):
        """initialize client"""

        self.conf = conf
        self.workers: List[TakWorker] = workers
        self.inq = asyncio.Queue()
        self.upq = asyncio.Queue(100)
        self.me = create_user(conf.user)
        self.me.contact.endpoint = self.resolve_user_endpoint(workers)
        self.state: TakState = TakState(self.me.uid, data_path)
        self.closing = False
        self.runner = None
        logger.info(f"{self.__class__.__name__} initialized as user {conf.user.uid} ({conf.user.callsign})")

    async def run(self, *additional_tasks):
        """run client tasks"""

        self.runner = asyncio.gather(
            *[w.run() for w in self.workers],
            *[self._inbound_merge(w.rxq) for w in self.workers],
            self._sa_loop(),
            self._inbound_loop(),
            self.state.run(),
            *additional_tasks
        )

        await self.runner

    def close(self, sig=None, frame=None):
        """graceful shutdown"""

        self.closing = True

        for w in self.workers:
            w.close()

        self.runner.cancel()

    @abc.abstractmethod
    def sa_cot(self):
        """create current SA cot message"""

        return cot_sa(self.me)

    async def inbound(self):
        """generator to consume inbound messages"""

        while not self.closing:
            yield await self.upq.get()

    @abc.abstractmethod
    async def outbound(self, cot: Any, to: str = "", tags: List[str] = []):
        """Transforms and sends outbound messages.

        Pass in an XML Element or TakMessage or list thereof.
        Or override this to transform internal models into such.
        """
        if isinstance(cot, str):
            await self._outbound_geochat(cot, to)
            return

        if not isinstance(cot, list):
            cot = [cot]

        asyncio.gather(*[
            self._outbound_cot(c, to, tags)
            for c in cot
        ])

    async def _outbound_geochat(self, text: str, to: str):
        """construct and send a geochat message"""

        # resolve recipients
        members = self.state.find_members(to)

        if len(members) == 0:
            logger.debug(f"Failed to find contacts for geochat to '{to}'")
            return

        uids = [m.uid for m in members]
        direct, stream, all = self.state.find_contacts(uids)

        # construct geochat cot
        cot = cot_chat(self.me, members, text)

        if all:

            # enqueue for mesh global chat workers
            await asyncio.gather(*[
                w.send_cot(cot)
                for w in self.workers if w.has_tag(TAG_GLOBALCHAT)
            ])

            # enqueue for stream workers
            await self._outbound_stream(cot)

        else:

            # enqueue direct contacts
            await self._outbound_direct(cot, direct)

            # enqueue stream contacts
            await self._outbound_stream(cot, stream)

    async def _outbound_cot(self, cot: TakMessage|XmlElement, to: str = "", tag: List[str] = []):
        """enqueue outbound cot message to appropriate workers"""

        if not to:
            await self._outbound_broadcast(cot, tag)
            return

        # resolve recipients
        members = self.state.find_members(to)
        uids = [m.uid for m in members]
        direct, stream, _ = self.state.find_contacts(uids)

        # enqueue direct contacts
        await self._outbound_direct(cot, direct)

        # enqueue stream contacts
        await self._outbound_stream(cot, stream)

    async def _outbound_stream(self, cot: TakMessage|XmlElement, contacts: List[StateContact] = []):
        """enqueue for stream endpoints; if no contact enqueue for all stream endpoints"""

        if len(contacts):

            # enqueue for specified stream endpoints
            urls = set(c.local_ep for c in contacts)
            for url in urls:
                cot_add_marti(cot, [s.callsign for s in contacts if s.local_ep == url])
                worker = self._find_worker_by_url(url)
                if worker:
                    await worker.send_cot(cot)

        else:

            # enqueue for all stream endpoints
            cot_add_marti(cot, [self.me.contact.callsign])
            await asyncio.gather(*[
                w.send_cot(cot)
                for w in self.workers if w.has_tag(TAG_MARTI)
            ])

    async def _outbound_direct(self, cot: TakMessage|XmlElement, contacts: List[StateContact]):
        """enqueue direct message for each contact"""

        tasks = []

        for c in contacts:
            msg = cot
            h, p, scheme = c.endpoint.split(":")

            # check for worker connected to this endpoint
            worker = self._find_worker_by_url(f"{scheme}://{h}:{p}")

            if worker is None:

                # find a worker supporting the endpoint's scheme
                worker = self._find_worker_by_url(f"{scheme}://")

                # tuple cot with endpoint so worker knows where to send
                msg = (cot, c.endpoint)

            if worker:
                tasks.append(
                    worker.send_cot(msg)
                )

        await asyncio.gather(*tasks)

    async def _outbound_broadcast(self, cot: TakMessage|XmlElement, tags: List[str] = []):

        if not len(tags):
            tags = [TAG_BCAST]

        logger.debug(f"Enqueue cot for tagged workers '{' '.join(tags)}'")

        await asyncio.gather(*[
            w.send_cot(cot)
            for w in self.workers
            if w.has_tag(tags)
        ])

    @abc.abstractmethod
    async def _inbound_handler(self, cot: CotEvent|GeoChat) -> Any|None:
        """Transform inbound cot message.

        Override this if your inbound consumer wants something
        other than a protobuf CotEvent message.

        GeoChat messages are already transformed.

        A returned value will be propagated inbound.
        """
        return cot

    async def _inbound_merge(self, wq: asyncio.Queue):
        """merge worker rxq into client rxq"""

        while not self.closing:
            await self.inq.put(
                await wq.get()
            )

    async def _inbound_loop(self):
        """dequeue and process inbound messages"""

        while not self.closing:

            msg, ep = await self.inq.get()

            self.state.update(msg, ep)

            # convert cot to internal objects
            cot = msg.cotEvent
            if cot.type == "b-t-f" and cot.uid.startswith('GeoChat'):
                model = chat_detail(self.me.uid, cot)
            else:
                model = await self._inbound_handler(cot)

            if model:
                if self.upq.full():
                    self.upq.get_nowait()
                self.upq.put_nowait(model)

    async def _sa_loop(self):
        """loop for sending sa cot"""

        while self.conf.sa_interval and not self.closing:
            sa = self.sa_cot()
            if sa:
                await asyncio.gather(*[
                    w.send_cot(sa)
                    for w in self.workers if w.has_tag(TAG_BCAST)
                ])
                # await asyncio.sleep(1.0)
                await asyncio.sleep(self.conf.sa_interval)

    def resolve_user_endpoint(self, workers: List[TakWorker]) -> str:
        """Use last non-streaming worker as the default direct endpoint"""

        urls = [w.ctx.url for w in reversed(workers) if not w.has_tag(TAG_MARTI)]
        url = urls[0] if len(urls) else "stcp://*:-1"
        u = urlparse(url)
        return f"{u.netloc}:{u.scheme}"

    def _find_worker_by_url(self, url) -> TakWorker:
        """find worker by url matching"""

        try:
            return next(w for w in self.workers if w.ctx.url.startswith(url))
        except:
            return None
