import sqlalchemy as sa
import httpx
import asyncio
from seplis import config, logger
from seplis.api.database import database
from seplis.api import exceptions, models, schemas

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
    await update_movie_metadata(movie)
    await update_images(movie)


async def update_movies_bulk(from_movie_id=None, do_async=False):
    logger.info('Updating movies')
    while True:
        try:
            async with database.session() as session:
                query = sa.select(models.Movie)
                if from_movie_id:
                    query = query.where(models.Movie.id >= from_movie_id)
                result = await session.stream(query)
                async for movies in result.yield_per(500):
                    for movie in movies:
                        try:
                            if not do_async:
                                await update_movie(movie=schemas.Movie.from_orm(movie))
                                from_movie_id = movie.id
                            else:
                                await database.redis_queue.enqueue_job('update_movie', movie_id=movie.Movie.id)
                        except (KeyboardInterrupt, SystemExit):
                            break
                        except exceptions.API_exception as e:
                            logger.error(e.message)
                        except Exception as e:
                            logger.exception(e)
                return
        except sa.exc.OperationalError as e:
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
            if data['page'] == data['total_pages']:
                break


async def update_movie_metadata(movie: schemas.Movie):
    logger.info(f'[Movie: {movie.id}] Updating metadata')
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
    data = await get_movie_data(themoviedb)
    await models.Movie.save(data=data, movie_id=movie.id, patch=True, overwrite_genres=True)


async def get_movie_data(themoviedb: int) -> schemas.Movie_update:
    r = await client.get(f'https://api.themoviedb.org/3/movie/{themoviedb}', params={
        'api_key': config.data.client.themoviedb,
        'append_to_response': 'alternative_titles',
    })
    if r.status_code >= 400:
        logger.error(
            f'[Movie] Failed to get movie from themoviedb ({themoviedb}): {r.content}')
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
    data.release_date = r['release_date']
    data.plot = r['overview'] or None
    data.tagline = r['tagline'] or None
    data.language = r['original_language']
    data.alternative_titles = [a['title']
                               for a in r['alternative_titles']['titles']]
    data.genres = [genre['name'] for genre in r['genres']]
    data.popularity = r['popularity']
    data.revenue = r['revenue']
    data.budget = r['budget']
    data.collection = r['belongs_to_collection']['name'] if r['belongs_to_collection'] else None
    return data


async def update_images(movie: schemas.Movie):
    logger.info(f'[Movie: {movie.id}] Updating images')
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
    logger.debug(
        f'[Movie: {movie.id}] Found {len(m["images"]["posters"])} posters')

    async def save_image(image):
        try:
            key = f'themoviedb-{image["file_path"]}'
            if key not in image_external_ids:
                source_url = f'https://image.tmdb.org/t/p/original{image["file_path"]}'
                logger.info(f'[Movie: {movie.id}] Saving image: {source_url}')
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
            key = f'themoviedb-{m["images"]["posters"][0]["file_path"]}'
        logger.info(
            f'[Movie: {movie.id}] Setting new primary image: "{image_external_ids[key].id}"')
        await models.Movie.save(data=schemas.Movie_update(
            poster_image_id=image_external_ids[key].id,
        ), movie_id=movie.id)
