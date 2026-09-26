import requests

from seplis.api.common import validate_python
from seplis.api.image import ImageImport
from seplis.api.series import EpisodeUpdate, SeriesUpdate

from .base import SeriesImporterBase, register_importer


class Tvmaze(SeriesImporterBase):
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

    async def info(self, external_id: str) -> SeriesUpdate | None:
        r = requests.get(self._url.format(external_id=external_id))
        if r.status_code != 200:
            return None
        series = r.json()
        externals: dict[str, str | None] = {
            key: str(series['externals'][key])
            for key in series['externals']
            if series['externals'][key]
        }
        externals[self.external_name] = str(series['id'])
        data = dict(
            title=series['name'][:200],
            original_title=series['name'][:200],
            plot=series['summary'][:2000]
            .replace('<p>', '')
            .replace('</p>', '')
            .replace('<b>', '')
            .replace('</b>', '')
            if series['summary']
            else None,
            externals=externals,
            status=self.parse_status(series['status']),
            runtime=series['runtime'],
            genre_names=series['genres'],
            premiered=series['premiered'] or None,
            language=series['language'],
        )
        return validate_python(SeriesUpdate, data)

    @staticmethod
    def parse_status(status_str: str) -> int:
        if status_str.lower() == 'ended':
            return 2
        return 1

    async def images(self, external_id: str) -> list[ImageImport] | None:
        r = requests.get(self._url.format(external_id=external_id))
        if r.status_code != 200:
            return None
        data = r.json()
        if not data['image']:
            return None
        if 'original' not in data['image']:
            return None
        if not data['image']['original']:
            return None
        return [
            ImageImport(
                external_name='tvmaze',
                external_id=str(data['id']),
                source_url=data['image']['original'],
                type='poster',
            )
        ]

    async def episodes(self, external_id: str) -> list[EpisodeUpdate] | None:
        r = requests.get(self._url_episodes.format(external_id=external_id))
        if r.status_code != 200:
            return None
        data = r.json()
        episodes: list[EpisodeUpdate] = []
        i = 0
        for episode in data:
            if episode['season'] == 0:
                continue
            if episode['number'] == 0:
                continue
            i += 1
            episodes.append(
                EpisodeUpdate(
                    number=i,
                    title=episode['name'][:200],
                    original_title=episode['name'][:200],
                    season=episode['season'],
                    episode=episode['number'],
                    air_date=episode['airdate'] if episode['airdate'] else None,
                    air_datetime=episode['airstamp'] if episode['airstamp'] else None,
                    plot=episode['summary'][:2000]
                    .replace('<p>', '')
                    .replace('</p>', '')
                    .replace('<b>', '')
                    .replace('</b>', '')
                    if episode['summary']
                    else None,
                )
            )
        return validate_python(list[EpisodeUpdate], episodes)

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
