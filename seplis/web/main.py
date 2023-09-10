import os
from fastapi import FastAPI, Request, Body
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import EmailStr
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


@app.post('/api/token', response_model=schemas.Token)
async def login(
    request: Request,
    login: str = Body(embed=True),
    password: str = Body(embed=True),
):
    r = await client.post('/2/token', json={
        'login': login,
        'password': password,
        'grant_type': 'password',
        'client_id': config.data.client.id,
    }, headers={
        'X-Real-IP': request.headers.get('X-Real-IP', ''),
        'X-Forwarded-For': request.headers.get('X-Forwarded-For', ''),
    })
    if r.status_code >= 400:
        return JSONResponse(content=r.json(), status_code=r.status_code)
    return r.json()


@app.post('/api/signup', response_model=schemas.Token)
async def signup(
    user_data: schemas.User_create
):
    r = await client.post('/2/users', json=user_data.model_dump())
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


@app.post('/api/users/send-reset-password', status_code=204)
async def send_reset_password(
    request: Request,
    email: EmailStr = Body(..., embed=True),
):
    r = await client.post('/2/users/send-reset-password', json={'email': email}, 
        headers={
            'X-Real-IP': request.headers.get('X-Real-IP'),
            'X-Forwarded-For': request.headers.get('X-Forwarded-For'),
        }
    )
    if r.status_code >= 400:
        return JSONResponse(content=r.json(), status_code=r.status_code)


@app.post('/api/users/reset-password', status_code=204)
async def reset_password(
    request: Request,
    key: str = Body(..., embed=True, min_length=36),
    new_password: schemas.USER_PASSWORD_TYPE = Body(..., embed=True),
):
    r = await client.post('/2/users/reset-password', json={'key': key, 'new_password': new_password}, 
        headers={
            'X-Real-IP': request.headers.get('X-Real-IP'),
            'X-Forwarded-For': request.headers.get('X-Forwarded-For'),
        }
    )
    if r.status_code >= 400:
        return JSONResponse(content=r.json(), status_code=r.status_code)


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