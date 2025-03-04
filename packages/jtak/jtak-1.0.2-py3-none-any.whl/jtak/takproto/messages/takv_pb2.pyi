from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Takv(_message.Message):
    __slots__ = ("device", "platform", "os", "version")
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    OS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    device: str
    platform: str
    os: str
    version: str
    def __init__(self, device: _Optional[str] = ..., platform: _Optional[str] = ..., os: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...
