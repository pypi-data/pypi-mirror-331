# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Functions to query local network settings"""
import ifaddr
import ipaddress
from typing import NamedTuple

class NetworkInterface(NamedTuple):
    ip: str
    adapter: str
    broadcast: str
    prefix: int

def is_ipaddress(value: str|int) -> bool:
    """Check if value is an ip address"""

    try:
        ipaddress.ip_network(value)
        return True
    except:
        return False

def is_multicast_ip(ip: str) -> bool:
    """Check if a ip is a multicast address"""

    try:
        return ipaddress.ip_address(ip).is_multicast
    except ValueError:
        return False

def to_broadcast_ip(ip: str, prefix: int) -> str:
    """convert ip/prefix to broadcast address"""

    iface = ipaddress.ip_interface(f"{ip}/{prefix}")
    return str(iface.network.broadcast_address)

def resolve_local_ip(target: str = None) -> NetworkInterface:
    """
    Heuristically determine local ip for multicast group registration.

    target can be a local ip address or adapter name

    Returns first found of the following:
    - specified ip
    - specified adapter
    - adapter starting with "w" (wifi)
    - adapter staring with "e" (ethernet)
    - adapter staring with "l" (loopback)

    as tuple(ip, adapter-name, network-prefix)
    """
    valid = is_ipaddress(target)
    ip = target if valid else None
    nic = (target or None) if not valid else None

    # get options
    nics = {a.nice_name: a for a in ifaddr.get_adapters()}
    ips = [x for k in nics for x in nics[k].ips if type(x.ip) is str]

    # if specified ip exists, use it
    try:
        match = next((x for x in ips if x.ip == ip))
        bcast = to_broadcast_ip(match.ip, match.network_prefix)
        return NetworkInterface(match.ip, match.nice_name, bcast, match.network_prefix)
    except:
        pass

    # if specified adapter exists, use it
    try:
        match = next((x for x in ips if nic in x.nice_name))
        bcast = to_broadcast_ip(match.ip, match.network_prefix)
        return NetworkInterface(match.ip, match.nice_name, bcast, match.network_prefix)
    except:
        pass

    # trying grabbing wi-fi then ethernet
    for t in ["w", "e", "l"]:
        try:
            match = next((x for x in ips if x.nice_name.lower().startswith(t)))
            bcast = to_broadcast_ip(match.ip, match.network_prefix)
            return NetworkInterface(match.ip, match.nice_name, bcast, match.network_prefix)
        except:
            pass

    return NetworkInterface("127.0.0.1", "loopback", "127.255.255.255", 8)
