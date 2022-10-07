from typing import Literal
from pydantic import BaseModel, AnyHttpUrl
from datetime import datetime


class Image_create(BaseModel):
    external_name: str | None
    external_id: str | None


IMAGE_TYPES = Literal['poster', 'backdrop']

class Image(Image_create):
    id: int
    height: int
    width: int
    hash: str
    type: IMAGE_TYPES
    created_at: datetime
    url: AnyHttpUrl

    class Config:
        orm_mode = True