from pydantic import BaseModel, constr
from .person import Person

class Movie_cast_person_create(BaseModel):
    movie_id: int | None
    person_id: int
    character: constr(min_length=1, max_length=200, strip_whitespace=True)
    order: int | None


class Movie_cast_person(BaseModel, orm_mode=True):
    movie_id: int
    person: Person
    character: str
    order: int | None