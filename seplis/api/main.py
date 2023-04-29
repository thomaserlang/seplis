
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .database import database
from . import exceptions
from .. import config, set_logger, config_load

config_load()
set_logger(f'api-{config.data.api.port}.log')

from .routes import (
    health,
    movie_watchlist,
    movie_favorite,
    play_server_users_movie_watchlist,
    play_server_users_series_watchlist,
    series_recently_aired,
    series_watchlist,
    series_favorite,
    series_cast,
    token,
    reset_password,
    search,
    user,
    user_series_stats,
    user_series_countdown,
    user_series_to_watch,
    user_play_server_invite_accept,
    user_watched,
    movie,
    movie_watched,
    movie_watched_position,
    movie_play_servers,
    movie_cast,
    series,
    series_user_settings,
    series_user_stats,
    series_user_rating,
    episodes,
    episode_watched,
    episode_watched_position,
    episode_to_watch,
    episode_play_servers,
    episode_last_watched,
    episode_cast,
    play_server,
    genres,
    person,
)


app = FastAPI()
app.include_router(health.router)
app.include_router(reset_password.router)
app.include_router(token.router)
app.include_router(search.router)
app.include_router(user.router)
app.include_router(user_series_stats.router)
app.include_router(series_recently_aired.router)
app.include_router(user_series_countdown.router)
app.include_router(user_series_to_watch.router)
app.include_router(user_play_server_invite_accept.router)
app.include_router(user_watched.router)
app.include_router(movie.router)
app.include_router(movie_watched.router)
app.include_router(movie_watched_position.router)
app.include_router(movie_watchlist.router)
app.include_router(movie_favorite.router)
app.include_router(movie_play_servers.router)
app.include_router(movie_cast.router)
app.include_router(series.router)
app.include_router(series_user_stats.router)
app.include_router(series_user_rating.router)
app.include_router(series_user_settings.router)
app.include_router(series_watchlist.router)
app.include_router(series_favorite.router)
app.include_router(series_cast.router)
app.include_router(episode_watched.router)
app.include_router(episode_watched_position.router)
app.include_router(episode_to_watch.router)
app.include_router(episode_play_servers.router)
app.include_router(episode_last_watched.router)
app.include_router(episode_cast.router)
app.include_router(play_server.router)
app.include_router(genres.router)
app.include_router(person.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
async def api_exception_handler(request: Request, exc: exceptions.API_exception):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'code': exc.code,
            'message': exc.message,
            'errors': exc.errors,
            'extra': exc.extra,
        },
        headers={
            'access-control-allow-origin': '*',
        },
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            'code': 0,
            'message': 'Internal server error',
        },
        headers={
            'access-control-allow-origin': '*',
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            'code': 1001,
            'message': 'One or more fields failed validation',
            'errors': [{
                'field': e['loc'], 
                'message': e['msg'],
            } for e in exc.errors()],
            'extra': None,
        },
        headers={
            'access-control-allow-origin': '*',
        },
    )