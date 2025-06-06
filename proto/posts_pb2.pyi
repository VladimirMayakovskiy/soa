from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Comment(_message.Message):
    __slots__ = ("id", "post_id", "user_id", "text", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    post_id: int
    user_id: str
    text: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., post_id: _Optional[int] = ..., user_id: _Optional[str] = ..., text: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateCommentRequest(_message.Message):
    __slots__ = ("post_id", "user_id", "text")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    post_id: int
    user_id: str
    text: str
    def __init__(self, post_id: _Optional[int] = ..., user_id: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class ListCommentsRequest(_message.Message):
    __slots__ = ("post_id", "page", "limit", "user_id")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: int
    page: int
    limit: int
    user_id: str
    def __init__(self, post_id: _Optional[int] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ..., user_id: _Optional[str] = ...) -> None: ...

class ListCommentsResponse(_message.Message):
    __slots__ = ("com", "total")
    COM_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    com: _containers.RepeatedCompositeFieldContainer[Comment]
    total: int
    def __init__(self, com: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class Post(_message.Message):
    __slots__ = ("id", "title", "description", "user_id", "created_at", "updated_at", "private", "tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    description: str
    user_id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    private: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., user_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., private: bool = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class PostRef(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_id: str
    def __init__(self, id: _Optional[int] = ..., user_id: _Optional[str] = ...) -> None: ...

class CreatePostRequest(_message.Message):
    __slots__ = ("title", "description", "user_id", "private", "tags")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    user_id: str
    private: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., user_id: _Optional[str] = ..., private: bool = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdatePostRequest(_message.Message):
    __slots__ = ("id", "title", "description", "user_id", "private", "tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    description: str
    user_id: str
    private: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., user_id: _Optional[str] = ..., private: bool = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class ListPostsRequest(_message.Message):
    __slots__ = ("page", "limit", "user_id")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    page: int
    limit: int
    user_id: str
    def __init__(self, page: _Optional[int] = ..., limit: _Optional[int] = ..., user_id: _Optional[str] = ...) -> None: ...

class ListPostsResponse(_message.Message):
    __slots__ = ("post", "total")
    POST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    post: _containers.RepeatedCompositeFieldContainer[Post]
    total: int
    def __init__(self, post: _Optional[_Iterable[_Union[Post, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...
