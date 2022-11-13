
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .database import database
from . import exceptions
from .. import config, set_logger, config_load, logger

config_load()
set_logger(f'api-{config.data.api.port}.log')

from .routes import (
    health,
    series_following,
    token,
    reset_password,
    search,
    user,
    user_series_following,
    user_series_watched,
    user_series_stats,
    user_series_air_dates,
    user_series_recently_aired,
    user_series_countdown,
    user_series_to_watch,
    user_movies_stared,
    user_movies_watched,
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
    episode_last_watched,
)


app = FastAPI()
app.include_router(health.router)
app.include_router(reset_password.router)
app.include_router(token.router)
app.include_router(search.router)
app.include_router(user.router)
app.include_router(user_series_following.router)
app.include_router(user_series_watched.router)
app.include_router(user_series_stats.router)
app.include_router(user_series_air_dates.router)
app.include_router(user_series_recently_aired.router)
app.include_router(user_series_countdown.router)
app.include_router(user_series_to_watch.router)
app.include_router(user_movies_stared.router)
app.include_router(user_movies_watched.router)
app.include_router(movie.router)
app.include_router(movie_watched.router)
app.include_router(movie_watched_position.router)
app.include_router(movie_stared.router)
app.include_router(movie_play_servers.router)
app.include_router(series.router)
app.include_router(series_user_stats.router)
app.include_router(series_user_rating.router)
app.include_router(series_user_settings.router)
app.include_router(series_following.router)
app.include_router(episode_watched.router)
app.include_router(episode_watched_position.router)
app.include_router(episode_to_watch.router)
app.include_router(episode_play_servers.router)
app.include_router(episode_last_watched.router)


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