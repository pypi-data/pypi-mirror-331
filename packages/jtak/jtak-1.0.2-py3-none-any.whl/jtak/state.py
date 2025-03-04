# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Module to handle TAK network state"""
import asyncio
import json
import logging
import delimited_protobuf as dpb
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, NamedTuple, Set, Tuple
from .chat import ChatGroupMember, chat_group_members
from .takproto import TakMessage, CotEvent


logger = logging.getLogger(__name__)
ATOM_STATE_FILE = "tak_state_atoms.tmp"
CONTACT_STATE_FILE = "tak_state_contacts.tmp"
GROUP_STATE_FILE = "tak_state_groups.tmp"
STATE_CLEAN_INTERVAL = 10
STALE_GRACE_SECONDS = 300
STREAMING_ENDPOINT = "*:-1:stcp"
ALL_CHAT_ROOMS = "All Chat Rooms"
ALL_CHAT_ROOMS_HINT = "/"

class StateContact(NamedTuple):
    uid: str
    callsign: str
    endpoint: str
    local_ep: str
    ts: int = 0

class TakState():
    def __init__(self, uid: str, data_path: str|Path = '.'):
        """initialize TakState with client uid and data_path of state storage"""

        self.me = uid
        self.path = Path(data_path)
        self.dirty = False
        self.atoms: Dict[str, CotEvent] = {}
        self.contacts: Dict[str, StateContact] = {}
        self.group_members: Set[ChatGroupMember] = set()
        self._load()

    def __del__(self):
        if self.dirty:
            self._save()

    async def run(self):
        """run periodic tasks"""

        await asyncio.gather(
            self._clean_loop()
        )

    def _load(self):
        """load any persisted state"""
        try:
            path = self.path / ATOM_STATE_FILE
            logger.info(f"loading TAK state from {path}")
            with open(path, "rb") as fh:
                while True:
                    cot = dpb.read(fh, CotEvent)
                    if cot:
                        self.atoms[cot.uid] = cot
                    else:
                        break
        except:
            pass

        try:
            path = self.path / CONTACT_STATE_FILE

            if path.stat().st_mtime + 120 < datetime.now().timestamp():
                path.unlink()

            logger.info(f"loading TAK state from {path}")
            with open(path, "r") as fh:
                contacts = json.load(fh)
                if len(contacts):
                    self.contacts = {f"{c.uid}:{c.endpoint}": c for c in contacts}
        except Exception as ex:
            pass

        try:
            path = self.path / GROUP_STATE_FILE

            if path.stat().st_mtime + 36000 < datetime.now().timestamp():
                path.unlink()

            logger.info(f"loading TAK state from {path}")
            with open(path, "r") as fh:
                self.group_members = set(ChatGroupMember(*m) for m in json.load(fh))

        except Exception as ex:
            pass

    def _save(self):
        """persist state to file"""
        path = self.path / ATOM_STATE_FILE
        with open(path, "wb") as fh:
            for c in self.atoms.values():
                dpb.write(fh, c)

        path = self.path / CONTACT_STATE_FILE
        with open(path, "w") as fh:
            json.dump(list(self.contacts.values()), fh, indent=2)

        path = self.path / GROUP_STATE_FILE
        with open(path, "w") as fh:
            json.dump(list(self.group_members), fh, indent=2)

    async def _clean_loop(self):
        """clean stale state"""

        while True:
            await self._clean()
            await asyncio.sleep(STATE_CLEAN_INTERVAL)

    async def _clean(self):
        """clean stale state"""

        for c in self.stale(grace=STALE_GRACE_SECONDS):
            self.atoms.pop(c.uid)
            self.dirty = True

        ts = datetime.now().timestamp() - 120
        for c in list(self.contacts.values()):
            if c.ts < ts:
                self.contacts.pop(f"{c.uid}:{c.endpoint}")
                self.dirty = True

        if self.dirty:
            self._save()
            self.dirty = False

    def update(self, msg: TakMessage, ep: str):
        """update state"""

        cot = msg.cotEvent

        if cot.type.startswith("a"):
            self.atoms[cot.uid] = cot
            self.dirty = True

            if cot.detail.contact.endpoint:
                self.contacts[f"{cot.uid}:{cot.detail.contact.endpoint}"] = StateContact(
                    cot.uid,
                    cot.detail.contact.callsign,
                    cot.detail.contact.endpoint,
                    ep,
                    datetime.now().timestamp()
                )

                if cot.detail.group.name:
                    room_id = "/".join(["", "TeamGroups", cot.detail.group.name])
                    room_name = "/".join(["", "Teams", cot.detail.group.name])
                    self.group_members.add(
                        ChatGroupMember(cot.uid, cot.detail.contact.callsign, room_id, room_name)
                    )

        if cot.type.startswith("b") and cot.uid.startswith("GeoChat"):
            self.group_members.update(
                chat_group_members(cot, [self.me])
            )
            self.dirty = True

    def stale(self, only_mine: bool = False, grace: int = 0):
        """get stale state values"""

        now = (datetime.now(timezone.utc).timestamp() - grace) * 1000
        values = (c for c in self.atoms.values() if c.staleTime < now)

        if only_mine:
            values = (c for c in values if c.uid == self.uid)

        return list(values)

    def find_contacts(self, uids: List[str]) -> Tuple[List[StateContact], List[StateContact], bool]:
        """find endpoints for uids organized by delivery mode"""

        contacts = set(c for c in self.contacts.values() if c.uid in uids)
        streaming = set(c for c in contacts if c.endpoint == STREAMING_ENDPOINT)

        return contacts - streaming, streaming, ALL_CHAT_ROOMS in uids


    def find_members(self, target: str) -> List[ChatGroupMember]:
        """find group members by matching room_id, uid or callsign"""

        if target == "/":
            return [
                ChatGroupMember(
                    ALL_CHAT_ROOMS,
                    ALL_CHAT_ROOMS,
                    f"/RootContactGroup/{ALL_CHAT_ROOMS}",
                    f"/Contact/{ALL_CHAT_ROOMS}"
                )
            ]

        group_members = (
            m for m in self.group_members
            if m.room_uid.startswith(target) or m.room_name.startswith(target)
        )

        target_user = target.split("/")[-1]
        direct_contacts = (
            ChatGroupMember(c.uid, c.callsign, f"/RootContactGroup/{c.uid}", f"/Contact/{c.callsign}")
            for c in self.contacts.values()
            if target_user in [c.uid, c.callsign]
        )

        return[*group_members, *direct_contacts]
