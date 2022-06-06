
from pydantic import BaseModel, conint, constr, Field
from typing import List, Optional
from datetime import date
from datetime import datetime, timezone

def get_utc_now_timestamp() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)

default_datetime = Field(
    default_factory=get_utc_now_timestamp
)

class Movie_externals_schema(BaseModel):
    imdb: Optional[constr(min_length=9, max_length=9, regex='^tt[0-9]{7}')]
    themoviedb: Optional[constr(min_length=1, max_length=10)]

    class Config:
        extra = 'forbid'

class Movie_schema(BaseModel):
    title: Optional[constr(min_length=1, max_length=100, strip_whitespace=True)]
    alternative_titles: Optional[List[constr(min_length=1, max_length=100, strip_whitespace=True)]]
    status: Optional[conint(gt=-1, lt=5)]
    description: Optional[constr(min_length=1, max_length=2000, strip_whitespace=True)]
    externals: Optional[Movie_externals_schema]
    status: Optional[conint(ge=0, le=5)] # Status: 0: Canceled, 1: Released, 2: Rumored, 3: Planned, 4: In production, 5: Post production
    language: Optional[constr(min_length=1, max_length=20)]
    poster_image_id: Optional[conint(gt=1)]
    runtime: Optional[conint(gt=1)]
    release_date: Optional[date]

    class Config:
        extra = 'forbid'

class Pagination_schema(BaseModel):

    page: Optional[List[conint(gt=0)]] = [1]
    per_page: Optional[List[conint(gt=0, le=500)]] = [25]