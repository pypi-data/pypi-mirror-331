from . import cotevent_pb2 as _cotevent_pb2
from . import takcontrol_pb2 as _takcontrol_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TakMessage(_message.Message):
    __slots__ = ("takControl", "cotEvent")
    TAKCONTROL_FIELD_NUMBER: _ClassVar[int]
    COTEVENT_FIELD_NUMBER: _ClassVar[int]
    takControl: _takcontrol_pb2.TakControl
    cotEvent: _cotevent_pb2.CotEvent
    def __init__(self, takControl: _Optional[_Union[_takcontrol_pb2.TakControl, _Mapping]] = ..., cotEvent: _Optional[_Union[_cotevent_pb2.CotEvent, _Mapping]] = ...) -> None: ...
