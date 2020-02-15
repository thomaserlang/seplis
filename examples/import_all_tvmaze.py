import requests, logging, aniso8601
from datetime import date
from seplis import Client, config, config_load, logger
config_load()

logger.logger.set_logger('test.log')
    
client = Client(
    url=config['client']['api_url'], 
    access_token=config['client']['access_token']
)

imdbids = []
shows = client.get('shows?sort=id&per_page=500')
for show in shows.all():
    imdbids.append(show['externals'].get('imdb'))

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
        if str(show['externals']['imdb']) in imdbids:
            continue
        if show['language'] != 'English':
            continue
        if show['premiered']:
            if aniso8601.parse_date(show['premiered']) < date(2018, 1, 1):
                continue
        else:
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
            #logging.error(str(e.message))
            pass
    page += 1