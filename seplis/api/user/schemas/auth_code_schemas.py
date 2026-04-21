from datetime import datetime
from typing import Annotated, TypedDict

from pydantic import BaseModel, ConfigDict, StringConstraints


class AuthCode(BaseModel):
    code: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthCodeRedeem(TypedDict):
    code: Annotated[
        str,
        StringConstraints(
            min_length=6, max_length=6, pattern='^[0-9]{6}$', strip_whitespace=True
        ),
    ]


class AuthCodeRedeemed(BaseModel):
    user_id: int
    scopes: list[str]

    model_config = ConfigDict(from_attributes=True)
