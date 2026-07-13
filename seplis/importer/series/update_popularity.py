from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import noload

from ... import logger
from ...api.database import database
from ...api.series import (
    MSeries,
    MSeriesPopularityHistory,
    SeriesImporters,
    SeriesUpdate,
    rebuild_series,
    save_series,
)
from ..themoviedb_export import get_ids
from . import TheMovieDB, importer


async def update_popularity(
    create_series: bool = True, create_above_popularity: float | None = 1.0
) -> None:
    logger.info('Updating series popularity')
    series: dict[str, int] = {}
    dt = datetime.now().date()
    async with database.session() as session:
        result = await session.stream(sa.select(MSeries).options(noload('*')))
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
                insert_data.append(
                    {
                        'series_id': series[id_],
                        'popularity': data.popularity or 0,
                        'date': dt,
                    }
                )
            elif (
                create_series
                and create_above_popularity is not None
                and data.popularity >= create_above_popularity
            ):
                ids_to_create.append(id_)
            if len(insert_data) == 10000:
                await session.execute(
                    sa.insert(MSeriesPopularityHistory.__table__)  # type: ignore
                    .prefix_with('IGNORE')
                    .values(insert_data)
                )
                insert_data = []
        if insert_data:
            await session.execute(
                sa.insert(MSeriesPopularityHistory.__table__)  # type: ignore
                .prefix_with('IGNORE')
                .values(insert_data)
            )

        await session.execute(
            sa.update(MSeries.__table__).values({MSeries.popularity: 0}),  # type: ignore
        )
        await session.execute(
            sa.update(MSeries.__table__)  # type: ignore
            .values({MSeries.popularity: MSeriesPopularityHistory.popularity})
            .where(
                MSeriesPopularityHistory.date == dt,
                MSeriesPopularityHistory.series_id == MSeries.id,
            ),
        )
        await session.commit()
        await rebuild_series()

    for id_ in ids_to_create:
        try:
            series_data = await TheMovieDB().info(id_)
            if not series_data:
                continue
            externals = series_data.get('externals') or {}
            imdb = externals.get('imdb')
            if not imdb:
                logger.debug(f'Series: {id_} missing imdb')
                continue

            if imdb in series:
                logger.info(f'Adding TMDb id {id_} to externals')
                await save_series(
                    series_id=series[imdb],
                    data=SeriesUpdate(
                        externals={'themoviedb': id_},
                    ),
                    patch=True,
                )
            else:
                logger.info(f'Creating TMDb id {id_}')
                series_data['importers'] = SeriesImporters(
                    info='themoviedb',
                    episodes='themoviedb',
                )
                s = await save_series(data=series_data, series_id=None)
                await importer.update_series(series=s)
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception as e:
            logger.error(str(e))
