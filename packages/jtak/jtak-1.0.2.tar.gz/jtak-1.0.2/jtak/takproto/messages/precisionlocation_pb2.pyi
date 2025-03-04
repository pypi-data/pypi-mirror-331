from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PrecisionLocation(_message.Message):
    __slots__ = ("geopointsrc", "altsrc")
    GEOPOINTSRC_FIELD_NUMBER: _ClassVar[int]
    ALTSRC_FIELD_NUMBER: _ClassVar[int]
    geopointsrc: str
    altsrc: str
    def __init__(self, geopointsrc: _Optional[str] = ..., altsrc: _Optional[str] = ...) -> None: ...
