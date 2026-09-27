from datetime import UTC, datetime
from typing import Any, cast

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from seplis import utils
from seplis.api import exceptions
from seplis.api.contexts import get_session
from seplis.api.database import database
from seplis.api.genre import Genre, MGenre, genre_mapper, get_or_create_genres
from seplis.api.image import MImage
from seplis.api.page_cursor import PageCursor, PageCursorQuery
from seplis.api.search.actions.search_index_actions import delete_document
from seplis.api.user import UserAuthenticated

from ..models.movie_collection_model import MMovieCollection
from ..models.movie_model import MMovie, MMovieExternal, MMovieGenre
from ..schemas.movie_schemas import Movie, MovieCreate, MovieUpdate
from ..types.movie_filter_types import MovieQueryFilter
from .movie_expand_actions import expand_movies
from .movie_filter_actions import filter_movies
from .movie_mapping import movie_row_mapper, select_movies
from .movie_search_actions import save_movie_for_search


async def get_movies(
    *,
    page_cursor: PageCursorQuery,
    filter_query: MovieQueryFilter,
    session: AsyncSession | None = None,
) -> PageCursor[Movie]:
    return await filter_movies(
        query=select_movies(),
        session=session,
        filter_query=filter_query,
        page_query=page_cursor,
    )


async def get_movie(
    *,
    movie_id: int,
    expand: list[str] | None,
    user: UserAuthenticated | None,
    session: AsyncSession | None = None,
) -> Movie:
    async with get_session(session) as session:
        movie = (
            (await session.execute(select_movies().where(MMovie.id == movie_id)))
            .mappings()
            .first()
        )
        if not movie:
            raise HTTPException(404, 'Unknown movie')
        data = movie_row_mapper(movie)
        await expand_movies(movies=[data], user=user, expand=expand)
        return data


async def create_movie(*, data: MovieCreate) -> Movie:
    movie = await save_movie(data, movie_id=None, patch=False)
    await database.redis_queue.enqueue_job('update_movie', int(movie.id))
    return movie


async def update_movie(*, movie_id: int, data: MovieUpdate) -> Movie:
    return await save_movie(movie_id=movie_id, data=data, patch=False)


async def patch_movie(*, movie_id: int, data: MovieUpdate) -> Movie:
    return await save_movie(movie_id=movie_id, data=data, patch=True)


async def delete_movie(*, movie_id: int) -> None:
    async with get_session() as session:
        await session.execute(
            sa.delete(cast(sa.Table, MMovie.__table__)).where(MMovie.id == movie_id)
        )
        await session.execute(
            sa.delete(cast(sa.Table, MImage.__table__)).where(
                MImage.relation_type == 'movie',
                MImage.relation_id == movie_id,
            )
        )
    await delete_document(f'movie-{movie_id}')


async def request_movie_update(*, movie_id: int) -> None:
    await database.redis_queue.enqueue_job('update_movie', movie_id)


async def save_movie(
    data: MovieCreate | MovieUpdate,
    movie_id: int | None = None,
    patch: bool = True,
    overwrite_genres: bool = False,
    session: AsyncSession | None = None,
) -> Movie:
    values = dict(data or {})
    async with get_session(session) as session:
        if not movie_id:
            result = cast(
                Any,
                await session.execute(sa.insert(cast(sa.Table, MMovie.__table__))),
            )
            movie_id = result.lastrowid
            values['created_at'] = datetime.now(tz=UTC)
        else:
            exists = await session.scalar(
                sa.select(MMovie.id).where(MMovie.id == movie_id)
            )
            if not exists:
                raise HTTPException(404, f'Unknown movie id: {movie_id}')
            values['updated_at'] = datetime.now(tz=UTC)

        if 'genre_names' in values:
            values['genres'] = await save_movie_genres(
                session=session,
                movie_id=movie_id,
                genres=values.pop('genre_names'),
                patch=False if overwrite_genres else patch,
            )
        if 'externals' in values:
            values['externals'] = await save_movie_externals(
                session=session,
                movie_id=movie_id,
                externals=values['externals'],
                patch=patch,
            )
        if 'alternative_titles' in values:
            values['alternative_titles'] = await save_movie_alternative_titles(
                session=session,
                movie_id=movie_id,
                alternative_titles=values['alternative_titles'],
                patch=patch,
            )
        if 'collection_name' in values:
            collection = values.pop('collection_name')
            if isinstance(collection, str):
                collection = await get_or_create_movie_collection(
                    name=collection,
                    session=session,
                )
            values['collection_id'] = collection
        if values.get('rating') and values.get('rating_votes'):
            values['rating_weighted'] = utils.calculate_weighted_rating(
                values['rating'], values['rating_votes']
            )
        if values:
            await session.execute(
                sa.update(cast(sa.Table, MMovie.__table__))
                .where(MMovie.id == movie_id)
                .values(**values)
            )
        movie = (
            (await session.execute(select_movies().where(MMovie.id == movie_id)))
            .mappings()
            .first()
        )
        if not movie:
            raise HTTPException(404, f'Unknown movie id: {movie_id}')
        mapped_movie = movie_row_mapper(movie)
        await save_movie_for_search(mapped_movie)
        return mapped_movie


