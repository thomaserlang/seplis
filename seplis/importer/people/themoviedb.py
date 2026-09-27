from seplis import config
from seplis.api.common import validate_python
from seplis.api.image import ImageImport
from seplis.api.person import PersonUpdate

from .base import ImporterBase, client, register_importer


class TheMovieDB(ImporterBase):
    display_name = 'TheMovieDB'
    external_name = 'themoviedb'
    supported = (
        'info',
        'images',
    )

    async def info(self, external_id: str) -> PersonUpdate | None:
        r = await client.get(
            f'https://api.themoviedb.org/3/person/{external_id}',
            params={
                'api_key': config.client.themoviedb,
                'language': 'en-US',
            },
        )
        if r.status_code != 200:
            return None
        person = r.json()

        externals = {}
        externals[self.external_name] = str(person['id'])
        if person.get('imdb_id'):
            externals['imdb'] = person['imdb_id']

        data = dict(
            name=person['name'][:500],
            also_known_as=[aka[:500] for aka in person['also_known_as']]
            if person['also_known_as']
            else [],
            birthday=person['birthday'] if person['birthday'] else None,
            deathday=person['deathday'] if person['deathday'] else None,
            gender=person['gender'],
            biography=person['biography'][:2000] if person['biography'] else None,
            place_of_birth=person['place_of_birth'][:100]
            if person['place_of_birth']
            else None,
            popularity=person['popularity'],
            externals=externals,
        )
        return validate_python(PersonUpdate, data)

    async def images(self, external_id: str) -> list[ImageImport] | None:
        r = await client.get(
            f'https://api.themoviedb.org/3/person/{external_id}',
            params={
                'api_key': config.client.themoviedb,
                'language': 'en-US',
            },
        )
        if r.status_code != 200:
            return None
        person = r.json()
        images: list[ImageImport] = []
        if person['profile_path']:
            images.append(
                ImageImport(
                    external_name='themoviedb',
                    external_id=person['profile_path'],
                    type='profile',
                    source_url=(
                        f'https://image.tmdb.org/t/p/original{person["profile_path"]}'
                    ),
                )
            )
        return images

    async def incremental_updates(self) -> list[str]:
        page = 1
        ids: list[str] = []
        while True:
            r = await client.get(
                'https://api.themoviedb.org/3/person/changes',
                params={
                    'api_key': config.client.themoviedb,
                    'page': page,
                },
            )
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
