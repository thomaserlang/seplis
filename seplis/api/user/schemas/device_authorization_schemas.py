from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Literal, TypedDict

from pydantic import StringConstraints

UserCode = Annotated[
    str,
    StringConstraints(
        min_length=6,
        max_length=8,
        pattern=r'^[0-9 -]+$',
        strip_whitespace=True,
    ),
]


@dataclass(slots=True, kw_only=True)
class DeviceAuthorization:
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_at: datetime
    poll_interval_seconds: int


class DeviceAuthorizationApprove(TypedDict):
    user_code: UserCode


class DeviceAuthorizationTokenRequest(TypedDict):
    device_code: Annotated[
        str,
        StringConstraints(min_length=32, max_length=512, strip_whitespace=True),
    ]


@dataclass(slots=True, kw_only=True)
class DeviceAuthorizationToken:
    status: Literal['pending', 'authorized']
    access_token: str | None = None
    token_type: str | None = None
