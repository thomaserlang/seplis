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
lookup = [show['externals']['imdb'] for show in shows if 'imdb' in show['externals']]        
for old in oldids:
    try:
        if old['imdb'] not in lookup:
            logging.error('created: {}'.format(old['imdb']))
            externals = {
                'imdb': str(old['imdb']),
                'seplis-v2': str(old['seplis']),
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
    except API_error as e:
        logging.exception('\n{}, {}'.format(old['imdb'], old['tvrage']))

    i += 1
    #print('{}/{}'.format(i, len(oldids)))