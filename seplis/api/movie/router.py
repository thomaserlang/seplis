from fastapi import APIRouter

from .routes import (
    movie_cast_routes,
    movie_image_routes,
    movie_play_server_routes,
    movie_routes,
    movie_user_favorite_routes,
    movie_user_watched_position_routes,
    movie_user_watched_routes,
    movie_user_watchlist_routes,
)

movie_router = APIRouter(tags=['Movie'])
movie_router.include_router(movie_routes.router, prefix='/movies')
movie_router.include_router(movie_cast_routes.router, prefix='/movies')
movie_router.include_router(movie_image_routes.router, prefix='/movies')
movie_router.include_router(movie_play_server_routes.router, prefix='/movies')
movie_router.include_router(movie_user_favorite_routes.router, prefix='/movies')
movie_router.include_router(movie_user_watched_routes.router, prefix='/movies')
movie_router.include_router(movie_user_watched_position_routes.router, prefix='/movies')
movie_router.include_router(movie_user_watchlist_routes.router, prefix='/movies')
