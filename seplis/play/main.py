from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from seplis.logger import set_logger
from . import config_load
from seplis import config
set_logger(f'play-server-{config.data.play.port}.log')

from . import database
from .routers import health, sources, thumbnails, keep_alive, subtitle_file, transcode

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
app.mount('/files', StaticFiles(directory=config.data.play.temp_folder), name='files')

@app.on_event('startup')
async def startup():
    database.setup(config.data.play.database)

@app.on_event('shutdown')
async def shutdown():
    await database.engine.dispose()

    from seplis.play.handlers.transcoders.video import sessions, close_session
    for session in list(sessions):
        close_session(session)