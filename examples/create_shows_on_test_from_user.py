import seplis
import requests
import logging
seplis.config_load()

logging.basicConfig(level=logging.DEBUG)

client = seplis.Client(
    url=seplis.config['client']['api_url'], 
    access_token=seplis.config['client']['access_token']
)
for show in requests.get('https://api.seplis.net/1/users/2/fan-of?per_page=500').json():
    logging.info('seplis.net id: {}'.format(show['id']))
    try:    
        if 'tvmaze' not in show['externals'] or 'imdb' not in show['externals']:
            continue
        if not show['externals']['tvmaze'] or not show['externals']['imdb']:
            continue
        logging.info('Creating show: {}'.format(show['externals']['imdb']))
        show = client.post('/shows', {
            'externals': {
                'imdb': show['externals']['imdb'],
                'tvmaze': show['externals']['tvmaze'],
            },
            'importers': {
                'info': 'tvmaze',
                'episodes': 'tvmaze',
            },
        })
        client.put('/users/1/fan-of/{}'.format(show['id']))
    except Exception:
        pass