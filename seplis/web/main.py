import os
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from seplis import config, set_logger, config_load, logger
from seplis.api import schemas

config_load()
set_logger(f'web-{config.data.web.port}.log')

from .client import client

app = FastAPI()
app.mount('/static', StaticFiles(directory=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')), name='static')
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates'),
    auto_reload=config.data.debug,
)
templates.env.globals['config'] = config

@app.get('/health')
async def health():
    return 'OK'

@app.get('/api/tvmaze-show-lookup')
async def tvmaze_lookup(tvmaze: int = None, imdb: str = None, thetvdb: int = None):
    if tvmaze:
        url = f'https://api.tvmaze.com/shows/{tvmaze}'
    else:
        url = 'https://api.tvmaze.com/lookup/shows'
    params = {}
    if imdb:
        params['imdb'] = imdb
    if thetvdb:
        params['thetvdb'] = thetvdb
    async with http_client.get(url, params=params) as r:
        return await r.json()


@app.post('/api/token', response_model=schemas.Token)
async def login(
    login: str = Body(embed=True),
    password: str = Body(embed=True),
):
    r = await client.post('/2/token', json={
        'login': login,
        'password': password,
        'grant_type': 'password',
        'client_id': config.data.client.id,
    })
    if r.status_code >= 400:
        return JSONResponse(content=r.json(), status_code=r.status_code)
    return r.json()


@app.get('/movie/{movie_id}', response_class=HTMLResponse)
@app.get('/movie/{movie_id}/{path:path}', response_class=HTMLResponse)
async def render(request: Request, movie_id: int, path: str = None):
    c = client.Async_client(config.data.client.api_url, version='1')
    movie = await c.get(f'/movies/{movie_id}')
    if not movie:
        raise HTTPException(404, 'Unknown movie')
    return templates.TemplateResponse('movie.html', {
        'request': request,
        'movie': movie.data,
    })


@app.get('/show/{series_id}', response_class=HTMLResponse)
@app.get('/show/{series_id}/{path:path}', response_class=HTMLResponse)
async def render(request: Request, series_id: int, path: str = None):
    c = client.Async_client(config.data.client.api_url, version='1')
    series = await c.get(f'/shows/{series_id}')
    if not series:
        raise HTTPException(404, 'Unknown series')
    return templates.TemplateResponse('series.html', {
        'request': request, 
        'series': series.data,
    })


@app.get('/{path:path}', response_class=HTMLResponse)
async def render(request: Request, path: str):
    return templates.TemplateResponse('ui/react.html', {
        'request': request,       
    })