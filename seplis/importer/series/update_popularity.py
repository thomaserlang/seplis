import sqlalchemy as sa
from ..themoviedb_export import get_ids
from . import importer, TheMovieDB
from ...api.database import database
from ...api import models, schemas
from ... import logger


async def update_popularity(create_series = True, create_above_popularity: float | None = 1.0):
    logger.info('Updating series popularity')
    series: dict[str, schemas.Series] = {}
    async with database.session() as session:
        result = await session.stream(sa.select(models.Series))
        async for db_series in result.yield_per(1000):
            for r in db_series:
                try:
                    s = schemas.Series.from_orm(r)
                    if s.externals.get('themoviedb'):
                        series[s.externals['themoviedb']] = s
                    if s.externals.get('imdb'):
                        series[s.externals['imdb']] = s
                except Exception as e:
                    logger.error(e)      

    async for data in get_ids('tv_series_ids'):
        try:
            id_ = str(data.id)
            if id_ in series:
                if series[id_].popularity == data.popularity:
                    continue
                logger.info(f'Updating series: {series[id_].id}, popularity: {data.popularity}')
                await models.Series.save(series_id=series[id_].id, data=schemas.Series_update(
                    popularity=data.popularity
                ))

            elif create_series and create_above_popularity != None and data.popularity >= create_above_popularity:                
                series_data = await TheMovieDB().info(id_)
                if not series_data:
                    continue
                if not series_data.externals.get('imdb'):
                    logger.debug(f'Series: {id_} missing imdb')
                    continue

                if series_data.externals['imdb'] in series:
                    logger.info(f'Adding themoviedb id {id_} to externals, popularity: {data.popularity}')
                    await models.Series.save(series_id=series[series_data.externals['imdb']].id, data=schemas.Series_update(
                        externals={'themoviedb': id_},
                        popularity=data.popularity,
                    ), patch=True)
                
                else:
                    logger.info(f'Creating themoviedb id {id_}, popularity: {data.popularity}')
                    series_data.importers = schemas.Series_importers(
                        info='themoviedb',
                        episodes='themoviedb',
                    )
                    s = await models.Series.save(data=series_data, series_id=None)
                    await importer.update_series(series=s)

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            logger.exception(f'update_popularity {data.id}')