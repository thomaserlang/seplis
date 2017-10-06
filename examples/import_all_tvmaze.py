import requests
import logging
from seplis import Client, config, config_load
config_load()

client = Client(
    url=config['client']['api_url'], 
    access_token=config['client']['access_token']
)

data = ['']
page = 1
while (len(data) != 0):
    logging.info('Page: {}'.format(page))
    data = requests.get('http://api.tvmaze.com/shows?page={}'.format(page)).json()
    for show in data:
        if not show['externals']:
            continue
        if 'imdb' not in show['externals']:
            continue
        if not show['externals']['imdb']:
            continue
        try:
            client.post('/shows', {
                'externals': {
                    'imdb': show['externals']['imdb'],
                    'tvmaze': show['id'],
                    'thetvdb': show['externals']['thetvdb'],
                },
                'importers': {
                    'info': 'tvmaze',
                    'episodes': 'tvmaze',
                }
            })
            logging.info('Show created. imdb: {} tvmaze: {}'.format(
                show['externals']['imdb'],
                show['id'],
            ))
        except Exception as e:
            logging.error(str(e))
            logging.exception('Failed to add show {}'.format(show))
    page += 1