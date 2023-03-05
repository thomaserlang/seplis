import requests
from seplis.api import schemas
from .base import Series_importer_base, register_importer
from seplis import logger

class Tvmaze(Series_importer_base):
    display_name = 'TVmaze'
    external_name = 'tvmaze'
    supported = (
        'info',
        'episodes',
        'images',
    )
    
    _url = 'http://api.tvmaze.com/shows/{external_id}'
    _url_episodes = 'http://api.tvmaze.com/shows/{external_id}/episodes'
    _url_update = 'http://api.tvmaze.com/updates/shows'

    async def info(self, external_id: str) -> schemas.Series_update:
        r = requests.get(self._url.format(external_id=external_id))
        if r.status_code != 200:
            return
        series = r.json()
        externals = {key: str(series['externals'][key]) for key in series['externals'] if series['externals'][key]}
        externals[self.external_name] = str(series['id'])
        return schemas.Series_update(
            title=series['name'][:200],
            original_title=series['name'][:200],
            plot=series['summary'][:2000].replace('<p>', '').replace('</p>', '').replace('<b>', '').replace('</b>', '') if series['summary'] else None,
            externals=externals,
            status=self.parse_status(series['status']),
            runtime=series['runtime'],
            genres=series['genres'],
            premiered=series['premiered'],
            language=series['language'],
        )

    @staticmethod
    def parse_status(status_str):
        if status_str.lower() == 'ended':
            return 2
        return 1


    async def images(self, external_id: str) -> list[schemas.Image_import]:
        r = requests.get(self._url.format(external_id=external_id))
        if r.status_code != 200:
            return
        data = r.json()
        if not data['image']:
            return
        if 'original' not in data['image']:
            return
        if not data['image']['original']:
            return
        return [schemas.Image_import(
            external_name='tvmaze',
            external_id=str(data['id']),
            source_url=data['image']['original'],
            type='poster',
        )]


    async def episodes(self, external_id) -> list[schemas.Episode_update]:
        r = requests.get(self._url_episodes.format(external_id=external_id))
        if r.status_code != 200:
            return
        data = r.json()
        episodes: list[schemas.Episode_update] = []
        i = 0
        for episode in data:
            if episode['season'] == 0:
                continue
            if episode['number'] == 0:
                continue
            i += 1
            episodes.append(schemas.Episode_update(
                number=i,
                title=episode['name'][:200],
                original_title=episode['name'][:200],
                season=episode['season'],
                episode=episode['number'],
                air_date=episode['airdate'] if episode['airdate'] else None,
                air_datetime=episode['airstamp'] if episode['airstamp'] else None,
                plot=episode['summary'][:2000].replace('<p>', '').replace('</p>', '').replace('<b>', '').replace('</b>', '') if episode['summary'] else None
            ))
        return episodes

    async def incremental_updates(self) -> list[str]:
        last_timestamp = self.last_update_timestamp()
        r = requests.get(self._url_update)
        if r.status_code != 200:
            return []
        shows = r.json()
        ids = []
        for key in shows:
            if shows[key] < last_timestamp:
                continue
            ids.append(key)
        return ids

register_importer(Tvmaze())