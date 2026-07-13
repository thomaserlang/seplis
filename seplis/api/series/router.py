from fastapi import APIRouter

from .routes import (
    episode_cast_routes,
    episode_last_watched_routes,
    episode_play_server_routes,
    episode_routes,
    episode_to_watch_routes,
    episode_watched_position_routes,
    episode_watched_routes,
    episodes_routes,
    series_cast_routes,
    series_image_routes,
    series_recently_aired_routes,
    series_routes,
    series_user_all_stats_routes,
    series_user_countdown_routes,
    series_user_favorite_routes,
    series_user_rating_routes,
    series_user_settings_routes,
    series_user_stats_routes,
    series_user_to_watch_routes,
    series_user_watchlist_routes,
)

series_router = APIRouter(tags=['Series'])
series_router.include_router(series_recently_aired_routes.router, prefix='/series')
series_router.include_router(series_user_all_stats_routes.router, prefix='/series')
series_router.include_router(series_user_countdown_routes.router, prefix='/series')
series_router.include_router(series_user_to_watch_routes.router, prefix='/series')
series_router.include_router(series_routes.router, prefix='/series')
series_router.include_router(series_cast_routes.router, prefix='/series')
series_router.include_router(series_image_routes.router, prefix='/series')
series_router.include_router(series_user_favorite_routes.router, prefix='/series')
series_router.include_router(series_user_rating_routes.router, prefix='/series')
series_router.include_router(series_user_settings_routes.router, prefix='/series')
series_router.include_router(series_user_stats_routes.router, prefix='/series')
series_router.include_router(series_user_watchlist_routes.router, prefix='/series')
series_router.include_router(episode_routes.router, prefix='/series')
series_router.include_router(episodes_routes.router, prefix='/series')
series_router.include_router(episode_cast_routes.router, prefix='/series')
series_router.include_router(episode_last_watched_routes.router, prefix='/series')
series_router.include_router(episode_play_server_routes.router, prefix='/series')
series_router.include_router(episode_to_watch_routes.router, prefix='/series')
series_router.include_router(episode_watched_routes.router, prefix='/series')
series_router.include_router(episode_watched_position_routes.router, prefix='/series')
