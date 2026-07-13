from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NotRequired, TypedDict

from pydantic import EmailStr


@dataclass(slots=True, kw_only=True)
class UserBasic:
    id: int
    username: str
    created_at: datetime
    scopes: list[str] | str

    def __post_init__(self) -> None:
        if isinstance(self.scopes, str):
            self.scopes = self.scopes.split(' ')


@dataclass(slots=True, kw_only=True)
class UserPublic:
    id: int
    username: str


@dataclass(slots=True, kw_only=True)
class User:
    id: int
    username: str
    email: str
    scopes: list[str]


class UserCreate(TypedDict):
    email: EmailStr
    username: str
    password: str


class UserUpdate(TypedDict, total=False):
    email: NotRequired[EmailStr | None]
    username: NotRequired[str | None]
