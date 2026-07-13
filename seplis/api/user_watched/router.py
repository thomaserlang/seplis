from fastapi import APIRouter

from .routes import user_watched_routes

user_watched_router = APIRouter(tags=['User'])
user_watched_router.include_router(user_watched_routes.router)
