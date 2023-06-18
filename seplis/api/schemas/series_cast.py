from pydantic import BaseModel, constr
from .person import Person


class Series_cast_role(BaseModel):
    character: constr(min_length=1, max_length=200, strip_whitespace=True) | None
    total_episodes: int


class Series_cast_person_create(BaseModel):
    series_id: int | None
    person_id: int
    roles: list[Series_cast_role] = []
    order: int | None


class Series_cast_person_update(Series_cast_person_create):
    pass


class Series_cast_person_import(BaseModel):
    external_name: str
    external_id: str
    roles: list[Series_cast_role] = []
    order: int | None
    total_episodes: int


class Series_cast_person(BaseModel, orm_mode=True):
    series_id: int
    person: Person
    roles: list[Series_cast_role] = []
    order: int | None
    total_episodes: int | None = 0