import seplis
import logging
import requests
seplis.config_load()

client = seplis.Client(
    url=seplis.config.data.client.api_url, 
    access_token=seplis.config.data.client.access_token
)

shows = client.get('/shows', {
    'sort': 'id',
    'per_page': 500,
})
for show in shows.all():
    if 'externals' not in show:
        continue
    if 'imdb' not in show['externals']:
        continue
    r = requests.get('http://api.tvmaze.com/lookup/shows', {
        'imdb': show['externals']['imdb'],
    })
    if r.status_code != 200:
        continue
    data = r.json()
    client.patch('/shows/{}'.format(show['id']), {
        'externals': {
            'tvmaze': str(data['id']),
        }
    }, timeout=100)
    print('Show {} done'.format(show['id']))