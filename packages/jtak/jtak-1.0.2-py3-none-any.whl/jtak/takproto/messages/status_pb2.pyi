from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Status(_message.Message):
    __slots__ = ("battery",)
    BATTERY_FIELD_NUMBER: _ClassVar[int]
    battery: int
    def __init__(self, battery: _Optional[int] = ...) -> None: ...
