from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class UserMovieStats:
    movies_watched: int = 0
    movie_watch_count: int = 0
    movies_watchlist: int = 0
    total_watch_minutes: int = 0
