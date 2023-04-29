from pydantic import BaseModel, constr
from .person import Person


class Series_cast_person_create(BaseModel):
    series_id: int | None
    person_id: int
    character: constr(min_length=1, max_length=200, strip_whitespace=True)
    order: int | None
    total_episodes: int | None


class Series_cast_person(BaseModel, orm_mode=True):
    series_id: int
    person: Person
    character: str
    order: int | None
    total_episodes: int