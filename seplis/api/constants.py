LEVEL_GOD = 6

PER_PAGE = 25

USER_TOKEN_EXPIRE_DAYS = 365


SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER = 1
SHOW_EPISODE_TYPE_SEASON_EPISODE = 2
SHOW_EPISODE_TYPE_AIR_DATE = 3
SHOW_EPISODE_TYPE = {
    SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER: 'Absolute number',
    SHOW_EPISODE_TYPE_SEASON_EPISODE: 'Season episode',
    SHOW_EPISODE_TYPE_AIR_DATE: 'Air date',
} 


SCOPES = {
    'me': 'Access to your own user info',
    'user:progress': 'Manage user progress of content watched/watching',
    'user:view_lists': 'View user lists like watchlist, favorites, etc',
    'user:manage_lists': 'Manage user lists like watchlist, favorites, etc',
    'user:manage_ratings': 'Manage user\'s ratings of movies, series, etc',
    'user:view_ratings': 'View user\'s ratings of movies, series, etc',
    'user:manage_ratings': 'Manage user\'s ratings of movies, series, etc',
    'user:play': 'Access to generating a play URL for a movie or episode',
    'user:list_play_servers': 'List play servers',
    'user:manage_play_servers': 'Manage play servers',
    'user:manage_play_settings': 'Manage play settings',
    'user:view_stats': 'View user stats',
    'user:read': 'Read user info',
    'user:edit': 'Edit user info',
    'series:create': 'Create series',
    'series:edit': 'Edit series',
    'series:delete': 'Delete series',
    'series:update': 'Request series update',
    'series:manage_images': 'Manage series images',
    'movie:create': 'Create movie',
    'movie:edit': 'Edit movie',
    'movie:delete': 'Delete movie',
    'movie:update': 'Request movie update',
    'movie:manage_images': 'Manage movie images',
    'person:create': 'Create person',
    'person:edit': 'Edit person',
    'person:delete': 'Delete person',
    'person:manage_images': 'Manage person images',
}

SCOPES_ME = (
    'user:progress',
    'user:view_lists',
    'user:manage_lists',
    'user:manage_ratings',
    'user:view_ratings',
    'user:manage_ratings',
    'user:play',
    'user:list_play_servers',
    'user:manage_play_servers',
    'user:manage_play_settings',
    'user:view_stats',
    'user:read',
    'user:edit',
)