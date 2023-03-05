import requests, json
from seplis import config, logger
from seplis.api import schemas
from dateutil import parser
from .base import Series_importer_base, register_importer

class Thetvdb(Series_importer_base):
    display_name = 'TheTVDB'
    external_name = 'thetvdb'
    supported = (
        'info',
        'episodes',
        'images',
    )
    _url = 'https://api.thetvdb.com'

    def __init__(self, apikey=None):
        super().__init__()
        self.apikey = apikey
        if not apikey:
            self.apikey = config.data.client.thetvdb

    def login_headers(self):
        headers = {
            'Accept-Language': 'en',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        r = requests.post(self._url+'/login', data=json.dumps({'apikey': self.apikey}), headers=headers)
        if r.status_code == 401:
            raise Exception(r.content)
        if r.status_code == 200:
            headers['Authorization'] = 'Bearer {}'.format(r.json()['token'])
            return headers
        raise Exception('Unknown status code from thetvdb: {} {}'.format(r.status_code, r.content))

    async def info(self, external_id: int) -> schemas.Series_update:
        r = requests.get(
            self._url+'/series/{}'.format(external_id),
            headers=self.login_headers(),
        )
        if r.status_code == 200:
            data = r.json()['data']
            externals = {
                'thetvdb': str(external_id),
            }
            if data['imdbId']:
                externals['imdb'] = data['imdbId']

            return schemas.Series_update(
                title=data['seriesName'][:200],
                original_title=data['seriesName'][:200],
                plot=data['summary'][:2000] if data.get('summary') else None,
                premiered=self.parse_date(data['firstAired']),
                externals=externals,
                status=self.parse_status(data['status']),
                runtime=int(data['runtime']) if data['runtime'] else None,
                genres=data['genre'],
            )


    async def episodes(self, external_id: int) -> list[schemas.Episode_update]:
        headers = self.login_headers()
        episodes: list[schemas.Episode_update] = []
        data = {'links': { 'next': 1 } }
        while data['links']['next']:
            r = requests.get(
                self._url+'/series/{}/episodes?page={}'.format(external_id, data['links']['next']),
                headers=headers,
            )
            if r.status_code == 200:
                data = r.json()
                if data['data']:
                    episodes.extend(self.parse_episodes(data['data']))
            else:
                break
        episodes = sorted(episodes, key=lambda k: (k.season, k.episode))
        for i, episode in enumerate(episodes):
            episode.number = i + 1
        return episodes


    async def images(self, external_id: int) -> list[schemas.Image_import]:
        r = requests.get(
            self._url+'/series/{}/images/query'.format(external_id),
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
            for image in sorted(data, reverse=True, key=lambda img: float(img['ratingsInfo']['average'])):
                images.append(schemas.Image_import(
                    external_name='thetvdb',
                    external_id=str(image['id']),
                    source_url=f'http://thetvdb.com/banners/{image["fileName"]}',
                    type='poster',
                ))
        return images


    async def incremental_updates(self) -> list[str]:
        timestamp = self.last_update_timestamp()
        r = requests.get(
            self._url+'/updated/query',
            params={'fromTime': timestamp},
            headers=self.login_headers(),
        )
        if r.status_code != 200:
            return
        data = r.json()['data']
        if not data:
            return
        return [str(s['id']) for s in data]


    def parse_status(self, status_str):
        if status_str == 'Ended':
            return 2
        elif status_str == 'Continuing':
            return 1
        return 1

    def parse_episodes(self, episodes) -> list[schemas.Episode_update]:
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

    def parse_episode(self, episode) -> schemas.Episode_update:
        return schemas.Episode_update(
            title=episode['episodeName'],
            original_title=episode['episodeName'],
            plot=episode.get('overview'),
            number=episode['absoluteNumber'],
            season=episode['airedSeason'],
            episode=episode['airedEpisodeNumber'],
            air_date=self.parse_date(episode['firstAired']) if episode['firstAired'] else None,
        )

    def parse_date(self, date):
        if not date:
            return None
        if date == '0000-00-00':
            return None
        try:
            return parser.parse(date).date().isoformat()
        except ValueError as e:
            logger.exception('Parsing date "{}"'.format(date))
        return None
        
register_importer(Thetvdb())