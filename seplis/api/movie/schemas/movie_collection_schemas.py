from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class MovieCollection:
    id: int
    name: str
