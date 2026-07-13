from fastapi import APIRouter

from .routes import (
    play_server_access_routes,
    play_server_invite_routes,
    play_server_register_episode_routes,
    play_server_register_movie_routes,
    play_server_routes,
    play_server_user_movie_watchlist_routes,
    play_server_user_series_watchlist_routes,
    play_servers_routes,
)

play_server_router = APIRouter(tags=['Play server'])
play_server_router.include_router(play_server_routes.router, prefix='/play-servers')
play_server_router.include_router(play_servers_routes.router, prefix='/play-servers')
play_server_router.include_router(
    play_server_access_routes.router, prefix='/play-servers'
)
play_server_router.include_router(
    play_server_invite_routes.router, prefix='/play-servers'
)
play_server_router.include_router(
    play_server_register_episode_routes.router, prefix='/play-servers'
)
play_server_router.include_router(
    play_server_register_movie_routes.router, prefix='/play-servers'
)
play_server_router.include_router(
    play_server_user_movie_watchlist_routes.router, prefix='/play-servers'
)
play_server_router.include_router(
    play_server_user_series_watchlist_routes.router, prefix='/play-servers'
)
