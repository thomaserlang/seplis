from pydantic import BaseModel, ConfigDict, constr, field_validator
from datetime import date
from .image import Image


class Person_create(BaseModel):
    name: constr(min_length=1, max_length=500, strip_whitespace=True)
    also_known_as: list[constr(min_length=1, max_length=500, strip_whitespace=True)] | None = []
    gender: int | None = None
    birthday: date | None = None
    deathday: date | None = None
    biography: constr(min_length=0, max_length=2000, strip_whitespace=True) | None = None
    place_of_birth: constr(min_length=0, max_length=100, strip_whitespace=True) | None = None
    popularity: float | None = None
    externals: dict[str, str | None] | None = None
    profile_image_id: int | None = None

    @field_validator('externals')
    @classmethod
    def externals_none_value(cls, v):
        for e in v:
            if v[e] == '':
                v[e] = None
        return v
    

class Person_update(Person_create):    
    name: constr(min_length=1, max_length=500) | None = None
        
    model_config = ConfigDict(from_attributes=True)


class Person(BaseModel):
    id: int | None = None
    name: str = None
    also_known_as: list[str] = []
    gender: int | None
    birthday: date | None = None
    deathday: date | None = None
    biography: str | None = None
    place_of_birth: str | None = None
    popularity: float | None = None
    externals: dict[str, str | None] = {}
    profile_image: Image | None = None

    def to_request(self):
        data = Person_update.model_validate(self)
        data.profile_image_id = self.profile_image.id if self.profile_image else None
        return data
    
    model_config = ConfigDict(from_attributes=True)