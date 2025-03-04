# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Worker Configuration Models"""
from asyncio import StreamReader, StreamWriter
from asyncio_dgram.aio import DatagramClient, DatagramServer
from typing import List, NamedTuple
from .io.tcp import TLSConf


TAG_BCAST = "bcast"
TAG_NOBCAST = "no_bcast"
TAG_GLOBALCHAT = "global_chat"
TAG_MARTI = "marti"

class WorkerConf(NamedTuple):
    url: str
    enabled: bool = True
    force_legacy: bool = False
    force_takp: bool = False
    username: str = ""
    password: str = ""
    local_net: str = ""
    tx_delay: float = 0.0
    mesh_ttl: int = 1
    mesh_mode: str = "rw"
    tags: List[str] = None
    tls: TLSConf = TLSConf()

class WorkerContext(NamedTuple):
    reader: StreamReader|DatagramServer
    writer: StreamWriter|DatagramClient
    delay: float = 0.0
    force_legacy: bool = False
    force_takp: bool = False
    uid: str = ""
    url: str = ""
    local_ip: str = ""
    tags: List[str] = None
