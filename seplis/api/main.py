
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .database import database
from . import exceptions
from .. import config, set_logger, config_load, logger

config_load()
set_logger(f'api-{config.data.api.port}.log')

from .routes import (
    health,
    user,
    token,
    search,
    movie,
    movie_watched,
    movie_watched_position,
    movie_stared,
    movie_play_servers,
    series,
    series_user_settings,
    series_user_stats,
    series_user_rating,
    episode_watched,
    episode_watched_position,
    episode_to_watch,
    episode_play_servers,
    last_watched_episode,
)


app = FastAPI()
app.include_router(health.router)
app.include_router(user.router)
app.include_router(token.router)
app.include_router(search.router)
app.include_router(movie.router)
app.include_router(movie_watched.router)
app.include_router(movie_watched_position.router)
app.include_router(movie_stared.router)
app.include_router(movie_play_servers.router)
app.include_router(series.router)
app.include_router(series_user_stats.router)
app.include_router(series_user_rating.router)
app.include_router(series_user_settings.router)
app.include_router(episode_watched.router)
app.include_router(episode_watched_position.router)
app.include_router(episode_to_watch.router)
app.include_router(episode_play_servers.router)
app.include_router(last_watched_episode.router)


@app.on_event('startup')
async def startup():
    if not config.data.test:
        await database.setup()
    else:
        await database.setup_test()


@app.on_event('shutdown')
async def shutdown():
    if not config.data.test:
        await database.close()
    else:
        await database.close_test()


@app.exception_handler(exceptions.API_exception)
async def unicorn_exception_handler(request: Request, exc: exceptions.API_exception):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'code': exc.code,
            'message': exc.message,
        },
    )