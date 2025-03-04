# Copyright 2025 Carnegie Mellon University
# Licensed under a MIT (SEI)-style license, please see LICENSE.md or contact permission@sei.cmu.edu for full terms.

"""Functions for handling tak protocol and messages"""
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from google.protobuf.internal.decoder import _DecodeVarint
from google.protobuf.internal.encoder import _EncodeVarint
from io import BytesIO
from typing import List, Optional, Tuple, Type
from . import MAX_PROTO_VERSION
from .messages import TakMessage


FMT_TIME = "%Y-%m-%dT%H:%M:%SZ"
FMT_TIME_MS = "%Y-%m-%dT%H:%M:%S.%fZ"

COT_DETAIL_ATTRIBUTE_MAP = {
    "contact": ("", ["endpoint", "callsign"], str),
    "__group": ("group", ["name", "role"], str),
    "precisionlocation": ("precisionLocation", ["geopointsrc", "altsrc"], str),
    "status": ("", ["battery"], int),
    "takv": ("", ["device", "platform", "os", "version"], str),
    "track": ("", ["speed", "course"], float)
}

def cot_time(stale_seconds: int = 0, with_ms: bool = False) -> Tuple[str, int]:
    """generate current cot time as str and epoch milliseconds (timeMs)"""

    dt = datetime.now(timezone.utc) + timedelta(seconds=int(stale_seconds))
    fmt = FMT_TIME_MS if with_ms else FMT_TIME
    return dt.strftime(fmt), int(dt.timestamp() * 1000)

def parse_timestamp(value: str) -> int:
    """convert string datetime to epoch milliseconds"""

    fmt = FMT_TIME_MS if "." in value else FMT_TIME
    dt = datetime.strptime(value, fmt.replace("Z", "%z"))
    return int(dt.timestamp() * 1000)

def format_timestamp(timeMs: int, tz = timezone.utc, with_ms: bool = False) -> str:
    """convert epoch milliseconds to iso string"""

    dt = datetime.fromtimestamp(timeMs / 1000, tz)
    fmt = FMT_TIME_MS if with_ms else FMT_TIME
    return dt.strftime(fmt)

def deserialize_mesh(data: bytes) -> TakMessage:
    """deserialize mesh bytes into TakMessage"""

    msg = TakMessage()
    msg.ParseFromString(data[3:])
    return msg

def deserialize_stream(data: bytes) -> TakMessage:
    """deserialize stream bytes into TakMessage"""

    msg = TakMessage()
    index, _ = deserialize_stream_header(data)
    msg.ParseFromString(data[index])

def deserialize_stream_header(data: bytes) -> Tuple[int, int]:
    """parse body index and size"""

    size, index = _DecodeVarint(data, 1)
    return index, size

def deserialize(data: bytes, emit_xml: bool = False) -> Optional[TakMessage|ET.Element]:
    """deserialize received bytes into message object

    Returns TakMessage or ET.Element (XML) depending on emit_xml.
    """
    if data[0] == 0xbf:
        msg = deserialize_mesh(data) if data[2] == 0xbf else deserialize_stream(data)
        return convert_to_xml(msg) if emit_xml else msg

    else:
        return ET.fromstring(data.decode()) if emit_xml else convert_to_protobuf(data)

def serialize(msg: TakMessage|ET.Element, proto_v: int) -> bytes:
    """serialize message for transmission according to takproto version"""

    if not proto_v:
        if type(msg) not in [ET.Element]:
            msg = convert_to_xml(msg)
        return ET.tostring(msg, "utf-8", xml_declaration=True)

    else:
        if type(msg) in [ET.Element]:
            msg = convert_to_protobuf(msg)
        return msg.SerializeToString()

def serialize_stream_header(msg_len: int) -> bytes:
    """get stream header for message length"""
    bf = BytesIO()
    bf.write(b'\xbf')
    _EncodeVarint(bf.write, msg_len)
    return bf.getvalue()

def serialize_takc(uid: str = "", min: int = 1, max: int = MAX_PROTO_VERSION) -> bytes:
    """Generate takc proto message"""

    msg = TakMessage()
    msg.takControl.contactUid = uid

    if min > 1:
        msg.takControl.minProtoVersion = min

    if max > 1:
        msg.takControl.maxProtoVersion = max

    hdr = bytes([0xbf, MAX_PROTO_VERSION, 0xbf])
    return hdr + msg.SerializeToString()

def _merge_attributes(attributes: List[str], src, dst, t: Type = str):
    """Merge attribute from src to dst with cast"""

    if src is None or dst is None:
        return

    for a in attributes:
        val = src.get(a)
        if val:
            setattr(dst, a, t(val))

def convert_to_xml(msg: TakMessage) -> ET.Element:
    """Convert TakMessage into XML Element."""

    cot = msg.cotEvent

    event = ET.Element("event", attrib={
        "version": "2.0",
        "time": format_timestamp(cot.sendTime),
        "start": format_timestamp(cot.startTime),
        "stale": format_timestamp(cot.staleTime)
    })

    point = ET.SubElement(event, "point")
    _merge_attributes(["type", "access", "qos", "opex", "uid", "how"], cot, event)
    _merge_attributes(["lat", "lon", "hae", "le", "ce"], cot, point)

    detail = ET.fromstring(f"<detail>{cot.detail.xmlDetail}</detail>")
    event.append(detail)

    for k, (n,a,_) in COT_DETAIL_ATTRIBUTE_MAP.items():
        src = getattr(cot.detail, n or k)
        if src is not None:
            dst = ET.SubElement(detail, k)
            _merge_attributes(a, src, dst, str)

    return event

def convert_to_protobuf(xml: bytes|ET.Element) -> TakMessage:
    """Convert XML to TakMessage."""

    if type(xml) not in [ET.Element]:
        xml = ET.fromstring(xml.decode())

    handled_nodes = set()
    event: ET.Element = xml
    msg = TakMessage()
    cot = msg.cotEvent

    _merge_attributes(["type", "access", "qos", "opex", "uid", "how"], event, cot)
    _merge_attributes(["lat", "lon", "hae", "ce", "le"], event.find("point"), cot, float)
    cot.sendTime = parse_timestamp(event.attrib["time"])
    cot.startTime = parse_timestamp(event.attrib["start"])
    cot.staleTime = parse_timestamp(event.attrib["stale"])

    detail = event.find("detail")
    if detail is not None:

        for k, (n,a,t) in COT_DETAIL_ATTRIBUTE_MAP.items():
            node = detail.find(k)
            if node is not None:
                _merge_attributes(a, node, getattr(cot.detail, n or k), t)
                handled_nodes.add(node)

        cot.detail.xmlDetail = ''.join(
            ET.tostring(e, "unicode")
            for e in detail if e not in handled_nodes
        )

    if cot.uid.startswith("GeoChat"):
        msg.takControl.contactUid = cot.uid.split(".")[1]

    return msg
