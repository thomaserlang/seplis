import asyncio
from datetime import date
from typing import Any

import httpx
import sqlalchemy as sa

from ... import config, logger
from ...api import exceptions
from ...api.database import database
from ...api.image import ImageImport, MImage, image_mapper
from ...api.image import save_image as save_image_action
from ...api.movie import (
    MMovie,
    MMovieCast,
    MMovieExternal,
    Movie,
    MovieCastPerson,
    MovieCastPersonUpdate,
    MovieUpdate,
    delete_movie,
    get_movie_from_external,
    save_movie,
)
from ...api.movie.actions.movie_cast_actions import (
    delete_movie_cast,
    movie_cast_person_model_mapper,
    save_movie_cast,
)
from ...api.movie.models.movie_model import movie_mapper
from ...api.person import get_person_from_external
from ...utils.compare import compare
from ..people.importer import create_person

statuses = {
    'Unknown': 0,
    'Released': 1,
    'Rumored': 2,
    'Planned': 3,
    'In production': 4,
    'Post production': 5,
    'Canceled': 6,
}

client = httpx.AsyncClient()


async def update_movie(movie_id: int | None = None, movie: Movie | None = None) -> None:
    if movie_id:
        async with database.session() as session:
            result = await session.scalar(sa.select(MMovie).where(MMovie.id == movie_id))
            if not result:
                logger.error(f'Unknown movie: {movie_id}')
                return
            movie = movie_mapper(result)
    if not movie:
        logger.error('Unknown movie')
        return
    logger.info(f'[Movie: {movie.id}] Updating')
    await update_movie_metadata(movie)
    await update_images(movie)
    await update_cast(movie)


async def update_movies_bulk(from_movie_id: int = 0, do_async: bool = False) -> None:
    logger.info('Updating movies')
    movies = await _get_movies(from_movie_id)
    while movies:
        for movie in movies:
            from_movie_id = movie.id
            try:
                if not do_async:
                    await update_movie(movie=movie_mapper(movie))
                else:
                    await database.redis_queue.enqueue_job(
                        'update_movie', movie_id=movie.id
                    )
            except KeyboardInterrupt, SystemExit:
                break
            except exceptions.APIException as e:
                logger.info(e.message)
            except Exception as e:
                logger.exception(e)
        else:
            movies = await _get_movies(from_movie_id)


async def _get_movies(from_movie_id: int) -> Any:
    async with database.session() as session:
        query = sa.select(MMovie)
        query = query.where(MMovie.id > from_movie_id).limit(100)
        return await session.scalars(query)


async def update_incremental() -> None:
    page = 1
    logger.info('Incremental update running')
    while True:
        r = await client.get(
            'https://api.themoviedb.org/3/movie/changes',
            params={
                'api_key': config.client.themoviedb,
                'page': page,
            },
        )
        r.raise_for_status()
        data = r.json()
        if not data or not data['results']:
            break
        async with database.session() as session:
            for r in data['results']:
                logger.info(f'Checking: {r["id"]}')
                result = await session.scalar(
                    sa.select(MMovie).where(
                        MMovieExternal.title == 'themoviedb',
                        MMovieExternal.value == r['id'],
                        MMovie.id == MMovieExternal.movie_id,
                    )
                )
                if not result:
                    continue
                movie = movie_mapper(result)
                if movie:
                    try:
                        await update_movie(movie=movie)
                    except KeyboardInterrupt, SystemExit:
                        break
                    except exceptions.APIException as e:
                        logger.error(e.message)
                    except Exception as e:
                        logger.exception(e)
            if page == data['total_pages']:
                break
            page += 1