async def get_movie_from_external(
    title: str,
    value: str,
    session: AsyncSession | None = None,
) -> Movie | None:
    async with get_session(session) as session:
        movie = (
            (
                await session.execute(
                    select_movies().where(
                        MMovie.id == MMovieExternal.movie_id,
                        MMovieExternal.title == title,
                        MMovieExternal.value == value,
                    )
                )
            )
            .mappings()
            .first()
        )
        if movie:
            return movie_row_mapper(movie)
        return None


async def get_or_create_movie_collection(
    name: str,
    session: AsyncSession,
) -> int:
    collection_id = await session.scalar(
        sa.select(MMovieCollection.id).where(MMovieCollection.name == name)
    )
    if not collection_id:
        result = cast(
            Any,
            await session.execute(
                sa.insert(cast(sa.Table, MMovieCollection.__table__)).values(name=name)
            ),
        )
        collection_id = result.lastrowid
    return collection_id


async def save_movie_externals(
    session: AsyncSession,
    movie_id: str | int,
    externals: dict[str, str],
    patch: bool,
) -> dict[str, str]:
    current_externals = {}
    if not patch:
        await session.execute(
            sa.delete(cast(sa.Table, MMovieExternal.__table__)).where(
                MMovieExternal.movie_id == movie_id
            )
        )
    else:
        result = (
            await session.execute(
                sa.select(MMovieExternal.__table__).where(
                    MMovieExternal.movie_id == movie_id
                )
            )
        ).mappings()
        if result:
            for external in result:
                current_externals[external['title']] = external['value']

    for key in externals:
        if externals[key]:
            duplicate_movie = (
                (
                    await session.execute(
                        select_movies().where(
                            MMovieExternal.title == key,
                            MMovieExternal.value == externals[key],
                            MMovieExternal.movie_id != movie_id,
                            MMovie.id == MMovieExternal.movie_id,
                        )
                    )
                )
                .mappings()
                .first()
            )
            if duplicate_movie:
                raise exceptions.MovieExternalDuplicated(
                    external_title=key,
                    external_value=externals[key],
                    movie=utils.json_loads(
                        utils.json_dumps(movie_row_mapper(duplicate_movie))
                    ),
                )

        if key not in current_externals:
            if externals[key]:
                await session.execute(
                    sa.insert(cast(sa.Table, MMovieExternal.__table__)).values(
                        movie_id=movie_id,
                        title=key,
                        value=externals[key],
                    )
                )
                current_externals[key] = externals[key]
        elif current_externals[key] != externals[key]:
            if externals[key]:
                await session.execute(
                    sa.update(cast(sa.Table, MMovieExternal.__table__))
                    .where(
                        MMovieExternal.movie_id == movie_id,
                        MMovieExternal.title == key,
                    )
                    .values(value=externals[key])
                )
                current_externals[key] = externals[key]
            else:
                await session.execute(
                    sa.delete(cast(sa.Table, MMovieExternal.__table__)).where(
                        MMovieExternal.movie_id == movie_id,
                        MMovieExternal.title == key,
                    )
                )
                current_externals.pop(key)
    return {key: value for key, value in current_externals.items() if value is not None}


async def save_movie_alternative_titles(
    session: AsyncSession,
    movie_id: str | int,
    alternative_titles: list[str],
    patch: bool,
) -> set[str]:
    if not patch:
        return set(alternative_titles)
    current_alternative_titles = (
        await session.scalar(
            sa.select(MMovie.alternative_titles).where(MMovie.id == movie_id)
        )
        or []
    )
    return set(current_alternative_titles + alternative_titles)


async def save_movie_genres(
    session: AsyncSession,
    movie_id: str | int,
    genres: list[str | int],
    patch: bool,
) -> list[Genre]:
    genre_ids = await get_or_create_genres(genres, type_='movie')
    current_genres: set[int] = set()
    if patch:
        current_genres = set(
            await session.scalars(
                sa.select(MMovieGenre.genre_id).where(MMovieGenre.movie_id == movie_id)
            )
        )
    else:
        await session.execute(
            sa.delete(cast(sa.Table, MMovieGenre.__table__)).where(
                MMovieGenre.movie_id == movie_id
            )
        )
    new_genre_ids = genre_ids - current_genres
    if new_genre_ids:
        await session.execute(
            sa.insert(cast(sa.Table, MMovieGenre.__table__)).prefix_with('IGNORE'),
            [{'movie_id': movie_id, 'genre_id': genre_id} for genre_id in new_genre_ids],
        )
    if new_genre_ids != current_genres:
        await session.execute(
            sa.text(
                'update genres set number_of = (select count(genres.id) '
                'from movie_genres where movie_genres.genre_id = genres.id) '
                'where type="movie"'
            )
        )
    rows = (
        await session.execute(
            sa.select(MGenre.__table__)
            .where(
                MMovieGenre.movie_id == movie_id,
                MGenre.id == MMovieGenre.genre_id,
            )
            .order_by(MGenre.name)
        )
    ).mappings()
    return [genre_mapper(row) for row in rows]
