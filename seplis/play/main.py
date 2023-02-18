from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from seplis.logger import set_logger
from . import config_load
from seplis import config
set_logger(f'play-server-{config.data.play.port}.log')

from .database import database
from .routers import health, sources, thumbnails, keep_alive, subtitle_file, transcode, close_session

app = FastAPI(
    title='SEPLIS Play Server'
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(health.router)
app.include_router(sources.router)
app.include_router(thumbnails.router)
app.include_router(keep_alive.router)
app.include_router(subtitle_file.router)
app.include_router(transcode.router)
app.include_router(close_session.router)
app.mount('/files', StaticFiles(directory=config.data.play.temp_folder), name='files')

@app.on_event('startup')
async def startup():
    database.setup()

@app.on_event('shutdown')
async def shutdown():
    await database.engine.dispose()

    from .transcoders.video import sessions, close_session as cs
    for session in list(sessions):
        cs(session)