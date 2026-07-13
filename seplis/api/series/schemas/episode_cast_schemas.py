from dataclasses import dataclass
from typing import Annotated, NotRequired, TypedDict

from pydantic import StringConstraints

from seplis.api.person import Person

CastCharacter = Annotated[
    str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
]


class EpisodeCastPersonCreate(TypedDict):
    person_id: int
    character: CastCharacter
    series_id: NotRequired[int | None]
    episode_number: NotRequired[int | None]
    order: NotRequired[int | None]


@dataclass(slots=True, kw_only=True)
class EpisodeCastPerson:
    person: Person
    character: str
    series_id: int | None = None
    episode_number: int | None = None
    order: int | None = None
