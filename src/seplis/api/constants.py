import re

index_types_names = (
    'tvrage',
    'thetvdb',
)

index_types = [
    {
        'name': index_types_names[0],
        'match': re.compile('^[0-9]+$'),
    },
    {
        'name': index_types_names[1],
        'match': re.compile('^[0-9]+$'),
    }
]

app_level_root = 6
app_level_min = 0

level_user_email = 3

per_page = 25