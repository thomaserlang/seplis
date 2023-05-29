import sqlalchemy as sa
import httpx
import asyncio
from ... import config, logger
from ...api.database import database
from ...api import exceptions, models, schemas
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


async def update_movie(movie_id=None, movie: schemas.Movie | None = None):
    if movie_id:
        async with database.session() as session:
            result = await session.scalar(sa.select(models.Movie).where(models.Movie.id == movie_id))
            if not result:
                logger.error(f'Unknown movie: {movie_id}')
                return
            movie = schemas.Movie.from_orm(result)
    if not movie:
        logger.error(f'Unknown movie')
        return
    logger.info(f'[Movie: {movie.id}] Updating')
    await update_movie_metadata(movie)
    await update_images(movie)
    await update_cast(movie)


async def update_movies_bulk(from_movie_id=None, do_async=False):
    logger.info('Updating movies')
    async with database.session() as session:
        query = sa.select(models.Movie)
        if from_movie_id:
            query = query.where(models.Movie.id >= from_movie_id)
        movies = await session.scalars(query)
        for movie in movies:
            try:
                if not do_async:
                    await update_movie(movie=schemas.Movie.from_orm(movie))
                else:
                    await database.redis_queue.enqueue_job('update_movie', movie_id=movie.Movie.id)
            except (KeyboardInterrupt, SystemExit):
                break
            except exceptions.API_exception as e:
                logger.error(e.message)
            except Exception as e:
                logger.exception(e)


async def update_incremental():
    page = 1
    logger.info('Incremental update running')
    while True:
        r = await client.get('https://api.themoviedb.org/3/movie/changes', params={
            'api_key': config.data.client.themoviedb,
            'page': page,
        })
        r.raise_for_status()
        data = r.json()
        if not data or not data['results']:
            break
        async with database.session() as session:
            for r in data['results']:
                logger.info(f'Checking: {r["id"]}')
                result = await session.scalar(sa.select(models.Movie).where(
                    models.Movie_external.title == 'themoviedb',
                    models.Movie_external.value == r['id'],
                    models.Movie.id == models.Movie_external.movie_id,
                ))
                if not result:
                    continue
                movie = schemas.Movie.from_orm(result)
                if movie:
                    try:
                        await update_movie(movie=movie)
                    except (KeyboardInterrupt, SystemExit):
                        break
                    except exceptions.API_exception as e:
                        logger.error(e.message)
                    except Exception as e:
                        logger.exception(e)
            if page == data['total_pages']:
                break
            page += 1


async def update_movie_metadata(movie: schemas.Movie):
    logger.debug(f'[Movie: {movie.id}] Updating metadata')
    themoviedb = movie.externals.get('themoviedb')
    if not themoviedb:
        if not movie.externals.get('imdb'):
            logger.info(f'[Movie: {movie.id}] externals.imdb doesn\'t exist')
            return
        r = await client.get(
            f'https://api.themoviedb.org/3/find/{movie.externals["imdb"]}',
            params={
                'api_key': config.data.client.themoviedb,
                'external_source': 'imdb_id',
            }
        )
        if r.status_code >= 400:
            logger.error(
                f'[Movie: {movie.id}] Failed to get movie "{movie.externals["imdb"]}" by imdb: {r.content}')
            return
        r = r.json()
        if not r['movie_results']:
            logger.warning(
                f'[Movie: {movie.id}] No movie found with imdb: "{movie.externals["imdb"]}"')
            return
        themoviedb = r['movie_results'][0]['id']
    new_data = await get_movie_data(themoviedb)
    if not new_data:
        return
    old_data = movie.to_request()
    data = compare(new_data, old_data, skip_keys=['alternative_titles'])
    missing_alternative_titles = [x for x in new_data.alternative_titles if x not in old_data.alternative_titles]
    if new_data.alternative_titles and missing_alternative_titles:
        data['alternative_titles'] = new_data.alternative_titles
    if data:
        logger.debug(f'[Movie: {movie.id}] Updating: {data}')
        await models.Movie.save(data=schemas.Movie_update.parse_obj(data), movie_id=movie.id, patch=True, overwrite_genres=True)
    else:
        logger.debug(f'[Movie: {movie.id}] No metadata updates')


async def get_movie_data(themoviedb: int) -> schemas.Movie_update:
    r = await client.get(f'https://api.themoviedb.org/3/movie/{themoviedb}', params={
        'api_key': config.data.client.themoviedb,
        'append_to_response': 'alternative_titles,keywords',
    })
    if r.status_code >= 400:
        logger.info(
            f'[Movie] Failed to get movie from themoviedb ({themoviedb}): {r.content}')
        error = r.json()
        if error['status_code'] == 34:
            m = await models.Movie.get_from_external('themoviedb', themoviedb)
            if m:
                await models.Movie.delete(movie_id=m.id)
                logger.info(f'Movie not found on TMDB, deleteing: TMDB {themoviedb} from the database')
            return
        return
    r = r.json()

    data = schemas.Movie_update()
    data.externals = {
        'themoviedb': themoviedb,
    }
    if r.get('imdb_id'):
        data.externals['imdb'] = r['imdb_id']
    data.title = r['title']
    data.original_title = r['original_title']
    data.status = statuses.get(r['status'], 0)
    data.runtime = r['runtime']
    data.release_date = r['release_date'] or None
    data.plot = r['overview'] or None
    data.tagline = r['tagline'] or None
    data.language = r['original_language']
    if 'alternative_titles' in r:
        data.alternative_titles = [a['title'][:200] for a in r['alternative_titles']['titles']]
    genres = [genre['name'] for genre in r['genres']]
    if r.get('keywords'):
        for keyword in r['keywords'].get('keywords', []):
            if keyword['name'].lower() == 'anime':
                genres.append('Anime')
    data.genre_names = genres
    data.popularity = r['popularity']
    data.revenue = r['revenue']
    data.budget = r['budget']
    data.collection_name = r['belongs_to_collection']['name'] if r['belongs_to_collection'] else None
    return data


