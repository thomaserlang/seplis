from pydantic import BaseModel, constr, validator
from datetime import date
from .image import Image


class Person_create(BaseModel):
    name: constr(min_length=1, max_length=500, strip_whitespace=True)
    also_known_as: list[constr(min_length=1, max_length=500, strip_whitespace=True)] | None = []
    gender: int | None
    birthday: date | None
    deathday: date | None
    biography: constr(min_length=0, max_length=2000, strip_whitespace=True) | None
    place_of_birth: constr(min_length=0, max_length=100, strip_whitespace=True) | None
    popularity: float | None
    externals: dict[str, str] | None
    profile_image_id: int | None

    @validator('externals')
    def externals_none_value(cls, externals):
        for e in externals:
            if externals[e] == '':
                externals[e] = None
        return externals
    

class Person_update(Person_create, orm_mode=True):    
    name: constr(min_length=1, max_length=500) | None


class Person(BaseModel, orm_mode=True):
    id: int | None
    name: str = None
    also_known_as: list[str] = []
    gender: int | None
    birthday: date | None
    deathday: date | None
    biography: str | None
    place_of_birth: str | None
    popularity: float | None
    externals: dict[str, str] = {}
    profile_image: Image | None

    def to_request(self):
        data = Person_update.from_orm(self)
        data.profile_image_id = self.profile_image.id if self.profile_image else None
        return data