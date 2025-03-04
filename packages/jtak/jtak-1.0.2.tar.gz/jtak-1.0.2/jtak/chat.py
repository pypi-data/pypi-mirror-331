# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Functions and models for GeoChat handling"""
import xml.etree.ElementTree as ET
from typing import List, NamedTuple, Tuple
from .takproto import CotEvent

class GeoChat(NamedTuple):
    room_path: str
    room_name: str
    sender_uid: str
    sender_name: str
    text: str
    time: str

class ChatGroupMember(NamedTuple):
    uid: str
    name: str
    room_uid: str
    room_name: str

class ChatRoom(NamedTuple):
    uid: str
    name: str
    parent_uid: str
    parent_name: str

def _extract_detail(cot: CotEvent|ET.Element) -> ET.Element:
    """extract detail as element"""

    if type(cot) in [CotEvent]:
        return ET.fromstring(f"<detail>{cot.detail.xmlDetail}</detail>")
    else:
        return cot.find("detail")

def chat_group_members(cot: CotEvent|ET.Element, exclude_uid: List[str] = []) -> List[ChatGroupMember]:
    """extract contacts from flattened group hierarchy"""

    detail = _extract_detail(cot)
    # TODO: handle Kicked members and Deleted groups
    return _extract_group_contacts(detail.find("__chat/hierarchy/group"), exclude_uid)

def chat_detail(me: str, cot: CotEvent|ET.Element) -> GeoChat:
    """extract chat details from cot message"""

    detail = _extract_detail(cot)
    remarks = detail.find("remarks")
    chat = detail.find("__chat")
    group = chat.find("chatgrp")

    parent = chat.attrib["parent"]
    members = _extract_group_contacts(chat.find("hierarchy/group"))

    if parent == "UserGroups":
        room_path = members[-1].room_uid
        room_name = members[-1].room_name
    elif chat.attrib["id"] == me:
        room_path = f"/{parent}/{group.attrib['uid0']}"
        room_name = chat.attrib["senderCallsign"]
    else:
        room_path = f"/{parent}/{chat.attrib['id']}"
        room_name = chat.attrib["chatroom"]

    return GeoChat(
        room_path,
        room_name,
        group.attrib["uid0"],
        chat.attrib["senderCallsign"],
        remarks.text,
        remarks.attrib.get("time")
    )

def _extract_group_contacts(
        group: ET.Element,
        exclude_uid: List[str] = [],
        path: str = "",
        name: str = ""
) -> List[ChatGroupMember]:
    """recursively collect group contacts"""

    if group is None:
        return []

    results: List[ChatGroupMember] = []
    p = "/".join([path, group.attrib["uid"]])
    n = "/".join([name, group.attrib["name"]])

    results.extend([
        ChatGroupMember(
            c.attrib["uid"],
            c.attrib["name"],
            str(p),
            str(n)
        ) for c in group.findall("contact") if c.attrib["uid"] not in exclude_uid
    ])

    for g in group.findall("group"):
        results.extend(
            _extract_group_contacts(g, exclude_uid, p, n)
        )

    return results

def chat_group_hierarchy(members: List[ChatGroupMember]) -> ET.Element:
    """create group heirarchy from member list"""

    room_path = zip(
        members[-1].room_uid.split("/")[1:],
        members[-1].room_name.split("/")[1:],
    )

    hierachy = ET.Element("hierarchy")
    group = hierachy

    for uid,name in room_path:

        group = ET.SubElement(group, "group", attrib={
            "uid": uid,
            "name": name
        })

        [
            ET.SubElement(group, "contact", attrib={
                "uid": m.uid,
                "name": m.name
            })
            for m in members if m.room_uid.endswith(uid)
        ]

    return hierachy

def chat_room_detail(members: List[ChatGroupMember]) -> Tuple[ChatRoom, ET.Element|None]:
    """build room model for building a geochat cot message"""

    # pull room info for last member
    member = members[-1]

    path = list(zip(
        member.room_uid.split("/")[1:],
        member.room_name.split("/")[1:],
    ))

    room = ChatRoom(*path[-1], *path[-2])
    hierachy = chat_group_hierarchy(members) if member.room_uid.startswith("/UserGroups") else None
    return room, hierachy

# def test():
#     detail = ET.fromstring(
#         """
#         <detail><__chat><hierarchy>
#         <group uid=\"UserGroups\" name=\"Groups\">
#             <group uid=\"294e2422-92e4-449e-a018-f98f91309ff5\" name=\"fires\">
#                 <contact uid=\"ANDROID-2b21bc48f6bf6698\" name=\"jam\"/>
#                 <contact uid=\"jtak-7eff15c001\" name=\"jtak.dev\"/>
#                 <group uid=\"123456789\" name=\"fdc\">
#                     <contact uid=\"jtak-7eff15c002\" name=\"jtak.not\"/>
#                 </group>
#             </group>
#         </group>
#         </hierarchy></__chat></detail>
#         """
#     )
#     members = _extract_group_contacts(detail.find("__chat/hierarchy/group"), [])
#     h = chat_group_hierarchy(members)
#     return members, h
