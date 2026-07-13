import asyncio

from seplis import logger
from seplis.api import elasticcreate
from seplis.api.database import database
from seplis.api.movie import rebuild_movies
from seplis.api.series import rebuild_series
from seplis.api.user.actions.token_actions import rebuild_tokens


async def rebuild() -> None:
    logger.info('Rebuilding cache/search data')
    await database.redis.flushdb()
    await elasticcreate.create_indices(database.es)
    await asyncio.gather(
        rebuild_movies(),
        rebuild_series(),
        rebuild_tokens(),
    )
    logger.info('Done')
