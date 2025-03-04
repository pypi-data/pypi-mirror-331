# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Functions and models for handling the Tak User"""
import random
from dataclasses import dataclass
from typing import NamedTuple

@dataclass
class CotEventPoint():
    lat: float = 0.0
    lon: float = 0.0
    hae: float = 0.0
    ce: float = 99999
    le: float = 99999

    def asdict(self):
        return {
            "lat": "{:.6f}".format(self.lat),
            "lon": "{:.6f}".format(self.lon),
            "hae": "{:.3f}".format(self.hae),
            "ce": str(self.ce),
            "le": str(self.le),
        }

@dataclass
class CotEventContact():
    callsign: str = ""
    endpoint: str = ""
    def asdict(self):
        return {
            "callsign": self.callsign,
            "endpoint": self.endpoint
        }

@dataclass
class CotEventGroup():
    name: str = "Cyan"
    role: str = "Team Member"
    def asdict(self):
        return {
            "name": self.name,
            "role": self.role
        }

@dataclass
class CotEventTrack():
    speed: float = 0.0
    course: float = 0.0
    def asdict(self):
        return {
            "speed": "{:.1f}".format(self.speed),
            "course": "{:.1f}".format(self.course)
        }

@dataclass
class CotEventStatus():
    battery: int = 0
    def asdict(self):
        return { "battery": str(self.battery)}

class TakUser(NamedTuple):
    uid: str
    cot_type: str = "a-f-G"
    group: CotEventGroup = CotEventGroup()
    contact: CotEventContact = CotEventContact()
    point: CotEventPoint = CotEventPoint()
    track: CotEventTrack = CotEventTrack()
    status: CotEventStatus = CotEventStatus()

class UserConf(NamedTuple):
    uid: str = ""
    callsign: str = ""
    cot_type: str = "a-f-G"
    team: str = "Cyan"
    role: str = "Team Member"
    lat: float = 0.0
    lon: float = 0.0
    hae: float = 0.0

def create_user(uc: UserConf) -> TakUser:
    """Map UserConf to TakUser"""

    uid = uc.uid or f"jtak-{random.randbytes(8).hex()}"
    user = TakUser(uid, uc.cot_type)
    user.contact.callsign = uc.callsign
    user.group.name = uc.team
    user.group.role = uc.role
    user.point.lat = uc.lat
    user.point.lon = uc.lon
    user.point.hae = uc.hae
    user.point.ce = 30 if uc.lat else 99999
    user.point.le = 30 if uc.lat else 99999
    return user
