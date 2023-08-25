from pydantic import BaseModel, ConfigDict, constr
from .person import Person

class Episode_cast_person_create(BaseModel):
    series_id: int | None = None
    episode_number: int | None = None
    person_id: int
    character: constr(min_length=1, max_length=200, strip_whitespace=True)
    order: int | None = None


class Episode_cast_person(BaseModel):
    series_id: int | None = None
    episode_number: int | None = None
    person: Person
    character: str
    order: int | None = None

    model_config = ConfigDict(from_attributes=True)