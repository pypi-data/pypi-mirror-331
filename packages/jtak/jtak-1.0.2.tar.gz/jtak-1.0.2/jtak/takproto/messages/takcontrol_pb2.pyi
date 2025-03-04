from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TakControl(_message.Message):
    __slots__ = ("minProtoVersion", "maxProtoVersion", "contactUid")
    MINPROTOVERSION_FIELD_NUMBER: _ClassVar[int]
    MAXPROTOVERSION_FIELD_NUMBER: _ClassVar[int]
    CONTACTUID_FIELD_NUMBER: _ClassVar[int]
    minProtoVersion: int
    maxProtoVersion: int
    contactUid: str
    def __init__(self, minProtoVersion: _Optional[int] = ..., maxProtoVersion: _Optional[int] = ..., contactUid: _Optional[str] = ...) -> None: ...
