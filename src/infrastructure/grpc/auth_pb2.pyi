from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LoginRequest(_message.Message):
    __slots__ = ("login", "password")
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    login: str
    password: str
    def __init__(self, login: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class TokenResponse(_message.Message):
    __slots__ = ("access_token", "token_type")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    token_type: str
    def __init__(self, access_token: _Optional[str] = ..., token_type: _Optional[str] = ...) -> None: ...

class ValidateRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class ValidateResponse(_message.Message):
    __slots__ = ("user_id", "login", "role", "is_valid")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    login: str
    role: str
    is_valid: bool
    def __init__(self, user_id: _Optional[int] = ..., login: _Optional[str] = ..., role: _Optional[str] = ..., is_valid: bool = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("login", "password", "role")
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    login: str
    password: str
    role: str
    def __init__(self, login: _Optional[str] = ..., password: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...

class UpdateUserRequest(_message.Message):
    __slots__ = ("id", "password", "role", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: int
    password: str
    role: str
    is_active: bool
    def __init__(self, id: _Optional[int] = ..., password: _Optional[str] = ..., role: _Optional[str] = ..., is_active: bool = ...) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    def __init__(self, result: bool = ...) -> None: ...

class UserListResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[UserResponse]
    def __init__(self, users: _Optional[_Iterable[_Union[UserResponse, _Mapping]]] = ...) -> None: ...

class UserResponse(_message.Message):
    __slots__ = ("id", "login", "role", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: int
    login: str
    role: str
    is_active: bool
    def __init__(self, id: _Optional[int] = ..., login: _Optional[str] = ..., role: _Optional[str] = ..., is_active: bool = ...) -> None: ...
