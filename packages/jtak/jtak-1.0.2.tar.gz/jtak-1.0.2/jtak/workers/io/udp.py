# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Utility functions for UDP connections"""
import asyncio_dgram
import ipaddress
import logging
import socket
import struct
from asyncio_dgram.aio import DatagramServer, DatagramClient
from typing import NamedTuple, Tuple
from urllib.parse import urlparse
from .net import NetworkInterface, is_multicast_ip


logger = logging.getLogger(__name__)

class SocketAddress(NamedTuple):
    ip: str
    port: int = 0

async def get_io(
    url: str,
    iface: NetworkInterface,
    mode: str = "rw",
    multicast_ttl: int = 1
) -> Tuple[DatagramServer, DatagramClient]:
    """Create a udp "connection" """

    url = urlparse(url)
    addr = SocketAddress(url.hostname, url.port)

    if addr.ip == iface.ip:
        mode = "r"

    writer = await udp_connect(addr, multicast_ttl) if "w" in mode else None
    reader = await udp_bind(addr, iface) if "r" in mode else None
    return reader, writer

async def udp_connect(addr: SocketAddress, multicast_ttl: int = 1) -> DatagramClient:
    """connect udp socket to remote endpoint"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(
        socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", multicast_ttl)
    )
    sock.connect(addr)
    writer = await asyncio_dgram.from_socket(sock)
    logger.debug(f"[socket] {writer.sockname} -> {writer.peername}")
    return writer

async def udp_bind(addr: SocketAddress, iface: NetworkInterface) -> DatagramServer:
    """bind a udp listening socket"""

    sock = udp_socket_default(True)
    register_multicast_group(sock, addr, iface.ip)
    try:
        sock.bind(addr)
    except:
        sock.bind((iface.ip, addr.port))
    reader = await asyncio_dgram.from_socket(sock)
    logger.debug(f"[socket] {reader.sockname} <- any")
    return reader

def udp_socket_default(reuse: bool = False):
    """get listener socket"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if reuse:
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass
    return sock

def register_multicast_group(sock, addr: SocketAddress, local_ip: str):
    """join multicast group"""

    if is_multicast_ip(addr.ip):
        ip = int(ipaddress.IPv4Address(local_ip))
        group = int(ipaddress.IPv4Address(addr.ip))
        sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            struct.pack("!LL", group, ip)
        )
