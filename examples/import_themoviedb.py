import requests, logging, aniso8601
from datetime import date
from seplis import Client, config, config_load
config_load()
    
client = Client(
    url=config.data.client.api_url, 
    access_token=config.data.client.access_token,
)

urls = [
    'https://api.themoviedb.org/3/movie/top_rated',
    'https://api.themoviedb.org/3/movie/popular',
]
for url in urls:
    page = 1
    while (page <= 500):
        logging.info(f'Page: {page}')
        data = requests.get(f'{url}?api_key={config.data.client.themoviedb}&language=en-US&page={page}').json()
        for movie in data['results']:
            logging.info(movie['original_language'])
            try:
                client.post('/movies', {
                    'externals': {
                        'themoviedb': movie['id'],
                    },
                })
                logging.info(f'Movie created. {movie["original_title"]} ({movie["id"]})')
            except Exception as e:
                #logging.error(str(e.message))
                pass
        page += 1