from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class UserWatchActivityPeriod:
    date: str
    episodes_watched: int = 0
    movies_watched: int = 0
    series_minutes: int = 0
    movie_minutes: int = 0
