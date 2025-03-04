from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Track(_message.Message):
    __slots__ = ("speed", "course")
    SPEED_FIELD_NUMBER: _ClassVar[int]
    COURSE_FIELD_NUMBER: _ClassVar[int]
    speed: float
    course: float
    def __init__(self, speed: _Optional[float] = ..., course: _Optional[float] = ...) -> None: ...
