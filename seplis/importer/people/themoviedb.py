from seplis.api import schemas
from .base import Importer_base, register_importer, client
from seplis import config


class TheMovieDB(Importer_base):
    display_name = 'TheMovieDB'
    external_name = 'themoviedb'
    supported = (
        'info',
        'images',
    )

    async def info(self, external_id: str) -> schemas.Person_update:
        r = await client.get(f'https://api.themoviedb.org/3/person/{external_id}', params={
            'api_key': config.data.client.themoviedb,
            'language': 'en-US',
        })
        if r.status_code != 200:
            return
        person = r.json()

        externals = {}
        externals[self.external_name] = str(person['id'])
        if person.get('imdb_id'):
            externals['imdb'] = person['imdb_id']

        return schemas.Person_update(
            name=person['name'][:500],
            also_known_as=[aka[:500] for aka in person['also_known_as']] if person['also_known_as'] else [],
            birthday=person['birthday'] if person['birthday'] else None,
            deathday=person['deathday'] if person['deathday'] else None,
            gender=person['gender'],
            biography=person['biography'][:2000] if person['biography'] else None,
            place_of_birth=person['place_of_birth'][:100] if person['place_of_birth'] else None,
            popularity=person['popularity'],
            externals=externals,
        )

    async def images(self, external_id: str) -> list[schemas.Image_import]:
        r = await client.get(f'https://api.themoviedb.org/3/person/{external_id}', params={
            'api_key': config.data.client.themoviedb,
            'language': 'en-US',
        })
        if r.status_code != 200:
            return
        person = r.json()
        images: list[schemas.Image_import] = []
        if person['profile_path']:
            images.append(schemas.Image_import(
                external_name='themoviedb',
                external_id=person['profile_path'],
                type='profile',
                source_url=f'https://image.tmdb.org/t/p/original{person["profile_path"]}',
            ))
        return images
    
    async def incremental_updates(self) -> list[str]:
        page = 1
        ids: list[str] = []
        while True:
            r = await client.get('https://api.themoviedb.org/3/person/changes', params={
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


register_importer(TheMovieDB())