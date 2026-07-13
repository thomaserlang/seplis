from fastapi import APIRouter

from .routes import (
    auth_code_routes,
    me_routes,
    reset_password_routes,
    token_routes,
    user_routes,
)

user_router = APIRouter(tags=['User'])
user_router.include_router(user_routes.router)
user_router.include_router(me_routes.router)
user_router.include_router(reset_password_routes.router)
user_router.include_router(auth_code_routes.router)
user_router.include_router(token_routes.router)
