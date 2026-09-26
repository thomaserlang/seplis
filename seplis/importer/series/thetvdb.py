import json
from datetime import date
from typing import Any

import requests
from dateutil import parser

from seplis import config, logger
from seplis.api.common import validate_python
from seplis.api.image import ImageImport
from seplis.api.series import EpisodeUpdate, SeriesUpdate

from .base import SeriesImporterBase, register_importer


class Thetvdb(SeriesImporterBase):
    display_name = 'TheTVDB'
    external_name = 'thetvdb'
    supported = (
        'info',
        'episodes',
        'images',
    )
    _url = 'https://api.thetvdb.com'

    def __init__(self, apikey: str | None = None) -> None:
        super().__init__()
        self.apikey = apikey
        if not apikey:
            self.apikey = config.client.thetvdb

    def login_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            'Accept-Language': 'en',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        r = requests.post(
            self._url + '/login',
            data=json.dumps({'apikey': self.apikey}),
            headers=headers,
        )
        if r.status_code == 401:
            raise Exception(r.content)
        if r.status_code == 200:
            headers['Authorization'] = 'Bearer {}'.format(r.json()['token'])
            return headers
        raise Exception(f'Unknown status code from thetvdb: {r.status_code} {r.content}')

    async def info(self, external_id: int) -> SeriesUpdate | None:
        r = requests.get(
            self._url + f'/series/{external_id}',
            headers=self.login_headers(),
        )
        if r.status_code == 200:
            data = r.json()['data']
            externals = {
                'thetvdb': str(external_id),
            }
            if data['imdbId']:
                externals['imdb'] = data['imdbId']

            info = dict(
                title=data['seriesName'][:200],
                original_title=data['seriesName'][:200],
                plot=data['summary'][:2000] if data.get('summary') else None,
                premiered=self.parse_date(data['firstAired']),
                externals=externals,
                status=self.parse_status(data['status']),
                runtime=int(data['runtime']) if data['runtime'] else None,
                genre_names=data['genre'],
            )
            return validate_python(SeriesUpdate, info)
        return None

    async def episodes(self, external_id: int) -> list[EpisodeUpdate]:
        headers = self.login_headers()
        episodes: list[EpisodeUpdate] = []
        data = {'links': {'next': 1}}
        while data['links']['next']:
            r = requests.get(
                self._url
                + '/series/{}/episodes?page={}'.format(
                    external_id, data['links']['next']
                ),
                headers=headers,
            )
            if r.status_code == 200:
                data = r.json()
                if data['data']:
                    episodes.extend(self.parse_episodes(data['data']))
            else:
                break
        episodes = sorted(episodes, key=lambda k: (k['season'], k['episode']))
        for i, episode in enumerate(episodes):
            episode['number'] = i + 1
        return episodes

    async def images(self, external_id: int) -> list[ImageImport]:
        r = requests.get(
            self._url + f'/series/{external_id}/images/query',
            params={
                'keyType': 'poster',
                'resolution': '680x1000',
            },
            headers=self.login_headers(),
        )
        images = []
        if r.status_code == 200:
            data = r.json()['data']
            if not data:
                return images
            for image in sorted(
                data, reverse=True, key=lambda img: float(img['ratingsInfo']['average'])
            ):
                images.append(
                    ImageImport(
                        external_name='thetvdb',
                        external_id=str(image['id']),
                        source_url=f'http://thetvdb.com/banners/{image["fileName"]}',
                        type='poster',
                    )
                )
        return images

    async def incremental_updates(self) -> list[str] | None:
        timestamp = self.last_update_timestamp()
        r = requests.get(
            self._url + '/updated/query',
            params={'fromTime': timestamp},
            headers=self.login_headers(),
        )
        if r.status_code != 200:
            return None
        data = r.json()['data']
        if not data:
            return None
        return [str(s['id']) for s in data]

    def parse_status(self, status_str: str) -> int:
        if status_str == 'Ended':
            return 2
        if status_str == 'Continuing':
            return 1
        return 1

    def parse_episodes(self, episodes: list[dict[str, Any]]) -> list[EpisodeUpdate]:
        _episodes = []
        for episode in episodes:
            try:
                if episode['airedSeason'] == 0:
                    continue
                if episode['airedEpisodeNumber'] == 0:
                    continue
                if not episode['absoluteNumber']:
                    continue
                _episodes.append(self.parse_episode(episode))
            except ValueError as e:
                logger.exception(f'Parsing episode "{episode}" faild with error: {e}')
        return _episodes

    def parse_episode(self, episode: dict[str, Any]) -> EpisodeUpdate:
        data = dict(
            title=episode['episodeName'],
            original_title=episode['episodeName'],
            plot=episode.get('overview'),
            number=episode['absoluteNumber'],
            season=episode['airedSeason'],
            episode=episode['airedEpisodeNumber'],
            air_date=self.parse_date(episode['firstAired'])
            if episode['firstAired']
            else None,
        )
        return validate_python(EpisodeUpdate, data)

    def parse_date(self, date_: str | None) -> date | None:
        if not date_:
            return None
        if date_ == '0000-00-00':
            return None
        try:
            return parser.parse(date_).date()
        except ValueError:
            logger.exception(f'Parsing date "{date_}"')
        return None


register_importer(Thetvdb())
