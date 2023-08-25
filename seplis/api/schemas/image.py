from typing import Literal
from pydantic import BaseModel, AnyHttpUrl, ConfigDict
from datetime import datetime
from fastapi import UploadFile

IMAGE_TYPES = Literal['poster', 'backdrop', 'profile']


class Image_create(BaseModel):
    external_name: str | None = None
    external_id: str | None = None


class Image_import(BaseModel):
    external_name: str
    external_id: str
    source_url: str | None = None
    type: IMAGE_TYPES
    file: UploadFile | None = None


class Image(Image_create):
    id: int
    height: int
    width: int
    file_id: str
    type: IMAGE_TYPES
    created_at: datetime
    url: str

    model_config = ConfigDict(from_attributes=True)