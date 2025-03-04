from . import detail_pb2 as _detail_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CotEvent(_message.Message):
    __slots__ = ("type", "access", "qos", "opex", "uid", "sendTime", "startTime", "staleTime", "how", "lat", "lon", "hae", "ce", "le", "detail")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    QOS_FIELD_NUMBER: _ClassVar[int]
    OPEX_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    SENDTIME_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    STALETIME_FIELD_NUMBER: _ClassVar[int]
    HOW_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    HAE_FIELD_NUMBER: _ClassVar[int]
    CE_FIELD_NUMBER: _ClassVar[int]
    LE_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    type: str
    access: str
    qos: str
    opex: str
    uid: str
    sendTime: int
    startTime: int
    staleTime: int
    how: str
    lat: float
    lon: float
    hae: float
    ce: float
    le: float
    detail: _detail_pb2.Detail
    def __init__(self, type: _Optional[str] = ..., access: _Optional[str] = ..., qos: _Optional[str] = ..., opex: _Optional[str] = ..., uid: _Optional[str] = ..., sendTime: _Optional[int] = ..., startTime: _Optional[int] = ..., staleTime: _Optional[int] = ..., how: _Optional[str] = ..., lat: _Optional[float] = ..., lon: _Optional[float] = ..., hae: _Optional[float] = ..., ce: _Optional[float] = ..., le: _Optional[float] = ..., detail: _Optional[_Union[_detail_pb2.Detail, _Mapping]] = ...) -> None: ...
