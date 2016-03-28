import re

LEVEL_PROGRESS = -1

LEVEL_USER = 0

LEVEL_EDIT_SHOW = 2

LEVEL_EDIT_USER = 3
LEVEL_SHOW_USER_EMAIL = LEVEL_EDIT_USER

LEVEL_GOD = 6

PER_PAGE = 25

USER_TOKEN_EXPIRE_DAYS = 365

EXTERNAL_TYPES = (
    'imdb',
    'thetvdb',
    'tvmaze'
)
EXTERNAL_TYPE_NAMES = {
    'imdb': 'IMDb',
    'thetvdb': 'TheTVDB',
    'tvmaze': 'TVmaze',
}
EXTERNAL_TYPE_URLS {
    'imdb': 'http://www.imdb.com/title/{id}',
    'thetvdb': 'http://thetvdb.com/?tab=series&id={id}',
    'tvmaze': 'http://www.tvmaze.com/shows/{id}',
}
EXTERNAL_REQUIRED_TYPES = (
    'imdb',
)

INDEX_TYPES = (
    ('info', (
        'thetvdb',
        'tvmaze',
    )),
    ('episodes', (
        'thetvdb',
        'tvmaze',
    )),
    ('images', (
        'thetvdb',
        'tvmaze',
    ))
)

INDEX_TYPE_NAMES = {
    'info': 'Info',
    'episodes': 'Episodes',
    'images': 'Images',
}

IMAGE_TYPE_POSTER = 1
IMAGE_TYPES = {
    IMAGE_TYPE_POSTER: 'poster',
}

SHOW_SORT_FIELDS = (
    ('title', 'Title'),
    ('fans', 'Fans'),
    ('premiered', 'Premiered'),
)

USER_STAT_FIELDS = (
    'fan_of',
    'episodes_watched',
)

SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER = 1
SHOW_EPISODE_TYPE_SEASON_EPISODE = 2
SHOW_EPISODE_TYPE_AIR_DATE = 3
SHOW_EPISODE_TYPE = {
    SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER: 'Absolute number',
    SHOW_EPISODE_TYPE_SEASON_EPISODE: 'Season episode',
    SHOW_EPISODE_TYPE_AIR_DATE: 'Air date',
} 