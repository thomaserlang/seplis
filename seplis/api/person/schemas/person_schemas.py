from dataclasses import dataclass, field
from datetime import date
from typing import Annotated, NotRequired, TypedDict

from pydantic import StringConstraints

from seplis.api.image import Image

PersonName = Annotated[
    str, StringConstraints(min_length=1, max_length=500, strip_whitespace=True)
]
PersonText = Annotated[
    str, StringConstraints(min_length=0, max_length=2000, strip_whitespace=True)
]
PersonPlace = Annotated[
    str, StringConstraints(min_length=0, max_length=100, strip_whitespace=True)
]


class PersonCreate(TypedDict):
    name: PersonName
    also_known_as: NotRequired[list[PersonName] | None]
    gender: NotRequired[int | None]
    birthday: NotRequired[date | None]
    deathday: NotRequired[date | None]
    biography: NotRequired[PersonText | None]
    place_of_birth: NotRequired[PersonPlace | None]
    popularity: NotRequired[float | None]
    externals: NotRequired[dict[str, str | None] | None]
    profile_image_id: NotRequired[int | None]


class PersonUpdate(TypedDict, total=False):
    name: NotRequired[PersonName | None]
    also_known_as: NotRequired[list[PersonName] | None]
    gender: NotRequired[int | None]
    birthday: NotRequired[date | None]
    deathday: NotRequired[date | None]
    biography: NotRequired[PersonText | None]
    place_of_birth: NotRequired[PersonPlace | None]
    popularity: NotRequired[float | None]
    externals: NotRequired[dict[str, str | None] | None]
    profile_image_id: NotRequired[int | None]


@dataclass(slots=True, kw_only=True)
class Person:
    id: int | None = None
    name: str | None = None
    also_known_as: list[str] = field(default_factory=list)
    gender: int | None = None
    birthday: date | None = None
    deathday: date | None = None
    biography: str | None = None
    place_of_birth: str | None = None
    popularity: float | None = None
    externals: dict[str, str | None] = field(default_factory=dict)
    profile_image: Image | None = None

    def to_request(self) -> PersonUpdate:
        return {
            'name': self.name,
            'also_known_as': self.also_known_as,
            'gender': self.gender,
            'birthday': self.birthday,
            'deathday': self.deathday,
            'biography': self.biography,
            'place_of_birth': self.place_of_birth,
            'popularity': self.popularity,
            'externals': self.externals,
            'profile_image_id': self.profile_image.id if self.profile_image else None,
        }
