from pydantic import BaseModel, constr
from .person import Person

class Episode_cast_person_create(BaseModel):
    series_id: int | None
    episode_number: int | None
    person_id: int
    character: constr(min_length=1, max_length=200, strip_whitespace=True)
    order: int | None


class Episode_cast_person(BaseModel, orm_mode=True):
    series_id: int | None
    episode_number: int | None
    person: Person
    character: str
    order: int | None