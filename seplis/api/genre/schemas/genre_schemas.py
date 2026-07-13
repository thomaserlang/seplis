from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class Genre:
    id: int
    name: str
    number_of: int = 0
