
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .database import database
from . import exceptions
from .. import config, set_logger, config_load, logger

config_load()
set_logger(f'api-{config.data.api.port}.log')

from .routes import (
    health,
    movie,
    series,
    user,
    token,
)

app = FastAPI()
app.include_router(health.router)
app.include_router(movie.router)
app.include_router(series.router)
app.include_router(user.router)
app.include_router(token.router)

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