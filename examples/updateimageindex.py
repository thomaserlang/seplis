import seplis
import logging
seplis.config_load()

client = seplis.Client(
    url=seplis.config['client']['api_url'], 
    access_token=seplis.config['client']['access_token']
)

shows = client.get('/shows', {
    'sort': 'id',
    'per_page': 500,
    'q': '_missing_:importers.image AND _exists_:externals.thetvdb',
})
for show in shows.all():
    client.patch('/shows/{}'.format(show['id']), {
        'importers': {
            'images': 'thetvdb',
        }
    }, timeout=100)
    print('Show {} done'.format(show['id']))