from pydantic import BaseModel, conint, constr, Field, AnyHttpUrl, EmailStr
from pydantic.generics import GenericModel
from typing import List, Literal, Optional, TypeVar, Generic
from datetime import date, time, datetime, timezone

T = TypeVar('T')

def get_utc_now_timestamp() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)

default_datetime = Field(
    default_factory=get_utc_now_timestamp
)

class BaseModel(BaseModel):
    
    class Config:
        extra = 'forbid'


class Page_cursor_query(BaseModel):
    before: str | None
    after: str | None
    limit = 25

class Page_cursor_links(BaseModel):
    next: AnyHttpUrl | None
    prev: AnyHttpUrl | None

class Page_cursor_result(GenericModel, Generic[T]):
    items: list[T]
    links = Page_cursor_links()

class Page_query(BaseModel):
    page: conint(ge=1) = 1
    per_page: conint(ge=1, le=100) = 25

class Page_links(BaseModel):
    next: AnyHttpUrl | None
    prev: AnyHttpUrl | None
    first: AnyHttpUrl | None
    last: AnyHttpUrl | None

class Page_result(GenericModel, Generic[T]):
    items: list[T]
    links = Page_links()
    total: int
    per_page: int
    page: int
    pages: int


IMAGE_TYPES = Literal['poster', 'backdrop']

class Image_create(BaseModel):
    external_name: str | None
    external_id: str | None

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


class Movie_base(BaseModel):
    title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    alternative_titles: List[constr(min_length=1, max_length=100, strip_whitespace=True)] | None
    status: conint(gt=-1, lt=5) | None
    description: constr(min_length=1, max_length=2000, strip_whitespace=True) | None
    externals: dict[constr(min_length=1, max_length=45, strip_whitespace=True), constr(min_length=1, max_length=45, strip_whitespace=True) | None] | None
    status: conint(ge=0, le=5) | None # Status: 0: Unknown, 1: Released, 2: Rumored, 3: Planned, 4: In production, 5: Post production, 6: Canceled,
    language: constr(min_length=1, max_length=20) | None
    runtime: conint(gt=1) | None
    release_date: date | None

class Movie_create(Movie_base):
    poster_image_id: conint(gt=1) | None

class Movie_update(Movie_create):
    pass

class Movie(Movie_create):
    id: int
    poster_image: Image | None

    class Config:
        orm_mode = True


class Description_schema(BaseModel):
    text: constr(min_length=1, max_length=2000, strip_whitespace=True) | None
    title: constr(min_length=1, max_length=45, strip_whitespace=True) | None
    url: AnyHttpUrl | None


class Episode_create(BaseModel):
    title: constr(max_length=200, strip_whitespace=True) | None
    number: conint(gt=0)
    season: conint(gt=0) | None
    episode: conint(gt=0) | None
    air_date: date | None
    air_time: time | None
    air_datetime: datetime | None
    description: Description_schema | None
    runtime: conint(ge=0) | None

class Episode_update(Episode_create):
    pass

class Episode(Episode_create):
    pass

    class Config:
        orm_mode = True


class Series_importers(BaseModel):
    info: constr(min_length=1, max_length=45, strip_whitespace=True) | None
    episodes: constr(min_length=1, max_length=45, strip_whitespace=True) | None

class Series_base(BaseModel):
    title: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    alternative_titles: List[constr(min_length=1, max_length=100, strip_whitespace=True)] | None
    externals: dict[constr(min_length=1, max_length=45, strip_whitespace=True), constr(min_length=1, max_length=45, strip_whitespace=True) | None] | None
    status: conint(gt=-1) | None
    description: Description_schema | None
    premiered: date | None
    ended: date | None
    importers: Series_importers | None
    runtime: conint(gt=0, lt=1440) | None
    genres: list[constr(min_length=1, max_length=45)] | None
    episode_type: conint(gt=0, lt=4) | None
    language: constr(min_length=1, max_length=100, strip_whitespace=True) | None

class Series_create(Series_base):
    poster_image_id: conint(gt=0) | None
    episodes: list[Episode] | None

class Series_update(Series_create):
    pass

class Series(Series_base):
    id: int
    created_at: datetime
    updated_at: datetime | None
    status: int
    fans: int
    seasons: list[dict[str, int]]
    total_episodes: int
    poster_image: Image | None

    class Config:
        orm_mode = True


class Pagination_schema(BaseModel):
    page: Optional[List[conint(gt=0)]] = [1]
    per_page: Optional[List[conint(gt=0, le=1000)]] = [25]


class Search_schema(BaseModel):
    query: Optional[List[constr(min_length=1, max_length=200)]]
    title: Optional[List[constr(min_length=1, max_length=200)]]
    type: Optional[List[Literal['series', 'movie']]]


class Subtitle_language(BaseModel):
    subtitle_lang: Optional[constr(min_length=1, max_length=20)]
    audio_lang: Optional[constr(min_length=1, max_length=20)]


class Search_title_document(BaseModel):
    type: str
    id: int
    title: str | None
    titles: List[dict[str, str]] | None
    release_date: date | None
    imdb: str | None
    poster_image: Image | None

    class Config:
        orm_mode = True


class User_authenticated(BaseModel):
    id: int
    level: int
    token: Optional[str]

    class Config:
        orm_mode = True

USER_PASSWORD_TYPE = constr(min_length=10)

class User_create(BaseModel):
    email: EmailStr
    username: constr(min_length=2, max_length=45, regex='^[A-Za-z0-9-_]+$', strip_whitespace=True)
    password: USER_PASSWORD_TYPE

class User_update(BaseModel):
    email: EmailStr | None
    username: constr(min_length=2, max_length=45, regex='^[A-Za-z0-9-_]+$', strip_whitespace=True) | None

class User_basic(BaseModel):
    id: int
    username: str
    created_at: datetime
    level: int

    class Config:
        orm_mode = True

class User(User_basic):
    email: str

class User_change_password(BaseModel):
    current_password: constr(min_length=1)
    new_password: USER_PASSWORD_TYPE


class Token_create(BaseModel):
    grant_type: Literal['password']
    email: str
    password: str
    client_id: str

class Token(BaseModel):
    access_token: str