import json
import logging
from seplis import Client, API_error, config, config_load
config_load()

with open('/home/te/oldseplis.json', 'r') as f:
    oldids = json.loads(f.read())

client = Client(
    url=config['client']['api_url'], 
    access_token=config['client']['access_token'],
)
i = 0
shows = client.get('/shows?per_page=1000').all()
lookup = {show['externals']['imdb']: show['externals'].get('seplis-v2') for show in shows if 'imdb' in show['externals']}
for old in oldids:
    try:
        if not old['imdb']:
            continue
        if old['imdb'] not in lookup:
            externals = {
                'imdb': str(old['imdb']),
                'seplis-v2': str(old['sid']),
            }
            indices = {}
            if old['tvrage']:
                externals['tvrage'] = str(old['tvrage'])            
                indices = {
                    'info': 'tvrage',
                    'episodes': 'tvrage',
                }
            client.post('/shows', {
                'externals': externals, 
                'indices': indices
            })
        else:
            if not lookup[old['imdb']]:
                client.patch('/shows/externals/imdb/{}'.format(old['imdb']),
                    {
                        'externals': {
                            'seplis-v2': str(old['sid']),
                        }
                    }
                )
    except API_error as e:
        logging.exception('\n{}, {}'.format(old['imdb'], old['tvrage']))

    i += 1
    #print('{}/{}'.format(i, len(oldids)))