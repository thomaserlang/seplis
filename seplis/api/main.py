from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from seplis.logger_utils import set_logger

from .. import config
from . import exceptions
from .database import database
from .genre.router import router as genre_router
from .health.router import router as health_router
from .movie.router import movie_router
from .person.router import person_router
from .play_server.router import play_server_router
from .search.router import router as search_router
from .series.router import series_router
from .user.router import user_router
from .user_watched.router import user_watched_router

set_logger(f'api-{config.api.port}.log')


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await database.setup()
    yield
    await database.close()


app = FastAPI(title='SEPLIS API', version='2.0', lifespan=lifespan)
app.include_router(search_router, prefix='/2')
app.include_router(series_router, prefix='/2')
app.include_router(movie_router, prefix='/2')
app.include_router(play_server_router, prefix='/2')
app.include_router(person_router, prefix='/2')
app.include_router(user_router, prefix='/2')
app.include_router(user_watched_router, prefix='/2')
app.include_router(genre_router, prefix='/2')
app.include_router(health_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(exceptions.APIException)
async def api_exception_handler(
    request: Request, exc: exceptions.APIException
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
