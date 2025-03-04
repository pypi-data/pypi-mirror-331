from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Group(_message.Message):
    __slots__ = ("name", "role")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    name: str
    role: str
    def __init__(self, name: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...
