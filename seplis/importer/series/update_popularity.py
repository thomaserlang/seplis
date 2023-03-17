import sqlalchemy as sa
from datetime import datetime
from ..themoviedb_export import get_ids
from . import importer, TheMovieDB
from ...api.database import database
from ...api import models, schemas
from ... import logger


async def update_popularity(create_series = True, create_above_popularity: float | None = 1.0):
    logger.info('Updating series popularity')
    series: dict[str, schemas.Series] = {}
    dt = datetime.now().date()
    async with database.session() as session:
        result = await session.stream(sa.select(models.Series).options(sa.orm.noload("*")))
        async for db_series in result.yield_per(1000):
            for r in db_series:
                if r.externals.get('themoviedb'):
                    series[r.externals['themoviedb']] = r.id
                if r.externals.get('imdb'):
                    series[r.externals['imdb']] = r.id

        ids_to_create = []
        insert_data = []
        async for data in get_ids('tv_series_ids'):
            id_ = str(data.id)
            if id_ in series:
                insert_data.append({
                    'series_id': series[id_], 
                    'popularity': data.popularity or 0,
                    'date': dt,
                })
            elif create_series and create_above_popularity != None and data.popularity >= create_above_popularity:                
                ids_to_create.append(id_)
            if len(insert_data) == 10000:
                await session.execute(sa.insert(models.Series_popularity_history).prefix_with('IGNORE').values(insert_data))
                insert_data = []
        if insert_data:
            await session.execute(sa.insert(models.Series_popularity_history).prefix_with('IGNORE').values(insert_data))

        await session.execute(sa.update(models.Series.__table__).values({
                models.Series.popularity: models.Series_popularity_history.popularity
            }).where(
                models.Series_popularity_history.date == dt,
                models.Series_popularity_history.series_id == models.Series.id,
            ),
        )
        await session.commit()
        await models.rebuild_series()

    for id_ in ids_to_create:
        try:
            series_data = await TheMovieDB().info(id_)
            if not series_data:
                continue
            if not series_data.externals.get('imdb'):
                logger.debug(f'Series: {id_} missing imdb')
                continue

            if series_data.externals['imdb'] in series:
                logger.info(f'Adding TMDb id {id_} to externals')
                await models.Series.save(series_id=series[series_data.externals['imdb']].id, data=schemas.Series_update(
                    externals={'themoviedb': id_},
                ), patch=True)        
            else:
                if not series_data.externals['imdb']:
                    continue
                logger.info(f'Creating TMDb id {id_}')
                series_data.importers = schemas.Series_importers(
                    info='themoviedb',
                    episodes='themoviedb',
                )
                s = await models.Series.save(data=series_data, series_id=None)
                await importer.update_series(series=s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            logger.error(str(e))