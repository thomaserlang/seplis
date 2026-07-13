from dataclasses import dataclass
from typing import Annotated, TypedDict

from pydantic import Field

from .user_field_constraints_schemas import PasswordStr


@dataclass(slots=True, kw_only=True)
class UserAuthenticated:
    id: int
    token: str | None = None
    scopes: list[str] | None = None


class UserChangePassword(TypedDict):
    current_password: Annotated[str, Field(min_length=1)]
    new_password: PasswordStr


class TokenCreate(TypedDict):
    login: str
    password: str


@dataclass(slots=True, kw_only=True)
class Token:
    access_token: str
    token_type: str = 'bearer'
