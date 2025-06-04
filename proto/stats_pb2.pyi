from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Metric(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VIEWS: _ClassVar[Metric]
    LIKES: _ClassVar[Metric]
    COMMENTS: _ClassVar[Metric]
VIEWS: Metric
LIKES: Metric
COMMENTS: Metric

class PostStats(_message.Message):
    __slots__ = ("post_id", "views", "likes", "comments")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    VIEWS_FIELD_NUMBER: _ClassVar[int]
    LIKES_FIELD_NUMBER: _ClassVar[int]
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    post_id: int
    views: int
    likes: int
    comments: int
    def __init__(self, post_id: _Optional[int] = ..., views: _Optional[int] = ..., likes: _Optional[int] = ..., comments: _Optional[int] = ...) -> None: ...

class DateCount(_message.Message):
    __slots__ = ("date", "count")
    DATE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    date: str
    count: int
    def __init__(self, date: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class PostDynamics(_message.Message):
    __slots__ = ("post_id", "data")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    post_id: int
    data: _containers.RepeatedCompositeFieldContainer[DateCount]
    def __init__(self, post_id: _Optional[int] = ..., data: _Optional[_Iterable[_Union[DateCount, _Mapping]]] = ...) -> None: ...

class PostRank(_message.Message):
    __slots__ = ("post_id", "count")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    post_id: int
    count: int
    def __init__(self, post_id: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class UserRank(_message.Message):
    __slots__ = ("user_id", "count")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    count: int
    def __init__(self, user_id: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class TopPostsResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[PostRank]
    def __init__(self, items: _Optional[_Iterable[_Union[PostRank, _Mapping]]] = ...) -> None: ...

class TopUsersResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[UserRank]
    def __init__(self, items: _Optional[_Iterable[_Union[UserRank, _Mapping]]] = ...) -> None: ...

class PostRequest(_message.Message):
    __slots__ = ("post_id",)
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: int
    def __init__(self, post_id: _Optional[int] = ...) -> None: ...

class TopRequest(_message.Message):
    __slots__ = ("metric",)
    METRIC_FIELD_NUMBER: _ClassVar[int]
    metric: Metric
    def __init__(self, metric: _Optional[_Union[Metric, str]] = ...) -> None: ...
