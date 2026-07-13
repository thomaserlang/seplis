from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, TypedDict

from pydantic import StringConstraints


@dataclass(slots=True, kw_only=True)
class AuthCode:
    code: str
    expires_at: datetime


class AuthCodeRedeem(TypedDict):
    code: Annotated[
        str,
        StringConstraints(
            min_length=6, max_length=6, pattern='^[0-9]{6}$', strip_whitespace=True
        ),
    ]


@dataclass(slots=True, kw_only=True)
class AuthCodeRedeemed:
    user_id: int
    scopes: list[str]
