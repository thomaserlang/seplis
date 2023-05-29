from typing import Literal
from pydantic import BaseModel, AnyHttpUrl
from datetime import datetime
from fastapi import UploadFile

IMAGE_TYPES = Literal['poster', 'backdrop', 'profile']


class Image_create(BaseModel):
    external_name: str | None
    external_id: str | None


class Image_import(BaseModel):
    external_name: str
    external_id: str
    source_url: str | None
    type: IMAGE_TYPES
    file: UploadFile | None


class Image(Image_create, orm_mode=True):
    id: int
    height: int
    width: int
    file_id: str
    type: IMAGE_TYPES
    created_at: datetime
    url: AnyHttpUrl