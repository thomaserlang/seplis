from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from seplis.logger import set_logger

from .. import config
from . import exceptions
from .database import database
from .routes import (
    genres,
    health,
    search,
    token,
)
from .routes.movie.router import router as movie_router
from .routes.person.router import router as person_router
from .routes.play_server.router import router as play_server_router
from .routes.series.router import router as series_router
from .routes.user.router import router as user_router

set_logger(f'api-{config.api.port}.log')


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    if not config.test:
        await database.setup()
    else:
        await database.setup_test()
    yield
    if not config.test:
        await database.close()
    else:
        await database.close_test()


app = FastAPI(title='SEPLIS API', version='2.0', lifespan=lifespan)
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
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(exceptions.API_exception)
async def api_exception_handler(
    request: Request, exc: exceptions.API_exception
) -> JSONResponse:
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
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
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
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            'code': 1001,
            'message': 'One or more fields failed validation',
            'errors': [
                {
                    'field': e['loc'],
                    'message': e['msg'],
                }
                for e in exc.errors()
            ],
            'extra': None,
        },
        headers={
            'access-control-allow-origin': '*',
        },
    )
