import asyncio

from seplis import logger
from seplis.api.database import database
from seplis.api.search.actions.search_rebuild_actions import rebuild_search
from seplis.api.user.actions.token_actions import rebuild_tokens


async def rebuild() -> None:
    logger.info('Rebuilding cache/search data')
    async for key in database.redis.scan_iter(match='seplis:tokens:*'):
        await database.redis.delete(key)
    await asyncio.gather(
        rebuild_search(),
        rebuild_tokens(),
    )
    logger.info('Done')
