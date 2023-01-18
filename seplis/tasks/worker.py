from arq import Worker
from arq.connections import RedisSettings
from .update_movie import update_movie
from .update_series import update_series
from seplis.api.database import database
from seplis import config

async def startup(ctx):
    await database.setup()

async def shutdown(ctx):
    await database.close()

def main():
    if config.data.api.redis.sentinel:
        settings = RedisSettings(
            host=config.data.api.redis.sentinel,
            sentinel=True,
            sentinel_master=config.data.api.redis.master_name,
            password=config.data.api.redis.password,
            database=config.data.api.redis.db,
        )
    else:
        settings = RedisSettings(
            host=config.data.api.redis.host,
            port=config.data.api.redis.port,
            password=config.data.api.redis.password,
            database=config.data.api.redis.db,
        )
    worker = Worker(
        functions=[
            update_movie,
            update_series,
        ],
        on_shutdown=shutdown,
        on_startup=startup,
        queue_name=config.data.api.redis.queue_name,
        job_completion_wait=config.data.api.redis.job_completion_wait,
        redis_settings=settings,
    )
    worker.run()