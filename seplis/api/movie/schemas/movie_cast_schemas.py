from dataclasses import dataclass
from typing import Annotated, NotRequired, TypedDict

from pydantic import StringConstraints

from seplis.api.person import Person


class MovieCastPersonCreate(TypedDict):
    person_id: int
    movie_id: NotRequired[int | None]
    character: NotRequired[
        Annotated[
            str | None,
            StringConstraints(min_length=1, max_length=200, strip_whitespace=True),
        ]
    ]
    order: NotRequired[int | None]


class MovieCastPersonUpdate(MovieCastPersonCreate):
    pass


@dataclass(slots=True, kw_only=True)
class MovieCastPerson:
    movie_id: int
    person: Person
    character: str | None = None
    order: int | None = None
