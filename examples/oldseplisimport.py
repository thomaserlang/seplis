import json
import logging
from seplis import Client, API_error, config, config_load
config_load()

with open('/home/te/oldseplis.json', 'r') as f:
    oldids = json.loads(f.read())

client = Client(
    url=config['api']['url'], 
    access_token=config['client']['access_token'],
)
i = 0
for old in oldids:
    try:
        show = client.get('/shows/externals/imdb/{}'.format(old['imdb']))
        if not show:
            client.post('/shows', {
                'externals': {
                    'imdb': str(old['imdb']),
                    'tvrage': str(old['tvrage']),
                    'seplis-v2': str(old['seplis']),
                }, 
                'indices': {
                    'info': 'imdb',
                    'episodes': 'tvrage',
                }
            })
        else:            
            client.patch('/shows/{}'.format(show['id']), {
                'externals': {
                    'imdb': str(old['imdb']),
                    'tvrage': str(old['tvrage']),
                    'seplis-v2': str(old['seplis']),
                }, 
                'indices': {
                    'info': 'imdb',
                    'episodes': 'tvrage',
                }
            })
    except API_error as e:
        logging.exception('\n{}, {}'.format(old['imdb'], old['tvrage']))

    i += 1
    print('{}/{}'.format(i, len(oldids)))