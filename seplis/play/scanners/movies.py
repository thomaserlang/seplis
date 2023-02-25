import asyncio
import sqlalchemy as sa
from datetime import datetime, timezone
from seplis import config, utils, logger
from seplis.play import models
from seplis.play.client import client
from seplis.play.database import database
from seplis.api import schemas
from guessit import guessit

from .base import Play_scan

class Movie_scan(Play_scan):

    def __init__(self, scan_path, make_thumbnails: bool = False, cleanup_mode = False):
        super().__init__(
            scan_path=scan_path,
            type_='movies',
            make_thumbnails=make_thumbnails,
            cleanup_mode=cleanup_mode,
        )

    async def scan(self):
        logger.info(f'Scanning: {self.scan_path}')
        files = self.get_files()
        for f in files:
            title = self.parse(f)
            if title:
                await self.save_item(title, f)  
            else:
                logger.debug(f'"{f}" didn\'t match any pattern')

    def parse(self, filename):
        d = guessit(filename, '-t movie')
        if d and d.get('title'):
            t = d['title']
            if d.get('part'):
                t += f' Part {d["part"]}'
            if d.get('year'):
                t += f" {d['year']}"
            return t        
        logger.info(f'{filename} doesn\'t look like a movie')

    async def save_item(self, item: str, path: str):
        movie_id = await self.lookup(item)
        if not movie_id:
            return

        async with database.session() as session:
            movie = await session.scalar(sa.select(models.Movie).where(
                models.Movie.movie_id == movie_id,
                models.Movie.path == path,
            ))
            modified_time = self.get_file_modified_time(path)
            if not movie or (movie.modified_time != modified_time) or not movie.meta_data:
                metadata = await self.get_metadata(path)
                if not metadata:
                    return

                if movie:
                    sql = sa.update(models.Movie).where(
                        models.Movie.movie_id == movie_id,
                        models.Movie.path == path,
                    ).values({
                        models.Movie.meta_data: metadata,
                        models.Movie.modified_time: modified_time,
                    })
                else:
                    sql = sa.insert(models.Movie).values({
                        models.Movie.movie_id: movie_id,
                        models.Movie.path: path,
                        models.Movie.meta_data: metadata,
                        models.Movie.modified_time: modified_time,
                    })
                await session.execute(sql)
                await session.commit()

                await self.add_to_index(movie_id=movie_id)

                logger.info(f'[movie-{movie_id}] Saved {path}')
            else:
                logger.info(f'[movie-{movie_id}] Nothing changed for {path}')
            if self.make_thumbnails:
                asyncio.create_task(self.thumbnails(f'movie-{movie_id}', path))
            return True

    async def add_to_index(self, movie_id: int):
        if self.cleanup_mode:
            return

        if not config.data.play.server_id:
            logger.warn(f'[movie-{movie_id}] No server_id specified')

        r = await client.patch(f'/2/play-servers/{config.data.play.server_id}/movies', data=utils.json_dumps([
            schemas.Play_server_movie_create(
                movie_id=movie_id,
                created_at=datetime.now(tz=timezone.utc)
            )
        ]), headers={
            'Authorization': f'Secret {config.data.play.secret}',
            'Content-Type': 'application/json',
        })
        if r.status_code >= 400:
            logger.error(f'[movie-{movie_id}] Faild to add the movie to the play server index ({config.data.play.server_id}): {r.content}')
        else:
            logger.info(f'[movie-{movie_id}] Added to play server index ({config.data.play.server_id})')

    async def lookup(self, title: str):
        logger.debug(f'Looking for a movie with title: "{title}"')
        async with database.session() as session:
            movie = await session.scalar(sa.select(models.Movie_id_lookup).where(
                models.Movie_id_lookup.file_title == title,
            ))
            if not movie:
                r = await client.get('/2/search', params={
                    'title': title,
                    'type': 'movie',
                })
                r.raise_for_status()
                movies = r.json()
                if not movies:
                    logger.info(f'Didn\'t find a match for movie "{title}"')
                    return
                logger.debug(f'[movie-{movies[0]["id"]}] Found: {movies[0]["title"]}')
                movie = models.Movie_id_lookup(
                    file_title=title,
                    movie_title=movies[0]["title"],
                    movie_id=movies[0]["id"],
                    updated_at=datetime.now(tz=timezone.utc),
                )
                await session.merge(movie)
                await session.commit()
                return movie.movie_id
            else:                
                logger.debug(f'[movie-{movie.movie_id}] Found from cache: {movie.movie_title}')
                return movie.movie_id

    async def delete_item(self, item, path):        
        movie_id = await self.lookup(item)
        async with database.session() as session:
            m = await session.scalar(sa.select(models.Movie.movie_id).where(
                models.Movie.movie_id == movie_id,
                models.Movie.path == path,
            ))
            if m:
                await session.execute(sa.delete(models.Movie).where(
                    models.Movie.movie_id == movie_id,
                    models.Movie.path == path,
                ))
                await session.commit()

                await self.delete_from_index(movie_id=movie_id, session=session)

                logger.info(f'[movie-{movie_id}] Deleted movie: {item}, path: {path}')
                return True
                
        return False

    async def delete_from_index(self, movie_id: int, session):
        if self.cleanup_mode:
            return
        m = await session.scalar(sa.select(models.Movie).where(
            models.Movie.movie_id == movie_id,
        ))
        if m:
            return
        if config.data.play.server_id:
            r = await client.delete(f'/2/play-servers/{config.data.play.server_id}/movies/{movie_id}', 
            headers={
                'Authorization': f'Secret {config.data.play.secret}'
            })
            if r.status_code >= 400:
                logger.error(f'[movie-{movie_id}] Faild to inform that we have the movie: {r.content}')
            else:
                logger.info(f'[movie-{movie_id}] Added to play server index')
        else:
            logger.warn(f'[movie-{movie_id}] No server_id specified')
