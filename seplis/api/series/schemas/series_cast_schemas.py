from dataclasses import dataclass, field
from typing import Annotated, NotRequired, TypedDict

from pydantic import StringConstraints

from seplis.api.person import Person

SeriesCastCharacter = Annotated[
    str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)
]


class SeriesCastRoleCreate(TypedDict):
    total_episodes: int
    character: NotRequired[SeriesCastCharacter | None]


@dataclass(slots=True, kw_only=True)
class SeriesCastRole:
    total_episodes: int
    character: str | None = None


class SeriesCastPersonCreate(TypedDict):
    person_id: int
    series_id: NotRequired[int | None]
    roles: NotRequired[list[SeriesCastRoleCreate]]
    order: NotRequired[int | None]
    total_episodes: NotRequired[int | None]


class SeriesCastPersonUpdate(SeriesCastPersonCreate, total=False):
    pass


class SeriesCastPersonImport(TypedDict):
    external_name: str
    external_id: str
    total_episodes: int
    roles: NotRequired[list[SeriesCastRoleCreate]]
    order: NotRequired[int | None]


@dataclass(slots=True, kw_only=True)
class SeriesCastPerson:
    series_id: int
    person: Person
    roles: list[SeriesCastRole] = field(default_factory=list)
    order: int | None = None
    total_episodes: int | None = 0
