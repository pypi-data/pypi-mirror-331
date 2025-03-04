# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Utility functions for generating CoT messages"""
import platform
import uuid
import xml.etree.ElementTree as ET
from typing import Dict, List
from .__version__ import __version__ as jtak_version
from .chat import ChatGroupMember, chat_room_detail
from .takproto import cot_time
from .user import TakUser

TAKV = {
    "device": platform.node(),
    "os": platform.platform(),
    "platform": "jtak",
    "version": jtak_version
}

def cot_base(uid, cot_type, stale=20, how="m-g", point: Dict=None):
    """Generate cot shell"""

    ts, _ = cot_time()
    sts, _ = cot_time(stale)

    cot = ET.Element("event", attrib={
        "version": "2.0",
        "type": cot_type,
        "uid": uid,
        "how": how,
        "time": ts,
        "start": ts,
        "stale": sts,
    })

    if point is not None:
        ET.SubElement(cot, "point", attrib=point)

    return cot

def cot_remove(uid: str, target_uid: str):
    """Generate a force delete cot message"""

    cot = cot_base(uid, "t-x-d-d", 0)

    detail = ET.SubElement(cot, "detail")

    ET.SubElement(detail, "link", attrib={
        "uid": f"{target_uid}",
        "relation": "none",
        "type": "none"
    })

    ET.SubElement(detail, "__forcedelete")

    return cot

def cot_sa(me: TakUser, stale: float = 30):
    """Generate SA cot xml"""

    cot = cot_base(me.uid, me.cot_type, stale, point=me.point.asdict())

    detail = ET.SubElement(cot, "detail")

    ET.SubElement(detail, "contact", attrib=me.contact.asdict())

    ET.SubElement(detail, "__group", attrib=me.group.asdict())

    ET.SubElement(detail, "status", attrib=me.status.asdict())

    ET.SubElement(detail, "track", attrib=me.track.asdict())

    ET.SubElement(detail, "precisionlocation", attrib={
        "geopointsrc": "GPS",
        "altsrc": "DTED"
    })

    ET.SubElement(detail, "takv", attrib=TAKV)

    ET.SubElement(detail, "uid", attrib={
        "JTAK": me.uid
    })

    return cot

def cot_chat(me: TakUser, members: List[ChatGroupMember], text: str) -> ET.Element:
    """generate geochat cot message"""

    room, hierarchy = chat_room_detail(members)

    msg_id = str(uuid.uuid4())
    uid = f"GeoChat.{me.uid}.{room.uid}.{msg_id}"

    cot = cot_base(uid, "b-t-f", 86400, point=me.point.asdict())

    detail = ET.SubElement(cot, "detail")

    chat = ET.SubElement(detail, "__chat", attrib={
        "parent": room.parent_uid,
        "groupOwner": "false",
        "messageId": msg_id,
        "chatroom": room.name,
        "id": room.uid,
        "senderCallsign": me.contact.callsign
    })

    grp = {f"uid{i}": v.uid for i,v in enumerate([me, *members])}
    grp["id"] = room.uid
    ET.SubElement(chat, "chatgrp", attrib=grp)

    if hierarchy:
        chat.append(hierarchy)

    ET.SubElement(detail, "link", attrib={
        "uid": me.uid,
        "type": me.cot_type,
        "relation": "p-p"
    })

    ET.SubElement(detail, "__serverdestination", attrib={
        "destinations": f"{me.contact.endpoint}:{me.uid}"
    })

    remarks = ET.SubElement(detail, "remarks", attrib={
        "source": f"BAO.F.ATAK.{me.uid}",
        "time": cot.attrib["time"]
    })
    if len(members) == 1:
        remarks.attrib["to"] = members[0].uid
    remarks.text = text

    return cot

def cot_add_marti(cot: ET.Element, dest: List[str]):
    """insert marti dest into cot message"""

    detail = cot.find("detail")
    marti = detail.find("detail/marti")

    if marti is not None:
        detail.remove(marti)

    marti = ET.SubElement(detail, "marti")
    for d in dest:
        ET.SubElement(marti, "dest", attrib={"callsign": d})
