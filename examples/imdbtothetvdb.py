import requests
import xmltodict
from seplis import Client, config, config_load
config_load()

client = Client(
    url=config['client']['api_url'], 
    access_token=config['client']['access_token']
)

_thetvdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid={}'

shows = client.get('shows?sort=id&per_page=500')
for i, show in enumerate(shows.all()):
    print(i)
    if 'imdb' not in show['externals'] or i < 4683:
        continue
    r = requests.get(
        _thetvdb.format(
            show['externals']['imdb'],
        )
    )
    if r.status_code == 200:
        data = xmltodict.parse(r.content)
        if not data['Data']:
            continue
        if isinstance(data['Data']['Series'], list):
            data['Data']['Series'] = data['Data']['Series'][0]
        r = client.patch('/shows/{}'.format(show['id']), {
            'title': data['Data']['Series']['SeriesName'],
            'externals': {
                'thetvdb': str(data['Data']['Series']['id']),
            },
            'indices': {
                'info': 'thetvdb',
            }
        })