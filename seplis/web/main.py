import os
from fastapi import FastAPI, Request, Body
from fastapi.exceptions import RequestValidationError
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


@app.post('/api/signup', response_model=schemas.Token)
async def login(
    user_data: schemas.User_create
):
    r = await client.post('/2/users', json=user_data.dict())
    if r.status_code >= 400:
        return JSONResponse(content=r.json(), status_code=r.status_code)
    
    r = await client.post('/2/token', json={
        'login': user_data.email,
        'password': user_data.password,
        'grant_type': 'password',
        'client_id': config.data.client.id,
    })
    if r.status_code >= 400:
        return JSONResponse(content=r.json(), status_code=r.status_code)
    return r.json()


@app.get('/{path:path}', response_class=HTMLResponse)
async def render(request: Request, path: str):
    return templates.TemplateResponse('ui/react.html', {
        'request': request,       
    })


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