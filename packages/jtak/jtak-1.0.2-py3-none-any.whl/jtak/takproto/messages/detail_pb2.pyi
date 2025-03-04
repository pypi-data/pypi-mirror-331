from . import contact_pb2 as _contact_pb2
from . import group_pb2 as _group_pb2
from . import precisionlocation_pb2 as _precisionlocation_pb2
from . import status_pb2 as _status_pb2
from . import takv_pb2 as _takv_pb2
from . import track_pb2 as _track_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Detail(_message.Message):
    __slots__ = ("xmlDetail", "contact", "group", "precisionLocation", "status", "takv", "track")
    XMLDETAIL_FIELD_NUMBER: _ClassVar[int]
    CONTACT_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    PRECISIONLOCATION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TAKV_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    xmlDetail: str
    contact: _contact_pb2.Contact
    group: _group_pb2.Group
    precisionLocation: _precisionlocation_pb2.PrecisionLocation
    status: _status_pb2.Status
    takv: _takv_pb2.Takv
    track: _track_pb2.Track
    def __init__(self, xmlDetail: _Optional[str] = ..., contact: _Optional[_Union[_contact_pb2.Contact, _Mapping]] = ..., group: _Optional[_Union[_group_pb2.Group, _Mapping]] = ..., precisionLocation: _Optional[_Union[_precisionlocation_pb2.PrecisionLocation, _Mapping]] = ..., status: _Optional[_Union[_status_pb2.Status, _Mapping]] = ..., takv: _Optional[_Union[_takv_pb2.Takv, _Mapping]] = ..., track: _Optional[_Union[_track_pb2.Track, _Mapping]] = ...) -> None: ...
