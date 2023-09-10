
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
    token,
    search,
    genres,
)
from .routes.series.router import router as series_router
from .routes.movie.router import router as movie_router
from .routes.play_server.router import router as play_server_router
from .routes.person.router import router as person_router
from .routes.user.router import router as user_router


app = FastAPI(title='SEPLIS API', version='2.0')
app.include_router(token.router)
app.include_router(search.router)
app.include_router(series_router)
app.include_router(movie_router)
app.include_router(play_server_router)
app.include_router(person_router)
app.include_router(user_router)
app.include_router(genres.router)
app.include_router(health.router)


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