from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, NotRequired, TypedDict

from fastapi import UploadFile

IMAGE_TYPES = Literal['poster', 'backdrop', 'profile']


class ImageCreate(TypedDict, total=False):
    external_name: NotRequired[str | None]
    external_id: NotRequired[str | None]


class ImageImport(TypedDict):
    external_name: str
    external_id: str
    type: IMAGE_TYPES
    source_url: NotRequired[str | None]
    file: NotRequired[UploadFile | None]


@dataclass(slots=True, kw_only=True)
class Image:
    id: int
    height: int
    width: int
    file_id: str
    type: IMAGE_TYPES
    created_at: datetime
    url: str
    external_name: str | None = None
    external_id: str | None = None
