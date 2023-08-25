from pydantic import BaseModel, ConfigDict, constr
from .person import Person

class Movie_cast_person_create(BaseModel):
    movie_id: int | None = None
    person_id: int
    character: constr(min_length=1, max_length=200, strip_whitespace=True) | None = None
    order: int | None = None

class Movie_cast_person_update(Movie_cast_person_create):
    pass


class Movie_cast_person(BaseModel):
    movie_id: int
    person: Person
    character: str | None = None
    order: int | None = None
    
    model_config = ConfigDict(from_attributes=True)