async def update_movie_metadata(movie: Movie) -> None:
    logger.debug(f'[Movie: {movie.id}] Updating metadata')
    themoviedb = movie.externals.get('themoviedb')
    if not themoviedb:
        if not movie.externals.get('imdb'):
            logger.info(f"[Movie: {movie.id}] externals.imdb doesn't exist")
            return
        r = await client.get(
            f'https://api.themoviedb.org/3/find/{movie.externals["imdb"]}',
            params={
                'api_key': config.client.themoviedb,
                'external_source': 'imdb_id',
            },
        )
        if r.status_code >= 400:
            logger.error(
                f'[Movie: {movie.id}] Failed to get movie '
                f'"{movie.externals["imdb"]}" by imdb: {r.content}'
            )
            return
        r = r.json()
        if not r['movie_results']:
            logger.warning(
                f'[Movie: {movie.id}] No movie found with imdb: '
                f'"{movie.externals["imdb"]}"'
            )
            return
        themoviedb = r['movie_results'][0]['id']
    new_data = await get_movie_data(themoviedb)
    if not new_data:
        return
    old_data = movie.to_request()
    data = compare(new_data, old_data, skip_keys=['alternative_titles'])
    missing_alternative_titles = [
        title
        for title in new_data.get('alternative_titles') or []
        if title not in (old_data.get('alternative_titles') or [])
    ]
    if new_data.get('alternative_titles') and missing_alternative_titles:
        data['alternative_titles'] = new_data['alternative_titles']
    if data:
        logger.debug(f'[Movie: {movie.id}] Updating: {data}')
        await save_movie(
            data=MovieUpdate(**data),
            movie_id=movie.id,
            patch=True,
            overwrite_genres=True,
        )
    else:
        logger.debug(f'[Movie: {movie.id}] No metadata updates')


async def get_movie_data(themoviedb: int | str) -> MovieUpdate | None:
    r = await client.get(
        f'https://api.themoviedb.org/3/movie/{themoviedb}',
        params={
            'api_key': config.client.themoviedb,
            'append_to_response': 'alternative_titles,keywords',
        },
    )
    if r.status_code >= 400:
        logger.info(
            f'[Movie] Failed to get movie from themoviedb ({themoviedb}): {r.content}'
        )
        error = r.json()
        if error['status_code'] == 34:
            movie = await get_movie_from_external('themoviedb', str(themoviedb))
            if movie:
                await delete_movie(movie_id=movie.id)
                logger.info(
                    f'Movie not found on TMDB, deleteing: TMDB {themoviedb} '
                    'from the database'
                )
        return None
    r = r.json()

    externals: dict[str, str | None] = {'themoviedb': str(themoviedb)}
    data = MovieUpdate(externals=externals)
    if r.get('imdb_id'):
        externals['imdb'] = r['imdb_id']
    data['title'] = r['title']
    data['original_title'] = r['original_title']
    data['status'] = statuses.get(r['status'], 0)
    data['runtime'] = r['runtime']
    data['release_date'] = (
        date.fromisoformat(r['release_date']) if r['release_date'] else None
    )
    data['plot'] = r['overview'] or None
    data['tagline'] = r['tagline'] or None
    data['language'] = r['original_language']
    if 'alternative_titles' in r:
        data['alternative_titles'] = [
            a['title'][:200] for a in r['alternative_titles']['titles']
        ]
    genres = [genre['name'] for genre in r['genres']]
    if r.get('keywords'):
        for keyword in r['keywords'].get('keywords', []):
            if keyword['name'].lower() == 'anime':
                genres.append('Anime')
    data['genre_names'] = genres
    data['popularity'] = r['popularity']
    data['revenue'] = r['revenue']
    data['budget'] = r['budget']
    data['collection_name'] = (
        r['belongs_to_collection']['name'] if r['belongs_to_collection'] else None
    )
    return data


async def update_images(movie: Movie) -> None:
    logger.debug(f'[Movie: {movie.id}] Updating images')
    if not movie.externals.get('themoviedb'):
        logger.error(f'Missing externals.themoviedb for movie: "{movie.id}"')
        return

    async with database.session() as session:
        result = await session.scalars(
            sa.select(MImage).where(
                MImage.relation_type == 'movie',
                MImage.relation_id == movie.id,
            )
        )
        image_external_ids = {
            f'{image.external_name}-{image.external_id}': image_mapper(image)
            for image in result
        }

    r = await client.get(
        f'https://api.themoviedb.org/3/movie/{movie.externals["themoviedb"]}',
        params={
            'append_to_response': 'images',
            'api_key': config.client.themoviedb,
        },
    )
    if r.status_code >= 400:
        logger.error(
            f'[Movie: {movie.id}] Failed to get movie images for '
            f'"{movie.externals["themoviedb"]}" from themoviedb: {r.content}'
        )
        return
    m = r.json()
    if 'images' not in m:
        logger.debug(f"[Movie: {movie.id}] Didn't find any images")
        return
    logger.debug(f'[Movie: {movie.id}] Found {len(m["images"]["posters"])} posters')

    async def save_movie_image(image: dict[str, Any]) -> None:
        try:
            key = f'themoviedb-{image["file_path"]}'
            if key not in image_external_ids:
                source_url = f'https://image.tmdb.org/t/p/original{image["file_path"]}'
                logger.debug(f'[Movie: {movie.id}] Saving image: {source_url}')
                saved_image = await save_image_action(
                    relation_type='movie',
                    relation_id=movie.id,
                    image_data=ImageImport(
                        external_name='themoviedb',
                        external_id=image['file_path'],
                        type='poster',
                        source_url=source_url,
                    ),
                )
                image_external_ids[key] = saved_image
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception:
            logger.exception(f'[Movie: {movie.id}] Failed saving image')

    await asyncio.gather(*[save_movie_image(image) for image in m['images']['posters']])

    if m['poster_path']:
        key = f'themoviedb-{m["poster_path"]}'
        if key not in image_external_ids:
            logger.info('No image to set as primary')
            return
        if not movie.poster_image or movie.poster_image.id != image_external_ids[key].id:
            logger.info(
                f'[Movie: {movie.id}] Setting primary image: {image_external_ids[key].id}'
            )
            await save_movie(
                data=MovieUpdate(
                    poster_image_id=image_external_ids[key].id,
                ),
                movie_id=movie.id,
            )


