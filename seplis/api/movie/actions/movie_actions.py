from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any, cast

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from seplis import config, utils
from seplis.api import exceptions
from seplis.api.contexts import get_session
from seplis.api.database import database
from seplis.api.genre import Genre, MGenre, genre_mapper, get_or_create_genres
from seplis.api.image import MImage, image_mapper
from seplis.api.page_cursor import PageCursor, PageCursorQuery
from seplis.api.search import SearchTitleDocument, SearchTitleDocumentTitle
from seplis.api.user import UserAuthenticated

from ..models.movie_collection_model import MMovieCollection
from ..models.movie_model import MMovie, MMovieExternal, MMovieGenre, movie_mapper
from ..schemas.movie_collection_schemas import MovieCollection
from ..schemas.movie_schemas import Movie, MovieCreate, MovieUpdate
from ..types.movie_filter_types import MovieQueryFilter
from .movie_expand_actions import expand_movies
from .movie_filter_actions import filter_movies


async def get_movies(
    *,
    page_cursor: PageCursorQuery,
    filter_query: MovieQueryFilter,
    session: AsyncSession | None = None,
) -> PageCursor[Movie]:
    return await filter_movies(
        query=sa.select(MMovie),
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
        movie = await session.scalar(sa.select(MMovie).where(MMovie.id == movie_id))
        if not movie:
            raise HTTPException(404, 'Unknown movie')
        data = movie_mapper(movie)
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
        await session.execute(sa.delete(MMovie.__table__).where(MMovie.id == movie_id))  # type: ignore
        await session.execute(
            sa.delete(MImage.__table__).where(  # type: ignore
                MImage.relation_type == 'movie',
                MImage.relation_id == movie_id,
            )
        )
    await database.es.delete(
        index=config.api.elasticsearch.index_prefix + 'titles',
        id=f'movie-{movie_id}',
    )


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
                await session.execute(sa.insert(MMovie.__table__)),  # type: ignore
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
                sa.update(MMovie.__table__).where(MMovie.id == movie_id).values(**values)  # type: ignore
            )
        movie = await session.scalar(sa.select(MMovie).where(MMovie.id == movie_id))
        if not movie:
            raise HTTPException(404, f'Unknown movie id: {movie_id}')
        await save_movie_for_search(movie)
        return movie_mapper(movie)


async def get_movie_from_external(
    title: str,
    value: str,
    session: AsyncSession | None = None,
) -> Movie | None:
    async with get_session(session) as session:
        movie = await session.scalar(
            sa.select(MMovie).where(
                MMovie.id == MMovieExternal.movie_id,
                MMovieExternal.title == title,
                MMovieExternal.value == value,
            )
        )
        if movie:
            return movie_mapper(movie)
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
                sa.insert(MMovieCollection.__table__).values(name=name)  # type: ignore
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
            sa.delete(MMovieExternal.__table__).where(MMovieExternal.movie_id == movie_id)  # type: ignore
        )
    else:
        result = await session.scalars(
            sa.select(MMovieExternal).where(MMovieExternal.movie_id == movie_id)
        )
        if result:
            for external in result:
                current_externals[external.title] = external.value

    for key in externals:
        if externals[key]:
            duplicate_movie = await session.scalar(
                sa.select(MMovie).where(
                    MMovieExternal.title == key,
                    MMovieExternal.value == externals[key],
                    MMovieExternal.movie_id != movie_id,
                    MMovie.id == MMovieExternal.movie_id,
                )
            )
            if duplicate_movie:
                raise exceptions.MovieExternalDuplicated(
                    external_title=key,
                    external_value=externals[key],
                    movie=utils.json_loads(
                        utils.json_dumps(movie_mapper(duplicate_movie))
                    ),
                )

        if key not in current_externals:
            if externals[key]:
                await session.execute(
                    sa.insert(MMovieExternal.__table__).values(  # type: ignore
                        movie_id=movie_id,
                        title=key,
                        value=externals[key],
                    )
                )
                current_externals[key] = externals[key]
        elif current_externals[key] != externals[key]:
            if externals[key]:
                await session.execute(
                    sa.update(MMovieExternal.__table__)  # type: ignore
                    .where(
                        MMovieExternal.movie_id == movie_id,
                        MMovieExternal.title == key,
                    )
                    .values(value=externals[key])
                )
                current_externals[key] = externals[key]
            else:
                await session.execute(
                    sa.delete(MMovieExternal.__table__).where(  # type: ignore
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
            sa.delete(MMovieGenre.__table__).where(MMovieGenre.movie_id == movie_id)  # type: ignore
        )
    new_genre_ids = genre_ids - current_genres
    if new_genre_ids:
        await session.execute(
            sa.insert(MMovieGenre.__table__).prefix_with('IGNORE'),  # type: ignore
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
    rows = await session.scalars(
        sa.select(MGenre)
        .where(MMovieGenre.movie_id == movie_id, MGenre.id == MMovieGenre.genre_id)
        .order_by(MGenre.name)
    )
    return [genre_mapper(row) for row in rows]


async def save_movie_for_search(movie: MMovie) -> None:
    document = movie_title_document_mapper(movie)
    if not document:
        return
    await database.es.index(
        index=config.api.elasticsearch.index_prefix + 'titles',
        id=f'movie-{movie.id}',
        document=utils.json_loads(utils.json_dumps(document)),
    )


def movie_title_document_mapper(movie: MMovie) -> SearchTitleDocument | None:
    if not movie.title:
        return None
    titles = [movie.title, *(movie.alternative_titles or [])]
    year = str(movie.release_date.year) if movie.release_date else ''
    for title in titles[:]:
        if title and year not in title:
            title_with_year = f'{title} {year}'
            if title_with_year not in titles:
                titles.append(title_with_year)
    return SearchTitleDocument(
        type='movie',
        id=movie.id,
        title=movie.title,
        titles=[SearchTitleDocumentTitle(title=title) for title in titles],
        release_date=movie.release_date,
        imdb=(movie.externals or {}).get('imdb'),
        poster_image=image_mapper(movie.poster_image) if movie.poster_image else None,
        popularity=float(movie.popularity or 0),
        genres=genres_from_values(movie.genres),
        rating=float(movie.rating) if movie.rating is not None else None,
        rating_votes=movie.rating_votes,
        runtime=movie.runtime,
        language=movie.language,
    )


def movie_collection_mapper(collection: MMovieCollection) -> MovieCollection:
    return MovieCollection(
        id=collection.id,
        name=collection.name or '',
    )


def genre_from_value(value: Any) -> Genre:
    if isinstance(value, Genre):
        return value
    if isinstance(value, dict):
        return Genre(
            id=int(value.get('id') or 0),
            name=str(value.get('name') or ''),
            number_of=int(value.get('number_of') or 0),
        )
    return genre_mapper(value)


def genres_from_values(values: list[Any] | None) -> list[Genre]:
    return [genre_from_value(value) for value in values or []]


async def rebuild_movies() -> None:
    async def documents() -> AsyncIterator[dict[str, Any]]:
        async with database.session() as session:
            result = await session.stream(sa.select(MMovie))
            async for movies in result.yield_per(1000):
                for movie in movies:
                    document = movie_title_document_mapper(movie)
                    if not document:
                        continue
                    yield {
                        '_index': config.api.elasticsearch.index_prefix + 'titles',
                        '_id': f'movie-{movie.id}',
                        **utils.json_loads(utils.json_dumps(document)),
                    }

    from elasticsearch import helpers

    await helpers.async_bulk(database.es, documents())
