import asyncio

import sqlalchemy as sa

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.user import UserAuthenticated

from ..models.movie_favorite_model import MMovieFavorite
from ..models.movie_model import MMovieWatched
from ..models.movie_watchlist_model import MMovieWatchlist
from ..schemas.movie_schemas import Movie, MovieFavorite, MovieWatched, MovieWatchlist
from .movie_user_actions import movie_watched_mapper


async def expand_movies(
    expand: list[str] | None, user: UserAuthenticated | None, movies: list[Movie]
) -> None:
    if not expand:
        return
    if not user:
        raise exceptions.NotSignedInException()
    expand_tasks = []
    if 'user_watchlist' in expand:
        expand_tasks.append(
            expand_user_watchlist(
                user_id=user.id,
                movies=movies,
            )
        )
    if 'user_favorite' in expand:
        expand_tasks.append(
            expand_user_favorite(
                user_id=user.id,
                movies=movies,
            )
        )
    if 'user_watched' in expand:
        expand_tasks.append(
            expand_user_watched(
                user_id=user.id,
                movies=movies,
            )
        )
    if expand_tasks:
        await asyncio.gather(*expand_tasks)


async def expand_user_watchlist(
    user_id: int, movies: list[Movie], session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        movies_by_id: dict[int, Movie] = {}
        for movie in movies:
            movie.user_watchlist = MovieWatchlist()
            movies_by_id[movie.id] = movie
        result = (
            await session.execute(
                sa.select(MMovieWatchlist.__table__).where(
                    MMovieWatchlist.user_id == user_id,
                    MMovieWatchlist.movie_id.in_(set(movies_by_id.keys())),
                )
            )
        ).mappings()
        for movie_watchlist in result:
            movies_by_id[movie_watchlist['movie_id']].user_watchlist = MovieWatchlist(
                created_at=movie_watchlist['created_at'],
                on_watchlist=True,
            )


async def expand_user_favorite(
    user_id: int, movies: list[Movie], session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        movies_by_id: dict[int, Movie] = {}
        for movie in movies:
            movie.user_favorite = MovieFavorite()
            movies_by_id[movie.id] = movie
        result = (
            await session.execute(
                sa.select(MMovieFavorite.__table__).where(
                    MMovieFavorite.user_id == user_id,
                    MMovieFavorite.movie_id.in_(set(movies_by_id.keys())),
                )
            )
        ).mappings()
        for movie_favorite in result:
            movies_by_id[movie_favorite['movie_id']].user_favorite = MovieFavorite(
                created_at=movie_favorite['created_at'],
                favorite=True,
            )


async def expand_user_watched(
    user_id: int, movies: list[Movie], session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        movies_by_id: dict[int, Movie] = {}
        for movie in movies:
            movie.user_watched = MovieWatched()
            movies_by_id[movie.id] = movie
        result = (
            await session.execute(
                sa.select(MMovieWatched.__table__).where(
                    MMovieWatched.user_id == user_id,
                    MMovieWatched.movie_id.in_(set(movies_by_id.keys())),
                )
            )
        ).mappings()
        for movie_watched in result:
            movies_by_id[movie_watched['movie_id']].user_watched = movie_watched_mapper(
                movie_watched
            )
