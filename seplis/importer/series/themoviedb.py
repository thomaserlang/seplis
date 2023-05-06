from seplis.api import schemas
from .base import Series_importer_base, register_importer, client
from seplis import config

statuses = {
    'Unknown': 0,
    'Returning Series': 1,
    'Ended': 2,
    'Canceled': 3,
}

class TheMovieDB(Series_importer_base):
    display_name = 'TheMovieDB'
    external_name = 'themoviedb'
    supported = (
        'info',
        'episodes',
        'images',
        'cast',
    )

    async def info(self, external_id: str) -> schemas.Series_update:
        r = await client.get(f'https://api.themoviedb.org/3/tv/{external_id}', params={
            'api_key': config.data.client.themoviedb,
            'language': 'en-US',
            'append_to_response': 'external_ids,alternative_titles,keywords',
        })
        if r.status_code != 200:
            return
        series = r.json()

        externals = {}
        externals[self.external_name] = str(series['id'])
        if series['external_ids'].get('imdb_id'):
            externals['imdb'] = series['external_ids']['imdb_id']
        if series['external_ids'].get('tvdb_id'):
            externals['thetvdb'] = str(series['external_ids']['tvdb_id'])

        genres = [genre['name'] for genre in series['genres']]
        for keyword in series['keywords']['results']:
            if keyword['name'].lower() == 'anime':
                genres.append('Anime')

        return schemas.Series_update(
            title=series['name'][:200],
            original_title=series['original_name'][:200] if series['original_name'] else None,
            plot=series['overview'][:2000] if series['overview'] else None,
            externals=externals,
            status=statuses.get(series['status'], 0),
            runtime=series['episode_run_time'][0] if series['episode_run_time'] else None,
            genres=genres,
            premiered=series['first_air_date'] if series['first_air_date'] else None,
            language=series['original_language'] if series['original_language'] else None,
            popularity=series['popularity'],
            tagline=series['tagline'] if series['tagline'] else None,
            alternative_titles=[a['title'][:200] for a in series['alternative_titles']['results']],
        )

    async def images(self, external_id: str) -> list[schemas.Image_import]:
        r = await client.get(f'https://api.themoviedb.org/3/tv/{external_id}', params={
            'api_key': config.data.client.themoviedb,
            'language': 'en-US',
            'append_to_response': 'images',
        })
        if r.status_code != 200:
            return
        data = r.json()
        images: list[schemas.Image_import] = []
        if data['poster_path']:
            images.append(schemas.Image_import(
                external_name='themoviedb',
                external_id=data['poster_path'],
                type='poster',
                source_url=f'https://image.tmdb.org/t/p/original{data["poster_path"]}',
            ))
        images.extend([schemas.Image_import(
            external_name='themoviedb',
            external_id=image['file_path'],
            type='poster',
            source_url=f'https://image.tmdb.org/t/p/original{image["file_path"]}',
        ) for image in sorted(data['images']['posters'], reverse=True, key=lambda img: float(img['vote_average']))])
        return images

    async def episodes(self, external_id) -> list[schemas.Episode_update]:
        r = await client.get(f'https://api.themoviedb.org/3/tv/{external_id}', params={
            'api_key': config.data.client.themoviedb,
            'language': 'en-US',
        })
        if r.status_code != 200:
            return
        series = r.json()
        episodes_data = []
        for i in range(1, series['number_of_seasons']+1):
            r = await client.get(f'https://api.themoviedb.org/3/tv/{external_id}/season/{i}', params={
                'api_key': config.data.client.themoviedb,
                'language': 'en-US',
            })
            if r.status_code == 200:
                episodes_data.extend(r.json()['episodes'])
        episodes: list[schemas.Episode_update] = []
        i = 0
        for episode in episodes_data:
            if episode['season_number'] == 0:
                continue
            if episode['episode_number'] == 0:
                continue
            i += 1
            episodes.append(schemas.Episode_update(
                number=i,
                title=episode['name'][:200],
                original_title=episode['name'][:200],
                season=episode['season_number'],
                episode=episode['episode_number'],
                air_date=episode['air_date'] if episode['air_date'] else None,
                air_datetime=episode['air_date']+'T00:00:00Z' if episode['air_date'] else None,
                plot=episode['overview'][:2000] if episode['overview'] else None
            ))
        return episodes
    
    async def cast(self, external_id: str):
        r = await client.get(f'https://api.themoviedb.org/3/tv/{external_id}/aggregate_credits', params={
            'api_key': config.data.client.themoviedb,
            'language': 'en-US',
        })
        if r.status_code != 200:
            return
        data = r.json()
        return [schemas.Series_cast_person_import(
            external_name=self.external_name,
            external_id=str(person['id']),
            roles=[schemas.Series_cast_role(
                character=role['character'][:200] if role['character'] else None,
                total_episodes=role['episode_count'] if role['episode_count'] else None,
            ) for role in person['roles']],
            order=person['order'],
            total_episodes=person['total_episode_count'] if person['total_episode_count'] else None,
        ) for person in data['cast']]

    async def incremental_updates(self) -> list[str]:
        page = 1
        ids: list[str] = []
        while True:
            r = await client.get('https://api.themoviedb.org/3/tv/changes', params={
                'api_key': config.data.client.themoviedb,
                'page': page,
            })
            r.raise_for_status()
            data = r.json()
            if not data or not data['results']:
                break
            ids.extend([str(r['id']) for r in data['results']])
            if page == data['total_pages']:
                break
            page += 1
        return ids    

    async def lookup_from_imdb(self, imdb: str):
        r = await client.get(f'https://api.themoviedb.org/3/find/{imdb}', params={
            'api_key': config.data.client.themoviedb,
            'external_source': 'imdb_id',
        })
        if r.status_code == 200:
            data = r.json()
            if not data['tv_results']:
                return
            return data['tv_results'][0]['id']


register_importer(TheMovieDB())