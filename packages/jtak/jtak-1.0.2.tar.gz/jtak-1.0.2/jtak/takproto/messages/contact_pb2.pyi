from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Contact(_message.Message):
    __slots__ = ("endpoint", "callsign")
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    CALLSIGN_FIELD_NUMBER: _ClassVar[int]
    endpoint: str
    callsign: str
    def __init__(self, endpoint: _Optional[str] = ..., callsign: _Optional[str] = ...) -> None: ...
