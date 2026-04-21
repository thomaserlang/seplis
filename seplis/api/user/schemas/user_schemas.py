from dataclasses import dataclass
from datetime import datetime
from typing import NotRequired, Self, TypedDict

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator


class UserBasic(BaseModel):
    id: int
    username: str
    created_at: datetime
    scopes: list[str]

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    def scopes_check_str(self) -> Self:
        if isinstance(self.scopes, str):
            self.scopes = self.scopes.split(' ')
        return self


class UserPublic(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


@dataclass
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