async def update_images(movie: schemas.Movie):
    logger.debug(f'[Movie: {movie.id}] Updating images')
    if not movie.externals.get('themoviedb'):
        logger.error(f'Missing externals.themoviedb for movie: "{movie.id}"')
        return

    async with database.session() as session:
        result = await session.scalars(sa.select(models.Image).where(
            models.Image.relation_type == 'movie',
            models.Image.relation_id == movie.id,
        ))
        image_external_ids = {
            f'{image.external_name}-{image.external_id}': schemas.Image.from_orm(image) for image in result}

    r = await client.get(f'https://api.themoviedb.org/3/movie/{movie.externals["themoviedb"]}', params={
        'append_to_response': 'images',
        'api_key': config.data.client.themoviedb,
    })
    if r.status_code >= 400:
        logger.error(
            f'[Movie: {movie.id}] Failed to get movie images for "{movie.externals["themoviedb"]}" from themoviedb: {r.content}')
        return
    m = r.json()
    if 'images' not in m:
        logger.debug(f'[Movie: {movie.id}] Didn\'t find any images')
        return
    logger.debug(
        f'[Movie: {movie.id}] Found {len(m["images"]["posters"])} posters')

    async def save_image(image):
        try:
            key = f'themoviedb-{image["file_path"]}'
            if key not in image_external_ids:
                source_url = f'https://image.tmdb.org/t/p/original{image["file_path"]}'
                logger.debug(f'[Movie: {movie.id}] Saving image: {source_url}')
                saved_image = await models.Image.save(
                    relation_type='movie',
                    relation_id=movie.id,
                    image_data=schemas.Image_import(
                        external_name='themoviedb',
                        external_id=image['file_path'],
                        type='poster',
                        source_url=source_url,
                    )
                )
                image_external_ids[key] = saved_image
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            logger.exception(f'[Movie: {movie.id}] Failed saving image')

    await asyncio.gather(*[save_image(image) for image in m['images']['posters']])

    if not movie.poster_image and m['poster_path']:
        key = f'themoviedb-{m["poster_path"]}'
        if key not in image_external_ids:
            key = f'themoviedb-{m["poster_path"]}'
            if key not in image_external_ids:
                logger.info('No image to set as new primary')
                return
        logger.info(
            f'[Movie: {movie.id}] Setting new primary image: {image_external_ids[key].id}')
        await models.Movie.save(data=schemas.Movie_update(
            poster_image_id=image_external_ids[key].id,
        ), movie_id=movie.id)


async def update_cast(movie: schemas.Movie):
    logger.debug(f'[Movie: {movie.id}] Updating cast')
    if not movie.externals.get('themoviedb'):
        logger.error(f'Missing externals.themoviedb for movie: "{movie.id}"')
        return

    # Get existing cast
    async with database.session() as session:
        result = await session.scalars(sa.select(models.Movie_cast).where(
            models.Movie_cast.movie_id == movie.id,
        ))
        cast: dict[str, schemas.Movie_cast_person] = {f'themoviedb-{cast.person.externals["themoviedb"]}': 
                schemas.Movie_cast_person.from_orm(cast) for cast in result \
                    if cast.person.externals.get("themoviedb")}

    r = await client.get(f'https://api.themoviedb.org/3/movie/{movie.externals["themoviedb"]}/credits', params={
        'api_key': config.data.client.themoviedb,
        'language': 'en-US',
    })
    if r.status_code >= 400:
        logger.error(
            f'[Movie: {movie.id}] Failed to get movie credits for "{movie.externals["themoviedb"]}" from themoviedb: {r.content}')
        return
    m = r.json()
    if 'cast' not in m:
        logger.info(f'[Movie: {movie.id}] Didn\'t find any cast')
        return
    logger.debug(f'[Movie: {movie.id}] Found {len(m["cast"])} cast members')

    async def save_cast(member):
        try:
            key = f'themoviedb-{member["id"]}'
            if key not in cast:
                # Create the person if they don't "exist"
                person = await models.Person.get_from_external('themoviedb', member['id'])
                if not person:
                    person = await create_person('themoviedb', member['id'])
                cast[key] = schemas.Movie_cast_person(
                    movie_id=movie.id,
                    person=person,
                    character=None,
                )

            if cast[key].character != member['character'][:200] or \
                cast[key].order != member['order']:
                logger.debug(f'[Movie: {movie.id}] Saving cast: {member["name"]} ({member["id"]})')
                await models.Movie_cast.save(
                    data=schemas.Movie_cast_person_update(
                        movie_id=movie.id,
                        person_id=cast[key].person.id,
                        order=member['order'],
                        character=member['character'][:200] or None,
                    )
                )
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            logger.exception(f'[Movie: {movie.id}] Failed saving cast: {member["name"]} ({member["id"]})')

    await asyncio.gather(*[save_cast(member) for member in m['cast']])

    # Delete any cast members that don't exist anymore
    for key, member in cast.items():
        if not any(member.person.externals.get('themoviedb') == str(m['id']) for m in m['cast']):
            logger.debug(f'[Movie: {movie.id}] Deleting cast: {member.person.name}')
            await models.Movie_cast.delete(movie_id=movie.id, person_id=member.person.id)