async def update_cast(movie: Movie) -> None:
    logger.debug(f'[Movie: {movie.id}] Updating cast')
    if not movie.externals.get('themoviedb'):
        logger.error(f'Missing externals.themoviedb for movie: "{movie.id}"')
        return

    # Get existing cast
    async with database.session() as session:
        result = await session.scalars(
            sa.select(MMovieCast).where(
                MMovieCast.movie_id == movie.id,
            )
        )
        cast: dict[str, MovieCastPerson] = {}
        for movie_cast in result:
            externals = movie_cast.person.externals or {}
            themoviedb = externals.get('themoviedb')
            if themoviedb:
                cast[f'themoviedb-{themoviedb}'] = movie_cast_person_model_mapper(
                    movie_cast
                )

    r = await client.get(
        f'https://api.themoviedb.org/3/movie/{movie.externals["themoviedb"]}/credits',
        params={
            'api_key': config.client.themoviedb,
            'language': 'en-US',
        },
    )
    if r.status_code >= 400:
        logger.error(
            f'[Movie: {movie.id}] Failed to get movie credits for '
            f'"{movie.externals["themoviedb"]}" from themoviedb: {r.content}'
        )
        return
    m = r.json()
    if 'cast' not in m:
        logger.info(f"[Movie: {movie.id}] Didn't find any cast")
        return
    logger.debug(f'[Movie: {movie.id}] Found {len(m["cast"])} cast members')

    async def save_cast(member: dict[str, Any]) -> None:
        try:
            key = f'themoviedb-{member["id"]}'
            if key not in cast:
                # Create the person if they don't "exist"
                person = await get_person_from_external('themoviedb', member['id'])
                if not person:
                    person = await create_person('themoviedb', member['id'])
                if not person or person.id is None:
                    logger.error(
                        f'[Movie: {movie.id}] Failed creating cast person: '
                        f'{member["name"]} ({member["id"]})'
                    )
                    return
                cast[key] = MovieCastPerson(
                    movie_id=movie.id,
                    person=person,
                    character=None,
                )

            if (
                cast[key].character != member['character'][:200]
                or cast[key].order != member['order']
            ):
                person_id = cast[key].person.id
                if person_id is None:
                    logger.error(
                        f'[Movie: {movie.id}] Cast person is missing id: '
                        f'{member["name"]} ({member["id"]})'
                    )
                    return
                logger.debug(
                    f'[Movie: {movie.id}] Saving cast: {member["name"]} ({member["id"]})'
                )
                await save_movie_cast(
                    movie_id=movie.id,
                    data=MovieCastPersonUpdate(
                        person_id=person_id,
                        order=member['order'],
                        character=member['character'][:200] or None,
                    ),
                )
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception:
            logger.exception(
                f'[Movie: {movie.id}] Failed saving cast: {member["name"]} '
                f'({member["id"]})'
            )

    await asyncio.gather(*[save_cast(member) for member in m['cast']])

    # Delete any cast members that don't exist anymore
    for _, member in cast.items():
        if not any(
            member.person.externals.get('themoviedb') == str(cast_member['id'])
            for cast_member in m['cast']
        ):
            logger.debug(f'[Movie: {movie.id}] Deleting cast: {member.person.name}')
            if member.person.id is not None:
                await delete_movie_cast(movie_id=movie.id, person_id=member.person.id)
