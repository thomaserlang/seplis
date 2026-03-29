from arq import Worker
from arq.connections import RedisSettings

from seplis import config
from seplis.api.database import database

from .update_movie import update_movie
from .update_series import update_series


async def startup(ctx) -> None:
    await database.setup()


async def shutdown(ctx) -> None:
    await database.close()


def main() -> None:
    if config.api.redis.sentinel:
        settings = RedisSettings(
            host=config.api.redis.sentinel,
            sentinel=True,
            sentinel_master=config.api.redis.master_name,
            password=config.api.redis.password,
            database=config.api.redis.db,
        )
    else:
        settings = RedisSettings(
            host=config.api.redis.host,
            port=config.api.redis.port,
            password=config.api.redis.password,
            database=config.api.redis.db,
        )
    worker = Worker(
        functions=[
            update_movie,
            update_series,
        ],
        on_shutdown=shutdown,
        on_startup=startup,
        queue_name=config.api.redis.queue_name,
        job_completion_wait=config.api.redis.job_completion_wait,
        redis_settings=settings,
    )
    worker.run()
