import logging
import requests
from seplis import Client, config, constants

client = Client(
    url=config.data.client.api_url,
    access_token=config.data.client.access_token,
)
    
# Status: 0: Canceled, 1: Released, 2: Rumored, 3: Planned, 4: In production, 5: Post production
statuses = {
    'Unknown': 0,
    'Released': 1,
    'Rumored': 2,
    'Planned': 3,
    'In production': 4,
    'Post production': 5,
    'Canceled': 6,
}

def update_movie(movie_id=None, movie=None):
    try:
        if movie_id:
            movie = client.get(f'/movies/{movie_id}')
        update_movie_metadata(movie)
        update_images(movie)
    except:
        logging.exception(f'update movie {movie_id}')

def update_incremental():
    page = 1
    logging.info('Incremental update running')
    while True:
        r = requests.get('https://api.themoviedb.org/3/movie/changes', params={
            'api_key': config.data.client.themoviedb,
            'page': page,
        })
        r.raise_for_status()
        data = r.json()
        for r in data['results']:
            movie = client.get(f'/movies/external/themoviedb/{r["id"]}')
            if movie:
                update_movie(movie=movie)
            else:
                logging.debug(f'Didn\'t find TheMovieDB: {r["id"]}')
        if data['page'] == data['total_pages']:
            break            

def update_movie_metadata(movie):
    logging.info(f'[Movie: {movie["id"]}] Updating metadata')
    data = {}
    if not movie['externals'].get('themoviedb'):
        if not movie['externals'].get('imdb'):
            logging.info(f'[Movie: {movie["id"]}] externals.imdb doesn\'t exist')
            return
        r = requests.get(
            f'https://api.themoviedb.org/3/find/{movie["externals"]["imdb"]}',
            params={
                'api_key': config.data.client.themoviedb,
                'external_source': 'imdb_id',
            }
        )
        if r.status_code >= 400:
            logging.error(f'[Movie: {movie["id"]}] Failed to get movie "{movie["externals"]["imdb"]}" by imdb: {r.content}')
            return
        r = r.json()
        if not r['movie_results']:
            logging.warning(f'[Movie: {movie["id"]}] No movie found with imdb: "{movie["externals"]["imdb"]}"')
            return
        data.setdefault('externals', {})['themoviedb'] = r['movie_results'][0]['id']
        movie['externals']['themoviedb'] = r['movie_results'][0]['id']

    r = requests.get(f'https://api.themoviedb.org/3/movie/{movie["externals"]["themoviedb"]}', params={
        'api_key': config.data.client.themoviedb,
        'append_to_response': 'alternative_titles',
    })
    if r.status_code >= 400:
        logging.error(f'[Movie: {movie["id"]}] Failed to get movie from themoviedb: {r.content}')
        return
    r = r.json()
    
    if movie['title'] != r['title']:
        data['title'] = r['title']
    
    if movie['status'] != statuses.get(r['status'], 0):
        data['status'] = statuses.get(r['status'], 0)

    if movie['runtime'] != r['runtime']:
        data['runtime'] = r['runtime']

    if movie['release_date'] != r['release_date']:
        data['release_date'] = r['release_date']

    if movie['description'] != r['overview']:
        data['description'] = r['overview']    
    
    if movie['language'] != r['original_language']:
        data['language'] = r['original_language']

    alternative_titles = []
    if r['alternative_titles']:
        for a in r['alternative_titles']['titles']:
            if a['title'] not in movie['alternative_titles']:
                alternative_titles.append(a['title'])

    if alternative_titles:
        data['alternative_titles'] = alternative_titles

    if not data:
        logging.info(f'[Movie: {movie["id"]}] Nothing new')
        return    
    logging.info(f'[Movie: {movie["id"]}] Saving: {data}')

    movie = client.patch(f'/movies/{movie["id"]}', data)

def update_images(movie):
    logging.info(f'[Movie: {movie["id"]}] Updating images')
    if not movie['externals'].get('themoviedb'):
        logging.error(f'Missing externsl.themoviedb for movie: "{movie["id"]}"')
        return

    images = client.get(f'/movies/{movie["id"]}/images?per_page=500').all()
    image_external_ids = {
        f'{i["external_name"]}-{i["external_id"]}': i
            for i in images
    }

    r = requests.get(f'https://api.themoviedb.org/3/movie/{movie["externals"]["themoviedb"]}/images', params={
        'api_key': config.data.client.themoviedb,
        'language': 'en',
    })
    if r.status_code >= 400:
        logging.error(f'[Movie: {movie["id"]}] Failed to get movie images for "{movie["externals"]["themoviedb"]}" from themoviedb: {r.content}')
        return
    imp_images = r.json()['posters']
    for image in sorted(imp_images, reverse=True, key=lambda img: float(img['vote_average'])):
        si = None
        try:   
            key = f'themoviedb-{image["file_path"]}'
            if round(image['aspect_ratio'], 2) not in (0.67, 0.68):
                logging.info(f'[Movie: {movie["id"]}] Skipping image: {image["file_path"]}, aspect ratio: {round(image["aspect_ratio"])}')
                continue
            if key not in image_external_ids:
                source_url = f'https://image.tmdb.org/t/p/original{image["file_path"]}'
                logging.info(f'[Movie: {movie["id"]}] Saving image: {source_url}')
                si = client.post(f'/movies/{movie["id"]}/images', json={
                    'external_name': 'themoviedb',
                    'external_id': image["file_path"],
                    'source_url': source_url,
                    'source_title': 'TheMovieDB',
                    'type': constants.IMAGE_TYPE_POSTER,
                })
                image_external_ids[key] = si
            if key in image_external_ids:
                if not image_external_ids[key]['hash']:
                    r = requests.get(si['source_url'], stream=True)
                    r.raise_for_status()
                    client.put(f'/movies/{movie["id"]}/images/{si["id"]}/data', files={
                        si['source_url'][si['source_url'].rfind("/")+1:]: r.raw,
                    })
                if not movie.get('poster_image'):
                    logging.info(f'[Movie: {movie["id"]}] Setting new primary image: "{image_external_ids[key]["id"]}"')
                    movie = client.patch(f'/movies/{movie["id"]}', {
                        'poster_image_id': image_external_ids[key]["id"],
                    })
        except:
            logging.exception(f'[Movie: {movie["id"]}] Failed saving image')
            if si:
                client.delete(f'/movies/{movie["id"]}/images/{si["id"]}')