import seplis
import logging
seplis.config_load()

client = seplis.Client(
    url=seplis.config['api']['url'], 
    access_token=seplis.config['client']['access_token']
)

shows = client.get('/shows', {
    'sort': 'id',
    'per_page': 500,
    'q': '_missing_:indices.image AND _exists_:externals.thetvdb',
})
for show in shows.all():
    client.patch('/shows/{}'.format(show['id']), {
        'indices': {
            'images': 'thetvdb',
        }
    })